import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# पेज की सेटिंग
st.set_page_config(page_title="Sandhya Payment Portal", page_icon="💰")

# Google Sheets से सीधा कनेक्शन (बिना Secrets के)
sheet_url = "https://docs.google.com/spreadsheets/d/1K3ZeUuZbpB3FmUQlt2ryri_3su4EkLOqzS7uxUQYd1Y/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📲 संध्या इंटरप्राइजेज - पेमेंट अपडेट")
st.markdown("---")

# फॉर्म बनाना
with st.form("payment_form", clear_on_submit=True):
    st.subheader("पेमेंट की जानकारी भरें")
    
    date = st.date_input("तारीख (Date)", datetime.now())
    retailer = st.text_input("रिटेलर का नाम (Retailer Name)")
    amount = st.number_input("राशि (Amount)", min_value=0)
    mode = st.selectbox("पेमेंट मोड", ["Online/UPI", "Cash", "Bank Transfer"])
    txn_id = st.text_input("Transaction Id (यदि हो)")
    fse = st.selectbox("किसने कलेक्ट किया (Collected By)", ["Ravindra Sharma", "Lal Babu Das", "Self"])
    
    submit = st.form_submit_button("डेटा सुरक्षित करें")

    if submit:
        if retailer and amount > 0:
            try:
                # शीट का डेटा पढ़ना (वर्कशीट का नाम 'Sandhya Enterprises Payments' होना चाहिए)
                df = conn.read(spreadsheet=sheet_url, worksheet="Sandhya Enterprises Payments")
                
                # नया डेटा तैयार करना
                new_row = pd.DataFrame([{
                    "Date": str(date),
                    "Retailer": retailer,
                    "Amount": amount,
                    "Payment Mode": mode,
                    "Transaction Id": txn_id,
                    "Collected By": fse
                }])
                
                # डेटा को जोड़ना
                updated_df = pd.concat([df, new_row], ignore_index=True)
                
                # वापस गूगल शीट में अपडेट करना
                conn.update(spreadsheet=sheet_url, worksheet="Sandhya Enterprises Payments", data=updated_df)
                
                st.success(f"✅ {retailer} का ₹{amount} का पेमेंट सेव हो गया है!")
                st.balloons()
            except Exception as e:
                st.error("Error: कृपया सुनिश्चित करें कि गूगल शीट में नीचे वाले टैब का नाम 'Sandhya Enterprises Payments' ही है।")
        else:
            st.warning("कृपया रिटेलर का नाम और सही राशि भरें।")

st.markdown("---")
st.caption("Developed for Sandhya Enterprises")
