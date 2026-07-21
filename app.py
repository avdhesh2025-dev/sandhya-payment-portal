import streamlit as st
import pandas as pd
from utils import hash_password, ADMIN_HASH, load_data_from_sheet
import views

# 1. Page Config (A4 Size / Responsive Layout)
st.set_page_config(page_title="Sandhya ERP - Digital Committee", layout="centered", page_icon="🏢")

# 2. Custom CSS
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #ffffff;
        color: #1f2937;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        border-bottom: 6px solid #d1d5db;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        font-weight: bold;
        font-size: 15px;
        height: 60px;
        transition: all 0.1s ease-in-out;
    }
    div.stButton > button:active {
        border-bottom: 2px solid #d1d5db;
        transform: translateY(4px);
    }
    .main {
        max-width: 900px;
        margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Session State Initialization (Crash-Proof Setup)
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

if 'members_db' not in st.session_state:
    st.session_state.members_db = []
if 'payment_status' not in st.session_state:
    st.session_state.payment_status = {}
if 'ledger_transactions' not in st.session_state:
    st.session_state.ledger_transactions = []
if 'current_receiver' not in st.session_state:
    st.session_state.current_receiver = "कोई नहीं (नया)"

# ========================================
# SECURE LOGIN SYSTEM (Role Based)
# ========================================
if not st.session_state.auth_status:
    st.title("🏢 Sandhya Enterprises ERP")
    st.subheader("Secure Access Portal")
    
    with st.form("login_form"):
        role_select = st.selectbox("लॉगिन रोल (Role):", ["Admin", "Staff", "Member"])
        username = st.text_input("यूज़रनेम (Admin के लिए: admin)")
        password = st.text_input("पासवर्ड (Admin के लिए: 9557)", type="password")
        login_btn = st.form_submit_button("लॉगिन करें", use_container_width=True)
        
        if login_btn:
            if role_select == "Admin" and username == "admin" and hash_password(password) == ADMIN_HASH:
                st.session_state.auth_status = True
                st.session_state.role = "Admin"
                st.session_state.user_name = "Avdhesh Kumar"
                st.success("✅ एडमिन लॉगिन सफल! ऐप लोड हो रहा है...")
                st.rerun()
            elif role_select == "Staff" and password == "staff123":
                st.session_state.auth_status = True
                st.session_state.role = "Staff"
                st.session_state.user_name = username
                st.success("✅ स्टाफ लॉगिन सफल!")
                st.rerun()
            else:
                st.error("❌ गलत यूज़रनेम या पासवर्ड! कृपया दोबारा प्रयास करें।")
    st.stop() 

# ========================================
# MAIN ERP APP (Post-Login)
# ========================================

# --- SIDEBAR SETTINGS ---
st.sidebar.title("🏢 Sandhya Enterprises")
# Safely getting user_name and role using .get() to prevent any future AttributeError
current_user = st.session_state.get('user_name', 'Unknown')
current_role = st.session_state.get('role', 'Guest')
st.sidebar.success(f"👤 Logged in: {current_user} ({current_role})")

if st.sidebar.button("🔄 सिस्टम रिफ्रेश करें", use_container_width=True):
    st.rerun()

if st.sidebar.button("🚪 सुरक्षित लॉग आउट", use_container_width=True):
    st.session_state.auth_status = False
    st.session_state.role = None
    st.session_state.user_name = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📌 कमिटी सेटिंग्स")
active_com = st.sidebar.selectbox("एक्टिव कमिटी:", ["₹2,000 (10 Months)", "₹5,000 (10 Months)", "₹10,000 (10 Months)"])
st.sidebar.info(f"📍 Location: Meghpatti, Samastipur\n📞 Support: Admin")

# --- HEADER ---
st.title("💸 Digital Committee & ERP Manager")

# --- MENUS ---
c1, c2, c3 = st.columns(3)
if c1.button("📊 डैशबोर्ड & चार्ट्स", use_container_width=True): st.session_state.page = "Dashboard"
if c2.button("👤 मेंबर मैनेजमेंट", use_container_width=True): st.session_state.page = "Add_Member"
if c3.button("📒 स्मार्ट लेज़र", use_container_width=True): st.session_state.page = "Ledger"

c4, c5, c6 = st.columns(3)
if c4.button("💰 कलेक्शन & लोन", use_container_width=True): st.session_state.page = "Collection"
if c5.button("⚠️ फाइन & पेनल्टी", use_container_width=True): st.session_state.page = "Penalty"
if c6.button("📥 रिपोर्ट्स & बैकअप", use_container_width=True): st.session_state.page = "Report"

st.divider()

# --- DYNAMIC PAGE ROUTING ---
if st.session_state.page == "Dashboard":
    views.render_dashboard()

elif st.session_state.page == "Add_Member":
    if st.session_state.get('role') in ["Admin", "Staff"]:
        views.render_add_member()
    else:
        st.error("🚫 Access Denied: केवल Admin और Staff ही नए मेंबर जोड़ सकते हैं।")

elif st.session_state.page == "Ledger":
    views.render_ledger()

elif st.session_state.page == "Collection":
    st.header("💰 कलेक्शन, लोन ट्रांसफर & QR")
    st.info("यह मॉड्यूल लेज़र और डैशबोर्ड के साथ ऑटोमैटिक जुड़ा है। लोन और कलेक्शन की एंट्री लेज़र पेज से 'मैनुअल ट्रांज़ैक्शन' के ज़रिए भी की जा सकती है।")

elif st.session_state.page == "Penalty":
    st.header("⚠️ लेट फाइन मैनेजर")
    st.info("पेनल्टी जोड़ने के लिए लेज़र सेक्शन का उपयोग करें जहाँ ऑटोमैटिक फाइन कैलकुलेट होकर रनिंग बैलेंस में जुड़ जाता है।")

elif st.session_state.page == "Report":
    if st.session_state.get('role') == "Admin":
        views.render_reports()
    else:
        st.error("🚫 Access Denied: रिपोर्ट्स डाउनलोड करने का अधिकार केवल Admin के पास है।")
