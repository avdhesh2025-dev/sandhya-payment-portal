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

# 🟢 INITIALIZE ALL SESSION STATES
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "kb_retailer" not in st.session_state: st.session_state.kb_retailer = None
if "kb_action" not in st.session_state: st.session_state.kb_action = None
if "show_success_modal" not in st.session_state: st.session_state.show_success_modal = False
if "success_display_text" not in st.session_state: st.session_state.success_display_text = ""
if "success_txn_type" not in st.session_state: st.session_state.success_txn_type = ""
if "success_wa_link" not in st.session_state: st.session_state.success_wa_link = ""
if "role" not in st.session_state: st.session_state.role = None

# 💎 FULL SCREEN SUCCESS OVERLAY
if st.session_state.show_success_modal:
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 20px; border: 2px solid #86efac; padding: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); margin-top: 20px;">
        <div style="font-size: 90px; color: #16a34a; margin-bottom: 5px;">✅</div>
        <div style="font-size: 28px; font-weight: 800; color: #166534; margin-bottom: 10px; text-align: center;">Transaction Successful!</div>
        <div style="font-size: 50px; font-weight: 900; color: #0b57d0; margin-bottom: 5px; text-align: center;">{st.session_state.success_display_text}</div>
        <div style="font-size: 18px; font-weight: 700; color: #4b5563; margin-bottom: 25px; text-align: center; text-transform: uppercase; background: #e5e7eb; padding: 5px 15px; border-radius: 20px;">{st.session_state.success_txn_type}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.session_state.success_wa_link:
        st.markdown(f"<div style='text-align:center; margin-bottom: 20px;'><a href='{st.session_state.success_wa_link}' target='_blank' style='display:inline-block; padding:15px 30px; background-color:#25D366; color:white; font-size:18px; font-weight:800; border-radius:30px; text-decoration:none;'>📲 Send WhatsApp Receipt</a></div>", unsafe_allow_html=True)
    if st.button("❌ CLOSE & CONTINUE", use_container_width=True):
        st.session_state.show_success_modal = False
        st.session_state.success_wa_link = ""
        st.rerun()
    st.stop()

# 💎 CSS UI Design (Fixed Indentation Error)
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    [data-testid="stSidebar"] { display: none; }
    .app-header { background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%); color: white; padding: 20px; border-radius: 16px; text-align: center; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
    .stButton > button { border-radius: 12px; height: 65px; font-weight: 700; font-size: 16px; transition: 0.3s; margin-bottom: 10px; }
    .kb-header-container { display: flex; justify-content: space-around; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .kb-box { width: 45%; text-align: center; }
    .kb-ledger-row { display: flex; justify-content: space-between; border-bottom: 1px solid #eee; background: white; padding: 12px; align-items: center; }
    @media (max-width: 768px) { div[data-testid="stHorizontalBlock"] { flex-direction: row !important; flex-wrap: nowrap !important; gap: 8px !important; } }
    </style>
""", unsafe_allow_html=True)

# 🛑 CONFIGURATION
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyH_oGxKbNZQj2azNOR0FgkLyAKxBfaAoE0Yo3DHmRpNOFZczJRayBhPd056SGUVWbxWQ/exec"
sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

def create_pdf(r_name, r_mob, bal, r_data):
    if not HAS_FPDF: return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18); pdf.cell(0, 10, "Sandhya Enterprises", ln=True, align='C')
    pdf.set_font("Arial", 'B', 11); pdf.cell(0, 6, "Jio Authorized Distributor", ln=True, align='C')
    pdf.set_font("Arial", '', 9); pdf.cell(0, 5, "Register office: Rosera Road, Meghpatti, Samastipur, Bihar 848117", ln=True, align='C')
    pdf.cell(0, 5, "GSTIN: 10GQZPK8313P1Z1  |  PAN: GQZPK8313P", ln=True, align='C')
    pdf.cell(0, 5, "Email: smp.sandhya02@gmail.com  |  Contact: 7479584179", ln=True, align='C')
    pdf.line(10, 45, 200, 45); pdf.ln(10)
    pdf.set_font("Arial", 'B', 12); pdf.cell(100, 8, f"Retailer: {r_name}"); pdf.cell(0, 8, f"Date: {date.today().strftime('%d-%m-%Y')}", ln=True, align='R')
    pdf.cell(0, 8, f"Current Balance: Rs {bal:,.2f}", ln=True); pdf.ln(5)
    pdf.set_font("Arial", 'B', 9); pdf.cell(25, 8, "Date", 1); pdf.cell(75, 8, "Particulars", 1); pdf.cell(30, 8, "Aapne Diye", 1); pdf.cell(30, 8, "Aapko Mile", 1); pdf.cell(30, 8, "Bal", 1); pdf.ln()
    pdf.set_font("Arial", '', 9)
    for r in r_data:
        pdf.cell(25, 8, str(r['d']), 1); pdf.cell(75, 8, str(r['i'])[:40], 1); pdf.cell(30, 8, str(r['out']), 1); pdf.cell(30, 8, str(r['in']), 1); pdf.cell(30, 8, str(r['b']), 1); pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

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

# Logic to separate employees
valid_ret = ret_df[ret_df['Location'].astype(str).str.upper() != 'EMPLOYEE'] if ret_df is not None else None
retailers_dict = {f"{r['Retailer Name']} ({str(r['Mobile Number']).split('.')[0]})": r for _, r in valid_ret.iterrows()} if valid_ret is not None else {}

# 🔐 LOGIN SYSTEM
if not st.session_state.authenticated:
    st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Smart Management Login</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 Login", "📝 New Registration"])
    with tab1:
        l_mob = st.text_input("Mobile Number")
        l_pin = st.text_input("PIN", type="password")
        if st.button("🚀 UNLOCK APP", use_container_width=True):
            if l_mob == "7479584179" and l_pin == "9557":
                st.session_state.role = "Admin"; st.session_state.authenticated = True; st.rerun()
            elif l_mob == "7254972081" and l_pin == "2081":
                st.session_state.role = "Employee"; st.session_state.emp_name = "Babloo kumar singh"; st.session_state.emp_pin = "2081"; st.session_state.authenticated = True; st.rerun()
            elif ret_df is not None:
                emps = ret_df[ret_df['Location'].astype(str).str.upper() == 'EMPLOYEE']
                for _, r in emps.iterrows():
                    if str(r.get("Mobile Number")).split('.')[0] == l_mob and str(r.get("PRM ID")).replace("EMP_","") == l_pin:
                        st.session_state.role = "Employee"; st.session_state.emp_name = r["Retailer Name"]; st.session_state.emp_pin = l_pin; st.session_state.authenticated = True; st.rerun()
            st.error("❌ Wrong PIN or Number")
    with tab2:
        reg_n = st.text_input("Name"); reg_m = st.text_input("Mobile"); reg_p = st.text_input("4-Digit PIN", type="password")
        if st.button("Register Now"):
            requests.post(WEBHOOK_URL, json={"action":"add_retailer","name":reg_n.upper(),"mobile":reg_m,"prm":f"EMP_{reg_p}","location":"EMPLOYEE","date":date.today().strftime("%d-%m-%Y")})
            st.success("Success! Please Login."); st.cache_data.clear()
    st.stop()

# Helpers
fse_list = ["Avdhesh Kumar", "Babloo kumar singh"]
if st.session_state.role == "Employee": fse_list = [st.session_state.emp_name]
def verify_pin(n, p):
    if n == "Avdhesh Kumar" and p == "9557": return True
    if n == "Babloo kumar singh" and p == "2081": return True
    if st.session_state.role == "Employee" and p == st.session_state.emp_pin: return True
    return False

if "current_page" not in st.session_state: st.session_state.current_page = "HOME" if st.session_state.role == "Admin" else "EMP_HOME"
def go_to(p): st.session_state.current_page = p; st.session_state.kb_retailer = None; st.session_state.kb_action = None

# --- ADMIN DASH ---
if st.session_state.current_page == "HOME":
    c1, c2 = st.columns([4, 1]); c2.button("Logout", on_click=lambda: st.session_state.update({"authenticated":False}))
    st.markdown('<div class="app-header"><h3>Admin Dashboard</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Live Stock & FSE Sim", use_container_width=True): go_to("STOCK"); st.rerun()
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD"); st.rerun()
    with col2:
        if st.button("💸 Khatabook 3D", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("🚨 Urgent Recovery", use_container_width=True): go_to("URGENT"); st.rerun()

# --- EMP DASH ---
elif st.session_state.current_page == "EMP_HOME":
    c1, c2 = st.columns([3, 1]); c1.info(f"👤 {st.session_state.emp_name}")
    if c2.button("Exit"): st.session_state.authenticated = False; st.rerun()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 Khatabook 3D", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD"); st.rerun()
    with col2:
        if st.button("🚨 Urgent", use_container_width=True): go_to("URGENT"); st.rerun()
        if st.button("📦 My Sim Stock", use_container_width=True): go_to("STOCK"); st.rerun()

# --- KHATABOOK 3D (COMPLETE) ---
elif st.session_state.current_page == "DUES":
    st.button("⬅️ Back Menu", on_click=lambda: go_to("HOME" if st.session_state.role == "Admin" else "EMP_HOME"))
    
    if st.session_state.kb_retailer is None:
        all_r = []
        tm, ta = 0, 0
        for n, r in retailers_dict.items():
            u_led = led_df[led_df['Retailer Name'] == r['Retailer Name']]
            bal = pd.to_numeric(u_led['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_led['Amount In (Credit)'], errors='coerce').sum()
            if bal > 0: tm += bal
            else: ta += abs(bal)
            all_r.append({"Name": r['Retailer Name'], "Mob": r['Mobile Number'], "Bal": bal, "Disp": n})
        
        st.markdown(f"""<div class='kb-header-container'>
            <div class='kb-box'><h4>Aapko dene hain</h4><h2 style='color:#15803d;'>₹ {ta:,.0f}</h2></div>
            <div style='width:1px; background:#eee;'></div>
            <div class='kb-box'><h4>Aapko milenge</h4><h2 style='color:#b91c1c;'>₹ {tm:,.0f}</h2></div>
        </div>""", unsafe_allow_html=True)
        
        all_r.sort(key=lambda x: (0 if x['Bal'] > 0 else 1 if x['Bal'] < 0 else 2, -abs(x['Bal'])))
        sel = st.selectbox("🔍 Customer search karein...", ["All Customers"] + [x['Disp'] for x in all_r])
        
        for item in all_r:
            if sel == "All Customers" or item['Disp'] == sel:
                color = "#b91c1c" if item['Bal'] > 0 else "#15803d" if item['Bal'] < 0 else "#6b7280"
                with st.container(border=True):
                    col1, col2 = st.columns([3, 2])
                    if col1.button(item['Name'], key=f"r_{item['Name']}_{item['Mob']}"): 
                        st.session_state.kb_retailer = item['Name']; st.rerun()
                    col2.markdown(f"<div style='text-align:right; font-weight:800; font-size:18px; color:{color};'>₹ {abs(item['Bal']):,.0f}</div>", unsafe_allow_html=True)
    else:
        name = st.session_state.kb_retailer
        r_info = next(v for k, v in retailers_dict.items() if v['Retailer Name'] == name)
        st.markdown(f"<div style='background:#0b57d0; color:white; padding:15px; border-radius:10px;'><h3>{name}</h3><p>{r_info['Mobile Number']}</p></div>", unsafe_allow_html=True)
        
        u_led = led_df[led_df['Retailer Name'] == name].sort_values('DateObj')
        bal = 0; rows = []
        for _, r in u_led.iterrows():
            d = pd.to_numeric(r['Amount Out (Debit)'], errors='coerce') if pd.notnull(r['Amount Out (Debit)']) else 0
            c = pd.to_numeric(r['Amount In (Credit)'], errors='coerce') if pd.notnull(r['Amount In (Credit)']) else 0
            bal += (d - c)
            rows.append({"d": r['Date'], "i": r['Product/Service'], "out": d, "in": c, "b": bal})
        
        st.markdown(f"<div style='background:white; padding:20px; border-radius:10px; margin:10px 0; text-align:center;'><h4>Balance</h4><h2 style='color:#b91c1c;'>₹ {bal:,.0f}</h2></div>", unsafe_allow_html=True)
        
        # WhatsApp Text Logic
        wa_msg = f"*Sandhya Enterprises - Ledger*\n👤 Retailer: {name}\n💰 Balance: Rs {bal:,.0f}\n\n*Last Transactions:*\n"
        for r in reversed(rows[-5:]):
            wa_msg += f"• {r['d']} | {r['i']} | Bal: {r['b']}\n"
        wa_link = f"https://wa.me/91{r_info['Mobile Number']}?text={urllib.parse.quote(wa_msg)}"
        st.markdown(f"<div style='text-align:center;'><a href='{wa_link}' target='_blank' style='color:#25d366; font-weight:700;'>📲 Send WhatsApp Reminder</a></div>", unsafe_allow_html=True)

        if HAS_FPDF:
            pdf_b = create_pdf(name, r_info['Mobile Number'], bal, rows)
            st.download_button("📄 Download PDF Ledger", pdf_b, f"{name}_Ledger.pdf", "application/pdf", use_container_width=True)

        for r in reversed(rows):
            st.markdown(f"<div class='kb-ledger-row'><div style='width:50%'><b>{r['d']}</b><br>{r['i']}</div><div style='color:#b91c1c;'>{f'₹{r['out']:,.0f}' if r['out']>0 else ''}</div><div style='color:#15803d;'>{f'₹{r['in']:,.0f}' if r['in']>0 else ''}</div></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        b1, b2 = st.columns(2)
        if b1.button("🔴 AAPNE DIYE", use_container_width=True): st.session_state.kb_action = "diye"; st.rerun()
        if b2.button("🟢 AAPKO MILE", use_container_width=True): st.session_state.kb_action = "mile"; st.rerun()
        
        if st.session_state.kb_action == "diye":
            with st.form("diye_form"):
                t = st.selectbox("Type", ["Etop Transfer", "JPB V4", "Sim Card"])
                amt, qty = 0, 0
                if t == "Etop Transfer":
                    o = st.selectbox("Amount", ["5000", "3000", "2000", "1500", "500", "Manual"])
                    amt = float(o) if o != "Manual" else st.number_input("Enter Amount", min_value=1.0)
                elif t == "Sim Card": qty = st.number_input("Qty", min_value=1)
                else: amt = st.number_input("Amount"); qty = st.number_input("Qty")
                f = st.selectbox("FSE", fse_list); p = st.text_input("PIN", type="password")
                if st.form_submit_button("Save Entry"):
                    if verify_pin(f, p):
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"r_mob":r_info['Mobile Number'],"type":t,"qty":qty,"amt_out":amt,"amt_in":0,"fse":f,"txn_id":"KB"})
                        st.session_state.success_display_text = f"₹ {amt:,.0f}" if amt>0 else f"{int(qty)} SIMs"
                        st.session_state.success_txn_type = t
                        st.session_state.success_wa_link = f"https://wa.me/91{r_info['Mobile Number']}?text={urllib.parse.quote(f'*Sandhya Enterprises*\n{t} Done\nAmt: Rs {amt if amt>0 else qty}')}"
                        st.session_state.show_success_modal = True; st.cache_data.clear(); st.rerun()

        if st.session_state.kb_action == "mile":
            with st.form("mile_form"):
                m = st.selectbox("Mode", ["Cash", "Online"]); amt = st.number_input("Amount ₹", min_value=1.0)
                f = st.selectbox("FSE", fse_list); p = st.text_input("PIN", type="password")
                if st.form_submit_button("Save Entry"):
                    if verify_pin(f, p):
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"r_mob":r_info['Mobile Number'],"type":f"Payment ({m})","qty":0,"amt_out":0,"amt_in":amt,"fse":f,"txn_id":"KB"})
                        st.session_state.success_display_text = f"₹ {amt:,.0f}"
                        st.session_state.success_txn_type = f"Payment Received ({m})"
                        st.session_state.success_wa_link = f"https://wa.me/91{r_info['Mobile Number']}?text={urllib.parse.quote(f'*Sandhya Enterprises*\nPayment Received\nAmt: Rs {amt}')}"
                        st.session_state.show_success_modal = True; st.cache_data.clear(); st.rerun()

# --- STOCK MANAGEMENT ---
elif st.session_state.current_page == "STOCK":
    st.button("🔙 Back", on_click=lambda: go_to(get_home()))
    if st.session_state.role == "Admin":
        tab1, tab2 = st.tabs(["📱 FSE Sim Billing", "📦 Main Stock"])
        with tab1:
            with st.form("bill_fse"):
                f = st.selectbox("FSE", fse_list); q = st.number_input("SIM Qty", min_value=1); ap = st.text_input("Admin PIN", type="password")
                if st.form_submit_button("Bill SIMs"):
                    if ap == "9557":
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":f,"r_mob":"0","type":"Sim Allocation","qty":q,"amt_out":0,"amt_in":0,"fse":"Admin","txn_id":"S"})
                        st.success("SIM Billed!"); st.cache_data.clear()
        with tab2: st.dataframe(inv_df, use_container_width=True)
    else:
        alloc = pd.to_numeric(led_df[(led_df['Retailer Name']==st.session_state.emp_name)&(led_df['Product/Service']=='Sim Allocation')]['Qty'], errors='coerce').sum()
        dist = pd.to_numeric(led_df[(led_df['FSE Name']==st.session_state.emp_name)&(led_df['Product/Service']=='Sim Card')]['Qty'], errors='coerce').sum()
        st.metric("SIM Stock Balance", int(alloc - dist))
        st.write("---")
        st.write("### SIM Distribution History")
        st.dataframe(led_df[(led_df['FSE Name']==st.session_state.emp_name)&(led_df['Product/Service']=='Sim Card')][['Date','Retailer Name','Qty']], hide_index=True)

# --- URGENT ---
elif st.session_state.current_page == "URGENT":
    st.button("🔙 Back", on_click=lambda: go_to(get_home()))
    st.error("🚨 Pending Recovery Cases")
    # Custom recovery logic showing retailers with dues > 24hrs...
    st.info("Loading records from Ledger...")

# --- ADD RETAILER ---
elif st.session_state.current_page == "ADD":
    st.button("🔙 Back", on_click=lambda: go_to(get_home()))
    with st.form("add_r"):
        n = st.text_input("Retailer Name"); m = st.text_input("Mobile"); p = st.text_input("PRM ID"); l = st.text_input("Location")
        if st.form_submit_button("Add Retailer"):
            requests.post(WEBHOOK_URL, json={"action":"add_retailer","name":n.upper(),"mobile":m,"prm":p,"location":l.upper(),"date":date.today().strftime("%d-%m-%Y")})
            st.session_state.success_display_text = n.upper()
            st.session_state.success_txn_type = "Retailer Added"
            st.session_state.show_success_modal = True; st.cache_data.clear(); st.rerun()
