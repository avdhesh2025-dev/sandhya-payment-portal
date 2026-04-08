import streamlit as st
import requests

# App Title
st.set_page_config(page_title="Sandhya Enterprises Portal", layout="wide")

# ==========================================
# 🛑 APPS SCRIPT URL YAHAN DALEIN 🛑
# ==========================================
# Apne Google Apps Script ka 'Web App URL' yahan paste karein
WEB_APP_URL = "https://script.google.com/macros/s/AAPKA_URL_YAHAN_AAYEGA/exec"

# ==========================================
# SIDEBAR MENU
# ==========================================
st.sidebar.title("📋 Main Menu")
menu_options = [
    "Live stock", 
    "Today collection", 
    "Add Retailer", 
    "Stock /payment Entry", 
    "Ledger report", 
    "Dues list", 
    "Urgent recovery"
]
choice = st.sidebar.radio("Option Select Karein:", menu_options)

# ==========================================
# PAGES LOGIC
# ==========================================

if choice == "Stock /payment Entry":
    st.title("📝 Stock / Payment Entry")
    
    # 'st.form' use karne se st.rerun() wali warning nahi aayegi
    with st.form("payment_form", clear_on_submit=True):
        st.write("Nayi entry details bharein:")
        
        # Aap in inputs ko apni zaroorat ke hisaab se badal sakte hain
        date = st.date_input("Date")
        name = st.text_input("Name / Retailer Name")
        amount = st.number_input("Amount", min_value=0)
        status = st.selectbox("Status", ["Success", "Pending", "Credit"])
        
        # Submit Button
        submit_btn = st.form_submit_button("Submit Data 🚀")
        
        if submit_btn:
            if name.strip() == "":
                st.warning("⚠️ Kripya naam zaroor bharein!")
            elif WEB_APP_URL == "https://script.google.com/macros/s/AAPKA_URL_YAHAN_AAYEGA/exec":
                st.error("⚠️ Pura code chalane se pehle upar WEB_APP_URL me apna Apps Script ka link dalein!")
            else:
                try:
                    # Data jo Google Sheet (Apps Script) ko bheja jayega
                    data_to_send = {
                        "date": str(date),
                        "name": name,
                        "amount": amount,
                        "status": status
                    }
                    
                    # Apps Script URL par data bhejna (POST request)
                    response = requests.post(WEB_APP_URL, json=data_to_send)
                    
                    if response.status_code == 200:
                        st.success(f"🎉 Bohot badhiya! {name} ki entry Google Sheet me save ho gayi.")
                        st.balloons()
                    else:
                        st.error("❌ Google Sheet me entry nahi hui. Apps Script URL check karein.")
                        
                except Exception as e:
                    st.error(f"⚠️ Connection Error: {e}")

elif choice == "Live stock":
    st.title("📦 Live Stock")
    st.write("Yahan aapka Live Stock ka purana code aayega...")
    # Apna purana Live Stock ka code yahan paste karein

elif choice == "Today collection":
    st.title("💰 Today Collection")
    st.write("Yahan aapka Today Collection ka purana code aayega...")
    # Apna purana Today Collection ka code yahan paste karein

elif choice == "Add Retailer":
    st.title("🏪 Add Retailer")
    st.write("Yahan Retailer add karne ka purana code aayega...")
    # Apna purana Add Retailer ka code yahan paste karein

elif choice == "Ledger report":
    st.title("📊 Ledger Report")
    st.write("Yahan Ledger Report ka purana code aayega...")
    # Apna purana Ledger Report ka code yahan paste karein

elif choice == "Dues list":
    st.title("📋 Dues List")
    st.write("Yahan Dues List ka purana code aayega...")
    # Apna purana Dues List ka code yahan paste karein

elif choice == "Urgent recovery":
    st.title("🚨 Urgent Recovery")
    st.write("Yahan Urgent Recovery ka purana code aayega...")
    # Apna purana Urgent Recovery ka code yahan paste karein
