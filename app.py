import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- STEP 1: Google Sheet Connection Setup ---
# Dhyan rakhein: Apni JSON file ka naam exact 'credentials.json' rakh kar upload karein
JSON_FILE_NAME = "credentials.json" 

try:
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(JSON_FILE_NAME, scopes=scope)
    client = gspread.authorize(creds)
    
    # Sheet connect karein
    sheet = client.open("SANDHYA PAYMENTS DATA").sheet1
    
except FileNotFoundError:
    st.error(f"❌ Error: '{JSON_FILE_NAME}' file nahi mili! Kripya apni JSON file ka naam credentials.json rakh kar upload karein.")
    st.stop()
except Exception as e:
    st.error(f"❌ Connection Error: {e}\n(Check karein ki aapne JSON email ko sheet me Editor banaya hai ya nahi)")
    st.stop()


# --- STEP 2: Streamlit App Design & Logic ---
st.title("📝 Sandhya Enterprises - Data Entry")

# 'with st.form' use karne se warning nahi aayegi aur box submit hone par khali ho jayenge
with st.form("my_data_form", clear_on_submit=True):
    st.subheader("Nayi Entry Karein")
    
    # Yahan aapke inputs hain (Aap chahain toh purane inputs yahan badal sakte hain)
    date = st.date_input("Date")
    name = st.text_input("Name")
    amount = st.number_input("Amount", min_value=0)
    status = st.selectbox("Status", ["Success", "Pending"])
    
    # Submit Button
    submit_button = st.form_submit_button("Submit Data 🚀")
    
    # Submit dabane par kya hoga:
    if submit_button:
        if name.strip() == "":
            st.warning("⚠️ Kripya naam zaroor bharein!")
        else:
            try:
                # Naya data sheet ke liye list format mein taiyar karein
                new_row_data = [str(date), name, amount, status]
                
                # Google sheet mein naya row add karein
                sheet.append_row(new_row_data)
                
                # Success message
                st.success(f"🎉 Bohot badhiya! {name} ki entry Google Sheet mein save ho gayi.")
                st.balloons()
                
            except Exception as e:
                st.error(f"⚠️ Data add karne mein dikkat aayi: {e}")
