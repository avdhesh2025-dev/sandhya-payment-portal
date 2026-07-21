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

# 3. Session State for Navigation & Tracking
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

if 'payment_status' not in st.session_state:
    st.session_state.payment_status = {
        "Member 1": "❌ Pending",
        "Member 2": "❌ Pending",
        "Member 3": "❌ Pending",
        "Member 4": "❌ Pending",
        "Member 5": "❌ Pending",
        "Member 6": "❌ Pending",
        "Member 7": "❌ Pending",
        "Member 8": "❌ Pending",
        "Member 9": "❌ Pending",
        "Member 10": "❌ Pending"
    }

# इस महीने किसको पैसा मिला है उसका रिकॉर्ड (डिफ़ॉल्ट Member 1)
if 'current_receiver' not in st.session_state:
    st.session_state.current_receiver = "Member 1"

st.title("💸 डिजिटल कमिटी मैनेजर")

# 4. Main Menu Display (6 3D Boxes in 2 Rows)
c1, c2, c3 = st.columns(3)
if c1.button("📊 डैशबोर्ड", use_container_width=True): st.session_state.page = "Dashboard"
if c2.button("👤 नया मेंबर", use_container_width=True): st.session_state.page = "Add_Member"
if c3.button("📒 लेज़र", use_container_width=True): st.session_state.page = "Ledger"

c4, c5, c6 = st.columns(3)
if c4.button("💰 ट्रांसफर", use_container_width=True): st.session_state.page = "Collection"
if c5.button("⚠️ लेट फाइन", use_container_width=True): st.session_state.page = "Penalty"
if c6.button("📥 मंथली रिपोर्ट", use_container_width=True): st.session_state.page = "Report"

st.divider()

# ----------------------------------------
# PAGE 1: DASHBOARD (WITH 'PAID TO' COLUMN)
# ----------------------------------------
if st.session_state.page == "Dashboard":
    st.header("📊 कमिटी समरी & पेमेंट ट्रैकर")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("टोटल मेंबर्स", "10 / 10")
    m2.metric("कमिटी बैलेंस", "₹ 0")
    m3.metric("रनिंग बैलेंस", "₹ 20,000")
    m4.metric("इस महीने का रिसीवर", st.session_state.current_receiver)
    
    st.markdown("---")
    st.subheader("🟢 इस महीने किसका पेमेंट आया / किसका बाकी है?")
    st.info("टेबल में आपको यह भी दिखेगा कि इस महीने किस मेंबर को भुगतान (पैसे मिलने वाले हैं) होना है।")
    
    # स्टेटस अपडेट करने का ऑप्शन
    update_member = st.selectbox("स्टेटस बदलने के लिए मेंबर चुनें:", list(st.session_state.payment_status.keys()))
    new_status = st.radio("नया स्टेटस चुनें:", ["✅ Complete", "❌ Pending"], horizontal=True)
    
    if st.button("स्टेटस अपडेट करें"):
        st.session_state.payment_status[update_member] = new_status
        st.success(f"✅ {update_member} का स्टेटस अपडेट होकर '{new_status}' हो गया है!")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # डेटा तैयार करना जिसमें 'भुगतान किसको हुआ' कॉलम भी शामिल है
    table_data = []
    for member, status in st.session_state.payment_status.items():
        # अगर यह वही मेंबर है जिसे इस महीने पैसा मिलना है, तो उसके आगे उसका नाम दिखेगा
        receiver_info = st.session_state.current_receiver if member == st.session_state.current_receiver else "-"
        table_data.append({
            "मेंबर का नाम": member,
            "भुगतान स्टेटस": status,
            "इस महीने भुगतान किसको मिलना है (Receiver)": receiver_info
        })
        
    status_df = pd.DataFrame(table_data)
    st.dataframe(status_df, use_container_width=True)

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
            reference = st.selectbox("रेफरेंस / गारंटर *", ["-- चुनें --", "Member 1", "Member 2", "Admin"])
            
        photo = st.file_uploader("मेंबर की फोटो अपलोड करें *", type=["jpg", "png", "jpeg"])
        
        submit = st.form_submit_button("डेटा सेव करें", use_container_width=True)
        
        if submit:
            if not name or not mobile or not aadhar or not pan or not address or not upi_id or reference == "-- चुनें --" or not photo:
                st.error("⚠️ कृपया सभी अनिवार्य (*) फील्ड भरें और फोटो अपलोड करें!")
            else:
                st.success(f"✅ {name} का प्रोफाइल सफलतापूर्वक बन गया है!")

# ----------------------------------------
# PAGE 3: MEMBER LEDGER
# ----------------------------------------
elif st.session_state.page == "Ledger":
    st.header("📒 व्यक्तिगत मेंबर लेज़र")
    
    selected_member = st.selectbox("हिसाब देखने के लिए मेंबर चुनें:", list(st.session_state.payment_status.keys()))
    
    if selected_member:
        st.markdown("---")
        p_col1, p_col2, p_col3 = st.columns([1, 2, 2])
        
        with p_col1:
            st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=120)
            st.success("🟢 Active")
            
        with p_col2:
            st.write(f"👤 **नाम:** {selected_member}")
            st.write("📱 **मोबाइल:** 9876543210")
            st.write("📍 **पता:** Samastipur, Bihar")
            
        with p_col3:
            st.write("🏛️ **Aadhar:** XXXX-XXXX")
            st.write("💳 **PAN:** ABCDE1234F")
            st.write("📅 **जॉइनिंग:** 01-Jul-2026")
            
        st.markdown("<br>", unsafe_allow_html=True)
        f_col1, f_col2, f_col3 = st.columns(3)
        f_col1.metric("कुल जमा", "₹ 2,000")
        f_col2.metric("कुल प्रॉफिट", "₹ 90")
        f_col3.metric("बैलेंस", "₹ 2,090")
            
        st.divider()
        st.subheader("💳 ट्रांज़ैक्शन हिस्ट्री")
        ledger_data = pd.DataFrame({
            "तारीख": ["01-Jul", "05-Jul"],
            "विवरण": ["मंथली जमा", "प्रॉफिट मिला"],
            "क्रेडिट": ["₹ 2000", "₹ 40"],
            "डेबिट": ["-", "-"],
            "बैलेंस": ["₹ 2000", "₹ 2040"]
        })
        st.dataframe(ledger_data, use_container_width=True)

# ----------------------------------------
# PAGE 4: COLLECTION & TRANSFER WITH QR
# ----------------------------------------
elif st.session_state.page == "Collection":
    st.header("💰 मंथली कलेक्शन और ट्रांसफर")
    
    colA, colB = st.columns(2)
    with colA:
        loan_taker = st.selectbox("इस महीने पैसा किसको मिला?", list(st.session_state.payment_status.keys()))
        receiver_upi = st.text_input("मेंबर की UPI ID", value="7479584179@ybl")
    with colB:
        total_amount = st.number_input("टोटल अमाउंट (₹)", value=20000)
    
    interest_rate = st.number_input("ब्याज (%)", value=2.0)
    base_interest = (total_amount * interest_rate) / 100
    bid_amount = st.number_input("बोली का डिस्काउंट (₹)", value=500.0, step=100.0)
    
    total_deduction = base_interest + bid_amount
    final_amount_to_give = total_amount - total_deduction
    per_member_profit = total_deduction / 10
    
    st.markdown("---")
    qr_col, detail_col = st.columns([1, 2])
    
    with detail_col:
        st.write(f"**कुल काटा गया अमाउंट:** ₹ {total_deduction}")
        st.markdown(f"#### **{loan_taker} को ट्रांसफर होगा:** ₹ {final_amount_to_give}")
        st.write(f"**हर मेंबर को प्रॉफिट बँटेगा:** ₹ {per_member_profit}")
        
    with qr_col:
        if receiver_upi:
            qr_img = generate_qr(receiver_upi, loan_taker, final_amount_to_give)
            st.image(qr_img, width=200, caption="स्कैन करके पेमेंट करें")
            
    if st.button("✅ कंप्लीट ट्रांसफर दर्ज करें", use_container_width=True):
        # सेव कर लें कि इस महीने किसे पैसा मिला है
        st.session_state.current_receiver = loan_taker
        st.success(f"✅ {loan_taker} को इस महीने का मुख्य रिसीवर सेट कर दिया गया है और ₹ {final_amount_to_give} ट्रांसफर की एंट्री हो गई है!")

# ----------------------------------------
# PAGE 5: LATE FINE (PENALTY) WITH QR
# ----------------------------------------
elif st.session_state.page == "Penalty":
    st.header("⚠️ लेट फाइन (Penalty) कैलकुलेटर")
    
    late_member = st.selectbox("लेट पेमेंट करने वाला मेंबर चुनें:", list(st.session_state.payment_status.keys()))
    monthly_due = st.number_input("मंथली जमा राशि (₹)", value=2000)
    days_late = st.number_input("कितने दिन लेट किया?", min_value=1, value=1)
    admin_upi = st.text_input("एडमिन की UPI ID", value="admin@ybl")
    
    fine_amount = 0
    if 1 <= days_late <= 6:
        fine_amount = days_late * 20
    elif days_late >= 7:
        fine_amount = ((monthly_due * 3) / 100) * days_late
        
    profit_per_member = fine_amount / 10
    
    st.markdown("---")
    f_qr_col, f_detail_col = st.columns([1, 2])
    
    with f_detail_col:
        st.markdown(f"#### **कुल फाइन ({late_member}):** ₹ {fine_amount}")
        st.write(f"**हर मेंबर में प्रॉफिट बँटेगा:** ₹ {profit_per_member}")
        
    with f_qr_col:
        if admin_upi and fine_amount > 0:
            qr_img = generate_qr(admin_upi, "Admin", fine_amount)
            st.image(qr_img, width=200, caption="एडमिन को फाइन भेजें")
            
    if st.button("✅ फाइन जमा करें", use_container_width=True):
        st.success("फाइन जमा हो गया!")

# ----------------------------------------
# PAGE 6: MONTHLY REPORT & EXCEL EXPORT
# ----------------------------------------
elif st.session_state.page == "Report":
    st.header("📥 मंथली रिपोर्ट जनरेटर")
    
    report_month = st.selectbox("महीना चुनें", ["July 2026", "August 2026"])
    total_collection = 20000
    loan_receiver = st.session_state.current_receiver
    total_profit_pool = 1000
    per_member_profit = 100.0
    
    st.markdown(f"### 📋 {report_month} का फाइनल हिसाब")
    st.write(f"🔹 **कुल कलेक्शन:** ₹ {total_collection}")
    st.write(f"🔹 **भुगतान किसको हुआ (Receiver):** {loan_receiver}")
    st.success(f"💸 **हर मेंबर का प्रॉफिट:** ₹ {per_member_profit}")
    
    report_data = {
        "विवरण": ["महीना", "टोटल कलेक्शन", "भुगतान किसको हुआ (Receiver)", "हर मेंबर का प्रॉफिट"],
        "डेटा": [report_month, f"₹ {total_collection}", loan_receiver, f"₹ {per_member_profit}"]
    }
    df_report = pd.DataFrame(report_data)
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_report.to_excel(writer, sheet_name="Report", index=False)
    
    st.download_button(
        label="📥 एक्सेल फाइल (Excel) डाउनलोड करें",
        data=buffer,
        file_name=f"Committee_Report_{report_month}.xlsx",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )
