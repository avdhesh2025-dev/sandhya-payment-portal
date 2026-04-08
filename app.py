import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import urllib.parse
import requests
import time

# 1. Page Configuration (No Sidebar)
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# 💎 Global CSS Design
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    .app-header {
        background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%);
        color: white; padding: 35px 20px; border-radius: 16px;
        text-align: center; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    .urgent-card {
        background-color: #ffebee; border-left: 10px solid #d32f2f;
        padding: 15px; border-radius: 10px; margin-bottom: 10px; color: #b71c1c;
    }
    .stButton > button {
        height: 75px; background: #ffffff; color: #1e293b;
        border: 1.5px solid #e2e8f0; border-radius: 14px;
        font-size: 18px; font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 15px;
    }
    .stButton > button:hover { border-color: #3b82f6; color: #3b82f6; box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# 🛑 URLS
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby_yV4nEMwrBODnkVh0x5DrVqcbj42iDMLNlX8M7QPrVGGMltoOfZhlid_gXlB0dwMvZQ/exec"
sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"
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
        inv_df = pd.read_csv(f"{inventory_csv}&cb={cb}").dropna(how="all").fillna("")
        led_df = pd.read_csv(f"{ledger_csv}&cb={cb}").dropna(how="all").fillna("")
        led_df['DateObj'] = pd.to_datetime(led_df['Date'], format='%d-%m-%Y', errors='coerce')
        return ret_df, inv_df, led_df
    except: return None, None, None

ret_df, inv_df, led_df = load_data()

retailers_data = {}; prm_mapping = {}; dropdown_options = ["Type here to search..."]
if ret_df is not None:
    for _, row in ret_df.iterrows():
        prm = str(row.get("PRM ID", "")).split('.')[0].strip()
        name = str(row.get("Retailer Name", "")).strip()
        mob = str(row.get("Mobile Number", "")).split('.')[0].strip()
        m_prm = clean_prm_id(row.get("PRM ID", ""))
        if m_prm and name:
            retailers_data[f"{prm} - {name}"] = {"Name": name, "Mobile": mob, "PRM": prm}
            prm_mapping[m_prm] = {"Name": name, "Mobile": mob}
            dropdown_options.append(f"{prm} - {name}")

if "current_page" not in st.session_state: st.session_state.current_page = "HOME"
def go_to(page): st.session_state.current_page = page; st.rerun()

st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Smart Business Management System</p></div>', unsafe_allow_html=True)

# --- 🏠 HOME PAGE ---
if st.session_state.current_page == "HOME":
    if st.button("🔄 Refresh System Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Live Stock", use_container_width=True): go_to("STOCK")
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD_RETAILER")
        if st.button("📜 Ledger Report", use_container_width=True): go_to("LEDGER")
        if st.button("📂 Bulk Entry (Excel)", use_container_width=True): go_to("BULK")
    with col2:
        if st.button("💰 Today's Collection", use_container_width=True): go_to("COLLECTION")
        if st.button("📦 Stock / Payment Entry", use_container_width=True): go_to("ENTRY")
        if st.button("💸 Dues List", use_container_width=True): go_to("DUES")
        if st.button("🚨 Urgent Recovery", use_container_width=True): go_to("URGENT")

# --- 🚨 8. URGENT RECOVERY ---
elif st.session_state.current_page == "URGENT":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.error("### 🚨 Urgent Recovery Alert")
    f_n = st.selectbox("Select FSE", ["Babloo kumar singh", "Avdhesh Kumar"])
    f_p = st.text_input("Enter PIN", type="password")
    if (f_n=="Babloo kumar singh" and f_p=="2081") or (f_n=="Avdhesh Kumar" and f_p=="9557"):
        now = datetime.now()
        found = False
        for _, row in led_df.iterrows():
            r_type, r_date = str(row['Product/Service']), row['DateObj']
            a_out = float(pd.to_numeric(row['Amount Out (Debit)'], errors='coerce') or 0)
            a_in = float(pd.to_numeric(row['Amount In (Credit)'], errors='coerce') or 0)
            is_u = False
            if "Etop" in r_type and (now - r_date) > timedelta(hours=24) and a_out > a_in: is_u = True
            if "JPB" in r_type and (now - r_date) > timedelta(days=15) and a_out > a_in: is_u = True
            if is_u:
                found = True
                st.markdown(f"""<div class="urgent-card"><b>Retailer:</b> {row['Retailer Name']}<br><b>Dues:</b> ₹{a_out - a_in} | <b>Date:</b> {row['Date']} ({r_type})</div>""", unsafe_allow_html=True)
                with st.form(f"rsn_{_}"):
                    rsn = st.text_area("Reason for pending amount")
                    if st.form_submit_button("Submit Reason"):
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":row['Retailer Name'],"type":"Recovery Alert Reason","txn_id":rsn,"fse":f_n,"amt_in":0,"amt_out":0})
                        st.success("Reason Recorded!")
        if not found: st.success("No urgent recovery needed at the moment.")

# --- 📊 1. STOCK PAGE ---
elif st.session_state.current_page == "STOCK":
    c1, c2 = st.columns(2); c1.button("🔙 Back Menu", on_click=go_to, args=("HOME",)); c2.button("🔄 Refresh", on_click=st.rerun)
    st.header("📊 Live Inventory Stock")
    if inv_df is not None: st.dataframe(inv_df, use_container_width=True, hide_index=True)

# --- 💰 2. TODAY COLLECTION ---
elif st.session_state.current_page == "COLLECTION":
    c1, c2 = st.columns(2); c1.button("🔙 Back Menu", on_click=go_to, args=("HOME",)); c2.button("🔄 Refresh", on_click=st.rerun)
    st.header("💸 Today's Collection")
    if ret_df is not None and led_df is not None:
        for _, row in ret_df.iterrows():
            name, mob = row["Retailer Name"], row["Mobile Number"]
            u_led = led_df[led_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_led['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_led['Amount In (Credit)'], errors='coerce').sum()
            if dues > 0:
                with st.expander(f"👤 {name} | 🚩 Dues: ₹{dues}"):
                    st.markdown(f"### [📞 Call](tel:{mob})")
                    with st.form(f"col_{_}"):
                        p_amt = st.number_input("Amount", min_value=1.0)
                        f_n = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"], key=f"fse_{_}")
                        f_p = st.text_input("PIN", type="password", key=f"pin_{_}")
                        if st.form_submit_button("Save"):
                            if (f_n=="Avdhesh Kumar" and f_p=="9557") or (f_n=="Babloo kumar singh" and f_p=="2081"):
                                requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"r_mob":mob,"type":"Collection","amt_in":p_amt,"amt_out":0,"fse":f_n,"txn_id":"DIRECT"})
                                st.success("Saved!"); st.cache_data.clear()
                            else: st.error("Wrong PIN")

# --- 📦 3. ENTRY PAGE (3D Wobble) ---
elif st.session_state.current_page == "ENTRY":
    st.markdown("""<style>.stButton>button { background-color: #ffffff !important; border-left: 6px solid #007bff !important; box-shadow: 0 6px 0 #d1d9e6 !important; }</style>""", unsafe_allow_html=True)
    c1, c2 = st.columns(2); c1.button("🔙 Back Menu", on_click=go_to, args=("HOME",)); c2.button("🔄 Refresh", on_click=st.rerun)
    st.header("📦 Stock / Payment Entry")
    t_date = st.date_input("Date", date.today())
    t_prm = st.selectbox("Select Retailer*", options=dropdown_options)
    col1, col2 = st.columns(2)
    with col1:
        t_type = st.selectbox("Entry Type", ["Etop Transfer", "Payment Received", "JPB V4", "Sim Card"])
        fse = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
        fse_pin = st.text_input("Enter PIN", type="password")
    with col2:
        t_qty, t_amt = 0, 0.0
        if t_type == "Etop Transfer":
            etop_opt = st.selectbox("Amount ₹", ["5000", "3000", "2000", "1500", "500", "Manual"])
            t_amt = float(etop_opt) if etop_opt != "Manual" else st.number_input("Enter Amount", min_value=1.0)
        elif t_type == "Payment Received":
            t_amt = st.number_input("Enter Amount", min_value=1.0, value=None)
        elif t_type == "JPB V4":
            t_qty = st.number_input("Qty", min_value=1)
            rate = st.number_input("Rate", min_value=1.0)
            t_amt = t_qty * rate
        elif t_type == "Sim Card":
            t_qty = st.number_input("Qty", min_value=1)
        txn_id = st.text_input("Remark")

    if st.button("🚀 Save and Send WhatsApp", use_container_width=True):
        if (fse=="Avdhesh Kumar" and fse_pin=="9557") or (fse=="Babloo kumar singh" and fse_pin=="2081"):
            r_name = retailers_data[t_prm]["Name"]; r_mob = retailers_data[t_prm]["Mobile"]
            payload = {"action":"add_txn","date":t_date.strftime("%d-%m-%Y"),"r_name":r_name,"r_mob":r_mob,"type":t_type,"qty":t_qty,"amt_out":t_amt if t_type!="Payment Received" else 0,"amt_in":t_amt if t_type=="Payment Received" else 0,"fse":fse,"txn_id":txn_id}
            requests.post(WEBHOOK_URL, json=payload)
            st.success("✅ Saved!"); st.cache_data.clear()
            msg = urllib.parse.quote(f"*Sandhya Enterprises*\nRetailer: {r_name}\nType: {t_type}\nAmount: ₹{t_amt}")
            st.markdown(f"### [🟢 Send WhatsApp](https://wa.me/91{r_mob}?text={msg})")
        else: st.error("Wrong PIN")

# --- ➕ 4. ADD RETAILER ---
elif st.session_state.current_page == "ADD_RETAILER":
    c1, c2 = st.columns(2); c1.button("🔙 Back Menu", on_click=go_to, args=("HOME",)); c2.button("🔄 Refresh", on_click=st.rerun)
    st.header("➕ Add Retailer")
    with st.form("add_r"):
        n, m, p = st.text_input("Name"), st.text_input("Mobile"), st.text_input("PRM ID")
        if st.form_submit_button("Save"):
            requests.post(WEBHOOK_URL, json={"action":"add_retailer","name":n.upper(),"mobile":m,"prm":p,"location":"Manual","date":date.today().strftime("%d-%m-%Y")})
            st.success("Added!"); st.cache_data.clear()
    
    st.markdown("---")
    st.header("📂 Bulk Retailer Upload (with Balance)")
    up = st.file_uploader("Excel: Name, PRM, Details, DUSE, ADVANCE", type=["xlsx","csv"])
    if up:
        df_up = pd.read_excel(up) if up.name.endswith('xlsx') else pd.read_csv(up)
        df_up.columns = [' '.join(str(col).upper().split()) for col in df_up.columns]
        st.dataframe(df_up, use_container_width=True)
        if st.button("🚀 Upload All"):
            prog = st.progress(0); sess = requests.Session()
            for i, row in df_up.iterrows():
                b_name = str(row.get("RETAILER NAME", "")).upper()
                b_prm = str(row.get("PRM ID", "")).split('.')[0]
                b_mob = str(row.get("DETAILS", "")).split('.')[0]
                b_dues = float(str(row.get("DUSE", 0)).replace(',',''))
                b_adv = float(str(row.get("ADVANCE", 0)).replace(',',''))
                if b_name:
                    sess.post(WEBHOOK_URL, json={"action":"add_retailer","name":b_name,"mobile":b_mob,"prm":b_prm,"location":"BULK","date":date.today().strftime("%d-%m-%Y")})
                    time.sleep(0.5)
                    if b_dues > 0: sess.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":b_name,"r_mob":b_mob,"type":"Opening Dues","amt_out":b_dues,"amt_in":0,"fse":"SYSTEM","txn_id":"OPENING"})
                    if b_adv > 0: sess.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":b_name,"r_mob":b_mob,"type":"Opening Advance","amt_out":0,"amt_in":b_adv,"fse":"SYSTEM","txn_id":"OPENING"})
                    time.sleep(0.5)
                prog.progress((i+1)/len(df_up))
            st.success("Bulk Uploaded!"); st.cache_data.clear()

# --- 📜 5. LEDGER ---
elif st.session_state.current_page == "LEDGER":
    c1, c2 = st.columns(2); c1.button("🔙 Back Menu", on_click=go_to, args=("HOME",)); c2.button("🔄 Refresh", on_click=st.rerun)
    st.header("📜 Ledger Report")
    search = st.selectbox("Select Retailer", options=dropdown_options)
    if search != "Type here to search...":
        r_name = retailers_data[search]["Name"]
        f_led = led_df[led_df['Retailer Name'] == r_name].sort_values(by='DateObj')
        st.dataframe(f_led.drop(columns=['DateObj']), use_container_width=True)

# --- 📂 7. BULK ETOP ---
elif st.session_state.current_page == "BULK":
    c1, c2 = st.columns(2); c1.button("🔙 Back Menu", on_click=go_to, args=("HOME",)); c2.button("🔄 Refresh", on_click=st.rerun)
    st.header("📂 Jio Bulk Etop (3% Margin)")
    up_j = st.file_uploader("Upload Jio Export", type=["xlsx","csv"])
    if up_j:
        df_j = pd.read_excel(up_j) if up_j.name.endswith('xlsx') else pd.read_csv(up_j)
        df_j.columns = [' '.join(str(col).split()) for col in df_j.columns]
        st.dataframe(df_j, use_container_width=True)
        f_n = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
        f_p = st.text_input("PIN", type="password")
        if st.button("🚀 Match & Upload"):
            if (f_n=="Avdhesh Kumar" and f_p=="9557") or (f_n=="Babloo kumar singh" and f_p=="2081"):
                prog = st.progress(0); sess = requests.Session()
                for i, row in df_j.iterrows():
                    prm = clean_prm_id(row.get("Partner PRM ID", ""))
                    if prm in prm_mapping:
                        amt = float(str(row.get("Transfer Amount", 0)).replace(',',''))
                        sess.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":prm_mapping[prm]['Name'],"r_mob":prm_mapping[prm]['Mobile'],"type":"Etop Transfer","amt_out":round(amt*0.97,2),"amt_in":0,"fse":f_n,"txn_id":str(row.get("Order ID",""))})
                        time.sleep(0.6)
                    prog.progress((i+1)/len(df_j))
                st.success("Bulk Added!"); st.cache_data.clear()
