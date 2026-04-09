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

# 1. Page Configuration (Fixed A4 Scale)
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="centered", initial_sidebar_state="collapsed")

# 🟢 PERSISTENT SESSION STATES
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "kb_retailer" not in st.session_state: st.session_state.kb_retailer = None
if "kb_action" not in st.session_state: st.session_state.kb_action = None
if "show_success_modal" not in st.session_state: st.session_state.show_success_modal = False
if "success_display_text" not in st.session_state: st.session_state.success_display_text = ""
if "success_txn_type" not in st.session_state: st.session_state.success_txn_type = ""
if "success_wa_link" not in st.session_state: st.session_state.success_wa_link = ""
if "role" not in st.session_state: st.session_state.role = None
if "current_page" not in st.session_state: st.session_state.current_page = "LOGIN"

# 💎 FULL SCREEN SUCCESS POPUP
if st.session_state.show_success_modal:
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; background: #f0fdf4; border-radius: 20px; border: 2px solid #86efac; padding: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); margin-top: 20px;">
        <div style="font-size: 90px;">✅</div>
        <div style="font-size: 28px; font-weight: 800; color: #166534; margin-bottom: 10px;">Successful!</div>
        <div style="font-size: 50px; font-weight: 900; color: #0b57d0; margin-bottom: 5px;">{st.session_state.success_display_text}</div>
        <div style="font-size: 18px; color: #4b5563; text-transform: uppercase; background: #e5e7eb; padding: 5px 15px; border-radius: 20px;">{st.session_state.success_txn_type}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.session_state.success_wa_link:
        st.markdown(f"<div style='text-align:center; margin-bottom: 20px;'><a href='{st.session_state.success_wa_link}' target='_blank' style='display:inline-block; padding:15px 30px; background-color:#25D366; color:white; font-size:18px; font-weight:800; border-radius:30px; text-decoration:none;'>📲 Send WhatsApp Receipt</a></div>", unsafe_allow_html=True)
    if st.button("❌ CLOSE & CONTINUE", use_container_width=True):
        st.session_state.show_success_modal = False
        st.rerun()
    st.stop()

# 💎 CSS DESIGN (Joined Card Layout)
st.markdown("""
    <style>
    .main .block-container { max-width: 480px; padding: 1.5rem; background: white; min-height: 100vh; margin: auto; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { display: none; }
    .app-header { background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%); color: white; padding: 25px; border-radius: 16px; text-align: center; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }
    
    /* 📱 JOINED BOX DESIGN (No Gap) */
    .stButton > button { 
        border-radius: 12px 0 0 12px !important; 
        height: 75px !important; 
        font-weight: 700 !important; 
        font-size: 15px !important; 
        margin-bottom: 12px !important; 
        border: 1.5px solid #e2e8f0 !important; 
        background: white !important; 
        color: #1e293b !important;
        text-align: left !important;
        padding-left: 15px !important;
        width: 100% !important;
    }
    
    .amt-joined-red { 
        background: linear-gradient(135deg, #ff4b4b 0%, #b91c1c 100%); 
        color: white; height: 75px; display: flex; align-items: center; justify-content: center; 
        font-weight: 800; font-size: 17px; border-radius: 0 12px 12px 0; 
        margin-left: -2px; margin-bottom: 12px; border: 1.5px solid #b91c1c;
    }
    .amt-joined-green { 
        background: linear-gradient(135deg, #4ade80 0%, #15803d 100%); 
        color: white; height: 75px; display: flex; align-items: center; justify-content: center; 
        font-weight: 800; font-size: 17px; border-radius: 0 12px 12px 0; 
        margin-left: -2px; margin-bottom: 12px; border: 1.5px solid #15803d;
    }
    
    .kb-header-container { display: flex; justify-content: space-around; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .kb-ledger-row { display: flex; justify-content: space-between; border-bottom: 1px solid #eee; background: white; padding: 12px; align-items: center; }
    
    @media (max-width: 768px) { 
        div[data-testid="stHorizontalBlock"] { gap: 0px !important; } 
    }
    </style>
""", unsafe_allow_html=True)

# 🛑 CONFIG & DATA
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

# 🔐 LOGIN SYSTEM
if not st.session_state.authenticated:
    st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Secure Login</p></div>', unsafe_allow_html=True)
    l_mob = st.text_input("Mobile Number")
    l_pin = st.text_input("PIN", type="password")
    if st.button("🚀 UNLOCK DASHBOARD", use_container_width=True):
        if l_mob == "7479584179" and l_pin == "9557":
            st.session_state.role = "Admin"; st.session_state.authenticated = True; st.session_state.current_page = "HOME"; st.rerun()
        elif l_mob == "7254972081" and l_pin == "2081":
            st.session_state.role = "Employee"; st.session_state.emp_name = "Babloo kumar singh"; st.session_state.authenticated = True; st.session_state.current_page = "EMP_HOME"; st.rerun()
        st.error("Invalid Details")
    st.stop()

# Helpers
def go_to(p): st.session_state.current_page = p; st.session_state.kb_retailer = None; st.session_state.kb_action = None
fse_list = ["Avdhesh Kumar", "Babloo kumar singh"]
def verify_pin(n, p):
    if n == "Avdhesh Kumar" and p == "9557": return True
    if n == "Babloo kumar singh" and p == "2081": return True
    if st.session_state.role == "Employee" and p == st.session_state.emp_pin: return True
    return False

# --- DASHBOARDS ---
if st.session_state.current_page == "HOME":
    st.markdown('<div class="app-header"><h3>Admin Dashboard</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💸 Khatabook 3D", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("📊 Live Stock", use_container_width=True): go_to("STOCK"); st.rerun()
    with col2:
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD"); st.rerun()
        if st.button("🚪 Logout", use_container_width=True): st.session_state.authenticated = False; st.rerun()

elif st.session_state.current_page == "EMP_HOME":
    st.info(f"👤 Welcome, {st.session_state.emp_name}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 Khatabook", use_container_width=True): go_to("DUES"); st.rerun()
    with col2:
        if st.button("📦 Sim Stock", use_container_width=True): go_to("STOCK"); st.rerun()

# --- 📲 KHATABOOK 3D (JOINED DESIGN) ---
elif st.session_state.current_page == "DUES":
    st.button("🔙 Back Menu", on_click=lambda: go_to("HOME" if st.session_state.role=="Admin" else "EMP_HOME"))
    if st.session_state.kb_retailer is None:
        all_r = []; tm, ta = 0, 0
        for n, r in retailers_dict.items():
            u_led = led_df[led_df['Retailer Name'] == r['Retailer Name']]
            bal = pd.to_numeric(u_led['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_led['Amount In (Credit)'], errors='coerce').sum()
            if bal > 0: tm += bal
            else: ta += abs(bal)
            prm = str(r.get('PRM ID','')).split('.')[0]
            all_r.append({"Name": r['Retailer Name'], "PRM": prm, "Mob": str(r['Mobile Number']).split('.')[0], "Bal": bal, "Disp": n})
        
        st.markdown(f"<div class='kb-header-container'><div class='kb-box'><h4>Dene hain</h4><h2 style='color:#15803d;'>₹ {ta:,.0f}</h2></div><div class='kb-box'><h4>Milenge</h4><h2 style='color:#b91c1c;'>₹ {tm:,.0f}</h2></div></div>", unsafe_allow_html=True)
        all_r.sort(key=lambda x: -abs(x['Bal']))
        sel = st.selectbox("🔍 Search...", ["All"] + [x['Disp'] for x in all_r])
        for i in all_r:
            if sel == "All" or i['Disp'] == sel:
                cls = "amt-joined-red" if i['Bal'] > 0 else "amt-joined-green"
                c1, c2 = st.columns([3, 1])
                with c1:
                    if st.button(f"👤 {i['Name']} ({i['PRM']})", key=f"btn_{i['Disp']}", use_container_width=True):
                        st.session_state.kb_retailer = i['Name']; st.rerun()
                with c2: 
                    st.markdown(f"<div class='{cls}'>₹ {abs(i['Bal']):,.0f}</div>", unsafe_allow_html=True)
    else:
        # SINGLE RETAILER VIEW
        name = st.session_state.kb_retailer
        r_info = next(v for k, v in retailers_dict.items() if v['Retailer Name'] == name)
        mob = str(r_info['Mobile Number']).split('.')[0]
        u_led = led_df[led_df['Retailer Name'] == name].sort_values('DateObj')
        bal = 0; rows = []
        for _, r in u_led.iterrows():
            d = pd.to_numeric(r['Amount Out (Debit)'], 0); c = pd.to_numeric(r['Amount In (Credit)'], 0)
            bal += (d - c); rows.append({"d": r['Date'], "i": r['Product/Service'], "out": d, "in": c, "b": bal})
        
        st.markdown(f"<div style='background:#0b57d0; color:white; padding:15px; border-radius:12px; margin-bottom:10px; text-align:center;'><h3>{name}</h3><p>{mob}</p><a href='tel:{mob}' style='display:block; text-align:center; background:white; color:#0b57d0; padding:10px; border-radius:8px; text-decoration:none; font-weight:800;'>📞 CALL NOW</a></div>", unsafe_allow_html=True)
        st.write(f"## Balance: ₹ {bal:,.0f}")
        for r in reversed(rows):
            st.markdown(f"<div class='kb-ledger-row'><div style='width:50%'><b>{r['d']}</b><br>{r['i']}</div><div style='color:#b91c1c;'>{f'₹{r['out']:,.0f}' if r['out']>0 else ''}</div><div style='color:#15803d;'>{f'₹{r['in']:,.0f}' if r['in']>0 else ''}</div></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        b1, b2 = st.columns(2)
        if b1.button("🔴 DIYE", use_container_width=True): st.session_state.kb_action = "diye"; st.rerun()
        if b2.button("🟢 MILE", use_container_width=True): st.session_state.kb_action = "mile"; st.rerun()
        
        if st.session_state.kb_action == "diye":
            with st.form("d"):
                t = st.selectbox("Type", ["Etop Transfer", "Sim Card", "JPB V4"]); a = st.number_input("Amount"); f = st.selectbox("FSE", fse_list); p = st.text_input("PIN", type="password")
                if st.form_submit_button("Save"):
                    if verify_pin(f, p):
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"type":t,"amt_out":a,"fse":f,"txn_id":"KB"})
                        st.session_state.success_display_text = f"₹ {a}"; st.session_state.success_txn_type = t; st.session_state.show_success_modal = True; st.cache_data.clear(); st.rerun()

        if st.session_state.kb_action == "mile":
            with st.form("m"):
                m = st.selectbox("Mode", ["Cash", "Online"]); a = st.number_input("Amount"); f = st.selectbox("FSE", fse_list); p = st.text_input("PIN", type="password")
                if st.form_submit_button("Save"):
                    if verify_pin(f, p):
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"type":f"Payment ({m})","amt_in":a,"fse":f,"txn_id":"KB"})
                        st.session_state.success_display_text = f"₹ {a}"; st.session_state.success_txn_type = f"Payment ({m})"; st.session_state.show_success_modal = True; st.cache_data.clear(); st.rerun()

elif st.session_state.current_page == "STOCK":
    st.button("🔙 Back", on_click=lambda: go_to(get_home()))
    st.write("Loading Stock Data...")

elif st.session_state.current_page == "ADD":
    st.button("🔙 Back", on_click=lambda: go_to(get_home()))
    with st.form("add"):
        n=st.text_input("Name"); m=st.text_input("Mob"); p=st.text_input("PRM"); l=st.text_input("Loc")
        if st.form_submit_button("Add"):
            requests.post(WEBHOOK_URL, json={"action":"add_retailer","name":n.upper(),"mobile":m,"prm":p,"location":l.upper(),"date":date.today().strftime("%d-%m-%Y")})
            st.success("Added!"); st.cache_data.clear()
