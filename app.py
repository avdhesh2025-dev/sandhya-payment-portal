import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# पेज की सेटिंग
st.set_page_config(page_title="Sandhya Payment Portal", page_icon="💰")

# आपकी गूगल शीट का लिंक
sheet_url = "https://docs.google.com/spreadsheets/d/1K3ZeUuZbpB3FmUQlt2ryri_3su4EkLOqzS7uxUQYd1Y/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📲 संध्या इंटरप्राइजेज - पेमेंट अपडेट")
st.markdown("---")

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
                # 1. डेटा पढ़ना
                df = conn.read(spreadsheet=sheet_url, worksheet="Payments")
                
                # 2. नया डेटा तैयार करना (सब कुछ Text में बदल दिया है)
                new_row = pd.DataFrame([{
                    "Date": str(date),
                    "Retailer": str(retailer).strip(),
                    "Amount": str(amount),
                    "Payment Mode": str(mode),
                    "Transaction Id": str(txn_id).strip(),
                    "Collected By": str(fse)
                }])
                
                # 3. डेटा को जोड़ना
                if not df.empty:
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                else:
                    updated_df = new_row
                
                # 4. डेटा क्लीन करना (सबसे ज़रूरी कदम ताकि 400 Error न आए)
                updated_df = updated_df.astype(str)
                updated_df = updated_df.replace("nan", "")
                updated_df = updated_df.replace("NaN", "")
                updated_df = updated_df.replace("None", "")
                
                # 5. वापस गूगल शीट में अपडेट करना
                conn.update(spreadsheet=sheet_url, worksheet="Payments", data=updated_df)
                
                st.success(f"✅ {retailer} का ₹{amount} का पेमेंट सेव हो गया है!")
                st.balloons()
                
            except Exception as e:
                st.error(f"एरर 400: डेटा सेव नहीं हुआ। इसका मतलब गूगल हमें बिना 'Service Account' के एंट्री नहीं करने दे रहा है।")
                st.info("टेक्निकल एरर कोड: " + str(e))
        else:
            st.warning("कृपया रिटेलर का नाम और सही राशि भरें।")

st.markdown("---")
st.caption("Developed for Sandhya Enterprises")
