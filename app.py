import streamlit as st
from datetime import datetime

# पेज की सेटिंग
st.set_page_config(page_title="Sandhya ERP System", page_icon="🏢", layout="wide")

# मेनू को 'बॉक्स' (Box) जैसा बनाने के लिए छोटा सा CSS कोड
st.markdown("""
    <style>
    div.row-widget.stRadio > div { flex-direction: column; }
    div.row-widget.stRadio > div > label {
        background-color: #f0f2f6;
        padding: 12px 15px;
        border-radius: 8px;
        border: 1px solid #d0d2d6;
        margin-bottom: 8px;
        cursor: pointer;
        font-weight: 500;
        transition: 0.3s;
    }
    div.row-widget.stRadio > div > label:hover {
        background-color: #e0e2e6;
        border-color: #b0b2b6;
    }
    </style>
""", unsafe_allow_html=True)

# साइडबार (मेनू)
st.sidebar.title("📲 संध्या इंटरप्राइजेज")
st.sidebar.markdown("---")
menu = st.sidebar.radio("मेनू चुनें:", [
    "📊 डैशबोर्ड (स्टॉक)", 
    "➕ नया रिटेलर जोड़ें", 
    "📦 माल / पेमेंट एंट्री", 
    "📜 लेजर (खाता) देखें"
])

# ---------------------------------------------------------
# 1. डैशबोर्ड
if menu == "📊 डैशबोर्ड (स्टॉक)":
    st.title("📊 लाइव इन्वेंट्री स्टॉक")
    st.info("यहाँ हम आपकी Google Sheet से सिम, फोन और बैलेंस का लाइव स्टॉक दिखाएंगे। (कनेक्शन चालू होना बाकी है)")
    
# ---------------------------------------------------------
# 2. नया रिटेलर जोड़ें
elif menu == "➕ नया रिटेलर जोड़ें":
    st.title("➕ नया रिटेलर जोड़ें")
    with st.form("add_retailer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            r_name = st.text_input("रिटेलर का नाम (Retailer Name)*")
            r_mobile = st.text_input("मोबाइल नंबर (Mobile Number)*", max_chars=10)
        with col2:
            r_prm = st.text_input("PRM ID* (अनिवार्य)")
            r_loc = st.text_input("लोकेशन (Location)")
            
        submit_retailer = st.form_submit_button("नया रिटेलर सेव करें")
        if submit_retailer:
            st.success("✅ डिज़ाइन काम कर रहा है! (डेटाबेस से जुड़ना बाकी है)")

# ---------------------------------------------------------
# 3. माल इशू / पेमेंट एंट्री
elif menu == "📦 माल / पेमेंट एंट्री":
    st.title("📦 स्टॉक आउट / पेमेंट लें")
    with st.form("transaction_form", clear_on_submit=True):
        t_date = st.date_input("तारीख", datetime.now())
        
        col1, col2 = st.columns(2)
        with col1:
            # अब एंट्री PRM ID से होगी
            t_prm = st.text_input("रिटेलर की PRM ID (जिसको माल/बैलेंस देना है)*")
            t_type = st.selectbox("क्या एंट्री करनी है?", ["Jio Phone", "SIM Card", "Etop Recharge", "पेमेंट (Payment Received)"])
            fse = st.selectbox("एंट्री करने वाला (FSE)", ["Ravindra Sharma", "Lal Babu Das", "Self"])
        with col2:
            # Qty और Amount को अलग-अलग कर दिया गया है
            t_qty = st.number_input("मात्रा (Quantity - SIM/Phone के लिए)", min_value=0)
            t_amount = st.number_input("राशि (Amount ₹ - Recharge/Payment के लिए)", min_value=0.0, step=10.0)
            
        submit_txn = st.form_submit_button("एंट्री सेव करें और WhatsApp भेजें")
        if submit_txn:
            st.success("✅ ट्रांजैक्शन फॉर्म काम कर रहा है! (WhatsApp जुड़ना बाकी है)")

# ---------------------------------------------------------
# 4. लेजर (खाता)
elif menu == "📜 लेजर (खाता) देखें":
    st.title("📜 रिटेलर का पूरा खाता")
    # लेजर भी अब PRM ID से सर्च होगा
    search_prm = st.text_input("रिटेलर की PRM ID डालें और Enter दबाएं:")
    search_btn = st.button("हिसाब खोजें")
    
    if search_btn:
        st.info("यहाँ PRM ID के आधार पर रिटेलर का पूरा पुराना हिसाब, बकाया और एडवांस दिखेगा।")
