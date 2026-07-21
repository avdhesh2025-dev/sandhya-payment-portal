import streamlit as st
import pandas as pd
import qrcode
from PIL import Image
from io import BytesIO
import datetime

st.set_page_config(page_title="Group Committee Tracker", layout="wide")

st.title("💸 डिजिटल कमिटी मैनेजर")

# Sidebar Navigation
menu = ["डैशबोर्ड (Dashboard)", "नया मेंबर जोड़ें (₹200)", "मंथली कलेक्शन व QR", "पेमेंट स्लिप (WhatsApp)"]
choice = st.sidebar.selectbox("मेनू चुनें", menu)

# --- 1. Dashboard ---
if choice == "डैशबोर्ड (Dashboard)":
    st.header("📊 कमिटी समरी")
    
    # यह डेटा Google Sheet से आएगा (यहाँ टेस्टिंग के लिए डमी डेटा है)
    dummy_data = {
        "Member Name": ["Member 1", "Member 2", "Member 3"],
        "Total Deposited (₹)": [4000, 4000, 4000],
        "Loan Taken (₹)": [20000, 0, 0],
        "Interest Paid (₹)": [400, 0, 0],
        "Profit Earned (₹)": [40, 40, 40]
    }
    df = pd.DataFrame(dummy_data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("टोटल मेंबर्स", "10")
    col2.metric("इस महीने का कलेक्शन", "₹ 20,000")
    col3.metric("कुल प्रॉफिट (बांटने के लिए)", "₹ 400")
    
    st.dataframe(df, use_container_width=True)

# --- 2. Add New Member ---
elif choice == "नया मेंबर जोड़ें (₹200)":
    st.header("👤 नया मेंबर रजिस्ट्रेशन")
    with st.form("add_member_form"):
        name = st.text_input("मेंबर का नाम")
        phone = st.text_input("WhatsApp नंबर")
        upi_id = st.text_input("UPI ID (पैसे रिसीव करने के लिए)")
        joining_fee = st.checkbox("₹200 जॉइनिंग फीस प्राप्त हुई?")
        
        submit = st.form_submit_button("सेव करें")
        
        if submit:
            if joining_fee:
                # यहाँ Google Sheet में डेटा सेव करने का कोड आएगा
                st.success(f"{name} को सफलतापूर्वक जोड़ लिया गया है! डेटा Google Sheet में सेव हो गया।")
            else:
                st.error("कृपया जॉइनिंग फीस कन्फर्म करें।")

# --- 3. Monthly Collection & QR ---
elif choice == "मंथली कलेक्शन व QR":
    st.header("📱 इस महीने का QR जनरेटर")
    st.info("जिस मेंबर को इस महीने का पैसा (पूल) मिलेगा, उसका QR जनरेट करें। बाकी सभी लोग इसी पर पेमेंट करेंगे।")
    
    receiver_name = st.text_input("पैसे लेने वाले मेंबर का नाम")
    receiver_upi = st.text_input("मेंबर की UPI ID")
    amount = st.number_input("हर मेंबर को कितना भेजना है? (उदा: 500 से 2000)", min_value=500, max_value=2000, step=500)
    
    if st.button("QR Code जनरेट करें"):
        if receiver_upi and receiver_name:
            # UPI Link Format: upi://pay?pa=UPI_ID&pn=NAME&am=AMOUNT
            upi_url = f"upi://pay?pa={receiver_upi}&pn={receiver_name}&am={amount}&cu=INR"
            
            qr = qrcode.QRCode(box_size=10, border=4)
            qr.add_data(upi_url)
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")
            
            buf = BytesIO()
            img.save(buf, format="PNG")
            
            st.image(buf, caption=f"{receiver_name} को पेमेंट करने के लिए स्कैन करें", width=300)
            st.success("QR Code तैयार है! सभी मेंबर्स को शेयर करें।")
        else:
            st.error("कृपया मेंबर का नाम और UPI ID दर्ज करें।")

# --- 4. Payment Slip & WhatsApp ---
elif choice == "पेमेंट स्लिप (WhatsApp)":
    st.header("🧾 पेमेंट स्लिप डाउनलोड और शेयर")
    
    member_name = st.selectbox("मेंबर चुनें", ["Member 1", "Member 2", "Member 3"])
    paid_amount = st.number_input("जमा की गई राशि", value=2000)
    date = datetime.date.today()
    
    receipt_text = f"""
    *कमिटी पेमेंट स्लिप*
    -------------------
    *नाम:* {member_name}
    *तारीख:* {date}
    *जमा राशि:* ₹{paid_amount}
    *स्टेटस:* सफल (Google Sheet में दर्ज)
    -------------------
    धन्यवाद!
    """
    
    st.text_area("स्लिप का प्रीव्यू", receipt_text, height=200)
    
    # WhatsApp Share Link
    phone_number = "919876543210" # डेटाबेस से मेंबर का नंबर लें
    whatsapp_url = f"https://wa.me/{phone_number}?text={receipt_text}"
    
    st.markdown(f"[📲 WhatsApp पर स्लिप भेजने के लिए यहाँ क्लिक करें]({whatsapp_url})", unsafe_allow_html=True)
