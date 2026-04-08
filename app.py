import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import urllib.parse
import requests
import time

# 1. Page Configuration (No Sidebar)
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# 💎 Global CSS Design (Hiding sidebar and styling header/buttons)
st.markdown("""
    <style>
    /* App Background */
    .stApp { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Hide Sidebar completely */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    
    /* 🌟 Premium Header */
    .app-header {
        background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%);
        color: white; padding: 25px 20px; border-radius: 16px;
        text-align: center; margin-top: 10px; margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    .app-header h1 { font-size: 2.4rem; font-weight: 700; margin-bottom: 5px; color: #ffffff;}
    .app-header p { font-size: 1.1rem; font-weight: 300; opacity: 0.8; margin: 0;}
    
    /* Input Box Design */
    .stDataFrame, .stSelectbox, .stNumberInput, .stTextInput, .stDateInput {
        background-color: white; border-radius: 10px; padding: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .urgent-card {
        background-color: #fff5f5; border-left: 5px solid #ff4b4b;
        padding: 15px; border-radius: 10px; margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 🛑 YOUR APPS SCRIPT URL
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

# Create Retailer Dropdown List & PRM Mapping
retailers_data = {}
prm_mapping = {} 
dropdown_options = ["Type here to search..."]
if ret_df is not None:
    for index, row in ret_df.iterrows():
        disp_prm = str(row.get("PRM ID", "")).split('.')[0].strip()
        name = str(row.get("Retailer Name", "")).strip()
        mobile = str(row.get("Mobile Number", "")).split('.')[0].strip()
        
        match_prm = clean_prm_id(row.get("PRM ID", ""))
        
        if match_prm and name and match_prm != "NAN":
            retailers_data[f"{disp_prm} - {name}"] = {"Name": name, "Mobile": mobile, "PRM": disp_prm}
            prm_mapping[match_prm] = {"Name": name, "Mobile": mobile}
            dropdown_options.append(f"{disp_prm} - {name}")

# Session State for Navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "HOME"

def go_to(page):
    st.session_state.current_page = page

# --- 🌟 APP HEADER ---
st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Smart Business Management System</p></div>', unsafe_allow_html=True)

# --- 🏠 HOME PAGE (Premium Grid - No Sidebar) ---
if st.session_state.current_page == "HOME":
    if st.button("🔄 Refresh System Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
    st.markdown("""
    <style>
    /* Home Page Buttons Design */
    .stButton > button {
        height: 75px; background: #ffffff; color: #1e293b;
        border: 1.5px solid #e2e8f0; border-radius: 14px;
        font-size: 18px; font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 15px;
    }
    .stButton > button:hover { border-color: #3b82f6; color: #3b82f6; box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Live Stock", use_container_width=True): go_to("STOCK"); st.rerun()
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD_RETAILER"); st.rerun()
        if st.button("📜 Ledger Report", use_container_width=True): go_to("LEDGER"); st.rerun()
        if st.button("📂 Bulk Entry (Excel)", use_container_width=True): go_to("BULK"); st.rerun()

    with col2:
        if st.button("💰 Today's Collection", use_container_width=True): go_to("COLLECTION"); st.rerun()
        if st.button("📦 Stock / Payment Entry", use_container_width=True): go_to("ENTRY"); st.rerun()
        if st.button("💸 Dues List (Bulk SMS)", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("🚨 Urgent Recovery", use_container_width=True): go_to("URGENT"); st.rerun()

# --- 📊 1. STOCK PAGE ---
elif st.session_state.current_page == "STOCK":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("📊 Live Inventory Stock")
    if inv_df is not None: st.dataframe(inv_df, use_container_width=True, hide_index=True)

# --- 💰 2. TODAY COLLECTION ---
elif st.session_state.current_page == "COLLECTION":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("💸 Today's Collection")
    if ret_df is not None and led_df is not None:
        for index, row in ret_df.iterrows():
            name = row["Retailer Name"]
            mobile = str(row["Mobile Number"]).split('.')[0]
            u_data = led_df[led_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
            
            if dues > 0:
                with st.expander(f"👤 {name} | 🚩 Dues: ₹{dues}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"### [📞 Call](tel:{mobile})")
                    with c2:
                        with st.form(f"pay_form_{name}", clear_on_submit=True):
                            p_amt = st.number_input(f"Payment Amount (₹)", min_value=1.0, key=f"amt_{name}")
                            p_mode = st.selectbox("Payment Mode", ["Cash", "Online"], key=f"mode_{name}")
                            p_fse = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"], key=f"fse_{name}")
                            p_pin = st.text_input("PIN", type="password", key=f"pin_{name}")
                            if st.form_submit_button("Save Payment", use_container_width=True):
                                if (p_fse == "Avdhesh Kumar" and p_pin != "9557") or (p_fse == "Babloo kumar singh" and p_pin != "2081"):
                                    st.error("❌ Invalid PIN!")
                                else:
                                    payload = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": name, "r_mob": mobile, "type": f"Payment ({p_mode})", "qty": 0, "amt_out": 0, "amt_in": p_amt, "fse": p_fse, "txn_id": f"Direct_{p_mode}"}
                                    res = requests.post(WEBHOOK_URL, json=payload)
                                    if res.status_code == 200:
                                        st.success(f"✅ ₹{p_amt} collected from {name} successfully!")
                                        st.cache_data.clear()
                                    else:
                                        st.error("Server Error: Data not saved.")

# --- 📦 3. ENTRY PAGE (3D Wobble Buttons + Original Options) ---
elif st.session_state.current_page == "ENTRY":
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #ffffff !important; color: #1a1a1a !important;
            border: none !important; border-radius: 12px !important;
            font-size: 18px !important; font-weight: 700 !important;
            box-shadow: 0 6px 0 #d1d9e6, 0 10px 15px rgba(0,0,0,0.1) !important;
            transition: all 0.2s ease-out !important;
            border-left: 6px solid #007bff !important; position: relative; top: 0;
        }
        .stButton>button:hover {
            color: #007bff !important; border-left: 6px solid #00c6ff !important;
            top: -3px !important; box-shadow: 0 9px 0 #d1d9e6, 0 15px 20px rgba(0,0,0,0.15) !important;
            animation: wobble-hor-bottom 0.5s both !important;
        }
        .stButton>button:active { top: 4px !important; box-shadow: 0 2px 0 #d1d9e6, 0 5px 10px rgba(0,0,0,0.1) !important; animation: none !important; }
        @keyframes wobble-hor-bottom {
            0%, 100% { transform: translateX(0%); }
            15% { transform: translateX(-4px) rotate(-1deg); }
            30% { transform: translateX(3px) rotate(1deg); }
            45% { transform: translateX(-2px) rotate(-0.5deg); }
            60% { transform: translateX(1px) rotate(0.2deg); }
        }
        </style>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("📦 Stock Out / Payment Entry")
    
    t_date = st.date_input("Date", date.today())
    t_prm = st.selectbox("Select Retailer*", options=dropdown_options)
    
    col1, col2 = st.columns(2)
    with col1:
        t_type = st.selectbox("Select Entry Type", ["Etop Transfer", "Payment Received", "JPB V4", "Sim Card"])
        fse = st.selectbox("Select FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
        fse_pin = st.text_input("Enter 4-digit PIN*", type="password", max_chars=4)

    with col2:
        t_qty = 0; t_amount = 0.0; p_mode = ""
        
        if t_type == "Etop Transfer":
            etop_opt = st.selectbox("Select Amount ₹", ["5000", "3000", "2000", "1500", "500", "Manual"])
            if etop_opt == "Manual":
                t_amt_input = st.number_input("Enter Manual Amount ₹", min_value=1.0, value=None, step=10.0)
                t_amount = t_amt_input if t_amt_input else 0.0
            else:
                t_amount = float(etop_opt)
                
        # 🟢 RESTORED: Cash/Online Option for Payment Received
        elif t_type == "Payment Received":
            p_mode = st.selectbox("Payment Mode", ["Cash", "Online"])
            t_amt_input = st.number_input("Enter Amount ₹", min_value=1.0, value=None, step=10.0)
            t_amount = t_amt_input if t_amt_input else 0.0
            
        elif t_type == "JPB V4":
            t_qty = st.number_input("Quantity (Piece)", min_value=1)
            t_rate_input = st.number_input("Rate ₹", min_value=0.0, value=None, step=10.0)
            if t_rate_input:
                t_amount = t_qty * t_rate_input
                st.info(f"Total Amount: ₹{t_amount}")
            else:
                t_amount = 0.0
                
        elif t_type == "Sim Card":
            t_qty = st.number_input("Quantity (SIM)", min_value=1)
            t_amount = 0.0

        txn_id = st.text_input("Transaction ID (If any)")

    if st.button("🚀 Save and Send WhatsApp", use_container_width=True):
        if t_prm == "Type here to search...": st.error("Please select a retailer from the list!")
        elif (t_type != "Sim Card") and (t_amount == 0.0 or t_amount is None): st.error("Please enter a valid amount!")
        elif fse == "Avdhesh Kumar" and fse_pin != "9557": st.error("❌ Invalid PIN for Avdhesh Kumar!")
        elif fse == "Babloo kumar singh" and fse_pin != "2081": st.error("❌ Invalid PIN for Babloo kumar singh!")
        else:
            r_name = retailers_data[t_prm]["Name"]
            r_mob = retailers_data[t_prm]["Mobile"]
            amt_out = t_amount if t_type != "Payment Received" else 0
            amt_in = t_amount if t_type == "Payment Received" else 0
            
            # Update type to include mode if it's payment
            final_type = f"{t_type} ({p_mode})" if t_type == "Payment Received" else t_type
            
            payload = {"action": "add_txn", "date": t_date.strftime("%d-%m-%Y"), "r_name": r_name, "r_mob": r_mob, "type": final_type, "qty": t_qty, "amt_out": amt_out, "amt_in": amt_in, "fse": fse, "txn_id": txn_id}
            try:
                res = requests.post(WEBHOOK_URL, json=payload)
                if res.status_code == 200:
                    st.success("✅ Saved successfully!")
                    st.cache_data.clear()
                    msg = f"*🧾 Sandhya Enterprises*\nDate: {t_date.strftime('%d-%m-%Y')}\nRetailer: {r_name}\nItem: {final_type}\nAmount: ₹{t_amount}\n🙏 Thank You!"
                    st.markdown(f"### [🟢 Send WhatsApp Receipt](https://wa.me/91{r_mob}?text={urllib.parse.quote(msg)})", unsafe_allow_html=True)
                else:
                    st.error("Error: Could not reach Google Sheet.")
            except Exception as e:
                st.error(f"Network Error: {e}")

# --- ➕ 4. ADD RETAILER (Original Form Restored) ---
elif st.session_state.current_page == "ADD_RETAILER":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("➕ Add Single Retailer")
    # 🟢 RESTORED: 2-Column layout with 'Location' Box
    with st.form("add_retailer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            r_name = st.text_input("Retailer Name*")
            r_mobile = st.text_input("Mobile Number*", max_chars=10)
        with col2:
            r_prm = st.text_input("PRM ID*")
            r_loc = st.text_input("Location")
        
        if st.form_submit_button("Save Retailer", use_container_width=True):
            if r_name and r_prm and r_mobile:
                payload = {"action": "add_retailer", "name": r_name.upper(), "mobile": r_mobile, "prm": r_prm, "location": r_loc.upper(), "date": datetime.now().strftime("%d-%m-%Y")}
                try:
                    res = requests.post(WEBHOOK_URL, json=payload)
                    if res.status_code == 200:
                        st.success("Retailer saved successfully!")
                        st.cache_data.clear()
                    else:
                        st.error("Failed to save to Google Sheet.")
                except Exception as e:
                    st.error(f"Network Error: {e}")
            else:
                st.error("Name, Mobile, and PRM ID are required!")

    # Bulk Upload Section
    st.markdown("---")
    st.header("📂 Bulk Retailer & Opening Balance Upload")
    st.info("Upload Excel: Retailer Name | PRM ID | Details | DUSE | ADVANCE")
    
    uploaded_ret_file = st.file_uploader("Upload Retailers Excel File", type=["csv", "xlsx"])
    if uploaded_ret_file is not None:
        try:
            if uploaded_ret_file.name.endswith('.csv'): df_ret = pd.read_csv(uploaded_ret_file).fillna("")
            else: df_ret = pd.read_excel(uploaded_ret_file).fillna("")
            
            df_ret.columns = [' '.join(str(col).upper().split()) for col in df_ret.columns]
            st.write("### 👁️ Preview of Retailers Data")
            st.dataframe(df_ret, use_container_width=True)
            
            c1, c2 = st.columns(2)
            bulk_fse = c1.selectbox("Select FSE", ["Avdhesh Kumar", "Babloo kumar singh"], key="b_ret_fse")
            bulk_pin = c2.text_input("Enter 4-digit PIN*", type="password", max_chars=4, key="b_ret_pin")
            
            if st.button("🚀 Upload Retailers & Balances", use_container_width=True):
                if bulk_fse == "Avdhesh Kumar" and bulk_pin != "9557": st.error("❌ Invalid PIN!")
                elif bulk_fse == "Babloo kumar singh" and bulk_pin != "2081": st.error("❌ Invalid PIN!")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    total_rows = len(df_ret)
                    success_ret = 0
                    
                    col_name = next((c for c in df_ret.columns if "NAME" in c or "RETAILER" in c), df_ret.columns[0] if len(df_ret.columns) > 0 else None)
                    col_prm = next((c for c in df_ret.columns if "PRM" in c), df_ret.columns[1] if len(df_ret.columns) > 1 else None)
                    col_mob = next((c for c in df_ret.columns if "DETAIL" in c or "MOB" in c), df_ret.columns[2] if len(df_ret.columns) > 2 else None)
                    col_dues = next((c for c in df_ret.columns if "DUS" in c or "DUE" in c), df_ret.columns[3] if len(df_ret.columns) > 3 else None)
                    col_adv = next((c for c in df_ret.columns if "ADV" in c), df_ret.columns[4] if len(df_ret.columns) > 4 else None)
                    
                    session = requests.Session()
                    
                    for idx, row in df_ret.iterrows():
                        b_name = str(row.get(col_name, "")).strip().upper() if col_name else ""
                        if b_name == "NAN" or "UNNAMED" in b_name or b_name == "RETAILER NAME": b_name = ""
                        b_prm = clean_prm_id(row.get(col_prm, ""))
                        b_mob = clean_prm_id(row.get(col_mob, ""))
                        
                        try:
                            val_dues = str(row.get(col_dues, "0")).replace(',', '').strip()
                            b_dues = float(val_dues) if val_dues != "nan" and val_dues != "" else 0.0
                        except: b_dues = 0.0
                        
                        try:
                            val_adv = str(row.get(col_adv, "0")).replace(',', '').strip()
                            b_adv = float(val_adv) if val_adv != "nan" and val_adv != "" else 0.0
                        except: b_adv = 0.0
                        
                        if b_name: 
                            payload_ret = {"action": "add_retailer", "name": b_name, "mobile": b_mob, "prm": b_prm, "location": "BULK UPLOAD", "date": date.today().strftime("%d-%m-%Y")}
                            try:
                                session.post(WEBHOOK_URL, json=payload_ret)
                                success_ret += 1
                                if b_dues > 0:
                                    payload_dues = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": b_name, "r_mob": b_mob, "type": "Opening Dues", "qty": 0, "amt_out": b_dues, "amt_in": 0, "fse": bulk_fse, "txn_id": "OPENING_BAL"}
                                    session.post(WEBHOOK_URL, json=payload_dues)
                                if b_adv > 0:
                                    payload_adv = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": b_name, "r_mob": b_mob, "type": "Opening Advance", "qty": 0, "amt_out": 0, "amt_in": b_adv, "fse": bulk_fse, "txn_id": "OPENING_BAL"}
                                    session.post(WEBHOOK_URL, json=payload_adv)
                            except Exception as e: pass
                            
                        progress_bar.progress((idx + 1) / total_rows)
                        status_text.text(f"Uploading... {idx + 1}/{total_rows}")
                        
                    st.success(f"✅ Successfully uploaded {success_ret} Retailers!")
                    st.cache_data.clear()
        except Exception as e: st.error(f"❌ Error: {str(e)}")

# --- 📜 5. LEDGER ---
elif st.session_state.current_page == "LEDGER":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("📜 Retailer Ledger Report")
    search_prm = st.selectbox("Select Retailer:", options=dropdown_options)
    if search_prm != "Type here to search...":
        r_name = retailers_data[search_prm]["Name"]
        led_df['DateObj'] = pd.to_datetime(led_df['Date'], format='%d-%m-%Y', errors='coerce')
        user_df = led_df[led_df['Retailer Name'] == r_name].sort_values(by='DateObj')
        st.markdown(f"### 👤 {r_name}'s Ledger")
        col_d1, col_d2 = st.columns(2)
        s_date = col_d1.date_input("Start Date:", date.today().replace(day=1))
        e_date = col_d2.date_input("End Date:", date.today())
        if s_date <= e_date:
            f_df = user_df[(user_df['DateObj'].dt.date >= s_date) & (user_df['DateObj'].dt.date <= e_date)].copy()
            f_df['Amount Out (Debit)'] = pd.to_numeric(f_df['Amount Out (Debit)'], errors='coerce').fillna(0)
            f_df['Amount In (Credit)'] = pd.to_numeric(f_df['Amount In (Credit)'], errors='coerce').fillna(0)
            f_df['Balance'] = (f_df['Amount Out (Debit)'] - f_df['Amount In (Credit)']).cumsum()
            st.dataframe(f_df.drop(columns=['DateObj']), use_container_width=True, hide_index=True)
            t_out = f_df['Amount Out (Debit)'].sum()
            t_in = f_df['Amount In (Credit)'].sum()
            st.error(f"Total Debit: ₹{t_out} | Total Credit: ₹{t_in} | Dues: ₹{t_out - t_in}")
            c1, c2 = st.columns(2)
            c1.download_button("📥 Download Excel", f_df.to_csv(index=False).encode('utf-8-sig'), f"{r_name}_Ledger.csv", "text/csv", use_container_width=True)
            html = f"<h2>Sandhya Enterprises</h2><b>Retailer:</b> {r_name}<br><b>Period:</b> {s_date} to {e_date}<br><br>" + f_df.drop(columns=['DateObj']).to_html(index=False)
            c2.download_button("📄 PDF (Report)", html.encode('utf-8-sig'), f"{r_name}_Report.html", "text/html", use_container_width=True)

# --- 💸 6. DUES REMINDERS ---
elif st.session_state.current_page == "DUES":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("💰 Dues Collection List (Bulk SMS)")
    if st.button("🔄 Check All Dues", use_container_width=True):
        summary = []
        for key, val in retailers_data.items():
            name = val["Name"]
            u_data = led_df[led_df['Retailer Name'] == name]
            d = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
            c = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
            if (d - c) > 0: summary.append({"Retailer": name, "Mobile": val["Mobile"], "Dues": d - c})
        s_df = pd.DataFrame(summary)
        if not s_df.empty:
            st.error(f"💸 Total Market Dues: ₹{s_df['Dues'].sum()}")
            st.dataframe(s_df, use_container_width=True, hide_index=True)
            for _, row in s_df.iterrows():
                msg = f"Dear Partner, your pending dues are ₹{row['Dues']}. Please clear your payment. Regards, Sandhya Enterprises."
                st.markdown(f"**{row['Retailer']}** (₹{row['Dues']}) -> [📲 Send Reminder](https://wa.me/91{row['Mobile']}?text={urllib.parse.quote(msg)})")
        else: st.success("No dues pending!")

# --- 📂 7. DIRECT JIO EXCEL UPLOAD ---
elif st.session_state.current_page == "BULK":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("📂 Auto-Match Bulk Entry (Etop Transfer)")
    st.info("Directly upload your Jio Export Excel. The system will automatically match PRM IDs and deduct 3% margin.")
    
    uploaded_file = st.file_uploader("Upload Direct Jio Excel/CSV File", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'): df_upload = pd.read_csv(uploaded_file).fillna("")
            else: df_upload = pd.read_excel(uploaded_file).fillna("")
            
            df_upload.columns = [' '.join(str(col).split()) for col in df_upload.columns]
            st.write("### 👁️ Preview of Uploaded Data")
            st.dataframe(df_upload, use_container_width=True) 
            
            st.write("### 🔐 Authentication & Upload")
            col1, col2 = st.columns(2)
            fse = col1.selectbox("Select FSE", ["Avdhesh Kumar", "Babloo kumar singh"], key="bulk_fse")
            fse_pin = col2.text_input("Enter 4-digit PIN*", type="password", max_chars=4, key="bulk_pin")
            
            if st.button("🚀 Match & Upload Etop Transfers", use_container_width=True):
                if fse == "Avdhesh Kumar" and fse_pin != "9557": st.error("❌ Invalid PIN for Avdhesh Kumar!")
                elif fse == "Babloo kumar singh" and fse_pin != "2081": st.error("❌ Invalid PIN for Babloo kumar singh!")
                elif "Partner PRM ID" not in df_upload.columns or "Transfer Amount" not in df_upload.columns:
                    st.error("❌ Error: Missing 'Partner PRM ID' or 'Transfer Amount' columns. Make sure you upload the correct Jio file.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    total_rows = len(df_upload)
                    success_count = 0
                    not_found_count = 0
                    
                    session = requests.Session()
                    
                    for idx, row in df_upload.iterrows():
                        raw_prm = clean_prm_id(row.get("Partner PRM ID", ""))
                        
                        if raw_prm in prm_mapping:
                            r_name = prm_mapping[raw_prm]["Name"]
                            r_mob = prm_mapping[raw_prm]["Mobile"]
                            
                            raw_date = str(row.get("Transfer Date", date.today().strftime("%d-%m-%Y")))
                            r_date = raw_date.replace('.', '-')
                            
                            try:
                                val_amt = str(row.get("Transfer Amount", "0")).replace(',', '').strip()
                                r_amt_out = float(val_amt) if val_amt != "nan" and val_amt != "" else 0.0
                            except: r_amt_out = 0.0
                            
                            r_txn = str(row.get("Order ID", ""))
                            actual_amt_out = round(r_amt_out - (r_amt_out * 0.03), 2)
                            
                            if actual_amt_out > 0:
                                payload = {
                                    "action": "add_txn", "date": r_date, "r_name": r_name, "r_mob": r_mob, 
                                    "type": "Etop Transfer", "qty": 0, "amt_out": actual_amt_out, "amt_in": 0, 
                                    "fse": fse, "txn_id": r_txn
                                }
                                try:
                                    session.post(WEBHOOK_URL, json=payload)
                                    success_count += 1
                                except: pass
                        else:
                            not_found_count += 1
                            
                        progress_bar.progress((idx + 1) / total_rows)
                        status_text.text(f"Processing... {idx + 1}/{total_rows}")
                        
                    st.success(f"✅ Completed! Successfully added {success_count} Etop Transfers (with 3% deduction applied).")
                    if not_found_count > 0:
                        st.warning(f"⚠️ {not_found_count} PRMs from Excel were not found in your Retailer list. They were skipped.")
                    st.cache_data.clear()
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# --- 🚨 8. URGENT RECOVERY ---
elif st.session_state.current_page == "URGENT":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.error("### 🚨 Urgent Recovery Panel")
    f_n = st.selectbox("Select FSE", ["Babloo kumar singh", "Avdhesh Kumar"])
    f_p = st.text_input("Enter PIN", type="password")
    
    if (f_p=="2081" and f_n=="Babloo kumar singh") or (f_p=="9557" and f_n=="Avdhesh Kumar"):
        now = datetime.now()
        u_list = []
        for _, row in led_df.iterrows():
            r_type = str(row['Product/Service'])
            r_date = row['DateObj']
            a_out = float(pd.to_numeric(row['Amount Out (Debit)'], errors='coerce') or 0)
            a_in = float(pd.to_numeric(row['Amount In (Credit)'], errors='coerce') or 0)
            is_u = False
            
            if "Etop" in r_type and (now - r_date) > timedelta(hours=24) and a_out > a_in: is_u = True
            if "JPB" in r_type and (now - r_date) > timedelta(days=15) and a_out > a_in: is_u = True
            
            if is_u:
                u_list.append({"Retailer": row['Retailer Name'], "Amount": a_out-a_in, "Date": row['Date'], "Type": r_type})
                st.markdown(f"""<div class="urgent-card"><b>{row['Retailer Name']}</b> | ₹{a_out-a_in} | Since: {row['Date']} ({r_type})</div>""", unsafe_allow_html=True)
                with st.form(f"r_{_}"):
                    rsn = st.text_input("Reason for delay")
                    if st.form_submit_button("Submit"):
                        requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":row['Retailer Name'],"type":"Urgent Reason","txn_id":rsn,"fse":f_n,"amt_in":0,"amt_out":0,"qty":0})
                        st.success("Reason Recorded!")
                        st.cache_data.clear()
        
        if u_list:
            st.download_button("📥 Download Urgent List (Excel)", pd.DataFrame(u_list).to_csv(index=False).encode('utf-8-sig'), "Urgent_Recovery.csv", "text/csv", use_container_width=True)
