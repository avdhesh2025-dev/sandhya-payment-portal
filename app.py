import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import urllib.parse
import requests
import time

# 1. Page Configuration
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# 💎 Global CSS Design
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    .app-header {
        background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%);
        color: white; padding: 25px 20px; border-radius: 16px;
        text-align: center; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    .urgent-card {
        background-color: #ffebee; border-left: 10px solid #d32f2f;
        padding: 15px; border-radius: 10px; margin-bottom: 10px; color: #b71c1c;
    }
    .stButton > button {
        height: 70px; background: #ffffff; color: #1e293b;
        border: 1.5px solid #e2e8f0; border-radius: 14px; font-size: 16px; font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# 🛑 YOUR APPS SCRIPT URL
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby_yV4nEMwrBODnkVh0x5DrVqcbj42iDMLNlX8M7QPrVGGMltoOfZhlid_gXlB0dwMvZQ/exec"

sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

def clean_prm_id(val):
    s = str(val).strip()
    if not s or s.lower() == 'nan': return ""
    try: return str(int(float(s)))
    except: return s.split('.')[0].replace(" ", "").upper()

@st.cache_data(ttl=5)
def load_data():
    try:
        cb = int(time.time())
        ret_df = pd.read_csv(f"{retailers_csv}&cb={cb}").dropna(how="all").fillna("")
        led_df = pd.read_csv(f"{ledger_csv}&cb={cb}").dropna(how="all").fillna("")
        led_df['DateObj'] = pd.to_datetime(led_df['Date'], format='%d-%m-%Y', errors='coerce')
        return ret_df, led_df
    except: return None, None

ret_df, led_df = load_data()

retailers_data = {}
prm_mapping = {} 
dropdown_options = ["Type here to search..."]
if ret_df is not None:
    for _, row in ret_df.iterrows():
        disp_prm = str(row.get("PRM ID", "")).split('.')[0].strip()
        name = str(row.get("Retailer Name", "")).strip()
        mob = str(row.get("Mobile Number", "")).split('.')[0].strip()
        match_prm = clean_prm_id(row.get("PRM ID", ""))
        if match_prm and name:
            retailers_data[f"{disp_prm} - {name}"] = {"Name": name, "Mobile": mob}
            prm_mapping[match_prm] = {"Name": name, "Mobile": mob}
            dropdown_options.append(f"{disp_prm} - {name}")

if "current_page" not in st.session_state: st.session_state.current_page = "HOME"
def go_to(page): st.session_state.current_page = page; st.rerun()

st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Smart Management System</p></div>', unsafe_allow_html=True)

# --- 🏠 HOME PAGE ---
if st.session_state.current_page == "HOME":
    if st.button("🔄 Refresh System Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD_RETAILER")
        if st.button("📜 Ledger Report", use_container_width=True): go_to("LEDGER")
        if st.button("📂 Bulk Entry", use_container_width=True): go_to("BULK")
    with col2:
        if st.button("💰 Today's Collection", use_container_width=True): go_to("COLLECTION")
        if st.button("📦 Stock/Payment Entry", use_container_width=True): go_to("ENTRY")
        if st.button("🚨 Urgent Recovery", use_container_width=True): go_to("URGENT")

# --- 🚨 URGENT RECOVERY (Babloo Kumar Singh Exclusive) ---
elif st.session_state.current_page == "URGENT":
    if st.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    st.error("### 🚨 Urgent Recovery Panel")
    
    fse_name = st.selectbox("Select FSE", ["Babloo kumar singh", "Avdhesh Kumar"])
    pin = st.text_input("Enter PIN", type="password")
    
    if pin == "2081" or pin == "9557":
        st.write("Checking for overdue payments...")
        now = datetime.now()
        overdue_found = False
        
        for _, row in led_df.iterrows():
            r_name = row['Retailer Name']
            r_type = row['Product/Service']
            r_date = row['DateObj']
            r_amt_out = float(row['Amount Out (Debit)'] or 0)
            r_amt_in = float(row['Amount In (Credit)'] or 0)
            
            is_urgent = False
            if "Etop" in r_type and (now - r_date) > timedelta(hours=24) and r_amt_out > r_amt_in:
                is_urgent = True
            if "JPB" in r_type and (now - r_date) > timedelta(days=15) and r_amt_out > r_amt_in:
                is_urgent = True
                
            if is_urgent:
                overdue_found = True
                st.markdown(f"""<div class="urgent-card"><b>Retailer:</b> {r_name}<br><b>Type:</b> {r_type}<br><b>Amount:</b> ₹{r_amt_out} | <b>Date:</b> {row['Date']}</div>""", unsafe_allow_html=True)
                with st.form(f"reason_{_}"):
                    reason = st.text_area("Why is this payment pending?")
                    if st.form_submit_button("Submit Reason"):
                        payload = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": r_name, "type": "Urgent Alert Reason", "amt_out": 0, "amt_in": 0, "txn_id": reason, "fse": fse_name}
                        requests.post(WEBHOOK_URL, json=payload)
                        st.success("Reason recorded!")
        if not overdue_found: st.success("No urgent recovery pending.")

# --- 📂 BULK ENTRY (Enhanced Fix) ---
elif st.session_state.current_page == "BULK":
    if st.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    st.header("📂 Bulk Entry (Jio Excel)")
    uploaded_file = st.file_uploader("Upload Jio Export", type=["xlsx", "csv"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        df.columns = [' '.join(str(col).split()) for col in df.columns]
        st.dataframe(df, use_container_width=True)
        
        fse = st.selectbox("Select FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
        pin = st.text_input("Enter PIN", type="password")
        
        if st.button("🚀 Upload All Data", use_container_width=True):
            if (fse == "Avdhesh Kumar" and pin == "9557") or (fse == "Babloo kumar singh" and pin == "2081"):
                prog = st.progress(0)
                session = requests.Session()
                for i, row in df.iterrows():
                    raw_prm = clean_prm_id(row.get("Partner PRM ID", ""))
                    if raw_prm in prm_mapping:
                        amt = float(str(row.get("Transfer Amount", "0")).replace(',',''))
                        final_amt = round(amt * 0.97, 2)
                        payload = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": prm_mapping[raw_prm]['Name'], "r_mob": prm_mapping[raw_prm]['Mobile'], "type": "Etop Transfer", "amt_out": final_amt, "amt_in": 0, "fse": fse, "txn_id": str(row.get("Order ID", ""))}
                        session.post(WEBHOOK_URL, json=payload)
                        time.sleep(0.6) # Safety Delay
                    prog.progress((i+1)/len(df))
                st.success("Bulk Upload Completed!")
            else: st.error("Wrong PIN")

# --- (Note: ADD_RETAILER, LEDGER, ENTRY pages logic remains same as per your final master code) ---
elif st.session_state.current_page == "ADD_RETAILER":
    if st.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    st.header("➕ Add Retailer")
    # [Rest of your Add Retailer logic here...]

elif st.session_state.current_page == "LEDGER":
    if st.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    # [Rest of your Ledger logic here...]

elif st.session_state.current_page == "ENTRY":
    if st.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    # [Rest of your Stock Entry logic here...]
