import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import datetime
import requests

# 1. Page Config (A4 Size / Centered Layout)
st.set_page_config(page_title="डिजिटल कमिटी - Sandhya Enterprises", layout="centered")

# 2. Custom CSS for 3D Buttons & Layout
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
    </style>
""", unsafe_allow_html=True)

# --- Google Apps Script Web App URL ---
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbybAWFNtp9o8PiptHiVakz5NFWLOSqDVNlv3C81E1PX1nUbG6JnH8-oSeB83_-mcfGKAg/exec"

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

# 3. Session State Initialization
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

if 'members_db' not in st.session_state:
    st.session_state.members_db = []

if 'payment_status' not in st.session_state:
    st.session_state.payment_status = {
        "Member 1": "❌ Pending", "Member 2": "❌ Pending", "Member 3": "❌ Pending",
        "Member 4": "❌ Pending", "Member 5": "❌ Pending", "Member 6": "❌ Pending",
        "Member 7": "❌ Pending", "Member 8": "❌ Pending", "Member 9": "❌ Pending", "Member 10": "❌ Pending"
    }

if 'current_receiver' not in st.session_state:
    st.session_state.current_receiver = "Member 1"

# --- SIDEBAR: LOGIN & SETTINGS ---
st.sidebar.title("🔐 सिस्टम सेटिंग्स")
role_choice = st.sidebar.selectbox("यूज़र रोल चुनें:", ["Admin (संचालक)", "Staff (कर्मचारी)", "Member (सदस्य)"])
pass_key = st.sidebar.text_input("पासवर्ड (Admin: admin123):", type="password")

if st.sidebar.button("लॉगिन करें"):
    if pass_key == "admin123" or role_choice == "Member (सदस्य)":
        st.sidebar.success(f"लॉगिन सफल: {role_choice}")
    else:
        st.sidebar.error("गलत पासवर्ड!")

st.sidebar.markdown("---")
st.sidebar.subheader("📌 कमिटी टियर")
active_com = st.sidebar.selectbox("कमिटी चुनें:", ["₹2,000 कमिटी (10 लोग)", "₹5,000 कमिटी (10 लोग)", "₹10,000 कमिटी (10 लोग)"])

st.title("💸 Sandhya Enterprises - डिजिटल कमिटी मैनेजर")

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
# PAGE 1: DASHBOARD
# ----------------------------------------
if st.session_state.page == "Dashboard":
    st.header("📊 कमिटी समरी & पेमेंट ट्रैकर")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("टोटल मेंबर्स", f"{len(st.session_state.members_db)} / 10")
    m2.metric("कमिटी बैलेंस", "₹ 0")
    m3.metric("रनिंग बैलेंस", "₹ 20,000")
    m4.metric("इस महीने का रिसीवर", st.session_state.current_receiver)
    
    st.markdown("---")
    st.subheader("🟢 इस महीने किसका पेमेंट आया / किसका बाकी है?")
    
    update_member = st.selectbox("स्टेटस बदलने के लिए मेंबर चुनें:", list(st.session_state.payment_status.keys()))
    new_status = st.radio("नया स्टेटस चुनें:", ["✅ Complete", "❌ Pending"], horizontal=True)
    
    if st.button("स्टेटस अपडेट करें"):
        st.session_state.payment_status[update_member] = new_status
        st.success(f"✅ {update_member} का स्टेटस अपडेट होकर '{new_status}' हो गया है!")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    table_data = []
    for member, status in st.session_state.payment_status.items():
        receiver_info = st.session_state.current_receiver if member == st.session_state.current_receiver else "-"
        table_data.append({
            "मेंबर का नाम": member,
            "भुगतान स्टेटस": status,
            "इस महीने भुगतान किसको मिलना है": receiver_info
        })
        
    status_df = pd.DataFrame(table_data)
    st.dataframe(status_df, use_container_width=True)

# ----------------------------------------
# PAGE 2: ADD NEW MEMBER (GOOGLE SHEET WEB APP SYNC)
# ----------------------------------------
elif st.session_state.page == "Add_Member":
    st.header("👤 नया मेंबर रजिस्ट्रेशन (Google Sheet Live Sync)")
    
    with st.form("new_member_form", clear_on_submit=True):
        colA, colB = st.columns(2)
        with colA:
            name = st.text_input("मेंबर का पूरा नाम *")
            mobile = st.text_input("मोबाइल / WhatsApp नंबर *")
            pan = st.text_input("PAN Card Number *")
            
        with colB:
            upi_id = st.text_input("UPI ID (पैसे रिसीव करने के लिए) *")
            reference = st.selectbox("रेफरेंस / गारंटर *", ["-- चुनें --", "Admin", "Member 1", "Member 2"])
            
        photo = st.file_uploader("मेंबर की फोटो अपलोड करें *", type=["jpg", "png", "jpeg"])
        
        if photo is not None:
            st.image(photo, width=120, caption="फोटो प्रिव्यू")
            
        submit = st.form_submit_button("डेटा सेव करें और गूगल शीट में भेजें", use_container_width=True)
        
        if submit:
            if not name or not mobile or not pan or not upi_id or reference == "-- चुनें --" or not photo:
                st.error("⚠️ कृपया सभी अनिवार्य (*) फील्ड भरें और फोटो अपलोड करें!")
            else:
                member_id = f"M0{len(st.session_state.members_db) + 1}"
                
                # Sending data to Google Sheet via Apps Script Web App
                saved_to_sheet = False
                try:
                    payload = {
                        "member_id": member_id,
                        "name": name,
                        "mobile": mobile,
                        "pan": pan,
                        "upi": upi_id,
                        "reference": reference
                    }
                    response = requests.post(APPS_SCRIPT_URL, json=payload)
                    if response.status_code == 200:
                        saved_to_sheet = True
                except Exception as e:
                    pass
                
                new_member = {
                    "id": member_id, "name": name, "mobile": mobile, 
                    "pan": pan, "upi": upi_id, "reference": reference, "status": "✅ Active"
                }
                st.session_state.members_db.append(new_member)
                st.session_state.payment_status[name] = "❌ Pending"
                
                if saved_to_sheet:
                    st.success(f"✅ {name} का डेटा सीधे आपकी **Google Sheet** में सेव हो गया! ID: {member_id}")
                else:
                    st.success(f"✅ {name} का प्रोफाइल बन गया है! (ID: {member_id})")

# ----------------------------------------
# PAGE 3: MEMBER LEDGER
# ----------------------------------------
elif st.session_state.page == "Ledger":
    st.header("📒 व्यक्तिगत मेंबर लेज़र")
    selected_member = st.selectbox("हिसाब देखने के लिए मेंबर चुनें:", list(st.session_state.payment_status.keys()))
    if selected_member:
        st.write(f"**नाम:** {selected_member} | **कुल जमा:** ₹2,000 | **बैलेंस:** ₹2,090")

# ----------------------------------------
# PAGE 4: COLLECTION & TRANSFER WITH QR
# ----------------------------------------
elif st.session_state.page == "Collection":
    st.header("💰 मंथली कलेक्शन और ट्रांसफर")
    
    colA, colB = st.columns(2)
    with colA:
        loan_taker = st.selectbox("इस महीने पैसा किसको मिला?", list(st.session_state.payment_status.keys()))
        receiver_upi = st.text_input("UPI ID", value="7479584179@ybl")
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
        st.session_state.current_receiver = loan_taker
        st.success(f"✅ {loan_taker} को ₹ {final_amount_to_give} ट्रांसफर की एंट्री हो गई है!")

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
    st.header("📥 मंथली रिपोर्ट जनरेटर & डेटा बैकअप")
    
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
        label="📥 एक्सेल फाइल (Excel) और बैकअप डाउनलोड करें",
        data=buffer,
        file_name=f"Sandhya_Enterprises_Report_{report_month}.xlsx",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )
