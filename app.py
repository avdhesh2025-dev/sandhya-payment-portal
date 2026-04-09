import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import urllib.parse
import requests
import time

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# 1. Page Configuration (A4 scale)
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="centered", initial_sidebar_state="collapsed")

# 🟢 PERSISTENT SESSION STATES
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "kb_retailer" not in st.session_state: st.session_state.kb_retailer = None
if "kb_action" not in st.session_state: st.session_state.kb_action = None
if "show_success_modal" not in st.session_state: st.session_state.show_success_modal = False
if "success_display_text" not in st.session_state: st.session_state.success_display_text = ""
if "success_txn_type" not in st.session_state: st.session_state.success_txn_type = ""
if "role" not in st.session_state: st.session_state.role = None
if "current_page" not in st.session_state: st.session_state.current_page = "LOGIN"

# 💎 FULL SCREEN SUCCESS POPUP
if st.session_state.show_success_modal:
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; background: #f0fdf4; border-radius: 20px; border: 2px solid #86efac; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-top: 20px;">
        <div style="font-size: 80px;">✅</div>
        <div style="font-size: 28px; font-weight: 800; color: #166534;">Success!</div>
        <div style="font-size: 45px; font-weight: 900; color: #0b57d0;">{st.session_state.success_display_text}</div>
        <div style="font-size: 18px; color: #4b5563; text-transform: uppercase;">{st.session_state.success_txn_type}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("❌ CLOSE & CONTINUE", use_container_width=True):
        st.session_state.show_success_modal = False
        st.rerun()
    st.stop()

# 💎 CSS UI (A4 Scale & Professional Ledger)
st.markdown("""
    <style>
    .main .block-container { max-width: 480px; padding: 1.5rem; background: white; box-shadow: 0 0 15px rgba(0,0,0,0.1); min-height: 100vh; margin: auto; }
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { display: none; }
    .app-header { background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 15px; }
    
    .stButton > button { border-radius: 12px; height: 70px; font-weight: 700; border: 1.5px solid #e2e8f0; background: white; }
    .amt-box-red { background: linear-gradient(135deg, #ff4b4b 0%, #b91c1c 100%); color: white; border-radius: 10px; padding: 8px 12px; font-weight: 800; font-size: 16px; text-align: center; min-width: 90px; }
    .amt-box-green { background: linear-gradient(135deg, #4ade80 0%, #15803d 100%); color: white; border-radius: 10px; padding: 8px 12px; font-weight: 800; font-size: 16px; text-align: center; min-width: 90px; }
    
    /* 📝 LEDGER ROW STYLING */
    .ledger-card { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f0f0; padding: 12px 0; }
    .ledger-info { flex: 2; text-align: left; }
    .ledger-debit { flex: 1; text-align: right; color: #b91c1c; font-weight: 700; font-size: 15px; }
    .ledger-credit { flex: 1; text-align: right; color: #15803d; font-weight: 700; font-size: 15px; }
    
    @media (max-width: 768px) { div[data-testid="stHorizontalBlock"] { gap: 0px !important; } }
    </style>
""", unsafe_allow_html=True)

# 🛑 DATA CONNECTION
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyH_oGxKbNZQj2azNOR0FgkLyAKxBfaAoE0Yo3DHmRpNOFZczJRayBhPd056SGUVWbxWQ/exec"
sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

@st.cache_data(ttl=5)
def load_data():
    try:
        cb = int(time.time())
        ret = pd.read_csv(f"{retailers_csv}&cb={cb}").dropna(how="all").fillna("")
        led = pd.read_csv(f"{ledger_csv}&cb={cb}").dropna(how="all").fillna("")
        led['DateObj'] = pd.to_datetime(led['Date'], format='%d-%m-%Y', errors='coerce')
        return ret, led
    except: return None, None

ret_df, led_df = load_data()
valid_ret = ret_df[ret_df['Location'].astype(str).str.upper() != 'EMPLOYEE'] if ret_df is not None else None
retailers_dict = {f"{r['Retailer Name']} ({str(r['Mobile Number']).split('.')[0]})": r for _, r in valid_ret.iterrows()} if valid_ret is not None else {}

# 🔐 LOGIN
if not st.session_state.authenticated:
    st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Smart Login Portal</p></div>', unsafe_allow_html=True)
    l_mob = st.text_input("Mobile")
    l_pin = st.text_input("PIN", type="password")
    if st.button("🚀 LOGIN", use_container_width=True):
        if l_mob == "7479584179" and l_pin == "9557":
            st.session_state.role = "Admin"; st.session_state.authenticated = True; st.session_state.current_page = "HOME"; st.rerun()
        elif l_mob == "7254972081" and l_pin == "2081":
            st.session_state.role = "Employee"; st.session_state.emp_name = "Babloo kumar singh"; st.session_state.authenticated = True; st.session_state.current_page = "EMP_HOME"; st.rerun()
        st.error("Invalid Details")
    st.stop()

def go_to(p): st.session_state.current_page = p; st.session_state.kb_retailer = None; st.session_state.kb_action = None

# --- DASHBOARDS ---
if st.session_state.current_page == "HOME":
    st.markdown('<div class="app-header"><h3>Admin Dashboard</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💸 Khatabook 3D", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("📊 Live Stock", use_container_width=True): go_to("STOCK"); st.rerun()
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD"); st.rerun()
    with col2:
        if st.button("💰 Today Collection", use_container_width=True): go_to("COL"); st.rerun()
        if st.button("📦 Entry", use_container_width=True): go_to("ENTRY"); st.rerun()
        if st.button("🚪 Logout", use_container_width=True): st.session_state.authenticated = False; st.rerun()

elif st.session_state.current_page == "EMP_HOME":
    st.info(f"👤 User: {st.session_state.emp_name}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 Khatabook", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("📦 Sim Stock", use_container_width=True): go_to("STOCK"); st.rerun()
    with col2:
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD"); st.rerun()
        if st.button("Exit", use_container_width=True): st.session_state.authenticated = False; st.rerun()

# --- 💸 KHATABOOK & LEDGER ---
elif st.session_state.current_page == "DUES":
    st.button("🔙 Back Menu", on_click=lambda: go_to("HOME" if st.session_state.role=="Admin" else "EMP_HOME"))
    if st.session_state.kb_retailer is None:
        all_r = []; tm, ta = 0, 0
        for n, r in retailers_dict.items():
            u_led = led_df[led_df['Retailer Name'] == r['Retailer Name']]
            bal = pd.to_numeric(u_led['Amount Out (Debit)'], 0).sum() - pd.to_numeric(u_led['Amount In (Credit)'], 0).sum()
            if bal > 0: tm += bal
            else: ta += abs(bal)
            all_r.append({"Name": r['Retailer Name'], "PRM": str(r.get('PRM ID','')).split('.')[0], "Mob": str(r['Mobile Number']).split('.')[0], "Bal": bal, "Disp": n})
        
        st.markdown(f"<div class='kb-header-container'><div class='kb-box'><h4>Dene hain</h4><h2 style='color:#15803d;'>₹ {ta:,.0f}</h2></div><div class='kb-box'><h4>Milenge</h4><h2 style='color:#b91c1c;'>₹ {tm:,.0f}</h2></div></div>", unsafe_allow_html=True)
        all_r.sort(key=lambda x: -abs(x['Bal']))
        sel = st.selectbox("🔍 Search...", ["All Customers"] + [x['Disp'] for x in all_r])
        for i in all_r:
            if sel == "All Customers" or i['Disp'] == sel:
                box_cls = "amt-box-red" if i['Bal'] > 0 else "amt-box-green"
                c1, c2 = st.columns([3, 1])
                if c1.button(f"👤 {i['Name']} ({i['PRM']})", key=f"b_{i['Disp']}", use_container_width=True):
                    st.session_state.kb_retailer = i['Name']; st.rerun()
                c2.markdown(f"<div style='padding-top:15px;'><div class='{box_cls}'>₹ {abs(i['Bal']):,.0f}</div></div>", unsafe_allow_html=True)
    else:
        # SINGLE RETAILER LEDGER VIEW
        name = st.session_state.kb_retailer
        r_info = next(v for k, v in retailers_dict.items() if v['Retailer Name'] == name)
        mob = str(r_info['Mobile Number']).split('.')[0]
        
        # 🟢 CALCULATION LOGIC
        u_led = led_df[led_df['Retailer Name'] == name].sort_values('DateObj')
        bal = 0; rows = []
        for _, r in u_led.iterrows():
            d = pd.to_numeric(r['Amount Out (Debit)'], errors='coerce') if pd.notnull(r['Amount Out (Debit)']) else 0
            c = pd.to_numeric(r['Amount In (Credit)'], errors='coerce') if pd.notnull(r['Amount In (Credit)']) else 0
            bal += (d - c)
            rows.append({"d": r['Date'], "i": r['Product/Service'], "out": d, "in": c, "b": bal})

        # HEADER & ACTION BUTTONS
        st.markdown(f"""
        <div style='background:#0b57d0; color:white; padding:15px; border-radius:12px; margin-bottom:10px; text-align:center;'>
            <h3>{name}</h3><p>{mob}</p>
            <div style='display:flex; justify-content:space-around;'>
                <a href='tel:{mob}' style='background:white; color:#0b57d0; padding:10px 25px; border-radius:8px; text-decoration:none; font-weight:800;'>📞 CALL</a>
                <a href='https://wa.me/91{mob}?text=Namaste%2C%20Sandhya%20ERP%20Reminder%3A%20Balance%20Rs%20{abs(bal)}' style='background:#25D366; color:white; padding:10px 25px; border-radius:8px; text-decoration:none; font-weight:800;'>📲 WA</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<div style='background:white; padding:20px; border-radius:10px; text-align:center;'><h4>Current Balance</h4><h2 style='color:#b91c1c;'>₹ {bal:,.0f}</h2></div>", unsafe_allow_html=True)

        # 🟢 LEDGER TABLE (Debit, Credit, Bal)
        st.markdown("<div style='background:#f9fafb; padding:10px; font-weight:800; display:flex; justify-content:space-between;'><div style='width:40%'>Entries</div><div style='width:30%; text-align:right'>Debit (-)</div><div style='width:30%; text-align:right'>Credit (+)</div></div>", unsafe_allow_html=True)
        for r in reversed(rows):
            st.markdown(f"""
            <div class='ledger-card'>
                <div class='ledger-info'><b>{r['d']}</b><br><small>{r['i']}</small><br><span style='color:#6b7280; font-size:11px;'>Bal: ₹{r['b']:,.0f}</span></div>
                <div class='ledger-debit'>{f"₹{r['out']:,.0f}" if r['out']>0 else ""}</div>
                <div class='ledger-credit'>{f"₹{r['in']:,.0f}" if r['in']>0 else ""}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        b1, b2 = st.columns(2)
        if b1.button("🔴 DIYE (Stock)", use_container_width=True): st.session_state.kb_action = "diye"; st.rerun()
        if b2.button("🟢 MILE (Payment)", use_container_width=True): st.session_state.kb_action = "mile"; st.rerun()
        
        if st.session_state.kb_action == "diye":
            with st.form("d_f"):
                t = st.selectbox("Type", ["Etop Transfer", "Sim Card", "JPB V4"]); a = st.number_input("Amount", min_value=0.0)
                if st.form_submit_button("Save"):
                    requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"type":t,"amt_out":a,"txn_id":"KB"})
                    st.session_state.success_display_text = f"₹ {a}"; st.session_state.show_success_modal = True; st.cache_data.clear(); st.rerun()

        if st.session_state.kb_action == "mile":
            with st.form("m_f"):
                m = st.selectbox("Mode", ["Cash", "Online"]); a = st.number_input("Amount Received", min_value=0.0)
                if st.form_submit_button("Save"):
                    requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"type":f"Payment ({m})","amt_in":a,"txn_id":"KB"})
                    st.session_state.success_display_text = f"₹ {a}"; st.session_state.show_success_modal = True; st.cache_data.clear(); st.rerun()

# --- OTHER PAGES (ADD, STOCK) ---
elif st.session_state.current_page == "ADD":
    st.button("⬅️ Back Menu", on_click=lambda: go_to(get_home()))
    with st.form("add_ret"):
        n=st.text_input("Retailer Name"); m=st.text_input("Mobile"); p=st.text_input("PRM ID"); l=st.text_input("Loc")
        if st.form_submit_button("Save"):
            requests.post(WEBHOOK_URL, json={"action":"add_retailer","name":n.upper(),"mobile":m,"prm":p,"location":l.upper(),"date":date.today().strftime("%d-%m-%Y")})
            st.success("Retailer Added!"); st.cache_data.clear()

elif st.session_state.current_page == "STOCK":
    st.button("⬅️ Back Menu", on_click=lambda: go_to(get_home()))
    st.header("📦 Inventory Stock")
    st.dataframe(led_df[led_df['Product/Service']=='Sim Allocation'] if st.session_state.role=="Admin" else led_df[led_df['FSE Name']==st.session_state.emp_name], hide_index=True)
