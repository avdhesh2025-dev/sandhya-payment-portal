import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO

# 1. Page Config (A4 Size / Centered Layout)
st.set_page_config(page_title="डिजिटल कमिटी", layout="centered")

# 2. Custom CSS for 3D Buttons & Layout
st.markdown("""
    <style>
    /* 3D Button Style */
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
    /* Hide Sidebar completely */
    [data-testid="collapsedControl"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- QR Code Generator Function ---
def generate_qr(upi_id, name, amount):
    upi_url = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf

# 3. Session State for Navigation
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

st.title("💸 डिजिटल कमिटी मैनेजर")

# 4. Main Menu Display (5 3D Boxes)
col1, col2, col3, col4, col5 = st.columns(5)
if col1.button("📊 डैशबोर्ड", use_container_width=True): st.session_state.page = "Dashboard"
if col2.button("👤 नया मेंबर", use_container_width=True): st.session_state.page = "Add_Member"
if col3.button("📒 लेज़र", use_container_width=True): st.session_state.page = "Ledger"
if col4.button("💰 ट्रांसफर", use_container_width=True): st.session_state.page = "Collection"
if col5.button("⚠️ लेट फाइन", use_container_width=True): st.session_state.page = "Penalty"

st.divider()

# ----------------------------------------
# PAGE 1: DASHBOARD
# ----------------------------------------
if st.session_state.page == "Dashboard":
    st.header("📊 कमिटी समरी (Dashboard)")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("टोटल मेंबर्स", "10 / 10")
    m2.metric("कमिटी के पास बैलेंस", "₹ 0")
    m3.metric("टोटल रनिंग बैलेंस", "₹ 20,000")
    m4.metric("वर्तमान लोन धारक", "अवधेश (Jul)")
    
    st.subheader("इस महीने का पेमेंट स्टेटस")
    status_data = pd.DataFrame({
        "मेंबर का नाम": ["Member 1", "Member 2", "Member 3", "Member 4"],
        "जमा राशि": ["₹2000", "₹2000", "₹0", "₹0"],
        "स्टेटस": ["✅ Complete", "✅ Complete", "❌ Pending", "❌ Pending"]
    })
    st.dataframe(status_data, use_container_width=True)

# ----------------------------------------
# PAGE 2: ADD NEW MEMBER
# ----------------------------------------
elif st.session_state.page == "Add_Member":
    st.header("👤 नया मेंबर रजिस्ट्रेशन")
    st.info("नोट: नीचे दिए गए सभी फील्ड भरना अनिवार्य (Mandatory) है।")
    
    with st.form("new_member_form"):
        colA, colB = st.columns(2)
        with colA:
            name = st.text_input("मेंबर का पूरा नाम *")
            mobile = st.text_input("मोबाइल / WhatsApp नंबर *")
            aadhar = st.text_input("Aadhar Number *")
            upi_id = st.text_input("UPI ID (पैसे रिसीव करने के लिए) *")
            
        with colB:
            pan = st.text_input("PAN Card Number *")
            address = st.text_input("पूरा पता *")
            reference = st.selectbox("रेफरेंस / गारंटर (किसके थ्रू आए हैं) *", ["-- चुनें --", "Member 1", "Member 2", "Admin"])
            
        photo = st.file_uploader("मेंबर की फोटो अपलोड करें *", type=["jpg", "png", "jpeg"])
        
        submit = st.form_submit_button("डेटा सेव करें", use_container_width=True)
        
        if submit:
            if not name or not mobile or not aadhar or not pan or not address or not upi_id or reference == "-- चुनें --" or not photo:
                st.error("⚠️ कृपया सभी अनिवार्य (*) फील्ड भरें और फोटो अपलोड करें!")
            else:
                st.success(f"✅ {name} का प्रोफाइल सफलतापूर्वक बन गया है!")

# ----------------------------------------
# PAGE 3: MEMBER LEDGER (PROFESSIONAL PROFILE)
# ----------------------------------------
elif st.session_state.page == "Ledger":
    st.header("📒 व्यक्तिगत मेंबर लेज़र")
    
    selected_member = st.selectbox("हिसाब देखने के लिए मेंबर चुनें:", ["Member 1", "Member 2", "Member 3"])
    
    if selected_member:
        st.markdown("---")
        p_col1, p_col2, p_col3 = st.columns([1, 2, 2])
        
        with p_col1:
            st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=120)
            st.success("🟢 Active Member")
            
        with p_col2:
            st.write(f"👤 **नाम:** {selected_member}")
            st.write("📱 **मोबाइल:** 9876543210")
            st.write("📍 **पता:** Meghpatti, Samastipur, Bihar")
            
        with p_col3:
            st.write("🏛️ **Aadhar:** XXXX-XXXX-XXXX")
            st.write("💳 **PAN:** ABCDE1234F")
            st.write("📅 **जॉइनिंग Date:** 01-Jul-2026")
            st.write("🤝 **गारंटर:** Admin")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("##### 📊 वित्तीय सारांश (Financial Summary)")
        f_col1, f_col2, f_col3 = st.columns(3)
        f_col1.metric("कुल जमा (Total Deposit)", "₹ 2,000")
        f_col2.metric("कुल प्रॉफिट (Profit Earned)", "₹ 90")
        f_col3.metric("वर्तमान बैलेंस (Current Balance)", "₹ 2,090")
            
        st.divider()
        
        st.subheader("💳 ट्रांज़ैक्शन हिस्ट्री")
        ledger_data = pd.DataFrame({
            "तारीख": ["01-Jul", "05-Jul", "05-Jul"],
            "विवरण": ["मंथली जमा", "लोन लिया", "प्रॉफिट मिला"],
            "क्रेडिट (आया)": ["₹ 2000", "₹ 20000", "₹ 40"],
            "डेबिट (गया)": ["-", "-", "-"],
            "बैलेंस": ["₹ 2000", "₹ -18000", "₹ -17960"]
        })
        st.dataframe(ledger_data, use_container_width=True)

# ----------------------------------------
# PAGE 4: COLLECTION & TRANSFER WITH QR
# ----------------------------------------
elif st.session_state.page == "Collection":
    st.header("💰 मंथली कलेक्शन और ट्रांसफर")
    st.info("यहाँ अमाउंट कैलकुलेट करें। नीचे दिए गए QR कोड से सभी मेंबर्स सीधा पैसा भेज सकते हैं।")
    
    colA, colB = st.columns(2)
    with colA:
        loan_taker = st.selectbox("इस महीने पैसा किसको मिला?", ["Member 1", "Member 2", "Member 3"])
        receiver_upi = st.text_input("मेंबर की UPI ID (पैसे रिसीव करने के लिए)", value="7479584179@ybl")
    with colB:
        total_amount = st.number_input("टोटल अमाउंट (₹)", value=20000)
    
    interest_rate = st.number_input("ब्याज (%)", value=2.0)
    base_interest = (total_amount * interest_rate) / 100
    
    bid_amount = st.number_input("बोली का अमाउंट (अगर किसी ने बोली नहीं लगाई तो 0 रहने दें - ₹)", value=500.0, step=100.0)
    
    total_deduction = base_interest + bid_amount
    final_amount_to_give = total_amount - total_deduction
    
    total_members = 10 
    per_member_profit = total_deduction / total_members
    
    st.markdown("---")
    
    # Show QR and Details side-by-side
    qr_col, detail_col = st.columns([1, 2])
    
    with detail_col:
        st.write(f"**फिक्स ब्याज ({interest_rate}%):** ₹ {base_interest}")
        st.write(f"**बोली का डिस्काउंट:** ₹ {bid_amount}")
        st.write(f"**कुल काटा गया अमाउंट:** ₹ {total_deduction}")
        st.markdown(f"#### **{loan_taker} को ट्रांसफर होगा:** ₹ {final_amount_to_give}")
        st.write(f"**हर मेंबर को प्रॉफिट बँटेगा:** ₹ {per_member_profit}")
        
    with qr_col:
        if receiver_upi:
            qr_img = generate_qr(receiver_upi, loan_taker, final_amount_to_give)
            st.image(qr_img, width=200, caption=f" स्कैन करके पेमेंट करें")
        else:
            st.warning("QR के लिए UPI ID डालें")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ कंप्लीट ट्रांसफर दर्ज करें", use_container_width=True):
        st.success(f"{loan_taker} को ₹ {final_amount_to_give} ट्रांसफर की एंट्री हो गई है! सभी मेंबर्स के लेज़र में ₹ {per_member_profit} प्रॉफिट क्रेडिट कर दिया गया।")

# ----------------------------------------
# PAGE 5: LATE FINE (PENALTY) WITH QR
# ----------------------------------------
elif st.session_state.page == "Penalty":
    st.header("⚠️ लेट फाइन (Penalty) कैलकुलेटर")
    st.error("लेट फाइन सीधा एडमिन (Admin) के खाते में जमा होगा, जिसे बाद में सभी मेंबर्स में बाँट दिया जाएगा।")
    
    late_member = st.selectbox("लेट पेमेंट करने वाला मेंबर चुनें:", ["Member 1", "Member 2", "Member 3"])
    monthly_due = st.number_input("मंथली जमा राशि (₹)", value=2000)
    days_late = st.number_input("कितने दिन लेट किया?", min_value=1, value=1)
    admin_upi = st.text_input("एडमिन की UPI ID (फाइन रिसीव करने के लिए)", value="admin@ybl")
    
    fine_amount = 0
    calculation_rule = ""
    
    if 1 <= days_late <= 6:
        fine_amount = days_late * 20
        calculation_rule = f"1 से 6 दिन वाला नियम: ({days_late} दिन x ₹20)"
    elif days_late >= 7:
        daily_3_percent = (monthly_due * 3) / 100
        fine_amount = daily_3_percent * days_late
        calculation_rule = f"7+ दिन वाला नियम: (रोज़ाना 3% यानी ₹{daily_3_percent} x {days_late} दिन)"
        
    total_members = 10
    profit_per_member = fine_amount / total_members
    
    st.markdown("---")
    
    # Show QR and Details side-by-side
    f_qr_col, f_detail_col = st.columns([1, 2])
    
    with f_detail_col:
        st.write(f"**कैलकुलेशन का नियम:** {calculation_rule}")
        st.markdown(f"#### **कुल फाइन ({late_member}):** ₹ {fine_amount}")
        st.write(f"**हर मेंबर में प्रॉफिट बँटेगा:** ₹ {profit_per_member}")
        
    with f_qr_col:
        if admin_upi and fine_amount > 0:
            qr_img = generate_qr(admin_upi, "Admin (Committee)", fine_amount)
            st.image(qr_img, width=200, caption="एडमिन को फाइन भेजने के लिए स्कैन करें")
            
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ फाइन जमा करें", use_container_width=True):
        st.success(f"{late_member} का ₹ {fine_amount} फाइन सफलतापूर्वक जमा हो गया! लेज़र में ₹ {profit_per_member} क्रेडिट कर दिए गए हैं।")
