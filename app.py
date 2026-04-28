import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Page Style & Layout
st.set_page_config(page_title="Cyber Safe Payment Portal", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main .block-container { background-color: #f8fafc; padding: 2rem; border-radius: 12px; max-width: 900px; }
    .red-alert { background-color: #fef2f2; color: #dc2626; padding: 15px; border-left: 5px solid #dc2626; border-radius: 5px; font-weight: bold; }
    .green-alert { background-color: #f0fdf4; color: #166534; padding: 15px; border-left: 5px solid #166534; border-radius: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 WEBHOOK AND SHEET ID (Aapki Detail Pehle se Set Hai)
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
# ==========================================

# 🟢 SMART DATA LOADER
@st.cache_data(ttl=1)
def load_data_from_sheet(sheet_name, expected_columns):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&cb={int(time.time())}"
    try:
        df = pd.read_csv(url).dropna(how="all").fillna("")
        if not df.empty:
            df.columns = [str(c).replace(" ", "").strip() for c in df.columns]
            return df
    except Exception as e:
        pass 
    return pd.DataFrame(columns=expected_columns)

# Data Load Karein
st.session_state.auth_retailers = load_data_from_sheet("Authorized_Retailers", ["RetailerName", "Mobile", "Auth_UPI"])
st.session_state.payment_ledger = load_data_from_sheet("Payment_Ledger", ["Date", "RetailerName", "Amount", "Mode", "SenderUPI_Mobile", "Status", "Reference"])

# Header
st.markdown("""
    <div style='background: linear-gradient(90deg, #b91c1c 0%, #ef4444 100%); padding: 25px; border-radius: 10px; text-align: center; color: white; margin-bottom: 25px;'>
        <h1 style='margin:0; font-size: 34px; font-weight: 800;'>🛡️ CYBER-SAFE PAYMENT PORTAL</h1>
        <p style='margin:5px 0 0 0; font-size: 16px;'>Sandhya Enterprises - Authorized Transactions Only</p>
    </div>
""", unsafe_allow_html=True)

if st.button("🔄 Sync Data with Google Sheet"):
    st.cache_data.clear()
    st.rerun()

tab1, tab2, tab3 = st.tabs(["💰 Register Payment", "📋 Transaction Ledger", "🛡️ Manage Authorized Retailers"])

# ==========================================
# TAB 1: REGISTER PAYMENT
# ==========================================
with tab1:
    st.markdown("### 💰 New Payment Entry & Verification")
    
    if st.session_state.auth_retailers.empty:
        st.warning("⚠️ Abhi koi Authorized Retailer list nahi hai. Pehle 'Manage Authorized Retailers' me add karein.")
    else:
        with st.form("payment_form"):
            col1, col2 = st.columns(2)
            with col1:
                ret_col = "RetailerName" if "RetailerName" in st.session_state.auth_retailers.columns else st.session_state.auth_retailers.columns[0]
                retailer_list = ["-- Select Retailer --"] + st.session_state.auth_retailers[ret_col].astype(str).tolist()
                
                selected_retailer = st.selectbox("👤 Select Retailer*", retailer_list)
                amount = st.number_input("Amount Received (Rs)*", min_value=0.0, step=10.0)
                purpose = st.text_input("UTR Number / Reference (Slip se dekh kar)*")
            with col2:
                pay_mode = st.selectbox("Payment Mode*", ["UPI / Online", "Bank Transfer", "Cash"])
                sender_detail = st.text_input("Sender UPI ya Bank ke Aakhiri 4 Ank (eg. 9424)*")
                
            if st.form_submit_button("🔍 Verify & Save Payment", type="primary", use_container_width=True):
                if selected_retailer == "-- Select Retailer --" or amount <= 0:
                    st.error("❌ Kripya sahi detail bharein.")
                elif pay_mode != "Cash" and (not sender_detail or not purpose):
                    st.error("❌ Online payment ke liye UTR aur Sender detail jaruri hai!")
                else:
                    status = "Verified"
                    if pay_mode != "Cash":
                        auth_data = st.session_state.auth_retailers[st.session_state.auth_retailers[ret_col] == selected_retailer].iloc[0]
                        
                        auth_upi = str(auth_data.get("Auth_UPI", "")).strip().lower()
                        auth_mobile = str(auth_data.get("Mobile", "")).strip()
                        entered_sender = str(sender_detail).strip().lower()
                        
                        # Verification Logic: Direct match ya 4-digit match
                        if entered_sender == auth_upi or entered_sender == auth_mobile or entered_sender in auth_upi:
                            status = "Verified (Safe)"
                            st.markdown(f"<div class='green-alert'>✅ **SAFE PAYMENT:** Ye {selected_retailer} ke pakke account se aaya hai.</div><br>", unsafe_allow_html=True)
                        else:
                            status = "UNVERIFIED (Danger)"
                            st.markdown(f"<div class='red-alert'>🚨 **RED ALERT:** Savdhan! Ye {selected_retailer} ke registered account se nahi aaya hai!</div><br>", unsafe_allow_html=True)
                    else:
                        status = "Cash (Safe)"
                        st.success("✅ Cash Payment Recorded.")

                    new_payment = {
                        "sheet_name": "Payment_Ledger",
                        "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": selected_retailer,
                        "Amount": amount,
                        "Mode": pay_mode,
                        "SenderUPI_Mobile": sender_detail if pay_mode != "Cash" else "Hand Cash",
                        "Status": status,
                        "Reference": purpose
                    }
                    try:
                        requests.post(WEBHOOK_URL, json=new_payment, timeout=3)
                    except: pass
                    
                    st.cache_data.clear()
                    time.sleep(1.5)
                    st.rerun()

# ==========================================
# TAB 2: TRANSACTION LEDGER
# ==========================================
with tab2:
    st.markdown("### 📋 Transaction History")
    if st.session_state.payment_ledger.empty:
        st.info("Abhi koi transaction nahi hai.")
    else:
        df_to_show = st.session_state.payment_ledger.copy()
        if "Status" in df_to_show.columns:
            def highlight_danger(val):
                return 'background-color: #fef2f2; color: #dc2626; font-weight: bold;' if 'UNVERIFIED' in str(val) else ''
            try:
                styled_df = df_to_show.style.map(highlight_danger, subset=['Status'])
            except:
                styled_df = df_to_show.style.applymap(highlight_danger, subset=['Status'])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.dataframe(df_to_show, use_container_width=True)

# ==========================================
# TAB 3: MANAGE RETAILERS
# ==========================================
with tab3:
    st.markdown("### 🛡️ Add Authorized Retailer")
    with st.form("add_retailer"):
        c1, c2, c3 = st.columns(3)
        new_ret_name = c1.text_input("Retailer Name*")
        new_ret_mob = c2.text_input("Mobile Number*")
        new_ret_upi = c3.text_input("Authorized UPI ya Bank A/C ke 4 Ank*")
        
        if st.form_submit_button("➕ Save to Google Sheet"):
            if new_ret_name and new_ret_mob and new_ret_upi:
                new_ret = {
                    "sheet_name": "Authorized_Retailers",
                    "RetailerName": new_ret_name.upper(), 
                    "Mobile": new_ret_mob, 
                    "Auth_UPI": new_ret_upi.lower()
                }
                try:
                    requests.post(WEBHOOK_URL, json=new_ret, timeout=3)
                except: pass
                st.success(f"✅ {new_ret_name} added!")
                st.cache_data.clear()
                time.sleep(1.5)
                st.rerun()
