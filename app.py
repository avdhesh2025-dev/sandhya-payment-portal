import streamlit as st
import pandas as pd
from datetime import datetime
import time

# 1. Page Configuration & Clean CSS
st.set_page_config(page_title="Cyber Safe Payment Portal", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main .block-container {
        background-color: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        max-width: 900px;
    }
    .red-alert { background-color: #fef2f2; color: #dc2626; padding: 15px; border-left: 5px solid #dc2626; border-radius: 5px; font-weight: bold; }
    .green-alert { background-color: #f0fdf4; color: #166534; padding: 15px; border-left: 5px solid #166534; border-radius: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 WEBHOOK AND SHEET ID
# ==========================================
WEBHOOK_URL = "यहाँ_अपना_नया_WEBHOOK_URL_डालें"
SHEET_ID = "यहाँ_अपनी_Google_Sheet_की_ID_डालें"
# ==========================================

# 2. Database Initialization
# Master list of Authorized Retailers (Name, Mobile, Auth_UPI)
if 'auth_retailers' not in st.session_state:
    st.session_state.auth_retailers = pd.DataFrame(columns=["RetailerName", "Mobile", "Auth_UPI"])

# Transaction Ledger
if 'payment_ledger' not in st.session_state:
    st.session_state.payment_ledger = pd.DataFrame(columns=[
        "Date", "RetailerName", "Amount", "Mode", "SenderUPI_Mobile", "Status", "Reference"
    ])

# 3. Main UI Header
st.markdown("""
    <div style='background: linear-gradient(90deg, #b91c1c 0%, #ef4444 100%); padding: 25px; border-radius: 10px; text-align: center; color: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h1 style='margin:0; font-size: 34px; font-weight: 800;'>🛡️ CYBER-SAFE PAYMENT PORTAL</h1>
        <p style='margin:5px 0 0 0; font-size: 16px;'>Sandhya Enterprises - Authorized Transactions Only</p>
    </div>
""", unsafe_allow_html=True)

# 4. Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💰 Register Payment", "📋 Transaction Ledger", "🛡️ Manage Authorized Retailers", "📂 Upload Excel"])

# ==========================================
# TAB 1: REGISTER PAYMENT (VERIFICATION LOGIC)
# ==========================================
with tab1:
    st.markdown("### 💰 New Payment Entry & Verification")
    st.info("💡 **सुरक्षा चेक:** पेमेंट की एंट्री करने से पहले यह ऐप चेक करेगा कि पैसा अधिकृत (Authorized) अकाउंट से आया है या किसी अनजान (Unknown) अकाउंट से।")

    if st.session_state.auth_retailers.empty:
        st.warning("⚠️ अभी कोई अधिकृत (Authorized) रिटेलर लिस्ट नहीं है। पहले 'Manage Authorized Retailers' टैब में रिटेलर्स जोड़ें या Excel अपलोड करें।")
    else:
        with st.form("payment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                retailer_list = ["-- Select Retailer --"] + st.session_state.auth_retailers["RetailerName"].tolist()
                selected_retailer = st.selectbox("👤 Select Retailer*", retailer_list)
                amount = st.number_input("Amount Received (रुपये)*", min_value=0.0, step=10.0)
                purpose = st.text_input("Reference / Purpose (किस काम के लिए?)")
                
            with col2:
                pay_mode = st.selectbox("Payment Mode*", ["UPI / Online", "Bank Transfer (NEFT/RTGS)", "Cash"])
                sender_detail = st.text_input("Sender UPI ID / Mobile No. (किस नंबर/UPI से पैसा आया?)*", placeholder="e.g. 9876543210@ybl")
                
            verify_and_save = st.form_submit_button("🔍 Verify & Save Payment", type="primary", use_container_width=True)

            if verify_and_save:
                if selected_retailer == "-- Select Retailer --" or amount <= 0:
                    st.error("❌ कृपया रिटेलर का नाम और सही अमाउंट डालें।")
                elif pay_mode != "Cash" and not sender_detail:
                    st.error("❌ ऑनलाइन पेमेंट के लिए भेजने वाले का UPI ID या नंबर डालना अनिवार्य है!")
                else:
                    # 🟢 VERIFICATION LOGIC 🟢
                    status = "Verified"
                    alert_msg = ""
                    
                    if pay_mode != "Cash":
                        # Find the authorized details for this retailer
                        auth_data = st.session_state.auth_retailers[st.session_state.auth_retailers["RetailerName"] == selected_retailer].iloc[0]
                        auth_upi = str(auth_data["Auth_UPI"]).strip().lower()
                        auth_mobile = str(auth_data["Mobile"]).strip()
                        entered_sender = str(sender_detail).strip().lower()
                        
                        # Check if entered sender matches Auth UPI OR Auth Mobile
                        if entered_sender == auth_upi or entered_sender == auth_mobile or entered_sender in auth_upi:
                            status = "Verified (Safe)"
                            alert_msg = f"✅ **SAFE PAYMENT:** यह पेमेंट {selected_retailer} के अधिकृत (Authorized) नंबर/UPI से आया है।"
                            st.markdown(f"<div class='green-alert'>{alert_msg}</div><br>", unsafe_allow_html=True)
                        else:
                            status = "UNVERIFIED (Danger)"
                            alert_msg = f"🚨 **RED ALERT:** सावधान! यह पेमेंट {selected_retailer} के पक्के नंबर से **नहीं** आया है! (Authorized: {auth_upi} | Received From: {sender_detail}). कृपया इसकी जांच करें!"
                            st.markdown(f"<div class='red-alert'>{alert_msg}</div><br>", unsafe_allow_html=True)
                    else:
                        status = "Cash (Safe)"
                        st.success("✅ Cash Payment Recorded.")

                    # Save the transaction
                    new_payment = {
                        "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": selected_retailer,
                        "Amount": amount,
                        "Mode": pay_mode,
                        "SenderUPI_Mobile": sender_detail if pay_mode != "Cash" else "Hand Cash",
                        "Status": status,
                        "Reference": purpose
                    }
                    st.session_state.payment_ledger = pd.concat([st.session_state.payment_ledger, pd.DataFrame([new_payment])], ignore_index=True)
                    st.success("💾 Payment Entry Saved to Ledger.")

# ==========================================
# TAB 2: TRANSACTION LEDGER (FIXED ERROR HERE)
# ==========================================
with tab2:
    st.markdown("### 📋 Transaction History")
    if st.session_state.payment_ledger.empty:
        st.info("अभी तक कोई ट्रांज़ैक्शन नहीं हुआ है।")
    else:
        # Highlight risky transactions
        def highlight_danger(val):
            color = '#fef2f2' if 'UNVERIFIED' in str(val) else ''
            return f'background-color: {color}'

        # 🟢 CRASH-PROOF STYLING (Handles both old and new Pandas versions)
        try:
            styled_df = st.session_state.payment_ledger.style.map(highlight_danger, subset=['Status'])
        except AttributeError:
            styled_df = st.session_state.payment_ledger.style.applymap(highlight_danger, subset=['Status'])

        st.dataframe(styled_df, use_container_width=True)
        
        csv = st.session_state.payment_ledger.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Ledger (Excel)", data=csv, file_name=f"Payment_Ledger_{datetime.now().strftime('%d-%m-%Y')}.csv", mime="text/csv")

# ==========================================
# TAB 3: MANAGE AUTHORIZED RETAILERS
# ==========================================
with tab3:
    st.markdown("### 🛡️ Authorized Retailer Registry")
    st.info("सिर्फ उन्ही रिटेलर्स और उनके UPI/नंबर को यहाँ डालें जिन पर आपको भरोसा है।")
    
    with st.form("add_retailer"):
        c1, c2, c3 = st.columns(3)
        new_ret_name = c1.text_input("Retailer Name*")
        new_ret_mob = c2.text_input("Registered Mobile Number*")
        new_ret_upi = c3.text_input("Authorized UPI ID*")
        
        if st.form_submit_button("➕ Add Authorized Retailer"):
            if new_ret_name and new_ret_mob and new_ret_upi:
                new_ret = {"RetailerName": new_ret_name.upper(), "Mobile": new_ret_mob, "Auth_UPI": new_ret_upi.lower()}
                st.session_state.auth_retailers = pd.concat([st.session_state.auth_retailers, pd.DataFrame([new_ret])], ignore_index=True)
                st.success(f"✅ {new_ret_name} added to safe list!")
                st.rerun()
            else:
                st.error("❌ सभी फील्ड भरना जरूरी है।")
                
    st.markdown("---")
    st.markdown("#### Your Safe List")
    st.dataframe(st.session_state.auth_retailers, use_container_width=True)

# ==========================================
# TAB 4: UPLOAD EXCEL (BULK ADD)
# ==========================================
with tab4:
    st.markdown("### 📂 Upload Retailer Master List")
    st.info("आप चाहें तो एक साथ अपनी Excel फाइल से सारे 'Authorized Retailers' की लिस्ट अपलोड कर सकते हैं।")
    st.caption("Excel में ये कॉलम होने चाहिए: 'RetailerName', 'Mobile', 'Auth_UPI'")
    
    uploaded_file = st.file_uploader("📥 Upload Excel/CSV", type=["xlsx", "xls", "csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.session_state.auth_retailers = pd.concat([st.session_state.auth_retailers, df], ignore_index=True)
            st.success("✅ Master List Loaded Successfully!")
        except Exception as e: st.error(f"Error: {e}")
