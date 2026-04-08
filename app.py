import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import urllib.parse
import requests
import time

# 1. Page Configuration
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# 💎 Premium CSS Design
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
    .stButton > button:hover { border-color: #3b82f6; color: #3b82f6; }
    </style>
""", unsafe_allow_html=True)

# 🛑 ENDPOINTS
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
            retailers_data[f"{disp_prm} - {name}"] = {"Name": name, "Mobile": mob, "PRM": disp_prm}
            prm_mapping[match_prm] = {"Name": name, "Mobile": mob}
            dropdown_options.append(f"{disp_prm} - {name}")

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

# --- 📊 1. STOCK ---
elif st.session_state.current_page == "STOCK":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("📊 Live Inventory Stock")
    if inv_df is not None: st.dataframe(inv_df, use_container_width=True, hide_index=True)

# --- 💰 2. TODAY COLLECTION ---
elif st.session_state.current_page == "COLLECTION":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("💸 Today's Collection")
    if ret_df is not None and led_df is not None:
        for _, row in ret_df.iterrows():
            name, mob = row["Retailer Name"], row["Mobile Number"]
            u_led = led_df[led_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_led['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_led['Amount In (Credit)'], errors='coerce').sum()
            if dues > 0:
                with st.expander(f"👤 {name} | 🚩 Dues: ₹{dues}"):
                    st.markdown(f"### [📞 Call Now](tel:{mob})")
                    with st.form(f"col_{_}"):
                        p_amt = st.number_input("Amount", min_value=1.0)
                        p_mode = st.selectbox("Mode", ["Cash", "Online"])
                        p_fse = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
                        p_pin = st.text_input("PIN", type="password")
                        if st.form_submit_button("Save Payment"):
                            if (p_fse=="Avdhesh Kumar" and p_pin=="9557") or (p_fse=="Babloo kumar singh" and p_pin=="2081"):
                                payload = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": name, "r_mob": mob, "type": f"Payment ({p_mode})", "qty": 0, "amt_out": 0, "amt_in": p_amt, "fse": p_fse, "txn_id": "Direct_Collection"}
                                requests.post(WEBHOOK_URL, json=payload)
                                st.success("Saved!"); st.cache_data.clear()
                            else: st.error("Wrong PIN")

# --- 📦 3. ENTRY PAGE (3D Effects) ---
elif st.session_state.current_page == "ENTRY":
    st.markdown("""<style>
        .stButton>button { background-color: #ffffff !important; border-left: 6px solid #007bff !important; box-shadow: 0 6px 0 #d1d9e6 !important; transition: 0.2s; }
        .stButton>button:hover { top: -3px; box-shadow: 0 9px 0 #d1d9e6 !important; }
    </style>""", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("📦 Stock / Payment Entry")
    t_date = st.date_input("Date", date.today())
    t_prm = st.selectbox("Select Retailer*", options=dropdown_options)
    col1, col2 = st.columns(2)
    with col1:
        t_type = st.selectbox("Entry Type", ["Etop Transfer", "Payment Received", "JPB V4", "Sim Card"])
        fse = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
        fse_pin = st.text_input("PIN", type="password")
    with col2:
        t_qty, t_amt = 0, 0.0
        if t_type == "Etop Transfer":
            etop_opt = st.selectbox("Amount ₹", ["5000", "3000", "2000", "1500", "500", "Manual"])
            t_amt = float(etop_opt) if etop_opt != "Manual" else st.number_input("Enter Amount", min_value=1.0)
        elif t_type == "Payment Received":
            p_mode = st.selectbox("Mode", ["Cash", "Online"])
            t_amt = st.number_input("Enter Amount", min_value=1.0, value=None)
        elif t_type == "JPB V4":
            t_qty = st.number_input("Qty", min_value=1)
            rate = st.number_input("Rate", min_value=1.0)
            t_amt = t_qty * rate
        elif t_type == "Sim Card":
            t_qty = st.number_input("Qty", min_value=1)
        
        txn_id = st.text_input("Txn ID / Remark")

    if st.button("🚀 Save and Send WhatsApp", use_container_width=True):
        if (fse=="Avdhesh Kumar" and fse_pin=="9557") or (fse=="Babloo kumar singh" and fse_pin=="2081"):
            r_name = retailers_data[t_prm]["Name"]; r_mob = retailers_data[t_prm]["Mobile"]
            a_out = t_amt if t_type != "Payment Received" else 0
            a_in = t_amt if t_type == "Payment Received" else 0
            payload = {"action": "add_txn", "date": t_date.strftime("%d-%m-%Y"), "r_name": r_name, "r_mob": r_mob, "type": t_type, "qty": t_qty, "amt_out": a_out, "amt_in": a_in, "fse": fse, "txn_id": txn_id}
            requests.post(WEBHOOK_URL, json=payload)
            st.success("Saved!"); st.cache_data.clear()
            msg = urllib.parse.quote(f"*Sandhya Enterprises*\nDate: {t_date}\nRetailer: {r_name}\nAmount: ₹{t_amt}\nStatus: Saved")
            st.markdown(f"### [🟢 Send WhatsApp](https://wa.me/91{r_mob}?text={msg})")
        else: st.error("Wrong PIN")

# --- ➕ 4. ADD RETAILER & BULK RETAILERS ---
elif st.session_state.current_page == "ADD_RETAILER":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("➕ Add New Retailer")
    with st.form("add_form"):
        n = st.text_input("Name")
        m = st.text_input("Mobile")
        p = st.text_input("PRM ID")
        if st.form_submit_button("Save"):
            requests.post(WEBHOOK_URL, json={"action":"add_retailer","name":n.upper(),"mobile":m,"prm":p,"location":"Manual","date":date.today().strftime("%d-%m-%Y")})
            st.success("Retailer Added!"); st.cache_data.clear()

    st.markdown("---")
    st.header("📂 Bulk Retailer Upload")
    up = st.file_uploader("Upload Excel (Name, PRM, Details, DUSE, ADVANCE)", type=["xlsx","csv"])
    if up:
        df_up = pd.read_excel(up) if up.name.endswith('xlsx') else pd.read_csv(up)
        df_up.columns = [' '.join(str(col).upper().split()) for col in df_up.columns]
        st.dataframe(df_up, use_container_width=True)
        if st.button("🚀 Process Bulk Retailers"):
            prog = st.progress(0)
            session = requests.Session()
            for i, row in df_up.iterrows():
                b_name = str(row.get("RETAILER NAME", "")).upper()
                b_prm = str(row.get("PRM ID", "")).split('.')[0]
                b_mob = str(row.get("DETAILS", "")).split('.')[0]
                b_dues = float(str(row.get("DUSE", 0)).replace(',',''))
                b_adv = float(str(row.get("ADVANCE", 0)).replace(',',''))
                if b_name:
                    session.post(WEBHOOK_URL, json={"action":"add_retailer","name":b_name,"mobile":b_mob,"prm":b_prm,"location":"BULK","date":date.today().strftime("%d-%m-%Y")})
                    time.sleep(0.5)
                    if b_dues > 0: session.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":b_name,"r_mob":b_mob,"type":"Opening Dues","amt_out":b_dues,"amt_in":0,"fse":"SYSTEM","txn_id":"OPENING"})
                    if b_adv > 0: session.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":b_name,"r_mob":b_mob,"type":"Opening Advance","amt_out":0,"amt_in":b_adv,"fse":"SYSTEM","txn_id":"OPENING"})
                    time.sleep(0.5)
                prog.progress((i+1)/len(df_up))
            st.success("Bulk Upload Success!"); st.cache_data.clear()

# --- 📜 5. LEDGER ---
elif st.session_state.current_page == "LEDGER":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("📜 Retailer Ledger Report")
    search = st.selectbox("Select Retailer", options=dropdown_options)
    if search != "Type here to search...":
        r_name = retailers_data[search]["Name"]
        user_led = led_df[led_df['Retailer Name'] == r_name].sort_values(by='DateObj')
        s_date = st.date_input("From", date.today().replace(day=1))
        e_date = st.date_input("To", date.today())
        f_led = user_led[(user_led['DateObj'].dt.date >= s_date) & (user_led['DateObj'].dt.date <= e_date)].copy()
        st.dataframe(f_led.drop(columns=['DateObj']), use_container_width=True)
        st.download_button("📥 Excel", f_led.to_csv(index=False).encode('utf-8-sig'), "Ledger.csv")

# --- 💸 6. DUES ---
elif st.session_state.current_page == "DUES":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("💰 Dues Collection List")
    if st.button("Check All Dues"):
        summary = []
        for k, v in retailers_data.items():
            name = v["Name"]
            d = pd.to_numeric(led_df[led_df['Retailer Name']==name]['Amount Out (Debit)'], errors='coerce').sum()
            c = pd.to_numeric(led_df[led_df['Retailer Name']==name]['Amount In (Credit)'], errors='coerce').sum()
            if (d-c) > 0: summary.append({"Retailer": name, "Mobile": v["Mobile"], "Dues": d-c})
        st.dataframe(pd.DataFrame(summary), use_container_width=True)

# --- 📂 7. BULK ENTRY (JIO) ---
elif st.session_state.current_page == "BULK":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("📂 Auto-Match Bulk Etop")
    up_jio = st.file_uploader("Upload Jio Export", type=["xlsx","csv"])
    if up_jio:
        df_j = pd.read_excel(up_jio) if up_jio.name.endswith('xlsx') else pd.read_csv(up_jio)
        df_j.columns = [' '.join(str(col).split()) for col in df_j.columns]
        st.dataframe(df_j, use_container_width=True)
        f_name = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
        f_pin = st.text_input("PIN", type="password")
        if st.button("🚀 Upload"):
            if (f_name=="Avdhesh Kumar" and f_pin=="9557") or (f_name=="Babloo kumar singh" and f_pin=="2081"):
                prog = st.progress(0)
                session = requests.Session()
                for i, row in df_j.iterrows():
                    prm = clean_prm_id(row.get("Partner PRM ID", ""))
                    if prm in prm_mapping:
                        amt = float(str(row.get("Transfer Amount", 0)).replace(',',''))
                        session.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":prm_mapping[prm]['Name'],"r_mob":prm_mapping[prm]['Mobile'],"type":"Etop Transfer","amt_out":round(amt*0.97,2),"amt_in":0,"fse":f_name,"txn_id":str(row.get("Order ID",""))})
                        time.sleep(0.6)
                    prog.progress((i+1)/len(df_j))
                st.success("Done!"); st.cache_data.clear()

# --- 🚨 8. URGENT RECOVERY ---
elif st.session_state.current_page == "URGENT":
    if st.button("🔙 Back Menu", use_container_width=True): go_to("HOME")
    st.error("### 🚨 Urgent Recovery Panel")
    f_n = st.selectbox("FSE", ["Babloo kumar singh", "Avdhesh Kumar"])
    f_p = st.text_input("PIN", type="password")
    if f_p == "2081" or f_p == "9557":
        now = datetime.now()
        for _, row in led_df.iterrows():
            r_type, r_date = str(row['Product/Service']), row['DateObj']
            a_out, a_in = float(row['Amount Out (Debit)'] or 0), float(row['Amount In (Credit)'] or 0)
            is_u = False
            if "Etop" in r_type and (now - r_date) > timedelta(hours=24) and a_out > a_in: is_u = True
            if "JPB" in r_type and (now - r_date) > timedelta(days=15) and a_out > a_in: is_u = True
            if is_u:
                st.markdown(f"""<div class="urgent-card"><b>{row['Retailer Name']}</b><br>₹{a_out} | {row['Date']}</div>""", unsafe_allow_html=True)
                with st.form(f"rsn_{_}"):
                    rsn = st.text_area("Reason")
                    if st.form_submit_button("Submit"):
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":row['Retailer Name'],"type":"Urgent Reason","txn_id":rsn,"fse":f_n})
                        st.success("Recorded!")
