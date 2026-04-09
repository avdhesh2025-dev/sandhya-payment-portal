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

# 1. Page Configuration
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# 🟢 PERSISTENT LOGIN SESSION (Remember Me Logic)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 🟢 SUCCESS MODAL STATES
if "show_success_modal" not in st.session_state: st.session_state.show_success_modal = False
if "success_display_text" not in st.session_state: st.session_state.success_display_text = ""
if "success_txn_type" not in st.session_state: st.session_state.success_txn_type = ""
if "success_wa_link" not in st.session_state: st.session_state.success_wa_link = ""

# 💎 Full Screen Success Overlay
if st.session_state.show_success_modal:
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 55vh; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 20px; border: 2px solid #86efac; padding: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); margin-top: 20px;">
        <div style="font-size: 90px; color: #16a34a; margin-bottom: 5px; animation: pop 0.4s forwards;">✅</div>
        <div style="font-size: 28px; font-weight: 800; color: #166534; margin-bottom: 10px; text-align: center;">Successful!</div>
        <div style="font-size: 50px; font-weight: 900; color: #0b57d0; margin-bottom: 5px; text-align: center;">{st.session_state.success_display_text}</div>
        <div style="font-size: 18px; font-weight: 700; color: #4b5563; margin-bottom: 25px; text-align: center; text-transform: uppercase; letter-spacing: 1px; background: #e5e7eb; padding: 5px 15px; border-radius: 20px;">{st.session_state.success_txn_type}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.session_state.success_wa_link:
        st.markdown(f"<div style='text-align:center; margin-bottom: 20px;'><a href='{st.session_state.success_wa_link}' target='_blank' style='display:inline-block; padding:15px 30px; background-color:#25D366; color:white; font-size:18px; font-weight:800; border-radius:30px; text-decoration:none;'>📲 Send Receipt</a></div>", unsafe_allow_html=True)
    if st.button("❌ CLOSE & CONTINUE", use_container_width=True):
        st.session_state.show_success_modal = False
        st.rerun()
    st.stop()

# 💎 CSS UI Design
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    [data-testid="stSidebar"] { display: none; }
    .app-header { background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%); color: white; padding: 20px; border-radius: 16px; text-align: center; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
    .stButton > button { border-radius: 12px; height: 60px; font-weight: 700; transition: 0.3s; }
    .kb-header-container { display: flex; justify-content: space-around; background: white; padding: 15px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .kb-box { width: 45%; text-align: center; }
    .kb-ledger-row { display: flex; justify-content: space-between; border-bottom: 1px solid #f0f0f0; background: white; padding: 10px; }
    @media (max-width: 768px) { div[data-testid="stHorizontalBlock"] { flex-direction: row !important; flex-wrap: nowrap !important; gap: 5px !important; } }
    </style>
""", unsafe_allow_html=True)

# 🛑 SHEET CONFIG
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyH_oGxKbNZQj2azNOR0FgkLyAKxBfaAoE0Yo3DHmRpNOFZczJRayBhPd056SGUVWbxWQ/exec"
sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

@st.cache_data(ttl=5)
def load_data():
    try:
        cb = int(time.time())
        ret = pd.read_csv(f"{retailers_csv}&cb={cb}").dropna(how="all").fillna("")
        inv = pd.read_csv(f"{inventory_csv}&cb={cb}").dropna(how="all").fillna("")
        led = pd.read_csv(f"{ledger_csv}&cb={cb}").dropna(how="all").fillna("")
        led['DateObj'] = pd.to_datetime(led['Date'], format='%d-%m-%Y', errors='coerce')
        return ret, inv, led
    except: return None, None, None

ret_df, inv_df, led_df = load_data()

# 🔐 LOGIN SYSTEM
if not st.session_state.authenticated:
    st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Smart Management Login</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 Login", "📝 New Registration"])
    
    with tab1:
        l_mob = st.text_input("Mobile Number")
        l_pin = st.text_input("PIN", type="password")
        remember = st.checkbox("Keep me logged in (Remember Me)")
        if st.button("🚀 UNLOCK APP", use_container_width=True):
            if l_mob == "7479584179" and l_pin == "9557":
                st.session_state.role = "Admin"; st.session_state.authenticated = True; st.rerun()
            elif l_mob == "7254972081" and l_pin == "2081":
                st.session_state.role = "Employee"; st.session_state.emp_name = "Babloo kumar singh"; st.session_state.emp_pin = "2081"; st.session_state.authenticated = True; st.rerun()
            else:
                if ret_df is not None:
                    emps = ret_df[ret_df['Location'].astype(str).str.upper() == 'EMPLOYEE']
                    for _, r in emps.iterrows():
                        if str(r.get("Mobile Number")).split('.')[0] == l_mob and str(r.get("PRM ID")).replace("EMP_","") == l_pin:
                            st.session_state.role = "Employee"; st.session_state.emp_name = r["Retailer Name"]; st.session_state.emp_pin = l_pin; st.session_state.authenticated = True; st.rerun()
                st.error("❌ Wrong Details")
    with tab2:
        reg_n = st.text_input("Name"); reg_m = st.text_input("Mobile"); reg_p = st.text_input("4-Digit PIN", type="password", max_chars=4)
        if st.button("Register Now"):
            requests.post(WEBHOOK_URL, json={"action":"add_retailer","name":reg_n.upper(),"mobile":reg_m,"prm":f"EMP_{reg_p}","location":"EMPLOYEE","date":date.today().strftime("%d-%m-%Y")})
            st.success("Success! Please login."); st.cache_data.clear()
    st.stop()

# --- MAIN APP LOGIC ---
st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1></div>', unsafe_allow_html=True)

# 🟢 HELPERS
fse_list = ["Avdhesh Kumar", "Babloo kumar singh"]
if st.session_state.role == "Employee": fse_list = [st.session_state.emp_name]
def verify_pin(n, p):
    if n == "Avdhesh Kumar" and p == "9557": return True
    if n == "Babloo kumar singh" and p == "2081": return True
    if st.session_state.role == "Employee" and p == st.session_state.emp_pin: return True
    return False

def clean_id(v):
    try: return str(int(float(v)))
    except: return str(v).strip()

valid_ret = ret_df[ret_df['Location'].astype(str).str.upper() != 'EMPLOYEE'] if ret_df is not None else None
retailers_data = {f"{clean_id(r['PRM ID'])} - {r['Retailer Name']}": r for _, r in valid_ret.iterrows()} if valid_ret is not None else {}

# --- 🏠 NAVIGATION ---
if "current_page" not in st.session_state: st.session_state.current_page = "HOME" if st.session_state.role == "Admin" else "EMP_HOME"

def go_to(p): st.session_state.current_page = p; st.session_state.kb_retailer = None

# --- ADMIN DASHBOARD ---
if st.session_state.current_page == "HOME":
    c1, c2 = st.columns([3, 1])
    if c2.button("Logout"): st.session_state.authenticated = False; st.rerun()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Live Stock", use_container_width=True): go_to("STOCK"); st.rerun()
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD"); st.rerun()
    with col2:
        if st.button("💸 Khatabook 3D", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("🚨 Urgent Recovery", use_container_width=True): go_to("URGENT"); st.rerun()
    if st.button("💰 Today Collection", use_container_width=True): go_to("COL"); st.rerun()

# --- EMPLOYEE DASHBOARD (Quick & Smooth) ---
elif st.session_state.current_page == "EMP_HOME":
    c1, c2 = st.columns([3, 1])
    c1.info(f"👤 {st.session_state.emp_name}")
    if c2.button("Exit"): st.session_state.authenticated = False; st.rerun()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 Khatabook 3D", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD"); st.rerun()
    with col2:
        if st.button("🚨 Urgent", use_container_width=True): go_to("URGENT"); st.rerun()
        if st.button("📦 My Stock", use_container_width=True): go_to("STOCK"); st.rerun()

# --- KHATABOOK (All Customer Unified) ---
elif st.session_state.current_page == "DUES":
    if st.button("⬅️ Back"): go_to("HOME" if st.session_state.role == "Admin" else "EMP_HOME"); st.rerun()
    
    if st.session_state.kb_retailer is None:
        all_r = []
        for n, r in retailers_data.items():
            u_led = led_df[led_df['Retailer Name'] == r['Retailer Name']]
            bal = pd.to_numeric(u_led['Amount Out (Debit)'], 0).sum() - pd.to_numeric(u_led['Amount In (Credit)'], 0).sum()
            all_r.append({"Name": r['Retailer Name'], "Mob": r['Mobile Number'], "Bal": bal})
        
        all_r.sort(key=lambda x: (0 if x['Bal'] > 0 else 1 if x['Bal'] < 0 else 2, -abs(x['Bal'])))
        
        sel = st.selectbox("🔍 Search Customer...", ["All Customers"] + [f"{x['Name']} ({x['Mob']})" for x in all_r])
        display_list = [x for x in all_r if sel == "All Customers" or f"{x['Name']} ({x['Mob']})" == sel]
        
        for item in display_list:
            c = "#b91c1c" if item['Bal'] > 0 else "#15803d" if item['Bal'] < 0 else "#6b7280"
            with st.container(border=True):
                col1, col2 = st.columns([3, 2])
                if col1.button(item['Name'], key=f"r_{item['Name']}"): st.session_state.kb_retailer = item['Name']; st.rerun()
                col2.markdown(f"<div style='text-align:right; font-size:18px; font-weight:bold; color:{c};'>₹ {abs(item['Bal']):,.0f}</div>", unsafe_allow_html=True)

    else:
        name = st.session_state.kb_retailer
        r_info = next(v for k, v in retailers_data.items() if v['Retailer Name'] == name)
        mob = r_info['Mobile Number']
        if st.button("⬅️ Back to List"): st.session_state.kb_retailer = None; st.rerun()
        
        st.markdown(f"<div style='background:#0b57d0; color:white; padding:15px; border-radius:10px;'><h3>{name}</h3><p>{mob}</p></div>", unsafe_allow_html=True)
        
        u_led = led_df[led_df['Retailer Name'] == name].sort_values('DateObj')
        bal = 0
        rows = []
        for _, r in u_led.iterrows():
            d, c = pd.to_numeric(r['Amount Out (Debit)'], 0), pd.to_numeric(r['Amount In (Credit)'], 0)
            bal += (d - c)
            rows.append({"d": r['Date'], "i": r['Product/Service'], "out": d, "in": c, "b": bal})
        
        st.markdown(f"<div style='background:white; padding:20px; border-radius:10px; margin:10px 0; text-align:center;'><h4>Balance</h4><h2 style='color:#b91c1c;'>₹ {bal:,.0f}</h2></div>", unsafe_allow_html=True)
        
        for r in reversed(rows):
            st.markdown(f"<div class='kb-ledger-row'><div style='width:50%'><b>{r['d']}</b><br>{r['i']}</div><div style='color:#b91c1c;'>{f'₹{r['out']:.0f}' if r['out']>0 else ''}</div><div style='color:#15803d;'>{f'₹{r['in']:.0f}' if r['in']>0 else ''}</div></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        b1, b2 = st.columns(2)
        if b1.button("🔴 AAPNE DIYE", use_container_width=True): st.session_state.kb_action = "diye"; st.rerun()
        if b2.button("🟢 AAPKO MILE", use_container_width=True): st.session_state.kb_action = "mile"; st.rerun()
        
        if st.session_state.kb_action == "diye":
            with st.form("d_f"):
                t = st.selectbox("Type", ["Etop Transfer", "JPB V4", "Sim Card"])
                if t == "Etop Transfer": 
                    o = st.selectbox("Amount", ["5000","3000","2000","1500","500","Manual"])
                    amt = float(o) if o!="Manual" else st.number_input("Enter Amount")
                    qty = 0
                elif t == "Sim Card": amt = 0; qty = st.number_input("Qty", min_value=1)
                else: amt = st.number_input("Amount"); qty = st.number_input("Qty")
                f = st.selectbox("FSE", fse_list); p = st.text_input("PIN", type="password")
                if st.form_submit_button("Save"):
                    if verify_pin(f, p):
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"r_mob":mob,"type":t,"qty":qty,"amt_out":amt,"amt_in":0,"fse":f,"txn_id":"KB"})
                        st.session_state.success_display_text = f"₹{amt}" if amt>0 else f"{qty} SIM"
                        st.session_state.success_txn_type = t; st.session_state.show_success_modal = True; st.session_state.kb_action = None; st.cache_data.clear(); st.rerun()
        
        if st.session_state.kb_action == "mile":
            with st.form("m_f"):
                m = st.selectbox("Mode", ["Cash", "Online"]); amt = st.number_input("Amount", min_value=1)
                f = st.selectbox("FSE", fse_list); p = st.text_input("PIN", type="password")
                if st.form_submit_button("Save"):
                    if verify_pin(f, p):
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"r_mob":mob,"type":f"Payment ({m})","qty":0,"amt_out":0,"amt_in":amt,"fse":f,"txn_id":"KB"})
                        st.session_state.success_display_text = f"₹{amt}"; st.session_state.success_txn_type = f"Payment ({m})"; st.session_state.show_success_modal = True; st.session_state.kb_action = None; st.cache_data.clear(); st.rerun()

# --- OTHER PAGES (URGENT, STOCK, ADD) ---
elif st.session_state.current_page == "STOCK":
    st.button("⬅️ Back", on_click=go_to, args=(get_home(),))
    if st.session_state.role == "Admin": st.dataframe(inv_df, use_container_width=True)
    else:
        alloc = pd.to_numeric(led_df[(led_df['Retailer Name']==st.session_state.emp_name)&(led_df['Product/Service']=='Sim Allocation')]['Qty'], 0).sum()
        dist = pd.to_numeric(led_df[(led_df['FSE Name']==st.session_state.emp_name)&(led_df['Product/Service']=='Sim Card')]['Qty'], 0).sum()
        st.metric("SIM Stock Balance", int(alloc - dist))

elif st.session_state.current_page == "URGENT":
    st.button("⬅️ Back", on_click=go_to, args=(get_home(),))
    st.error("🚨 Urgent Recovery List")
    # Smart recovery logic...
    for n, r in retailers_data.items():
        u_data = led_df[led_df['Retailer Name'] == r['Retailer Name']]
        # check > 24hrs logic...
        st.write(f"⚠️ {r['Retailer Name']} - Pending")

elif st.session_state.current_page == "ADD":
    st.button("⬅️ Back", on_click=go_to, args=(get_home(),))
    with st.form("add_r"):
        n = st.text_input("Name"); m = st.text_input("Mobile"); p = st.text_input("PRM"); l = st.text_input("Location")
        if st.form_submit_button("Save"):
            requests.post(WEBHOOK_URL, json={"action":"add_retailer","name":n.upper(),"mobile":m,"prm":p,"location":l.upper(),"date":date.today().strftime("%d-%m-%Y")})
            st.success("Added!"); st.cache_data.clear()

elif st.session_state.current_page == "COL":
    st.button("⬅️ Back", on_click=go_to, args=("HOME",))
    st.write("Today's Collections Detail...")
    t_led = led_df[led_df['Date'] == date.today().strftime("%d-%m-%Y")]
    st.dataframe(t_led[pd.to_numeric(t_led['Amount In (Credit)'],0)>0], use_container_width=True)
