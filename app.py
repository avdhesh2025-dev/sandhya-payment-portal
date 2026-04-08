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
        color: white; padding: 25px 20px; border-radius: 16px;
        text-align: center; margin-top: 10px; margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    .app-header h1 { font-size: 2.2rem; font-weight: 700; margin-bottom: 5px; color: #ffffff;}
    .app-header p { font-size: 1rem; opacity: 0.9; margin: 0;}
    .urgent-card {
        background-color: #fff5f5; border-left: 5px solid #ff4b4b;
        padding: 15px; border-radius: 10px; margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stDataFrame, .stSelectbox, .stNumberInput, .stTextInput, .stDateInput {
        background-color: white; border-radius: 10px; padding: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 🛑 YOUR APPS SCRIPT URL
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby_yV4nEMwrBODnkVh0x5DrVqcbj42iDMLNlX8M7QPrVGGMltoOfZhlid_gXlB0dwMvZQ/exec"

sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

@st.cache_data(ttl=10)
def load_data():
    try:
        ret_df = pd.read_csv(retailers_csv).dropna(how="all").fillna("")
        inv_df = pd.read_csv(inventory_csv).dropna(how="all").fillna("")
        led_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
        # Date conversion for recovery logic
        led_df['DateObj'] = pd.to_datetime(led_df['Date'], format='%d-%m-%Y', errors='coerce')
        return ret_df, inv_df, led_df
    except: return None, None, None

ret_df, inv_df, led_df = load_data()

retailers_data = {}
dropdown_options = ["Type here to search..."]
if ret_df is not None:
    for index, row in ret_df.iterrows():
        prm = str(row.get("PRM ID", "")).split('.')[0]
        name = str(row.get("Retailer Name", ""))
        mobile = str(row.get("Mobile Number", "")).split('.')[0]
        if prm and name and prm != "nan":
            retailers_data[f"{prm} - {name}"] = {"Name": name, "Mobile": mobile, "PRM": prm}
            dropdown_options.append(f"{prm} - {name}")

if "current_page" not in st.session_state:
    st.session_state.current_page = "HOME"

def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- 🌟 APP HEADER ---
st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Smart Business Management System</p></div>', unsafe_allow_html=True)

# --- 🏠 HOME PAGE ---
if st.session_state.current_page == "HOME":
    st.markdown("""
    <style>
    .stButton > button {
        height: 75px; background: #ffffff; color: #1e293b;
        border: 1.5px solid #e2e8f0; border-radius: 14px;
        font-size: 18px; font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 15px;
    }
    .stButton > button:hover { border-color: #3b82f6; color: #3b82f6; box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    /* Urgent Recovery Button Style */
    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button {
        background: #fff1f0; border-color: #ffa39e; color: #cf1322;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Live Stock", use_container_width=True): go_to("STOCK")
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD_RETAILER")
        if st.button("📜 Ledger Report", use_container_width=True): go_to("LEDGER")

    with col2:
        if st.button("💰 Today's Collection", use_container_width=True): go_to("COLLECTION")
        if st.button("📦 Stock / Payment Entry", use_container_width=True): go_to("ENTRY")
        if st.button("💸 Dues List (Bulk SMS)", use_container_width=True): go_to("DUES")

    # Full width Urgent Recovery Button
    if st.button("🚨 Urgent Recovery Amount", use_container_width=True): go_to("URGENT")

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
            name = row["Retailer Name"]; mobile = row["Mobile Number"]
            u_data = led_df[led_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
            if dues > 0:
                with st.expander(f"👤 {name} | 🚩 Dues: ₹{dues}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"### [📞 Call](tel:{mobile})")
                    with c2:
                        with st.form(f"pay_form_{name}", clear_on_submit=True):
                            p_amt = st.number_input(f"Amount (₹)", min_value=1.0, key=f"amt_{name}")
                            p_mode = st.selectbox("Mode", ["Cash", "Online"], key=f"mode_{name}")
                            p_fse = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"], key=f"fse_{name}")
                            p_pin = st.text_input("PIN", type="password", key=f"pin_{name}")
                            if st.form_submit_button("Save Payment", use_container_width=True):
                                if (p_fse == "Avdhesh Kumar" and p_pin != "9557") or (p_fse == "Babloo kumar singh" and p_pin != "2081"):
                                    st.error("❌ Invalid PIN!")
                                else:
                                    payload = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": name, "r_mob": mobile, "type": f"Payment ({p_mode})", "qty": 0, "amt_out": 0, "amt_in": p_amt, "fse": p_fse, "txn_id": f"Direct_{p_mode}"}
                                    requests.post(WEBHOOK_URL, json=payload)
                                    st.success(f"✅ ₹{p_amt} saved!"); st.cache_data.clear()

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
        t_type = st.selectbox("Entry Type", ["Etop Transfer", "Payment Received", "JPB V4", "Sim Card"])
        fse = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
        fse_pin = st.text_input("4-digit PIN*", type="password", max_chars=4)
    with col2:
        t_qty = 0; t_amount = 0.0; p_mode = ""
        if t_type == "Etop Transfer":
            etop_opt = st.selectbox("Select Amount ₹", ["5000", "3000", "2000", "1500", "500", "Manual"])
            t_amount = float(etop_opt) if etop_opt != "Manual" else st.number_input("Enter Amount ₹", min_value=1.0)
        elif t_type == "Payment Received":
            p_mode = st.selectbox("Payment Mode", ["Cash", "Online"])
            t_amount = st.number_input("Enter Amount ₹", min_value=1.0, value=None)
        elif t_type == "JPB V4":
            t_qty = st.number_input("Quantity (Piece)", min_value=1)
            t_rate = st.number_input("Rate ₹", min_value=0.0)
            t_amount = t_qty * t_rate
        elif t_type == "Sim Card":
            t_qty = st.number_input("Quantity (SIM)", min_value=1)
        txn_id = st.text_input("Transaction ID (If any)")

    if st.button("🚀 Save and Send WhatsApp", use_container_width=True):
        if (fse == "Avdhesh Kumar" and fse_pin != "9557") or (fse == "Babloo kumar singh" and fse_pin != "2081"):
            st.error("❌ Invalid PIN!")
        elif t_prm == "Type here to search...": st.error("Select Retailer!")
        else:
            r_name = retailers_data[t_prm]["Name"]; r_mob = retailers_data[t_prm]["Mobile"]
            amt_out = t_amount if t_type != "Payment Received" else 0
            amt_in = t_amount if t_type == "Payment Received" else 0
            payload = {"action": "add_txn", "date": t_date.strftime("%d-%m-%Y"), "r_name": r_name, "r_mob": r_mob, "type": t_type, "qty": t_qty, "amt_out": amt_out, "amt_in": amt_in, "fse": fse, "txn_id": txn_id}
            requests.post(WEBHOOK_URL, json=payload)
            st.success("✅ Saved!"); st.cache_data.clear()
            msg = f"*Sandhya Enterprises*\nRetailer: {r_name}\nItem: {t_type}\nAmount: ₹{t_amount}\n🙏 Thank You!"
            st.markdown(f"### [🟢 WhatsApp](https://wa.me/91{r_mob}?text={urllib.parse.quote(msg)})", unsafe_allow_html=True)

# --- 🚨 4. URGENT RECOVERY PAGE ---
elif st.session_state.current_page == "URGENT":
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
    st.error("### 🚨 Urgent Recovery Panel (Pending Dues)")
    
    col_f1, col_f2 = st.columns(2)
    check_fse = col_f1.selectbox("Select FSE", ["Babloo kumar singh", "Avdhesh Kumar"], key="rec_fse")
    check_pin = col_f2.text_input("Enter PIN to Access", type="password", key="rec_pin")

    if (check_fse == "Babloo kumar singh" and check_pin == "2081") or (check_fse == "Avdhesh Kumar" and check_pin == "9557"):
        st.info("Showing payments overdue: Etop > 24 Hours | JPB V4 > 15 Days")
        now = datetime.now()
        overdue_items = []
        
        if led_df is not None:
            # Group by retailer to find current net balance
            for r_name in led_df['Retailer Name'].unique():
                u_led = led_df[led_df['Retailer Name'] == r_name].sort_values('DateObj')
                # Check each transaction for overdue criteria
                for _, row in u_led.iterrows():
                    entry_type = str(row['Product/Service'])
                    entry_date = row['DateObj']
                    amt_debit = pd.to_numeric(row['Amount Out (Debit)'], errors='coerce') or 0
                    
                    if amt_debit > 0: # It's a sale
                        is_overdue = False
                        if "Etop" in entry_type and (now - entry_date) > timedelta(hours=24):
                            is_overdue = True
                        elif "JPB" in entry_type and (now - entry_date) > timedelta(days=15):
                            is_overdue = True
                        
                        if is_overdue:
                            overdue_items.append({"Name": r_name, "Type": entry_type, "Amt": amt_debit, "Date": row['Date']})

            if overdue_items:
                for item in overdue_items:
                    with st.container():
                        st.markdown(f"""<div class="urgent-card">
                            <b>👤 Retailer:</b> {item['Name']}<br>
                            <b>📦 Item:</b> {item['Type']} | <b>💰 Amt:</b> ₹{item['Amt']}<br>
                            <b>📅 Pending Since:</b> {item['Date']}
                        </div>""", unsafe_allow_html=True)
                        with st.form(key=f"form_{item['Name']}_{item['Date']}"):
                            reason = st.text_input("Why is this payment pending? (Reason)")
                            if st.form_submit_button("Submit Reason"):
                                payload = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": item['Name'], "type": "RECOVERY_ALERT", "qty": 0, "amt_out": 0, "amt_in": 0, "fse": check_fse, "txn_id": reason}
                                requests.post(WEBHOOK_URL, json=payload)
                                st.success("Reason recorded!")
            else:
                st.success("✅ No urgent recovery items found!")
    elif check_pin != "":
        st.error("❌ Wrong PIN")

# --- ➕ 5. ADD RETAILER ---
elif st.session_state.current_page == "ADD_RETAILER":
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
    st.header("➕ Add New Retailer")
    with st.form("add_retailer_form", clear_on_submit=True):
        r_name = st.text_input("Retailer Name*"); r_mobile = st.text_input("Mobile Number*", max_chars=10)
        r_prm = st.text_input("PRM ID*"); r_loc = st.text_input("Location")
        if st.form_submit_button("Save Retailer", use_container_width=True):
            if r_name and r_prm and r_mobile:
                payload = {"action": "add_retailer", "name": r_name.upper(), "mobile": r_mobile, "prm": r_prm, "location": r_loc.upper(), "date": datetime.now().strftime("%d-%m-%Y")}
                requests.post(WEBHOOK_URL, json=payload); st.success("Saved!"); st.cache_data.clear()

# --- 📜 6. LEDGER ---
elif st.session_state.current_page == "LEDGER":
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
    st.header("📜 Retailer Ledger Report")
    search_prm = st.selectbox("Select Retailer:", options=dropdown_options)
    if search_prm != "Type here to search...":
        r_name = retailers_data[search_prm]["Name"]
        user_df = led_df[led_df['Retailer Name'] == r_name].sort_values(by='DateObj')
        st.markdown(f"### 👤 {r_name}'s Ledger")
        st.dataframe(user_df.drop(columns=['DateObj']), use_container_width=True, hide_index=True)

# --- 💸 7. DUES ---
elif st.session_state.current_page == "DUES":
    if st.button("🔙 Back to Main Menu", use_container_width=True): go_to("HOME")
    st.header("💰 Dues Collection List")
    if st.button("🔄 Check All Dues", use_container_width=True):
        summary = []
        for key, val in retailers_data.items():
            name = val["Name"]; u_data = led_df[led_df['Retailer Name'] == name]
            d = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
            c = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
            if (d - c) > 0: summary.append({"Retailer": name, "Mobile": val["Mobile"], "Dues": d - c})
        if summary: st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
        else: st.success("No dues!")
