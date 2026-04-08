import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
import requests

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
        color: white;
        padding: 35px 20px;
        border-radius: 16px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    .app-header h1 { font-size: 2.4rem; font-weight: 700; margin-bottom: 5px; color: #ffffff;}
    .app-header p { font-size: 1.1rem; font-weight: 300; opacity: 0.8; margin: 0;}
    
    /* Input Box Design */
    .stDataFrame, .stSelectbox, .stNumberInput, .stTextInput, .stDateInput {
        background-color: white;
        border-radius: 10px;
        padding: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 🛑 YOUR APPS SCRIPT URL
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby_yV4nEMwrBODnkVh0x5DrVqcbj42iDMLNlX8M7QPrVGGMltoOfZhlid_gXlB0dwMvZQ/exec"

sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

@st.cache_data(ttl=30)
def load_data():
    try:
        ret_df = pd.read_csv(retailers_csv).dropna(how="all").fillna("")
        inv_df = pd.read_csv(inventory_csv).dropna(how="all").fillna("")
        led_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
        return ret_df, inv_df, led_df
    except: return None, None, None

ret_df, inv_df, led_df = load_data()

# Create Retailer Dropdown List & PRM Mapping Dictionary
retailers_data = {}
prm_mapping = {} 
dropdown_options = ["Type here to search..."]
if ret_df is not None:
    for index, row in ret_df.iterrows():
        disp_prm = str(row.get("PRM ID", "")).split('.')[0].strip()
        name = str(row.get("Retailer Name", "")).strip()
        mobile = str(row.get("Mobile Number", "")).split('.')[0].strip()
        
        # 🔴 Super-Clean PRM for Backend Matching (Removes all spaces)
        match_prm = str(row.get("PRM ID", "")).split('.')[0].replace(" ", "").strip().upper()
        
        if match_prm and name and match_prm != "NAN":
            retailers_data[f"{disp_prm} - {name}"] = {"Name": name, "Mobile": mobile, "PRM": disp_prm}
            prm_mapping[match_prm] = {"Name": name, "Mobile": mobile}
            dropdown_options.append(f"{disp_prm} - {name}")

# Session State for Navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "HOME"

def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- 🌟 APP HEADER ---
st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Smart Business Management System</p></div>', unsafe_allow_html=True)

# --- 🏠 HOME PAGE (Premium Grid - No Sidebar) ---
if st.session_state.current_page == "HOME":
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
        if st.button("📊 Live Stock", use_container_width=True): go_to("STOCK")
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD_RETAILER")
        if st.button("📜 Ledger Report", use_container_width=True): go_to("LEDGER")
        if st.button("📂 Bulk Entry (Excel)", use_container_width=True): go_to("BULK")

    with col2:
        if st.button("💰 Today's Collection", use_container_width=True): go_to("COLLECTION")
        if st.button("📦 Stock / Payment Entry", use_container_width=True): go_to("ENTRY")
        if st.button("💸 Dues List (Bulk SMS)", use_container_width=True): go_to("DUES")

# --- 📊 1. STOCK PAGE ---
elif st.session_state.current_page == "STOCK":
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
    st.header("📊 Live Inventory Stock")
    if inv_df is not None: st.dataframe(inv_df, use_container_width=True, hide_index=True)

# --- 💰 2. TODAY COLLECTION ---
elif st.session_state.current_page == "COLLECTION":
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
    st.header("💸 Today's Collection")
    if ret_df is not None and led_df is not None:
        for index, row in ret_df.iterrows():
            name = row["Retailer Name"]
            mobile = row["Mobile Number"]
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
                                    requests.post(WEBHOOK_URL, json=payload)
                                    st.success(f"✅ ₹{p_amt} collected from {name} successfully!")
                                    st.cache_data.clear()

# --- 📦 3. ENTRY PAGE (3D Wobble Buttons) ---
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
    
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
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
            else: t_amount = float(etop_opt)
        elif t_type == "Payment Received":
            p_mode = st.selectbox("Payment Mode", ["Cash", "Online"])
            t_amt_input = st.number_input("Enter Amount ₹ (Type Here)", min_value=1.0, value=None, step=10.0)
            t_amount = t_amt_input if t_amt_input else 0.0
        elif t_type == "JPB V4":
            t_qty = st.number_input("Quantity (Piece)", min_value=1)
            t_rate_input = st.number_input("Rate ₹", min_value=0.0, value=None, step=10.0)
            if t_rate_input:
                t_amount = t_qty * t_rate_input
                st.info(f"Total Amount: ₹{t_amount}")
            else: t_amount = 0.0
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
            final_type = f"{t_type} ({p_mode})" if t_type == "Payment Received" else t_type
            
            payload = {"action": "add_txn", "date": t_date.strftime("%d-%m-%Y"), "r_name": r_name, "r_mob": r_mob, "type": final_type, "qty": t_qty, "amt_out": amt_out, "amt_in": amt_in, "fse": fse, "txn_id": txn_id}
            requests.post(WEBHOOK_URL, json=payload)
            st.success("✅ Saved successfully!")
            st.cache_data.clear()
            msg = f"*🧾 Sandhya Enterprises*\nDate: {t_date.strftime('%d-%m-%Y')}\nRetailer: {r_name}\nItem: {final_type}\nAmount: ₹{t_amount}\n🙏 Thank You!"
            st.markdown(f"### [🟢 Send WhatsApp Receipt](https://wa.me/91{r_mob}?text={urllib.parse.quote(msg)})", unsafe_allow_html=True)

# --- ➕ 4. ADD RETAILER ---
elif st.session_state.current_page == "ADD_RETAILER":
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
    st.header("➕ Add New Retailer")
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
                requests.post(WEBHOOK_URL, json=payload)
                st.success("Retailer saved successfully!"); st.cache_data.clear()

# --- 📜 5. LEDGER ---
elif st.session_state.current_page == "LEDGER":
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
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
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
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

# --- 📂 7. DIRECT JIO EXCEL UPLOAD (AUTO-MATCH & 3% COMMISSION DEDUCTION) ---
elif st.session_state.current_page == "BULK":
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
    st.header("📂 Auto-Match Bulk Entry (Etop Transfer)")
    st.info("Directly upload your Jio Export Excel. The system will automatically match PRM IDs and deduct 3% margin from the Transfer Amount.")
    
    uploaded_file = st.file_uploader("Upload Direct Jio Excel/CSV File", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'): df_upload = pd.read_csv(uploaded_file).fillna("")
            else: df_upload = pd.read_excel(uploaded_file).fillna("")
            
            # 🔴 Removes extra/hidden spaces in Jio excel headers
            df_upload.columns = [' '.join(str(col).split()) for col in df_upload.columns]
                
            st.write("### 👁️ Preview of Uploaded Data")
            st.dataframe(df_upload, use_container_width=True) 
            
            st.markdown("---")
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
                    
                    for idx, row in df_upload.iterrows():
                        # 🔴 Super-Clean PRM for precise matching
                        raw_prm = str(row.get("Partner PRM ID", "")).split('.')[0].replace(" ", "").strip().upper()
                        
                        if raw_prm in prm_mapping:
                            r_name = prm_mapping[raw_prm]["Name"]
                            r_mob = prm_mapping[raw_prm]["Mobile"]
                            
                            raw_date = str(row.get("Transfer Date", date.today().strftime("%d-%m-%Y")))
                            r_date = raw_date.replace('.', '-')
                            
                            # Clean amount (removing commas if any)
                            raw_amt = str(row.get("Transfer Amount", "0")).replace(',', '').strip()
                            r_amt_out = float(raw_amt) if raw_amt else 0.0
                            
                            r_txn = str(row.get("Order ID", ""))
                            
                            # 🔴 NEW LOGIC: Deduct 3% from Transfer Amount
                            actual_amt_out = round(r_amt_out - (r_amt_out * 0.03), 2)
                            
                            if actual_amt_out > 0:
                                payload = {
                                    "action": "add_txn", "date": r_date, "r_name": r_name, "r_mob": r_mob, 
                                    "type": "Etop Transfer", "qty": 0, "amt_out": actual_amt_out, "amt_in": 0, 
                                    "fse": fse, "txn_id": r_txn
                                }
                                try:
                                    res = requests.post(WEBHOOK_URL, json=payload)
                                    if res.text == "Success": success_count += 1
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
