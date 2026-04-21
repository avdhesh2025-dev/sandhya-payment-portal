import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import urllib.parse
import requests
import time
import math

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# 1. Page Configuration (A4 Scale & Fixed Layout)
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="centered", initial_sidebar_state="collapsed")

# 🟢 GLOBAL FUNCTIONS 
def go_to(p): 
    st.session_state.current_page = p
    st.session_state.kb_retailer = None
    st.session_state.kb_action = None
    st.query_params["page"] = p

def set_kb_retailer(name):
    st.session_state.kb_retailer = name

def set_kb_action(act):
    st.session_state.kb_action = act

def do_logout():
    st.session_state.authenticated = False
    st.query_params.clear() 
    st.session_state.current_page = "LOGIN"
    st.session_state.kb_retailer = None

def get_home():
    return "HOME" if st.session_state.get("role") == "Admin" else "EMP_HOME"

def verify_pin(n, p):
    if n == "Avdhesh Kumar" and p == "9557": return True
    if n == "Babloo kumar singh" and p == "2081": return True
    if n == "Sunil Kumar" and p == "0788": return True
    if n == "Munna kumar" and p == "7302": return True
    if st.session_state.get("role") == "Employee" and p == st.session_state.get("emp_pin"): return True
    return False

# 🟢 GPS DISTANCE CALCULATOR (Haversine Formula)
def get_coords(url):
    try:
        if "?q=" in str(url):
            parts = str(url).split("?q=")[1].split(",")
            return float(parts[0]), float(parts[1])
    except: pass
    return None, None

def calculate_distance(lat1, lon1, lat2, lon2):
    try:
        R = 6371.0 # Earth radius in km
        dlat = math.radians(float(lat2) - float(lat1))
        dlon = math.radians(float(lon2) - float(lon1))
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 2)
    except: return 0.0

# 🟢 PERSISTENT LOGIN
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    if "auth" in st.query_params:
        st.session_state.authenticated = True
        st.session_state.role = st.query_params.get("role", "Employee")
        st.session_state.emp_name = st.query_params.get("name", "")
        st.session_state.emp_pin = st.query_params.get("pin", "")
        st.session_state.emp_mob = st.query_params.get("mob", "")
        st.session_state.current_page = st.query_params.get("page", "HOME" if st.session_state.role == "Admin" else "EMP_HOME")

# 🟢 INITIALIZE STATES
if "emp_mob" not in st.session_state: st.session_state.emp_mob = ""
if "kb_retailer" not in st.session_state: st.session_state.kb_retailer = None
if "kb_action" not in st.session_state: st.session_state.kb_action = None
if "show_success_modal" not in st.session_state: st.session_state.show_success_modal = False
if "success_display_text" not in st.session_state: st.session_state.success_display_text = ""
if "success_txn_type" not in st.session_state: st.session_state.success_txn_type = ""
if "success_wa_link" not in st.session_state: st.session_state.success_wa_link = ""
if "role" not in st.session_state: st.session_state.role = None
if "current_page" not in st.session_state: st.session_state.current_page = "LOGIN"

# 🟢 BROWSER BACK BUTTON
if st.session_state.authenticated:
    url_page = st.query_params.get("page")
    if url_page and url_page != st.session_state.current_page:
        st.session_state.current_page = url_page
        if url_page in ["HOME", "EMP_HOME"]:
            st.session_state.kb_retailer = None
            st.session_state.kb_action = None
    elif not url_page:
        st.query_params["page"] = st.session_state.current_page

# 💎 FULL SCREEN SUCCESS POPUP
if st.session_state.show_success_modal:
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; background: #f0fdf4; border-radius: 20px; border: 2px solid #86efac; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-top: 20px;">
        <div style="font-size: 80px; margin-bottom: 10px;">✅</div>
        <div style="font-size: 28px; font-weight: 800; color: #166534; margin-bottom: 10px;">Successful!</div>
        <div style="font-size: 40px; font-weight: 900; color: #0b57d0; margin-bottom: 10px; text-align: center;">{st.session_state.success_display_text}</div>
        <div style="font-size: 16px; color: #4b5563; font-weight: 700; text-transform: uppercase; background: white; padding: 8px 20px; border-radius: 20px; border: 1px solid #dcfce7; text-align: center;">{st.session_state.success_txn_type}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.session_state.success_wa_link:
        st.markdown(f"<div style='text-align:center; margin-top: 20px;'><a href='{st.session_state.success_wa_link}' target='_blank' style='display:inline-block; padding:15px 30px; background-color:#25D366; color:white; font-size:18px; font-weight:800; border-radius:30px; text-decoration:none; box-shadow: 0 4px 10px rgba(37,211,102,0.4);'>📲 Send WhatsApp Receipt</a></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("❌ CLOSE & CONTINUE", use_container_width=True):
        st.session_state.show_success_modal = False
        st.session_state.success_wa_link = ""
        st.rerun()
    st.stop()

# 💎 CSS DESIGN
st.markdown("""
    <style>
    input[type="text"], input[type="password"], input[type="number"], textarea, select { font-size: 16px !important; }
    .main .block-container { max-width: 480px !important; padding: 1.5rem !important; background: white !important; box-shadow: 0 0 15px rgba(0,0,0,0.1) !important; min-height: 100vh !important; margin: 0 auto !important; }
    .stApp { background-color: #e2e8f0; }
    [data-testid="stSidebar"] { display: none; }
    .app-header { background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 15px; }
    .login-spacer { margin-top: 18vh; }
    .stButton > button[kind="secondary"] { border-radius: 12px !important; padding: 20px 10px !important; height: auto !important; font-weight: 700 !important; font-size: 16px !important; border: 1.5px solid #e2e8f0 !important; background: white !important; color: #1e293b !important; width: 100% !important; }
    .stButton > button[kind="primary"] { border-radius: 12px 0 0 12px !important; background: #475569 !important; color: #ffffff !important; padding: 20px 15px !important; height: auto !important; min-height: 70px !important; font-weight: 700 !important; font-size: 15px !important; border: none !important; text-align: left !important; width: 100% !important; }
    .stDownloadButton > button { border-radius: 12px !important; background: #15803d !important; color: white !important; padding: 20px 10px !important; height: auto !important; font-weight: 800 !important; font-size: 16px !important; width: 100% !important; margin-top: 15px !important; }
    .amt-joined-red { background: linear-gradient(135deg, #ff4b4b 0%, #b91c1c 100%); color: white; min-height: 70px; height: 100%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 17px; border-radius: 0 12px 12px 0; margin-left: -2px; border: 1px solid #b91c1c;}
    .amt-joined-green { background: linear-gradient(135deg, #4ade80 0%, #15803d 100%); color: white; min-height: 70px; height: 100%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 17px; border-radius: 0 12px 12px 0; margin-left: -2px; border: 1px solid #15803d;}
    .amt-joined-grey { background: #94a3b8; color: white; min-height: 70px; height: 100%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 17px; border-radius: 0 12px 12px 0; margin-left: -2px; border: 1px solid #94a3b8;}
    .status-container { display: flex; gap: 8px; margin-bottom: 15px; }
    .status-box { flex: 1; padding: 10px; border-radius: 10px; text-align: center; color: white; font-weight: 700; font-size: 14px; }
    .bg-dues { background: #b91c1c; }
    .bg-adv { background: #15803d; }
    .bg-none { background: #6b7280; }
    .ledger-card { background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); display: flex; justify-content: space-between; align-items: flex-start;}
    .kb-header-container { display: flex; justify-content: space-around; background: white; padding: 15px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .kb-box { width: 45%; text-align: center; }
    @media (max-width: 768px) { div[data-testid="stHorizontalBlock"] { gap: 0px !important; } }
    </style>
""", unsafe_allow_html=True)

# 🛑 JAVASCRIPT: PREVENT ZOOM & FETCH GPS CONSTANTLY
st.components.v1.html("""
    <script>
    let meta = window.parent.document.querySelector('meta[name="viewport"]');
    if (!meta) {
        meta = window.parent.document.createElement('meta');
        meta.name = 'viewport';
        window.parent.document.head.appendChild(meta);
    }
    meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
    
    function fetchGPS() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(pos) {
                let link = "https://maps.google.com/?q=" + pos.coords.latitude + "," + pos.coords.longitude;
                let inputs = window.parent.document.querySelectorAll('input[type="text"]');
                inputs.forEach(inp => {
                    if(inp.getAttribute('aria-label') === '📍 Live Location (Auto GPS)') {
                        if(inp.value !== link) {
                            let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                            setter.call(inp, link);
                            inp.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }
                });
            });
        }
    }
    setInterval(fetchGPS, 3000);
    </script>
""", height=0, width=0)

# 🛑 DATA CONNECTION
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyH_oGxKbNZQj2azNOR0FgkLyAKxBfaAoE0Yo3DHmRpNOFZczJRayBhPd056SGUVWbxWQ/exec"
sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"

def create_pdf(r_name, r_mob, bal, r_data):
    if not HAS_FPDF: return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18); pdf.cell(0, 10, "Sandhya Enterprises", ln=True, align='C')
    pdf.set_font("Arial", 'B', 11); pdf.cell(0, 6, "Jio Authorized Distributor", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, "Register office: Rosera Road, Meghpatti, Samastipur, Bihar 848117", ln=True, align='C')
    pdf.cell(0, 5, "GSTIN: 10GQZPK8313P1Z1 | PAN: GQZPK8313P", ln=True, align='C')
    pdf.cell(0, 5, "Email: smp.sandhya02@gmail.com | Contact: 7479584179", ln=True, align='C')
    pdf.line(10, 45, 200, 45); pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12); pdf.cell(100, 8, f"Retailer: {r_name}"); pdf.cell(0, 8, f"Bal: Rs {bal:,.2f}", ln=True, align='R')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9); pdf.cell(25, 8, "Date", 1); pdf.cell(75, 8, "Particulars", 1); pdf.cell(30, 8, "Diye", 1); pdf.cell(30, 8, "Mile", 1); pdf.cell(30, 8, "Bal", 1); pdf.ln()
    pdf.set_font("Arial", '', 9)
    for r in r_data:
        pdf.cell(25, 8, str(r['d']), 1); pdf.cell(75, 8, str(r['i'])[:40], 1); pdf.cell(30, 8, f"{r['out']:,.0f}", 1); pdf.cell(30, 8, f"{r['in']:,.0f}", 1); pdf.cell(30, 8, f"{r['b']:,.0f}", 1); pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

def get_detail_string(prod_name, qty, amt_out):
    p = str(prod_name).strip()
    q = pd.to_numeric(qty, errors='coerce')
    a = pd.to_numeric(amt_out, errors='coerce')
    if pd.notnull(q) and q > 0:
        if p in ["JPB V4", "Other"] and pd.notnull(a) and a > 0:
            return f"{p} (Qty: {int(q)} @ ₹{(a/q):,.0f}/pc)"
        elif p in ["Sim Card", "Sim Allocation"]:
            return f"{p} (Qty: {int(q)})"
    return p

@st.cache_data(ttl=2)
def load_data():
    try:
        cb = int(time.time())
        ret = pd.read_csv(f"{retailers_csv}&cb={cb}").dropna(how="all").fillna("")
        inv = pd.read_csv(f"{inventory_csv}&cb={cb}").dropna(how="all").fillna("")
        led = pd.read_csv(f"{ledger_csv}&cb={cb}").dropna(how="all").fillna("")
        for col in ['Date', 'Retailer Name', 'Product/Service', 'Amount Out (Debit)', 'Amount In (Credit)', 'Qty', 'FSE Name']:
            if col not in led.columns: led[col] = ""
        led['DateObj'] = pd.to_datetime(led['Date'], format='%d-%m-%Y', errors='coerce')
        return ret, inv, led
    except: return None, None, None

ret_df, inv_df, led_df = load_data()
if led_df is not None:
    for col in ['Date', 'Retailer Name', 'Product/Service', 'Amount Out (Debit)', 'Amount In (Credit)', 'Qty', 'FSE Name']:
        if col not in led_df.columns: led_df[col] = ""

valid_ret = ret_df[ret_df['Location'].astype(str).str.upper() != 'EMPLOYEE'] if ret_df is not None else None
retailers_dict = {f"{r['Retailer Name']} ({str(r['Mobile Number']).split('.')[0]})": r for _, r in valid_ret.iterrows()} if valid_ret is not None else {}

# 🔐 LOGIN SYSTEM
if not st.session_state.authenticated:
    st.markdown('<div class="login-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="app-header"><h1>🏢 Sandhya ERP</h1><p>Secure Login</p></div>', unsafe_allow_html=True)
    l_mob = st.text_input("Mobile Number")
    l_pin = st.text_input("PIN", type="password")
    st.components.v1.html("""<script>window.parent.document.querySelectorAll('input').forEach(i=>{i.setAttribute('inputmode','numeric');});</script>""", height=0, width=0)

    if st.button("🚀 LOGIN", use_container_width=True, type="secondary"):
        if l_mob == "7479584179" and l_pin == "9557":
            st.session_state.role = "Admin"; st.session_state.emp_name = "Admin"; st.session_state.emp_mob = l_mob
        elif l_mob == "7254972081" and l_pin == "2081":
            st.session_state.role = "Employee"; st.session_state.emp_name = "Babloo kumar singh"; st.session_state.emp_mob = l_mob
        elif l_mob == "9507070788" and l_pin == "0788":
            st.session_state.role = "Employee"; st.session_state.emp_name = "Sunil Kumar"; st.session_state.emp_mob = l_mob
        elif l_mob == "8969957302" and l_pin == "7302":
            st.session_state.role = "Employee"; st.session_state.emp_name = "Munna kumar"; st.session_state.emp_mob = l_mob
        elif ret_df is not None:
            emps = ret_df[ret_df['Location'].astype(str).str.upper() == 'EMPLOYEE']
            for _, r in emps.iterrows():
                if str(r.get("Mobile Number")).split('.')[0] == l_mob and str(r.get("PRM ID")).replace("EMP_","") == l_pin:
                    st.session_state.role = "Employee"; st.session_state.emp_name = r["Retailer Name"]; st.session_state.emp_pin = l_pin; st.session_state.emp_mob = l_mob
        
        if st.session_state.role:
            st.session_state.authenticated = True
            st.session_state.current_page = "HOME" if st.session_state.role == "Admin" else "EMP_HOME"
            st.query_params["auth"] = "true"; st.query_params["role"] = st.session_state.role; st.query_params["name"] = st.session_state.emp_name; st.query_params["pin"] = l_pin; st.query_params["mob"] = l_mob; st.query_params["page"] = st.session_state.current_page
            st.rerun()
        else:
            st.error("Invalid Login Details")
    st.stop()

# 🟢 MAIN APP HEADER
st.markdown("""
<div class="app-header">
    <h1 style="font-size: 26px; margin-bottom: 5px;">🏢 SANDHYA ENTERPRISES</h1>
    <p style="margin: 2px 0px; font-size: 14px;">Register Office, Rosera Rod Meghpatti</p>
    <p style="margin: 2px 0px; font-size: 14px;">Email: smp.sandhya02@gmail.com</p>
    <p style="margin: 2px 0px; font-size: 14px;">📞 7479584179</p>
</div>
""", unsafe_allow_html=True)

fse_list = ["Avdhesh Kumar", "Babloo kumar singh", "Sunil Kumar", "Munna kumar"]
if ret_df is not None and "Location" in ret_df.columns:
    emp_names = ret_df[ret_df['Location'].astype(str).str.upper() == 'EMPLOYEE']['Retailer Name'].tolist()
    fse_list = list(set(fse_list + emp_names))

# --- DASHBOARDS ---
if st.session_state.current_page == "HOME":
    st.success(f"**Welcome To**\n\n👤 {st.session_state.emp_name} | 📞 {st.session_state.emp_mob}")
    col1, col2 = st.columns(2)
    with col1:
        st.button("💸 Khatabook 3D", use_container_width=True, type="secondary", on_click=go_to, args=("DUES",))
        st.button("📊 Live Stock", use_container_width=True, type="secondary", on_click=go_to, args=("STOCK",))
        st.button("➕ Add Retailer", use_container_width=True, type="secondary", on_click=go_to, args=("ADD",))
        st.button("📜 Ledger Report", use_container_width=True, type="secondary", on_click=go_to, args=("LEDGER",))
    with col2:
        st.button("💰 Today Collection", use_container_width=True, type="secondary", on_click=go_to, args=("COL",))
        st.button("🗺️ Beat Report", use_container_width=True, type="secondary", on_click=go_to, args=("BEAT_REPORT",))
        st.button("📦 Entry", use_container_width=True, type="secondary", on_click=go_to, args=("ENTRY",))
        st.button("🚪 Logout", use_container_width=True, type="secondary", on_click=do_logout)

elif st.session_state.current_page == "EMP_HOME":
    st.success(f"**Welcome To**\n\n👤 {st.session_state.emp_name} | 📞 {st.session_state.emp_mob}")
    col1, col2 = st.columns(2)
    with col1:
        st.button("📖 Khatabook", use_container_width=True, type="secondary", on_click=go_to, args=("DUES",))
        st.button("📦 Sim Stock", use_container_width=True, type="secondary", on_click=go_to, args=("STOCK",))
        st.button("📍 Beat (In/Out)", use_container_width=True, type="secondary", on_click=go_to, args=("BEAT",))
    with col2:
        st.button("💰 Collection", use_container_width=True, type="secondary", on_click=go_to, args=("COL",))
        st.button("➕ Add Retailer", use_container_width=True, type="secondary", on_click=go_to, args=("ADD",))
        st.button("Exit", use_container_width=True, type="secondary", on_click=do_logout)

# --- 📍 BEAT TRACKING (IN/OUT) ---
elif st.session_state.current_page == "BEAT":
    st.button("🔙 Back Menu", type="secondary", on_click=go_to, args=(get_home(),))
    st.header("📍 Daily Beat Tracking")
    
    t1, t2 = st.tabs(["🟢 PUNCH IN", "🔴 PUNCH OUT"])
    
    with t1:
        st.info("Start your market day. Keep your browser location ON.")
        with st.form("form_in"):
            loc_in = st.text_input("📍 Live Location (Auto GPS)", key="in_loc")
            if st.form_submit_button("Save PUNCH IN", type="secondary"):
                if loc_in:
                    time_str = datetime.now().strftime("%I:%M %p")
                    log_type = f"IN ({time_str}) | {loc_in}"
                    requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":st.session_state.emp_name,"r_mob":st.session_state.emp_mob,"type":log_type,"qty":0,"amt_out":0,"amt_in":0,"fse":"System","txn_id":"BEAT"})
                    st.success("✅ Punch IN Recorded Successfully!")
                    st.cache_data.clear(); time.sleep(2); st.rerun()
                else: st.error("⚠️ Please allow Location Access in browser!")
                    
    with t2:
        st.warning("End your day. System will auto-calculate your travel Distance.")
        with st.form("form_out"):
            loc_out = st.text_input("📍 Live Location (Auto GPS)", key="out_loc")
            if st.form_submit_button("Save PUNCH OUT & Calc KM", type="secondary"):
                if loc_out:
                    time_str = datetime.now().strftime("%I:%M %p")
                    today_str = date.today().strftime("%d-%m-%Y")
                    
                    in_recs = led_df[(led_df['Date'] == today_str) & (led_df['Retailer Name'] == st.session_state.emp_name) & (led_df['Product/Service'].str.startswith("IN ("))]
                    
                    total_km = 0.0
                    if not in_recs.empty:
                        last_in_str = in_recs.iloc[-1]['Product/Service']
                        lat1, lon1 = get_coords(last_in_str)
                        lat2, lon2 = get_coords(loc_out)
                        if lat1 and lat2: total_km = calculate_distance(lat1, lon1, lat2, lon2)
                    
                    log_type = f"OUT ({time_str}) | {loc_out}"
                    requests.post(WEBHOOK_URL, json={"action":"add_txn","date":today_str,"r_name":st.session_state.emp_name,"r_mob":st.session_state.emp_mob,"type":log_type,"qty":total_km,"amt_out":0,"amt_in":0,"fse":"System","txn_id":"BEAT"})
                    st.success(f"✅ Punch OUT Recorded! Total Auto-KM: {total_km} KM.")
                    st.cache_data.clear(); time.sleep(2.5); st.rerun()
                else: st.error("⚠️ Please allow Location Access in browser!")

elif st.session_state.current_page == "BEAT_REPORT":
    st.button("🔙 Back Menu", type="secondary", on_click=go_to, args=(get_home(),))
    st.header("🗺️ Employee Beat Report")
    
    if led_df is not None and not led_df.empty:
        beat_data = led_df[led_df['Product/Service'].str.contains("IN \(|OUT \(", na=False)].copy()
        if not beat_data.empty:
            disp_b = beat_data[['Date', 'Retailer Name', 'Product/Service', 'Qty']].copy()
            disp_b.columns = ['Date', 'Employee Name', 'Action (Time) & Location Link', 'Total KM']
            st.dataframe(disp_b, hide_index=True)
        else: st.info("No Beat Tracking data available yet.")
    else: st.info("Database is empty.")

# --- 💸 KHATABOOK 3D ---
elif st.session_state.current_page == "DUES":
    st.button("🔙 Back Menu", type="secondary", on_click=go_to, args=(get_home(),))
    
    if st.session_state.kb_retailer is None:
        all_r = []; tm, ta = 0, 0
        for n, r in retailers_dict.items():
            u_led = led_df[led_df['Retailer Name'] == r['Retailer Name']]
            bal = pd.to_numeric(u_led['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_led['Amount In (Credit)'], errors='coerce').sum()
            if bal > 0: tm += bal
            else: ta += abs(bal)
            prm = str(r.get('PRM ID','')).split('.')[0]
            all_r.append({"Name": r['Retailer Name'], "PRM": prm, "Bal": bal, "Disp": n})
        
        st.markdown(f"<div class='kb-header-container'><div class='kb-box'><h4>Dene hain</h4><h2 style='color:#15803d;'>₹ {ta:,.0f}</h2></div><div class='kb-box'><h4>Milenge</h4><h2 style='color:#b91c1c;'>₹ {tm:,.0f}</h2></div></div>", unsafe_allow_html=True)
        all_r.sort(key=lambda x: -abs(x['Bal']))
        sel = st.selectbox("🔍 Search Retailer...", ["All"] + [x['Disp'] for x in all_r])
        
        for i in all_r:
            if sel == "All" or i['Disp'] == sel:
                cls = "amt-joined-red" if i['Bal'] > 0 else "amt-joined-green" if i['Bal'] < 0 else "amt-joined-grey"
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.button(f"👤 {i['Name']} ({i['PRM']})", key=f"kb_{i['Disp']}", use_container_width=True, type="primary", on_click=set_kb_retailer, args=(i['Name'],))
                with c2: 
                    st.markdown(f"<div style='height: 100%;'><div class='{cls}'>₹ {abs(i['Bal']):,.0f}</div></div>", unsafe_allow_html=True)
    else:
        name = st.session_state.kb_retailer
        r_info = next(v for k, v in retailers_dict.items() if v['Retailer Name'] == name)
        mob = str(r_info['Mobile Number']).split('.')[0]
        prm = str(r_info.get('PRM ID','')).split('.')[0]
        
        u_led = led_df[led_df['Retailer Name'] == name].sort_values('DateObj')
        running_bal = 0; rows = []
        for _, r in u_led.iterrows():
            d_val = pd.to_numeric(r['Amount Out (Debit)'], errors='coerce')
            c_val = pd.to_numeric(r['Amount In (Credit)'], errors='coerce')
            d = d_val if pd.notnull(d_val) else 0
            c = c_val if pd.notnull(c_val) else 0
            running_bal += (d - c)
            
            status_text = f"🚩 Dues: ₹{running_bal:,.0f}" if running_bal > 0 else f"✅ Adv: ₹{abs(running_bal):,.0f}" if running_bal < 0 else "⚪ Settled: ₹0"
            detailed_prod = get_detail_string(r['Product/Service'], r['Qty'], d)
            rows.append({"d": r['Date'], "i": detailed_prod, "out": d, "in": c, "b": running_bal, "status": status_text})

        wa_msg = f"*Retailer:* {name} ({prm})\n*Aapka dues hai:* ₹ {abs(running_bal):,.0f}\n*Aaj hi online ya cash de kar apna dues clear kare.*\n\n*Last 5 Transactions:*\n"
        for r in rows[-5:]:
            amt_str = f"Diye (-): ₹{r['out']:,.0f}" if r['out']>0 else f"Mile (+): ₹{r['in']:,.0f}" if r['in']>0 else "₹0"
            wa_msg += f"🗓 {r['d']} | {r['i']} | {amt_str}\n"
        wa_msg += "\nRegards,\n*SANDHYA ENTERPRISES*\nAVDHESH KUMAR\n📞 7479584179"
        
        st.markdown(f"""
        <div style='background:#0b57d0; color:white; padding:15px; border-radius:12px; margin-bottom:10px; text-align:center;'>
            <h3 style='margin:0;'>{name}</h3><p style='margin:5px 0;'>PRM ID: {prm} | {mob}</p>
            <div style='display:flex; justify-content:space-around; margin-top:10px;'>
                <a href='tel:{mob}' style='background:white; color:#0b57d0; padding:8px 20px; border-radius:8px; text-decoration:none; font-weight:800; border:1px solid #e2e8f0;'>📞 CALL</a>
                <a href='https://wa.me/91{mob}?text={urllib.parse.quote(wa_msg)}' style='background:#25D366; color:white; padding:8px 20px; border-radius:8px; text-decoration:none; font-weight:800; border:1px solid #16a34a;'>📲 WA</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        cur_bal = rows[-1]['b'] if rows else 0
        st.markdown(f"""
        <div class='status-container'>
            <div class='status-box {"bg-dues" if cur_bal > 0 else "bg-none"}'>Dues<br>₹{cur_bal if cur_bal > 0 else 0:,.0f}</div>
            <div class='status-box {"bg-adv" if cur_bal < 0 else "bg-none"}'>Advance<br>₹{abs(cur_bal) if cur_bal < 0 else 0:,.0f}</div>
            <div class='status-box {"bg-none" if cur_bal == 0 else "bg-none"}'>Settled</div>
        </div>
        """, unsafe_allow_html=True)

        if HAS_FPDF:
            st.download_button("📄 Download PDF Ledger", create_pdf(name, mob, cur_bal, rows), f"{name}_Ledger.pdf", "application/pdf", use_container_width=True)

        st.markdown("<div style='background:#f9fafb; padding:10px; font-weight:800; display:flex; justify-content:space-between; margin-top:10px;'><div style='width:40%'>Entries</div><div style='width:30%; text-align:right'>Debit (-)</div><div style='width:30%; text-align:right'>Credit (+)</div></div>", unsafe_allow_html=True)
        for r in reversed(rows):
            box_color = "#fff5f5" if r['out'] > 0 else "#f0fdf4" if r['in'] > 0 else "white"
            st.markdown(f"""
            <div class="ledger-card" style="background: {box_color};">
                <div style="width:50%;"><div style="font-size:11px; color:#6b7280;">{r['d']}</div><div style="font-weight:700; font-size:14px; color:#1e293b;">{r['i']}</div><div style="font-size:12px; font-weight:600; color:#4b5563; margin-top:4px;">{r['status']}</div></div>
                <div style="width:25%; text-align:right; color:#b91c1c; font-weight:800;">{f"- ₹{r['out']:,.0f}" if r['out']>0 else ""}</div>
                <div style="width:25%; text-align:right; color:#15803d; font-weight:800;">{f"+ ₹{r['in']:,.0f}" if r['in']>0 else ""}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("⚙️ Edit / Delete Entry"):
            if rows:
                rev_rows = list(reversed(rows[-10:]))
                entry_opts = [f"{r['d']} | {str(r['i']).split(' (')[0]} | ₹ {r['out'] if r['out']>0 else r['in']}" for r in rev_rows]
                sel_e = st.selectbox("Select Entry", entry_opts)
                col_del, col_edit = st.columns(2)
                if col_del.button("🗑️ Delete", use_container_width=True):
                    requests.post(WEBHOOK_URL, json={"action":"delete_txn","r_name":name,"details":sel_e})
                    st.success("Delete command sent to Sheet!")
                    st.cache_data.clear(); time.sleep(2.5); st.rerun()
                if col_edit.button("✏️ Change", use_container_width=True): st.info("Delete the wrong entry first, then Add a correct one.")

        st.markdown("---")
        b1, b2 = st.columns(2)
        b1.button("🔴 DIYE (Stock)", use_container_width=True, type="secondary", on_click=set_kb_action, args=("diye",))
        b2.button("🟢 MILE (Payment)", use_container_width=True, type="secondary", on_click=set_kb_action, args=("mile",))
        
        if st.session_state.kb_action == "diye":
            t = st.selectbox("👉 Select Type", ["Etop Transfer", "Sim Card", "JPB V4", "Other"])
            with st.form("d_f"):
                if t == "Etop Transfer":
                    o = st.selectbox("Amount", ["5000", "3000", "2000", "1500", "500", "Manual"])
                    input_price = st.number_input("Enter Amount", min_value=0.0) if o == "Manual" else float(o)
                    input_qty = 0
                elif t == "Sim Card":
                    input_qty = st.number_input("Qty", min_value=1)
                    input_price = 0.0
                else:
                    input_price = st.number_input("Price Per Piece (₹)", min_value=0.0)
                    input_qty = st.number_input("Quantity", min_value=1, value=1)
                    st.info(f"💡 Total Amount will be saved as: **₹ {input_price * input_qty:,.0f}**")
                
                f = st.selectbox("FSE", fse_list); p = st.text_input("PIN", type="password")
                st.components.v1.html("""<script>window.parent.document.querySelectorAll('input[type="password"], input[type="number"]').forEach(i=>{i.setAttribute('inputmode','numeric');});</script>""", height=0, width=0)

                if st.form_submit_button("Save", type="secondary"):
                    if verify_pin(f, p):
                        if t in ["JPB V4", "Other"]: final_amt = input_price * input_qty; detail_str = f"{t} (Qty: {int(input_qty)} @ ₹{input_price:,.0f}/pc)"
                        elif t == "Sim Card": final_amt = 0; detail_str = f"{t} (Qty: {int(input_qty)})"
                        else: final_amt = input_price; detail_str = t
                            
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"r_mob":mob,"type":t,"qty":input_qty,"amt_out":final_amt,"amt_in":0,"fse":f,"txn_id":"KB"})
                        st.session_state.success_display_text = f"₹ {final_amt:,.0f}" if final_amt>0 else f"{int(input_qty)} SIMs"
                        st.session_state.success_txn_type = detail_str
                        st.session_state.show_success_modal = True
                        st.cache_data.clear(); time.sleep(2.5); st.rerun()

        if st.session_state.kb_action == "mile":
            with st.form("m_f"):
                m = st.selectbox("Mode", ["Cash", "Online"]); a = st.number_input("Amount Received", min_value=0.0)
                f = st.selectbox("FSE", fse_list); p = st.text_input("PIN", type="password")
                st.components.v1.html("""<script>window.parent.document.querySelectorAll('input[type="password"], input[type="number"]').forEach(i=>{i.setAttribute('inputmode','numeric');});</script>""", height=0, width=0)

                if st.form_submit_button("Save", type="secondary"):
                    if verify_pin(f, p):
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"r_mob":mob,"type":f"Payment ({m})","amt_in":a,"fse":f,"txn_id":"KB"})
                        st.session_state.success_display_text = f"₹ {a:,.0f}"; st.session_state.success_txn_type = f"Payment Received ({m})"
                        st.session_state.show_success_modal = True
                        st.cache_data.clear(); time.sleep(2.5); st.rerun()

# --- OTHER PAGES ---
elif st.session_state.current_page == "STOCK":
    st.button("🔙 Back Menu", type="secondary", on_click=go_to, args=(get_home(),))
    st.header("📦 Live Inventory Stock")
    
    if st.session_state.role == "Admin":
        t1, t2 = st.tabs(["📱 FSE Live Balances", "📦 Main Stock & Billing"])
        with t1:
            st.write("#### 📊 Current FSE Stock Balance")
            fse_stock_data = []
            for f_name in fse_list:
                f_name_clean = f_name.strip().upper()
                al = pd.to_numeric(led_df[(led_df['Retailer Name'].str.strip().str.upper()==f_name_clean)&(led_df['Product/Service']=='Sim Allocation')]['Qty'], errors='coerce').sum()
                di = pd.to_numeric(led_df[(led_df['FSE Name'].str.strip().str.upper()==f_name_clean)&(led_df['Product/Service']=='Sim Card')]['Qty'], errors='coerce').sum()
                if al > 0 or di > 0:
                    fse_stock_data.append({"FSE Name": f_name, "Received": al, "Billed": di, "Current Stock": al - di})
            if fse_stock_data: st.dataframe(pd.DataFrame(fse_stock_data), hide_index=True)
            else: st.info("No FSE SIM allocation data found.")
            
        with t2:
            st.write("#### ➕ Bill SIMs to FSE")
            with st.form("bill"):
                f = st.selectbox("Select FSE", fse_list)
                q = st.number_input("SIM Qty", min_value=1)
                ap = st.text_input("Admin PIN", type="password")
                st.components.v1.html("""<script>window.parent.document.querySelectorAll('input[type="password"], input[type="number"]').forEach(i=>{i.setAttribute('inputmode','numeric');});</script>""", height=0, width=0)
                if st.form_submit_button("Bill SIMs", type="secondary"):
                    if ap == "9557":
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":f,"r_mob":"0","type":"Sim Allocation","qty":q,"amt_out":0,"amt_in":0,"fse":"Admin","txn_id":"S"})
                        st.session_state.success_display_text = f"{int(q)} SIMs"
                        st.session_state.success_txn_type = f"Billed to {f}"
                        st.session_state.show_success_modal = True
                        st.cache_data.clear(); time.sleep(2.5); st.rerun()
                    else: st.error("Wrong Admin PIN")
            st.write("---")
            total_al = pd.to_numeric(led_df[led_df['Product/Service']=='Sim Allocation']['Qty'], errors='coerce').sum()
            st.warning(f"📉 Total SIMs Deducted (Given to FSEs): **{int(total_al)}**")
            st.write("#### 🏢 Master Inventory Sheet")
            if inv_df is not None and not inv_df.empty: st.dataframe(inv_df, use_container_width=True, hide_index=True)
            else: st.info("Inventory data not available.")
    else:
        emp_clean = st.session_state.emp_name.strip().upper()
        alloc = pd.to_numeric(led_df[(led_df['Retailer Name'].str.strip().str.upper()==emp_clean)&(led_df['Product/Service']=='Sim Allocation')]['Qty'], errors='coerce').sum()
        dist = pd.to_numeric(led_df[(led_df['FSE Name'].str.strip().str.upper()==emp_clean)&(led_df['Product/Service']=='Sim Card')]['Qty'], errors='coerce').sum()
        cur_bal = int(alloc - dist)
        
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; background:#0b57d0; color:white; padding:15px; border-radius:12px; margin-bottom:15px;'>
            <div style='text-align:center; width:33%;'>Received<br><b style='font-size:22px;'>{int(alloc)}</b></div>
            <div style='text-align:center; width:33%; border-left:1px solid #60a5fa; border-right:1px solid #60a5fa;'>Billed<br><b style='font-size:22px;'>{int(dist)}</b></div>
            <div style='text-align:center; width:33%;'>Stock<br><b style='font-size:22px; color:#86efac;'>{cur_bal}</b></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("### SIM Distribution History")
        dist_history = led_df[(led_df['FSE Name'].str.strip().str.upper()==emp_clean)&(led_df['Product/Service']=='Sim Card')][['Date','Retailer Name', 'Qty']]
        if not dist_history.empty: st.dataframe(dist_history, hide_index=True)
        else: st.info("No distribution history found.")

elif st.session_state.current_page == "ADD":
    st.button("🔙 Back Menu", type="secondary", on_click=go_to, args=(get_home(),))
    with st.form("add_ret"):
        n=st.text_input("Retailer Name"); m=st.text_input("Mobile"); p=st.text_input("PRM ID"); l=st.text_input("Loc")
        st.components.v1.html("""<script>window.parent.document.querySelectorAll('input').forEach(i=>{i.setAttribute('inputmode','numeric');});</script>""", height=0, width=0)
        if st.form_submit_button("Save Retailer", type="secondary"):
            requests.post(WEBHOOK_URL, json={"action":"add_retailer","name":n.upper(),"mobile":m,"prm":p,"location":l.upper(),"date":date.today().strftime("%d-%m-%Y")})
            st.success("Retailer Added!"); st.cache_data.clear()

elif st.session_state.current_page == "COL":
    st.button("🔙 Back Menu", type="secondary", on_click=go_to, args=(get_home(),))
    st.header("💰 Today's Collection")
    
    t_led = led_df[led_df['Date'] == date.today().strftime("%d-%m-%Y")].copy()
    t_led['Amount In (Credit)'] = pd.to_numeric(t_led['Amount In (Credit)'], errors='coerce').fillna(0)
    coll_df = t_led[t_led['Amount In (Credit)'] > 0]
    
    if st.session_state.role == "Employee":
        coll_df = coll_df[coll_df['FSE Name'].str.strip().str.upper() == st.session_state.emp_name.strip().upper()]
        
    if not coll_df.empty:
        disp_df = coll_df[['Retailer Name', 'Amount In (Credit)', 'Product/Service', 'FSE Name']].copy()
        disp_df.columns = ['Retailer Name', 'Amount (₹)', 'Payment Mode', 'Received By']
        st.dataframe(disp_df, hide_index=True)
        st.write(f"**Total Collected Today: ₹ {disp_df['Amount (₹)'].sum():,.0f}**")
        csv = disp_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Excel (CSV)", data=csv, file_name=f"Today_Collection_{date.today().strftime('%d-%m-%Y')}.csv", mime="text/csv", use_container_width=True)
    else: st.info("No collection data available today for your account.")

elif st.session_state.current_page == "ENTRY":
    st.button("🔙 Back Menu", type="secondary", on_click=go_to, args=(get_home(),))
    st.header("📦 Direct Stock/Payment Entry")
    
    t_type = st.selectbox("Transaction Type", ["Etop Transfer", "Payment Received", "JPB V4", "Sim Card"])
    r_sel = st.selectbox("Select Retailer", list(retailers_dict.keys()))
    
    with st.form("entry_form"):
        if t_type == "JPB V4":
            input_price = st.number_input("Price Per Piece (₹)", min_value=0.0)
            input_qty = st.number_input("Qty", min_value=1, value=1)
            st.info(f"💡 Total Amount: **₹ {input_price * input_qty:,.0f}**")
        elif t_type == "Sim Card":
            input_qty = st.number_input("Qty", min_value=1)
            input_price = 0.0
        else:
            input_price = st.number_input("Amount", min_value=0.0)
            input_qty = 0
            
        f_n = st.selectbox("FSE Name", fse_list)
        f_p = st.text_input("4-Digit PIN", type="password")
        
        if st.form_submit_button("Save Transaction", type="secondary"):
            if verify_pin(f_n, f_p):
                if t_type == "JPB V4": final_amt = input_price * input_qty
                else: final_amt = input_price
                    
                r_info = retailers_dict[r_sel]
                requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":r_info['Retailer Name'],"r_mob":str(r_info['Mobile Number']).split('.')[0],"type":t_type,"qty":input_qty,"amt_out":final_amt if t_type in ["Etop Transfer", "JPB V4"] else 0,"amt_in":final_amt if t_type=="Payment Received" else 0,"fse":f_n,"txn_id":"E"})
                st.session_state.success_display_text = f"₹ {final_amt:,.0f}" if t_type != "Sim Card" else f"{int(input_qty)} SIMs"
                st.session_state.success_txn_type = t_type
                st.session_state.show_success_modal = True
                st.cache_data.clear(); time.sleep(2.5); st.rerun()

elif st.session_state.current_page == "LEDGER":
    st.button("🔙 Back Menu", type="secondary", on_click=go_to, args=(get_home(),))
    st.header("📜 Ledger Report")
    sel = st.selectbox("Choose Retailer", list(retailers_dict.keys()))
    if sel:
        r_name = sel.split(" (")[0]
        disp_df = led_df[led_df['Retailer Name'] == r_name].sort_values('DateObj', ascending=False).copy()
        
        def fmt_p(row): return get_detail_string(row.get('Product/Service',''), row.get('Qty',0), row.get('Amount Out (Debit)',0))
        if not disp_df.empty: disp_df['Product/Service'] = disp_df.apply(fmt_p, axis=1)
        st.dataframe(disp_df[['Date', 'Product/Service', 'Amount Out (Debit)', 'Amount In (Credit)']], hide_index=True)

elif st.session_state.current_page == "URGENT":
    st.button("🔙 Back Menu", type="secondary", on_click=go_to, args=(get_home(),))
    st.error("🚨 Pending Recovery List (Dues > 24 Hours)")
    st.info("Loading urgent records from database...")
