import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

st.set_page_config(page_title="Cyber Safe Payment Portal", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main .block-container { background-color: #f8fafc; padding: 2rem; border-radius: 12px; max-width: 900px; }
    .red-alert { background-color: #fef2f2; color: #dc2626; padding: 15px; border-left: 5px solid #dc2626; border-radius: 5px; font-weight: bold; }
    .green-alert { background-color: #f0fdf4; color: #166534; padding: 15px; border-left: 5px solid #166534; border-radius: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 यहाँ अपना नया WEBHOOK और SHEET ID डालें 🔴
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzrsJYjhwSkdQZxjb2yUL67vwRtC2Kc5sJU21n7OtDEbm1uGMEhbz3JBZmUXAhSN28sGA/exec"
SHEET_ID = "https://docs.google.com/spreadsheets/d/17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM/edit?usp=sharing"
# ==========================================

@st.cache_data(ttl=2)
def load_retailers():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Authorized_Retailers&cb={int(time.time())}"
        df = pd.read_csv(url).dropna(how="all").fillna("")
        if not df.empty and "RetailerName" in df.columns:
            return df
    except: pass
    return pd.DataFrame(columns=["RetailerName", "Mobile", "Auth_UPI"])

@st.cache_data(ttl=2)
def load_ledger():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Payment_Ledger&cb={int(time.time())}"
        df = pd.read_csv(url).dropna(how="all").fillna("")
        if not df.empty and "Amount" in df.columns:
            return df
    except: pass
    return pd.DataFrame(columns=["Date", "RetailerName", "Amount", "Mode", "SenderUPI_Mobile", "Status", "Reference"])

if 'auth_retailers' not in st.session_state:
    st.session_state.auth_retailers = load_retailers()
else:
    st.session_state.auth_retailers = load_retailers()

if 'payment_ledger' not in st.session_state:
    st.session_state.payment_ledger = load_ledger()
else:
    st.session_state.payment_ledger = load_ledger()

st.markdown("""
    <div style='background: linear-gradient(90deg, #b91c1c 0%, #ef4444 100%); padding: 25px; border-radius: 10px; text-align: center; color: white; margin-bottom: 25px;'>
        <h1 style='margin:0; font-size: 34px; font-weight: 800;'>🛡️ CYBER-SAFE PAYMENT PORTAL</h1>
        <p style='margin:5px 0 0 0; font-size: 16px;'>Sandhya Enterprises - Authorized Transactions Only</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💰 Register Payment", "📋 Transaction Ledger", "🛡️ Manage Authorized Retailers"])

with tab1:
    st.markdown("### 💰 New Payment Entry & Verification")
    
    if st.session_state.auth_retailers.empty:
        st.warning("⚠️ अभी कोई अधिकृत (Authorized) रिटेलर लिस्ट नहीं है। पहले 'Manage Authorized Retailers' टैब में रिटेलर्स जोड़ें या सीधे Google Sheet में पेस्ट करें।")
    else:
        with st.form("payment_form"):
            col1, col2 = st.columns(2)
            with col1:
                retailer_list = ["-- Select Retailer --"] + st.session_state.auth_retailers["RetailerName"].astype(str).tolist()
                selected_retailer = st.selectbox("👤 Select Retailer*", retailer_list)
                amount = st.number_input("Amount Received (रुपये)*", min_value=0.0, step=10.0)
                purpose = st.text_input("Reference / Purpose (किस काम के लिए?)")
            with col2:
                pay_mode = st.selectbox("Payment Mode*", ["UPI / Online", "Bank Transfer (NEFT/RTGS)", "Cash"])
                sender_detail = st.text_input("Sender UPI ID / Mobile No. (किस नंबर/UPI से पैसा आया?)*")
                
            if st.form_submit_button("🔍 Verify & Save Payment", type="primary", use_container_width=True):
                if selected_retailer == "-- Select Retailer --" or amount <= 0:
                    st.error("❌ कृपया रिटेलर का नाम और सही अमाउंट डालें।")
                elif pay_mode != "Cash" and not sender_detail:
                    st.error("❌ ऑनलाइन पेमेंट के लिए भेजने वाले का UPI ID या नंबर डालना अनिवार्य है!")
                else:
                    status = "Verified"
                    if pay_mode != "Cash":
                        auth_data = st.session_state.auth_retailers[st.session_state.auth_retailers["RetailerName"] == selected_retailer].iloc[0]
                        auth_upi = str(auth_data.get("Auth_UPI", "")).strip().lower()
                        auth_mobile = str(auth_data.get("Mobile", "")).strip()
                        entered_sender = str(sender_detail).strip().lower()
                        
                        if entered_sender == auth_upi or entered_sender == auth_mobile or entered_sender in auth_upi:
                            status = "Verified (Safe)"
                            st.markdown(f"<div class='green-alert'>✅ **SAFE PAYMENT:** यह पेमेंट {selected_retailer} के अधिकृत नंबर/UPI से आया है।</div><br>", unsafe_allow_html=True)
                        else:
                            status = "UNVERIFIED (Danger)"
                            st.markdown(f"<div class='red-alert'>🚨 **RED ALERT:** सावधान! यह पेमेंट {selected_retailer} के पक्के नंबर से **नहीं** आया है! (Authorized: {auth_upi} | Received: {sender_detail})</div><br>", unsafe_allow_html=True)
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
                        if WEBHOOK_URL != "यहाँ_अपना_नया_WEBHOOK_URL_डालें":
                            requests.post(WEBHOOK_URL, json=new_payment, timeout=3)
                    except: pass
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()

with tab2:
    st.markdown("### 📋 Transaction History")
    if st.session_state.payment_ledger.empty:
        st.info("अभी तक कोई ट्रांज़ैक्शन नहीं हुआ है।")
    else:
        def highlight_danger(val):
            return 'background-color: #fef2f2; color: #dc2626; font-weight: bold;' if 'UNVERIFIED' in str(val) else ''
        try:
            styled_df = st.session_state.payment_ledger.style.map(highlight_danger, subset=['Status'])
        except:
            styled_df = st.session_state.payment_ledger.style.applymap(highlight_danger, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True)

with tab3:
    st.markdown("### 🛡️ Add Authorized Retailer")
    with st.form("add_retailer"):
        c1, c2, c3 = st.columns(3)
        new_ret_name = c1.text_input("Retailer Name*")
        new_ret_mob = c2.text_input("Registered Mobile Number*")
        new_ret_upi = c3.text_input("Authorized UPI ID*")
        
        if st.form_submit_button("➕ Save to Google Sheet"):
            if new_ret_name and new_ret_mob and new_ret_upi:
                new_ret = {
                    "sheet_name": "Authorized_Retailers",
                    "RetailerName": new_ret_name.upper(), 
                    "Mobile": new_ret_mob, 
                    "Auth_UPI": new_ret_upi.lower()
                }
                try:
                    if WEBHOOK_URL != "यहाँ_अपना_नया_WEBHOOK_URL_डालें":
                        requests.post(WEBHOOK_URL, json=new_ret, timeout=3)
                except: pass
                st.success(f"✅ {new_ret_name} added to safe list!")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ सभी फील्ड भरना जरूरी है।")
                
    st.markdown("---")
    st.markdown("#### Your Safe List (From Google Sheet)")
    st.dataframe(st.session_state.auth_retailers, use_container_width=True)
    st.info("💡 **TIP:** अगर आप एक साथ कई रिटेलर्स जोड़ना चाहते हैं, तो सीधे अपनी Google Sheet के 'Authorized_Retailers' पन्ने में जाकर पेस्ट कर दें। ऐप उसे खुद पढ़ लेगा!")
