import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- STEP 1: Google Sheet Connection (Aapka purana connection waisa hi rahega) ---
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Apni JSON file ka naam yahan dalein
creds = Credentials.from_service_account_file("aapka_json_file.json", scopes=scope)
client = gspread.authorize(creds)

# Sheet connect karein (Make sure JSON email ko Sheet me Editor permission mili ho)
sheet = client.open("SANDHYA PAYMENTS DATA").sheet1 


# --- STEP 2: Streamlit Form (Isse warning nahi aayegi aur UI pyara lagega) ---
st.title("📝 Sandhya Enterprises - Data Entry")

# clear_on_submit=True se submit hone ke baad box apne aap khali ho jayega
with st.form("my_data_form", clear_on_submit=True):
    st.subheader("Nayi Entry Karein")
    
    # Yahan aap apne purane inputs daal sakte hain (Yeh sirf example hai)
    date = st.date_input("Date")
    name = st.text_input("Name")
    amount = st.number_input("Amount", min_value=0)
    status = st.selectbox("Status", ["Success", "Pending"])
    
    # Pyar sa submit button 🚀
    submit_button = st.form_submit_button("Submit Data 🚀")
    
    # Jab koi Submit button dabayega, tab yeh code chalega
    if submit_button:
        if name != "": # Basic check ki naam khali na ho
            try:
                # 1. Jo data sheet me bhejna hai uski list banayein
                new_row_data = [str(date), name, amount, status]
                
                # 2. Google sheet me naya row add karein
                sheet.append_row(new_row_data)
                
                # 3. Success message aur balloons (Pyar wala option)
                st.success(f"🎉 Bohot badhiya! {name} ka data Google Sheet me save ho gaya.")
                st.balloons()
                
            except Exception as e:
                # Agar koi error aayi toh red color me dikhegi
                st.error(f"⚠️ Error aayi hai: {e}")
        else:
            st.warning("⚠️ Kripya naam zaroor bharein!")
