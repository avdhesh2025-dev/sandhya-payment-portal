import streamlit as st
import requests

# App Title & Layout
st.set_page_config(page_title="Sandhya Enterprises Portal", layout="wide")

# ==========================================
# 🛑 APPS SCRIPT URL YAHAN DALEIN 🛑
# ==========================================
WEB_APP_URL = "https://script.google.com/macros/s/AAPKA_URL_YAHAN_AAYEGA/exec"

# ==========================================
# 🎨 3D CARD CSS DESIGN (Jo touch karne par uthta hai)
# ==========================================
st.markdown("""
<style>
/* Sidebar ko puri tarah chupana */
[data-testid="collapsedControl"] {
    display: none;
}

/* Button ko 3D Box jaisa banana */
div.stButton > button {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Niche ki shadow */
    transition: transform 0.3s ease, box-shadow 0.3s ease; /* Smooth effect ke liye */
    width: 100%;
    height: 100px; /* Box ki height */
    font-size: 18px !important;
    font-weight: bold;
    color: #333333;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 🚀 TOUCH/HOVER KARNE PAR UPAR UTHNE KA EFFECT */
div.stButton > button:hover {
    transform: translateY(-8px); /* 8 pixel upar uthega */
    box-shadow: 0px 12px 20px rgba(0, 0, 0, 0.2); /* Shadow gehri hogi */
    color: #0056b3; /* Text color change */
    border: 1px solid #0056b3;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# PAGE NAVIGATION SYSTEM
# ==========================================
# Yaad rakhein ki hum kis page par hain
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# ==========================================
# 🏠 HOME PAGE (3D MENU OPTIONS)
# ==========================================
if st.session_state.current_page == "Home":
    st.title("🏢 Sandhya Enterprises - Main Menu")
    st.write("Kripya niche diye gaye kisi bhi box par click karein:")
    st.write("") # Thoda space
    
    # Grid Layout banaya hai (Row me boxes set karne ke liye)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📦 Live stock"): 
            st.session_state.current_page = "Live stock"
            st.rerun()
        st.write("")
        if st.button("📋 Dues list"): 
            st.session_state.current_page = "Dues list"
            st.rerun()
            
    with col2:
        if st.button("💰 Today collection"): 
            st.session_state.current_page = "Today collection"
            st.rerun()
        st.write("")
        if st.button("📊 Ledger report"): 
            st.session_state.current_page = "Ledger report"
            st.rerun()

    with col3:
        if st.button("🏪 Add Retailer"): 
            st.session_state.current_page = "Add Retailer"
            st.rerun()
        st.write("")
        if st.button("🚨 Urgent recovery"): 
            st.session_state.current_page = "Urgent recovery"
            st.rerun()
            
    # Niche alag se bada button Entry ke liye
    st.write("")
    st.write("")
    col_mid1, col_mid2, col_mid3 = st.columns([1, 2, 1])
    with col_mid2:
        if st.button("📝 Stock / Payment Entry"): 
            st.session_state.current_page = "Stock /payment Entry"
            st.rerun()

# ==========================================
# 🔙 BACK BUTTON (Har page par dikhega)
# ==========================================
if st.session_state.current_page != "Home":
    if st.button("🔙 Back to Main Menu"):
        st.session_state.current_page = "Home"
        st.rerun()
    st.divider()

# ==========================================
# 📝 ENTRY PAGE LOGIC
# ==========================================
if st.session_state.current_page == "Stock /payment Entry":
    st.title("📝 Stock / Payment Entry")
    
    # st.form use kiya hai taaki wo yellow warning na aaye
    with st.form("payment_form", clear_on_submit=True):
        date = st.date_input("Date")
        name = st.text_input("Name / Retailer Name")
        amount = st.number_input("Amount", min_value=0)
        status = st.selectbox("Status", ["Success", "Pending", "Credit"])
        
        submit_btn = st.form_submit_button("Submit Data 🚀")
        
        if submit_btn:
            if name.strip() == "":
                st.warning("⚠️ Kripya naam zaroor bharein!")
            elif "AAPKA_URL_YAHAN_AAYEGA" in WEB_APP_URL:
                st.error("⚠️ Apna Apps Script URL code me dalna na bhoolein!")
            else:
                try:
                    data_to_send = {
                        "date": str(date), "name": name, "amount": amount, "status": status
                    }
                    response = requests.post(WEB_APP_URL, json=data_to_send)
                    
                    if response.status_code == 200:
                        st.success(f"🎉 Bohot badhiya! {name} ki entry Apps Script se Google Sheet me save ho gayi.")
                        st.balloons()
                    else:
                        st.error("❌ Google Sheet me entry nahi hui. URL check karein.")
                except Exception as e:
                    st.error(f"⚠️ Connection Error: {e}")

# ==========================================
# 📦 BAAKI PURANE PAGES
# ==========================================
elif st.session_state.current_page == "Live stock":
    st.title("📦 Live Stock")
    st.write("Yahan aapka Live Stock ka purana code aayega...")

elif st.session_state.current_page == "Today collection":
    st.title("💰 Today Collection")
    st.write("Yahan aapka Today Collection ka purana code aayega...")

elif st.session_state.current_page == "Add Retailer":
    st.title("🏪 Add Retailer")
    st.write("Yahan Retailer add karne ka purana code aayega...")

elif st.session_state.current_page == "Ledger report":
    st.title("📊 Ledger Report")
    st.write("Yahan Ledger Report ka purana code aayega...")

elif st.session_state.current_page == "Dues list":
    st.title("📋 Dues List")
    st.write("Yahan Dues List ka purana code aayega...")

elif st.session_state.current_page == "Urgent recovery":
    st.title("🚨 Urgent Recovery")
    st.write("Yahan Urgent Recovery ka purana code aayega...")
