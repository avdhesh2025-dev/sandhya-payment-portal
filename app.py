import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sandhya Payment Portal", page_icon="💰")

# Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📲 संध्या इंटरप्राइजेज - पेमेंट अपडेट")

with st.form("payment_form", clear_on_submit=True):
    date = st.date_input("तारीख (Date)", datetime.now())
    retailer = st.text_input("रिटेलर का नाम (Retailer)")
    amount = st.number_input("राशि (Amount)", min_value=0)
    mode = st.selectbox("पेमेंट मोड", ["Online/UPI", "Cash", "Bank Transfer"])
    txn_id = st.text_input("Transaction Id (यदि हो)")
    fse = st.selectbox("Collected By", ["Ravindra Sharma", "Lal Babu Das", "Self"])
    
    submit = st.form_submit_button("डेटा सेव करें")

    if submit:
        if retailer and amount > 0:
            # शीट का डेटा पढ़ना
            df = conn.read(worksheet="Sandhya Enterprises Payments")
            # नया डेटा तैयार करना
            new_row = pd.DataFrame([{
                "Date": str(date),
                "Retailer": retailer,
                "Amount": amount,
                "Payment Mode": mode,
                "Transaction Id": txn_id,
                "Collected By": fse
            }])
            # डेटा जोड़ना और अपडेट करना
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sandhya Enterprises Payments", data=updated_df)
            st.success(f"✅ {retailer} का पेमेंट सेव हो गया!")
        else:
            st.warning("नाम और राशि भरना जरूरी है।")
