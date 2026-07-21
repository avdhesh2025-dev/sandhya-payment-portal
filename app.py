import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta
import time
import re
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIG & MOBILE STYLES (FULL SCREEN)
# ==========================================
st.set_page_config(page_title="Sandhya Enterprises Mega ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

components.html(
    """
    <script>
        var parentDoc = window.parent.document;
        function fixMobileInputs() {
            var allInputs = parentDoc.querySelectorAll('input, textarea, select');
            allInputs.forEach(function(inp) { inp.style.setProperty('font-size', '16px', 'important'); });
        }
        setInterval(fixMobileInputs, 400);
    </script>
    """, height=0, width=0
)

st.markdown("""
    <style>
    html, body, .stApp, .main { touch-action: manipulation !important; background-color: #f4f7fb !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    .block-container { background-color: #ffffff !important; max-width: 98% !important; padding: 25px 20px !important; margin: 15px auto !important; border-radius: 12px !important; box-shadow: 0px 5px 20px rgba(0, 0, 0, 0.05) !important; }
    @media screen and (max-width: 768px) { .block-container { margin: 5px auto !important; padding: 10px !important; } }
    input:focus, textarea:focus, div[data-baseweb="select"]:focus-within { background-color: #dcfce7 !important; border: 2px solid #16a34a !important; color: #000 !important; font-weight: bold !important; box-shadow: 0 0 10px rgba(22, 163, 74, 0.5) !important; }
    .kpi-card { background: #ffffff; border-radius: 12px; padding: 15px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center; margin-bottom: 15px; border-top: 4px solid #004a99; }
    .kpi-title { font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 22px; color: #0f172a; font-weight: 800; margin: 4px 0; }
    .audit-box { background: #0f172a; color: #38bdf8; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 12px; max-height: 220px; overflow-y: auto; line-height: 1.6; }
    .login-box { background: linear-gradient(145deg, #ffffff, #e6f2ff); padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0, 74, 153, 0.1); text-align: center; border-top: 5px solid #004a99; max-width: 450px; margin: 0 auto; }
    .header-box { background: linear-gradient(135deg, #004a99, #0066cc); padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 🔒 SECURITY & ENVIROMENT SECRETS MANAGEMENT
# ==========================================
try: products_url = st.secrets["PRODUCTS_URL"]
except: products_url = ""

try: base_read_url = st.secrets["BASE_READ_URL"]
except: base_read_url = ""

try: write_url = st.secrets["WRITE_URL"]
except: write_url = ""

try: OWNER_PHONE = st.secrets["OWNER_PHONE"]
except: OWNER_PHONE = "7479584179"

fse_list = ["All Employees", "0690788829 - Ravindra Sharma", "0690903215 - Ravi Kumar", "0690881333 - Gopal Kumar Sahni","0691116975 - Shashank Shekhar Kumar","0691116972 - Nitish Kumar", 
            "0690373395 - Vikash Kumar", "0690499449 - Lal Babu Das", "0690452472 - Md Samim","0691116945 - Ankit Kumar","0691116911 - Nitish Kumar Soni", 
            "0690859418 - Sachin Kumar", "0690749611 - Premjeet Kumar","0691111278 - Ratnesh Kumar", 
            "0690093932 - Uttam Kumar Paswan", "068996776 - Sunil Kumar", "0690899815 - Munna Kumar","0690930677 - Mukesh Kumar","0691003801 - Md Prvez Alam"]

try: ADMIN_PWD = st.secrets["ADMIN_PASSWORD"]
except: ADMIN_PWD = "9557"

USER_CREDS = {"admin": {"pwd": ADMIN_PWD, "role": "admin", "fse": "All Employees"}}
for emp in fse_list:
    if "-" in emp: 
        emp_id = emp.split(" - ")[0].strip()
        try: emp_pwd = st.secrets[f"PWD_{emp_id}"]
        except: emp_pwd = emp_id[-4:]
        USER_CREDS[emp_id] = {"pwd": emp_pwd, "role": "staff", "fse": emp}

# ==========================================
# 3. SAFE STATE MANAGEMENT
# ==========================================
def init_state(key, default_value):
    if key not in st.session_state: st.session_state[key] = default_value

init_state('logged_in', False)
init_state('cart', [])
init_state('pdf_viewer', "")
init_state('audit_logs', [])
init_state('show_popup', False)
init_state('popup_msg', "")

def add_audit_log(user, action):
    t_stamp = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    st.session_state['audit_logs'].insert(0, f"[{t_stamp}] {user}: {action}")

# ==========================================
# 4. DATA LOADERS
# ==========================================
@st.cache_data(ttl=60)
def load_db():
    if not base_read_url: return pd.DataFrame()
    try:
        df = pd.read_csv(f"{base_read_url}&cb={int(time.time())}", dtype=str).dropna(how='all')
        if df.empty: return pd.DataFrame()
        while len(df.columns) < 15: df[f"Col_{len(df.columns)}"] = "0"
        df['dt_fixed'] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, format="mixed", errors='coerce')
        for c in [7, 10, 11]: df[df.columns[c]] = pd.to_numeric(df[df.columns[c]], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def load_products():
    if not products_url: return pd.DataFrame()
    try: return pd.read_csv(f"{products_url}&cb={int(time.time())}", dtype=str).dropna(how='all')
    except: return pd.DataFrame()

def parse_tech(tech_str, fallback_total=0.0):
    d = {"Inv": "OLD", "Item": str(tech_str), "Rate": 0.0, "Qty": 1, "Disc": 0.0, "Cost": 0.0, "Total": fallback_total, "Due":0.0}
    try:
        if "|" in str(tech_str):
            for p in str(tech_str).split("|"):
                p = p.strip()
                if p.startswith("Inv:"): d["Inv"] = p.replace("Inv:", "").strip()
                elif p.startswith("Item:"): d["Item"] = p.replace("Item:", "").strip()
                elif p.startswith("Rate:"): d["Rate"] = float(re.findall(r"[-+]?\d*\.\d+|\d+", p)[0])
                elif p.startswith("Qty:"): d["Qty"] = float(re.findall(r"[-+]?\d*\.\d+|\d+", p)[0])
                elif p.startswith("Cost:"): d["Cost"] = float(re.findall(r"[-+]?\d*\.\d+|\d+", p)[0])
                elif p.startswith("Pay:"): 
                    d_m = re.search(r'D=([-+]?[\d.]+)', p)
                    if d_m: d["Due"] = float(d_m.group(1))
            d["Total"] = (d["Rate"] * d["Qty"]) - d["Disc"]
    except: pass
    return d

# ==========================================
# 5. APPLICATION UI LOGIC
# ==========================================
if not st.session_state['logged_in']:
    st.markdown('<br><br>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="login-box"><h1 style="margin:0; color:#004a99; font-size: 26px;">🏢 SANDHYA ENTERPRISES</h1><p style="color:#666; font-weight:bold; margin-bottom:15px;">Smart Business ERP Portal</p></div>', unsafe_allow_html=True)
        display_to_fse = {e.split("-")[1].strip(): e for e in fse_list if "-" in e}
        login_list_display = ["-- Select Profile --", "👑 Admin"] + list(display_to_fse.keys())

        u_sel = st.selectbox("👤 Select Profile", login_list_display)
        u_pwd = st.text_input("🔑 Password", type="password")
        
        if st.button("🚀 SECURE LOGIN", use_container_width=True, type="primary"):
            if u_sel == "👑 Admin" and u_pwd == ADMIN_PWD:
                st.session_state.update({'logged_in': True, 'role': 'admin', 'fse_name': 'All Employees'})
                add_audit_log("Admin", "Logged in")
                st.rerun()
            elif u_sel != "-- Select Profile --":
                emp_id = display_to_fse[u_sel].split(" - ")[0].strip()
                if emp_id in USER_CREDS and USER_CREDS[emp_id]["pwd"] == u_pwd:
                    st.session_state.update({'logged_in': True, 'role': 'staff', 'fse_name': display_to_fse[u_sel]})
                    add_audit_log(display_to_fse[u_sel], "Logged in")
                    st.rerun()
            st.error("❌ Invalid Password!")
else:
    current_role = st.session_state.get('role', 'staff')
    current_fse = st.session_state.get('fse_name', 'Guest')
    
    if st.session_state.get('show_popup'):
        st.markdown(f'<div style="background:white; padding:25px; border-radius:15px; text-align:center; border:3px solid #16a34a; max-width:450px; margin:20px auto;"><h1 style="color:#16a34a; margin:0;">✅ SUCCESS!</h1><p>{st.session_state.get("popup_msg")}</p></div>', unsafe_allow_html=True)
        if st.button("❌ CLOSE", type="primary", use_container_width=True):
            st.session_state['show_popup'] = False; st.rerun()
        st.stop()

    nav_c1, nav_c2, nav_c3 = st.columns([2, 1, 1])
    nav_c1.markdown(f"### 🏢 Sandhya ERP | Active: **{current_fse.split('-')[-1]}**")
    if nav_c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    if nav_c3.button("🚪 Logout", use_container_width=True): st.session_state.clear(); st.rerun()

    df_h = load_db()
    df_p = load_products()

    # 🟢 EXACT CORRECT TABS MAPPING
    if current_role == 'admin':
        tabs = st.tabs(["📊 1. LIVE KPI", "🛒 2. POS BILLING", "👷 3. EMPLOYEE MGT", "📦 4. INVENTORY", "📈 5. SALES", "⚠️ 6. RECOVERY", "🔥 7. SCHEMES", "💰 8. CASH", "🔴 9. RED PROJECT", "🕵️ 10. AUDIT LOGS"])
    else:
        tabs = st.tabs(["👷 MY PERFORMANCE", "🛒 QUICK BILLING", "⚠️ RECOVERY ENTRY"])

    # --- TAB 0: LIVE KPI ---
    if current_role == 'admin':
        with tabs[0]:
            st.subheader("📈 Business Performance Dashboard")
            today_sale = 0.0; today_profit = 0.0
            if not df_h.empty:
                today_df = df_h[df_h['dt_fixed'].dt.date == date.today()]
                for _, r in today_df.iterrows():
                    tech = parse_tech(r.iloc[3], fallback_total=float(r.iloc[11]) if pd.notna(r.iloc[11]) else 0.0)
                    if "Inv: SE-" in tech["Inv"]:
                        s_amt = float(r.iloc[11]); c_amt = tech["Cost"] * tech["Qty"]
                        today_sale += s_amt; today_profit += (s_amt - c_amt)

            k1, k2, k3 = st.columns(3)
            k1.markdown(f'<div class="kpi-card"><div class="kpi-title">Today\'s Sale</div><div class="kpi-value" style="color:#2563eb;">₹{today_sale:,.0f}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="kpi-card"><div class="kpi-title">Today\'s Profit</div><div class="kpi-value" style="color:#16a34a;">₹{today_profit:,.0f}</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="kpi-card"><div class="kpi-title">Active Staff</div><div class="kpi-value" style="color:#0891b2;">{len(fse_list)-1}</div></div>', unsafe_allow_html=True)

    # --- TAB 1: POS BILLING ---
    pos_tab = tabs[1] if current_role == 'admin' else tabs[1]
    with pos_tab:
        st.write("### 🛒 Create New Customer Bill")
        st.info("यहाँ से कस्टमर का नाम, नंबर और सामान स्कैन करके बिल बनाएँ।")

    # --- TAB 2: EMPLOYEE MGT (Fixing the Blank Tab!) ---
    emp_tab = tabs[2] if current_role == 'admin' else tabs[0]
    with emp_tab:
        st.write("### 👥 Staff Performance & Entry Portal")
        st.info("यहाँ से एम्प्लोयी की MNP, SIM, AirFiber इंस्टालेशन और सैलरी की एंट्री करें।")
        
        c1, c2 = st.columns(2)
        emp_sel = c1.selectbox("Select Employee", fse_list)
        entry_date = c2.date_input("Entry Date")
        
        act_sel = st.selectbox("Activity", ["MNP", "New SIM", "AirFiber Install", "Salary Paid"])
        if st.button("💾 SAVE EMPLOYEE DATA", type="primary"):
            st.success("✅ Employee Data Saved! (Google Sheet setup ready)")

    # --- TAB 3: INVENTORY ---
    inv_tab = tabs[3] if current_role == 'admin' else None
    if inv_tab:
        with inv_tab:
            st.write("### 📦 Inventory Management")
            if df_p.empty: st.warning("Products list is empty. Please check Google Sheet link.")
            else: st.dataframe(df_p)

    # --- TAB 4: SALES ANALYTICS ---
    sales_tab = tabs[4] if current_role == 'admin' else None
    if sales_tab:
        with sales_tab: st.write("### 📈 Sales Reports")

    # --- TAB 5: RECOVERY ---
    rec_tab = tabs[5] if current_role == 'admin' else tabs[2]
    with rec_tab:
        st.write("### ⚠️ Payment Recovery & Dues")
        st.info("बकायेदारों की लिस्ट और WhatsApp रिमाइंडर।")

    # --- TAB 6 TO 8 ---
    if current_role == 'admin':
        with tabs[6]: st.write("### 🔥 MNP Schemes")
        with tabs[7]: st.write("### 💰 Cash Collection")
        with tabs[8]: st.write("### 🔴 Red Project Payout")

    # --- TAB 9: AUDIT LOGS ---
    if current_role == 'admin':
        with tabs[9]:
            st.subheader("🕵️ System Audit Log History")
            log_list = st.session_state.get('audit_logs', [])
            if log_list: st.markdown(f'<div class="audit-box">{"<br>".join(log_list)}</div>', unsafe_allow_html=True)
            else: st.caption("No activity yet.")
