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

# 1. Page Configuration (A4 scale constraint)
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="centered", initial_sidebar_state="collapsed")

# 🟢 INITIALIZE SESSION STATES
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "kb_retailer" not in st.session_state: st.session_state.kb_retailer = None
if "kb_action" not in st.session_state: st.session_state.kb_action = None
if "show_success_modal" not in st.session_state: st.session_state.show_success_modal = False
if "success_display_text" not in st.session_state: st.session_state.success_display_text = ""
if "success_txn_type" not in st.session_state: st.session_state.success_txn_type = ""
if "role" not in st.session_state: st.session_state.role = None

# 💎 FULL SCREEN SUCCESS POPUP
if st.session_state.show_success_modal:
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; background: #f0fdf4; border-radius: 20px; border: 2px solid #86efac; padding: 20px; box-shadow: 0 15px 30px rgba(0,0,0,0.1); margin-top: 20px;">
        <div style="font-size: 80px;">✅</div>
        <div style="font-size: 25px; font-weight: 800; color: #166534;">Successful!</div>
        <div style="font-size: 45px; font-weight: 900; color: #0b57d0;">{st.session_state.success_display_text}</div>
        <div style="font-size: 18px; background: #e5e7eb; padding: 5px 15px; border-radius: 20px;">{st.session_state.success_txn_type}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("❌ CLOSE & CONTINUE", use_container_width=True):
        st.session_state.show_success_modal = False
        st.rerun()
    st.stop()

# 💎 CSS DESIGN (Professional & Fixed)
st.markdown("""
    <style>
    .main .block-container { max-width: 480px; padding: 1.5rem; background: white; min-height: 100vh; margin: auto; }
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { display: none; }
    .app-header { background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 15px; }
    
    /* 📝 3-Status Boxes */
    .status-container { display: flex; gap: 8px; margin-bottom: 15px; }
    .status-box { flex: 1; padding: 10px; border-radius: 10px; text-align: center; color: white; font-weight: 700; font-size: 14px; }
    .bg-dues { background: #b91c1c; }
    .bg-adv { background: #15803d; }
    .bg-none { background: #6b7280; }

    .ledger-card { background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
    .stButton > button { border-radius: 12px; height: 70px; font-weight: 700; border: 1.5px solid #e2e8e0; background: white; }
    
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
        ret = pd.read_csv(f"{retailers_csv}&cb={cb}").dropna(how="all").fillna("0")
        led = pd.read_csv(f"{ledger_csv}&cb={cb}").dropna(how="all").fillna("0")
        led['DateObj'] = pd.to_datetime(led['Date'], format='%d-%m-%Y', errors='coerce')
        return ret, led
    except: return None, None

ret_df, led_df = load_data()
valid_ret = ret_df[ret_df['Location'].astype(str).str.upper() != 'EMPLOYEE'] if ret_df is not None else None
retailers_dict = {f"{r['Retailer Name']} ({str(r['Mobile Number']).split('.')[0]})": r for _, r in valid_ret.iterrows()} if valid_ret is not None else {}

# 🔐 LOGIN
if not st.session_state.authenticated:
    st.markdown('<div class="app-header"><h1>🏢 Sandhya ERP</h1><p>Login to Continue</p></div>', unsafe_allow_html=True)
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

# --- ADMIN PANEL ---
if st.session_state.current_page == "HOME":
    st.markdown('<div class="app-header"><h3>Admin Dashboard</h3></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💸 Khatabook 3D", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("📊 Live Stock", use_container_width=True): go_to("STOCK"); st.rerun()
    with c2:
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD"); st.rerun()
        if st.button("🚪 Logout", use_container_width=True): st.session_state.authenticated = False; st.rerun()

# --- 💸 KHATABOOK & LEDGER ---
elif st.session_state.current_page == "DUES":
    st.button("🔙 Back Menu", on_click=lambda: go_to("HOME" if st.session_state.role=="Admin" else "EMP_HOME"))
    if st.session_state.kb_retailer is None:
        all_r = []
        for n, r in retailers_dict.items():
            u_led = led_df[led_df['Retailer Name'] == r['Retailer Name']]
            bal = pd.to_numeric(u_led['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_led['Amount In (Credit)'], errors='coerce').sum()
            prm = str(r.get('PRM ID','')).split('.')[0]
            all_r.append({"Name": r['Retailer Name'], "PRM": prm, "Bal": bal, "Disp": n})
        
        all_r.sort(key=lambda x: -abs(x['Bal']))
        sel = st.selectbox("🔍 Search Retailer...", ["All"] + [x['Disp'] for x in all_r])
        for i in all_r:
            if sel == "All" or i['Disp'] == sel:
                cls = "amt-part-red" if i['Bal'] > 0 else "amt-part-green"
                c1, c2 = st.columns([3, 1])
                if c1.button(f"👤 {i['Name']} ({i['PRM']})", key=f"kb_{i['Disp']}", use_container_width=True):
                    st.session_state.kb_retailer = i['Name']; st.rerun()
                c2.markdown(f"<div class='{cls}'>₹ {abs(i['Bal']):,.0f}</div>", unsafe_allow_html=True)
    else:
        # SINGLE LEDGER VIEW
        name = st.session_state.kb_retailer
        r_info = next(v for k, v in retailers_dict.items() if v['Retailer Name'] == name)
        prm = str(r_info.get('PRM ID','')).split('.')[0]
        mob = str(r_info['Mobile Number']).split('.')[0]
        
        # Calculation
        u_led = led_df[led_df['Retailer Name'] == name].sort_values('DateObj')
        running_bal = 0
        rows = []
        for _, r in u_led.iterrows():
            d = pd.to_numeric(r['Amount Out (Debit)'], errors='coerce') if pd.notnull(r['Amount Out (Debit)']) else 0
            c = pd.to_numeric(r['Amount In (Credit)'], errors='coerce') if pd.notnull(r['Amount In (Credit)']) else 0
            running_bal += (d - c)
            rows.append({"d": r['Date'], "i": r['Product/Service'], "out": d, "in": c, "b": running_bal})

        # Professional Header with Call/WA
        st.markdown(f"""
        <div style='background:#0b57d0; color:white; padding:15px; border-radius:12px; margin-bottom:10px; text-align:center;'>
            <h3 style='margin:0;'>{name}</h3>
            <p style='margin:5px 0;'>PRM ID: {prm} | {mob}</p>
            <div style='display:flex; justify-content:space-around; margin-top:10px;'>
                <a href='tel:{mob}' style='background:white; color:#0b57d0; padding:8px 20px; border-radius:8px; text-decoration:none; font-weight:800;'>📞 CALL</a>
                <a href='https://wa.me/91{mob}' style='background:#25D366; color:white; padding:8px 20px; border-radius:8px; text-decoration:none; font-weight:800;'>📲 WA</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 3-Status Boxes
        cur_bal = rows[-1]['b'] if rows else 0
        st.markdown(f"""
        <div class='status-container'>
            <div class='status-box {"bg-dues" if cur_bal > 0 else "bg-none"}'>Dues<br>₹{cur_bal if cur_bal > 0 else 0:,.0f}</div>
            <div class='status-box {"bg-adv" if cur_bal < 0 else "bg-none"}'>Advance<br>₹{abs(cur_bal) if cur_bal < 0 else 0:,.0f}</div>
            <div class='status-box {"bg-none" if cur_bal == 0 else "bg-none"}'>Settled</div>
        </div>
        """, unsafe_allow_html=True)

        # Entry Boxes
        for r in reversed(rows):
            st.markdown(f"""
            <div class='ledger-card'>
                <div class='ledger-info'>
                    <div style='font-size:11px; color:#6b7280;'>{r['d']}</div>
                    <div style='font-weight:700;'>{r['i']}</div>
                    <div style='font-size:12px; font-weight:600; color:#4b5563;'>Bal: ₹{r['b']:,.0f}</div>
                </div>
                <div class='ledger-debit'>{f"- ₹{r['out']:,.0f}" if r['out']>0 else ""}</div>
                <div class='ledger-credit'>{f"+ ₹{r['in']:,.0f}" if r['in']>0 else ""}</div>
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
