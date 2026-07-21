import streamlit as st
from utils import hash_password, ADMIN_HASH
import views

# 1. Page Config
st.set_page_config(page_title="Sandhya ERP - Digital Committee", layout="centered", page_icon="🏢")

# 2. Custom CSS 
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #ffffff; color: #1f2937; border: 2px solid #e5e7eb;
        border-radius: 12px; border-bottom: 6px solid #d1d5db;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1); font-weight: bold;
        font-size: 15px; height: 60px; transition: all 0.1s ease-in-out;
    }
    div.stButton > button:active { border-bottom: 2px solid #d1d5db; transform: translateY(4px); }
    </style>
""", unsafe_allow_html=True)

# 3. Session State Initialization
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
if 'members_db' not in st.session_state:
    st.session_state.members_db = []
if 'payment_status' not in st.session_state:
    st.session_state.payment_status = {}
if 'ledger_transactions' not in st.session_state:
    st.session_state.ledger_transactions = []

# ========================================
# SECURE LOGIN SYSTEM
# ========================================
if not st.session_state.auth_status:
    st.title("🏢 Sandhya Enterprises ERP")
    with st.form("login_form"):
        role_select = st.selectbox("लॉगिन रोल:", ["Admin", "Staff", "Member"])
        username = st.text_input("यूज़रनेम (Admin के लिए: admin)")
        password = st.text_input("पासवर्ड (Admin के लिए: 9557)", type="password")
        if st.form_submit_button("लॉगिन करें", use_container_width=True):
            if role_select == "Admin" and username == "admin" and hash_password(password) == ADMIN_HASH:
                st.session_state.auth_status = True
                st.session_state.role = "Admin"
                st.success("✅ लॉगिन सफल!")
                st.rerun()
            else:
                st.error("❌ गलत यूज़रनेम या पासवर्ड!")
    st.stop() 

# ========================================
# MAIN ERP APP
# ========================================
st.sidebar.title("🏢 Sandhya Enterprises")
if st.sidebar.button("🔄 सिस्टम रिफ्रेश करें", use_container_width=True):
    st.rerun()
if st.sidebar.button("🚪 सुरक्षित लॉग आउट", use_container_width=True):
    st.session_state.auth_status = False
    st.rerun()

st.title("💸 Digital Committee & ERP Manager")

c1, c2, c3 = st.columns(3)
if c1.button("📊 डैशबोर्ड & चार्ट्स", use_container_width=True): st.session_state.page = "Dashboard"
if c2.button("👤 मेंबर मैनेजमेंट", use_container_width=True): st.session_state.page = "Add_Member"
if c3.button("📒 लेज़र & कार्ड", use_container_width=True): st.session_state.page = "Ledger"

c4, c5, c6 = st.columns(3)
if c4.button("💰 कलेक्शन & बिडिंग", use_container_width=True): st.session_state.page = "Collection"
if c5.button("⚠️ फाइन & पेनल्टी", use_container_width=True): st.session_state.page = "Penalty"
if c6.button("📥 रिपोर्ट्स & बैकअप", use_container_width=True): st.session_state.page = "Report"

st.divider()

if st.session_state.page == "Dashboard": views.render_dashboard()
elif st.session_state.page == "Add_Member": views.render_add_member()
elif st.session_state.page == "Ledger": views.render_ledger()
elif st.session_state.page == "Collection": views.render_collection()
elif st.session_state.page == "Penalty": views.render_penalty()
elif st.session_state.page == "Report": views.render_reports()
