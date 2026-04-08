import streamlit as st
from datetime import datetime

# पेज की सेटिंग
st.set_page_config(page_title="Sandhya ERP System", page_icon="🏢", layout="wide")

# साइडबार (मेनू)
st.sidebar.title("📲 संध्या इंटरप्राइजेज")
st.sidebar.markdown("---")
menu = st.sidebar.radio("मेनू चुनें:", ["📊 डैशबोर्ड (स्टॉक)", "➕ नया रिटेलर जोड़ें", "📦 माल / पेमेंट एंट्री", "📜 लेजर (खाता) देखें"])

# 1. डैशबोर्ड
if menu == "📊 डैशबोर्ड (स्टॉक)":
    st.title("📊 लाइव इन्वेंट्री स्टॉक")
    st.info("यहाँ हम आपकी Google Sheet से सिम, फोन और बैलेंस का लाइव स्टॉक दिखाएंगे। (कनेक्शन चालू होना बाकी है)")
    
# 2. नया रिटेलर जोड़ें
elif menu == "➕ नया रिटेलर जोड़ें":
    st.title("➕ नया रिटेलर जोड़ें")
    with st.form("add_retailer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            r_name = st.text_input("रिटेलर का नाम (Retailer Name)*")
            r_mobile = st.text_input("मोबाइल नंबर (Mobile Number)*", max_chars=10)
        with col2:
            r_prm = st.text_input("PRM ID (यदि हो)")
            r_loc = st.text_input("लोकेशन (Location)")
            
        submit_retailer = st.form_submit_button("नया रिटेलर सेव करें")
        
        if submit_retailer:
            st.success("✅ डिज़ाइन काम कर रहा है! (डेटाबेस से जुड़ना बाकी है)")

# 3. माल इशू / पेमेंट एंट्री
elif menu == "📦 माल / पेमेंट एंट्री":
    st.title("📦 स्टॉक आउट / पेमेंट लें")
    with st.form("transaction_form", clear_on_submit=True):
        t_date = st.date_input("तारीख", datetime.now())
        
        col1, col2 = st.columns(2)
        with col1:
            t_mobile = st.text_input("रिटेलर का मोबाइल नंबर (जिसको माल देना है)*", max_chars=10)
            t_type = st.selectbox("क्या एंट्री करनी है?", ["Jio Phone", "SIM Card", "Etop Recharge", "पेमेंट (Payment Received)"])
        with col2:
            t_qty = st.number_input("कितना पीस / कितनी राशि (Qty/Amount)*", min_value=0)
            fse = st.selectbox("एंट्री करने वाला (FSE)", ["Ravindra Sharma", "Lal Babu Das", "Self"])
            
        submit_txn = st.form_submit_button("एंट्री सेव करें और WhatsApp भेजें")
        
        if submit_txn:
            st.success("✅ ट्रांजैक्शन फॉर्म काम कर रहा है! (WhatsApp ऑटोमेशन जुड़ना बाकी है)")

# 4. लेजर (खाता)
elif menu == "📜 लेजर (खाता) देखें":
    st.title("📜 रिटेलर का पूरा खाता")
    search_mobile = st.text_input("रिटेलर का मोबाइल नंबर डालें और Enter दबाएं:")
    search_btn = st.button("हिसाब खोजें")
    
    if search_btn:
        st.info("यहाँ रिटेलर का पूरा पुराना हिसाब, बकाया और एडवांस दिखेगा।")
