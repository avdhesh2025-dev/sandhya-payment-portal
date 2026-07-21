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
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw1cjdszgSRrSb8PlvupUVQTlea4e7dkvcCdDKJ-o8TssXJLmLRMBTJqBfhGhqcRjU-wg/exec"

# --- Google Sheet से पुराना डेटा लोड करने का फंक्शन ---
@st.cache_data(ttl=2)
def load_data_from_sheet():
    try:
        response = requests.get(APPS_SCRIPT_URL)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        pass
    return []

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

# 3. Session State Initialization & Sheet Sync
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

if 'members_db' not in st.session_state:
    raw_data = load_data_from_sheet()
    st.session_state.members_db = []
    for row in raw_data:
        m_name = row.get('Name') or row.get('name')
        if m_name:
            st.session_state.members_db.append({
                "id": row.get('Member ID') or row.get('member_id', 'M01'),
                "name": m_name,
                "mobile": str(row.get('Mobile') or row.get('mobile', '')),
                "identity_num": "[ID Redacted]",
                "pan": str(row.get('PAN') or row.get('pan', '')),
                "upi": str(row.get('UPI') or row.get('upi', '')),
                "address": str(row.get('Address') or row.get('address', '')),
                "reference": str(row.get('Reference') or row.get('reference', '')),
                "status": "✅ Active",
                "loan_status": "Clear"
            })

if 'payment_status' not in st.session_state:
    st.session_state.payment_status = {}
    for m in st.session_state.members_db:
        st.session_state.payment_status[m['name']] = "❌ Pending"

# लेज़र ट्रांज़ैक्शन डेटा स्टोर करने के लिए
if 'ledger_transactions' not in st.session_state:
    st.session_state.ledger_transactions = []

if 'current_receiver' not in st.session_state:
    st.session_state.current_receiver = "कोई नहीं (नया)"

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
    
    if len(st.session_state.payment_status) > 0:
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
    else:
        st.info("⚠️ अभी कोई भी मेंबर रजिस्टर्ड नहीं है। कृपया 'नया मेंबर' वाले पेज पर जाएं।")

# ----------------------------------------
# PAGE 2: ADD NEW MEMBER
# ----------------------------------------
elif st.session_state.page == "Add_Member":
    st.header("👤 नया मेंबर रजिस्ट्रेशन (Duplicate & Validation Check)")
    
    with st.form("new_member_form", clear_on_submit=True):
        colA, colB = st.columns(2)
        with colA:
            name = st.text_input("मेंबर का पूरा नाम *")
            mobile = st.text_input("मोबाइल / WhatsApp नंबर *")
            identity_num = st.text_input("ID / Aadhar Number * (12 Digits)")
            pan = st.text_input("PAN Card Number *")
            
        with colB:
            upi_id = st.text_input("UPI ID (पैसे रिसीव करने के लिए) *")
            address = st.text_area("पूरा पता (Village, Post, Dist, PIN) *")
            reference = st.selectbox("रेफरेंस / गारंटर *", ["-- चुनें --", "Admin"])
            
        photo = st.file_uploader("मेंबर की फोटो अपलोड करें *", type=["jpg", "png", "jpeg"])
        
        if photo is not None:
            st.image(photo, width=120, caption="फोटो प्रिव्यू")
            
        submit = st.form_submit_button("डेटा सेव करें और गूगल शीट में भेजें", use_container_width=True)
        
        if submit:
            existing_mobiles = [m['mobile'] for m in st.session_state.members_db]
            existing_pans = [m['pan'] for m in st.session_state.members_db]
            
            if not name or not mobile or not identity_num or not pan or not address or not upi_id or reference == "-- चुनें --" or not photo:
                st.error("⚠️ कृपया सभी अनिवार्य (*) फील्ड भरें और फोटो अपलोड करें!")
            elif len(identity_num) != 12 or not identity_num.isdigit():
                st.error("❌ त्रुटि: नंबर ठीक 12 अंकों का होना चाहिए!")
            elif len(pan) != 10:
                st.error("❌ त्रुटि: PAN कार्ड नंबर ठीक 10 अक्षरों का होना चाहिए!")
            elif mobile in existing_mobiles:
                st.error("❌ त्रुटि: यह मोबाइल नंबर पहले से रजिस्टर्ड है!")
            elif pan in existing_pans:
                st.error("❌ त्रुटि: यह PAN नंबर पहले से मौजूद है!")
            else:
                member_id = f"M0{len(st.session_state.members_db) + 1}"
                
                saved_to_sheet = False
                try:
                    payload = {
                        "member_id": member_id,
                        "name": name,
                        "mobile": mobile,
                        "identity": "[ID Redacted]",
                        "pan": pan,
                        "upi": upi_id,
                        "address": address,
                        "reference": reference
                    }
                    response = requests.post(APPS_SCRIPT_URL, json=payload)
                    if response.status_code == 200:
                        saved_to_sheet = True
                except Exception as e:
                    pass
                
                new_member = {
                    "id": member_id, "name": name, "mobile": mobile, 
                    "identity_num": "[ID Redacted]", "pan": pan, "upi": upi_id, 
                    "address": address, "reference": reference, "status": "✅ Active",
                    "loan_status": "Clear"
                }
                st.session_state.members_db.append(new_member)
                st.session_state.payment_status[name] = "❌ Pending"
                
                # ऑटोमैटिक पहला रजिस्ट्रेशन ट्रांज़ैक्शन जोड़ना
                st.session_state.ledger_transactions.append({
                    "name": name,
                    "date": str(datetime.date.today()),
                    desc_text := "खाता खुला / रजिस्ट्रेशन जमा": desc_text,
                    "credit": 2000,
                    "debit": 0,
                    "loan": 0,
                    "commission": 0,
                    "fine": 0,
                    "balance": 2000
                })
                
                if saved_to_sheet:
                    st.success(f"✅ {name} का डेटा सीधे आपकी **Google Sheet** और ऐप में सेव हो गया! ID: {member_id}")
                else:
                    st.success(f"✅ {name} का प्रोफाइल बन गया है! (ID: {member_id})")

# ----------------------------------------
# PAGE 3: MEMBER LEDGER (FULL TRANSACTION COLUMNS)
# ----------------------------------------
elif st.session_state.page == "Ledger":
    st.header("📒 व्यक्तिगत मेंबर लेज़र, लोन, कमीशन & ट्रांज़ैक्शन")
    
    if len(st.session_state.members_db) > 0:
        member_names = [m['name'] for m in st.session_state.members_db]
        selected_member = st.selectbox("हिसाब देखने के लिए मेंबर चुनें:", member_names)
        
        m_details = next((m for m in st.session_state.members_db if m['name'] == selected_member), None)
        
        if m_details:
            st.markdown("---")
            p_col1, p_col2, p_col3 = st.columns([1, 2, 2])
            
            with p_col1:
                st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=110)
                st.success(m_details['status'])
                
            with p_col2:
                st.write(f"👤 **नाम:** {m_details['name']}")
                st.write(f"📱 **मोबाइल:** {m_details['mobile']}")
                st.write(f"📍 **पता:** {m_details['address']}")
                
            with p_col3:
                st.write(f"🏛️ **ID/Number:** [ID Redacted]")
                st.write(f"💳 **PAN:** {m_details['pan']}")
                st.write(f"🏦 **UPI:** {m_details['upi']}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # इस मेंबर के कुल ट्रांज़ैक्शन फिल्टर करना
            member_txns = [t for t in st.session_state.ledger_transactions if t['name'] == selected_member]
            
            total_credit = sum([t['credit'] for t in member_txns])
            total_debit = sum([t['debit'] for t in member_txns])
            total_loan = sum([t['loan'] for t in member_txns])
            total_comm = sum([t['commission'] for t in member_txns])
            total_fine = sum([t['fine'] for t in member_txns])
            net_balance = total_credit - total_debit
            
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            f_col1.metric("कुल जमा (Credit)", f"₹ {total_credit}")
            f_col2.metric("कुल लोन लिया", f"₹ {total_loan}")
            f_col3.metric("कमीशन / प्रॉफिट", f"₹ {total_comm}")
            f_col4.metric("net बैलेंस", f"₹ {net_balance}")
                
            st.divider()
            
            # --- नया ट्रांज़ैक्शन जोड़ने का फॉर्म ---
            with st.expander("➕ इस मेंबर के लिए नया अमाउंट / लेज़र एंट्री जोड़ें"):
                with st.form(f"txn_form_{selected_member}"):
                    t_date = st.date_input("तारीख", datetime.date.today())
                    t_desc = st.text_input("विवरण (जैसे: मंथली किस्त, लोन वितरण, आदि)")
                    
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        c_amount = st.number_input("क्रेडिट / जमा (₹)", min_value=0.0, value=0.0)
                        l_amount = st.number_input("लोन लिया गया (₹)", min_value=0.0, value=0.0)
                        f_amount = st.number_input("फाइन / पेनल्टी (₹)", min_value=0.0, value=0.0)
                    with tc2:
                        d_amount = st.number_input("डेबिट / भुगतान (₹)", min_value=0.0, value=0.0)
                        comm_amount = st.number_input("कमीशन / प्रॉफिट मिला (₹)", min_value=0.0, value=0.0)
                        
                    t_submit = st.form_submit_button("लेज़र में एंट्री सेव करें")
                    
                    if t_submit:
                        new_bal = net_balance + c_amount - d_amount
                        st.session_state.ledger_transactions.append({
                            "name": selected_member,
                            "date": str(t_date),
                            "विवरण": t_desc if t_desc else "लेज़र एंट्री",
                            "credit": c_amount,
                            "debit": d_amount,
                            "loan": l_amount,
                            "commission": comm_amount,
                            "fine": f_amount,
                            "balance": new_bal
                        })
                        st.success("✅ लेज़र में एंट्री सफलतापूर्वक जोड़ दी गई है!")
                        st.rerun()

            st.subheader("💳 विस्तृत ट्रांज़ैक्शन हिस्ट्री")
            if len(member_txns) > 0:
                df_txn = pd.DataFrame(member_txns)
                # कॉलम नाम साफ़ करना
                df_txn = df_txn[['date', 'विवरण', 'credit', 'debit', 'loan', 'commission', 'fine', 'balance']]
                df_txn.columns = ['तारीख', 'विवरण', 'क्रेडिट (₹)', 'डेबिट (₹)', 'लोन (₹)', 'कमीशन (₹)', 'फाइन (₹)', 'बैलेंस (₹)']
                st.dataframe(df_txn, use_container_width=True)
            else:
                st.info("इस मेंबर की अभी कोई अतिरिक्त ट्रांज़ैक्शन एंट्री नहीं है। ऊपर दिए गए बॉक्स से एंट्री जोड़ें।")
    else:
        st.warning("⚠️ लेज़र देखने के लिए पहले 'नया मेंबर' विकल्प से कम से कम एक मेंबर रजिस्टर करें।")

# ----------------------------------------
# PAGE 4: COLLECTION & TRANSFER
# ----------------------------------------
elif st.session_state.page == "Collection":
    st.header("💰 मंथली कलेक्शन और लोन ट्रांसफर")
    
    if len(st.session_state.members_db) > 0:
        colA, colB = st.columns(2)
        with colA:
            loan_taker = st.selectbox("इस महीने पैसा किसको मिला?", [m['name'] for m in st.session_state.members_db])
            receiver_upi = st.text_input("UPI ID", value="7479584179@ybl")
        with colB:
            total_amount = st.number_input("टोटल अमाउंट (₹)", value=20000)
        
        interest_rate = st.number_input("ब्याज (%)", value=2.0)
        base_interest = (total_amount * interest_rate) / 100
        bid_amount = st.number_input("बोली का डिस्काउंट (₹)", value=500.0, step=100.0)
        
        total_deduction = base_interest + bid_amount
        final_amount_to_give = total_amount - total_deduction
        per_member_profit = total_deduction / len(st.session_state.members_db) if len(st.session_state.members_db) > 0 else 0
        
        st.markdown("---")
        qr_col, detail_col = st.columns([1, 2])
        
        with detail_col:
            st.write(f"**कुल काटा गया अमाउंट:** ₹ {total_deduction}")
            st.markdown(f"#### **{loan_taker} को ट्रांसफर होगा:** ₹ {final_amount_to_give}")
            st.write(f"**हर मेंबर को प्रॉफिट बँटेगा:** ₹ {per_member_profit:.2f}")
            
        with qr_col:
            if receiver_upi:
                qr_img = generate_qr(receiver_upi, loan_taker, final_amount_to_give)
                st.image(qr_img, width=200, caption="स्कैन करके पेमेंट करें")
                
        has_active_loan = False
        for m in st.session_state.members_db:
            if m['name'] == loan_taker and m.get('loan_status') == "Active Loan":
                has_active_loan = True
                
        if has_active_loan:
            st.error(f"❌ {loan_taker} को पहले ही लोन मिल चुका है और वह अभी चल रहा है! जब तक पिछला लोन क्लियर नहीं होता, इन्हें दोबारा पैसा नहीं मिल सकता।")
            if st.button("⚡ फोर्स क्लोज करें (₹500 पेनल्टी जमा करके)", use_container_width=True):
                for m in st.session_state.members_db:
                    if m['name'] == loan_taker:
                        m['loan_status'] = "Clear"
                st.success(f"✅ ₹500 पेनल्टी जमा हो गई और {loan_taker} का पिछला लोन फोर्स क्लोज कर दिया गया है!")
        else:
            if st.button("✅ कंप्लीट ट्रांसफर दर्ज करें", use_container_width=True):
                st.session_state.current_receiver = loan_taker
                for m in st.session_state.members_db:
                    if m['name'] == loan_taker:
                        m['loan_status'] = "Active Loan"
                
                # लेज़र में आटोमैटिक लोन और कमीशन की एंट्री जोड़ना
                st.session_state.ledger_transactions.append({
                    "name": loan_taker,
                    "date": str(datetime.date.today()),
                    "विवरण": "लोन वितरण (मंथली कमिटी)",
                    "credit": 0,
                    "debit": final_amount_to_give,
                    "loan": final_amount_to_give,
                    "commission": 0,
                    "fine": 0,
                    "balance": -final_amount_to_give
                })
                
                st.success(f"✅ {loan_taker} को ₹ {final_amount_to_give} ट्रांसफर की एंट्री हो गई है!")
    else:
        st.warning("⚠️ ट्रांसफर करने के लिए पहले 'नया मेंबर' जोड़ें।")

# ----------------------------------------
# PAGE 5: LATE FINE (PENALTY)
# ----------------------------------------
elif st.session_state.page == "Penalty":
    st.header("⚠️ लेट फाइन (Penalty) कैलकुलेटर")
    
    if len(st.session_state.members_db) > 0:
        late_member = st.selectbox("लेट पेमेंट करने वाला मेंबर चुनें:", [m['name'] for m in st.session_state.members_db])
        monthly_due = st.number_input("मंथली जमा राशि (₹)", value=2000)
        days_late = st.number_input("कितने दिन लेट किया?", min_value=1, value=1)
        admin_upi = st.text_input("एडमिन की UPI ID", value="admin@ybl")
        
        fine_amount = 0
        if 1 <= days_late <= 6:
            fine_amount = days_late * 20
        elif days_late >= 7:
            fine_amount = ((monthly_due * 3) / 100) * days_late
            
        profit_per_member = fine_amount / len(st.session_state.members_db)
        
        st.markdown("---")
        f_qr_col, f_detail_col = st.columns([1, 2])
        
        with f_detail_col:
            st.markdown(f"#### **कुल फाइन ({late_member}):** ₹ {fine_amount}")
            st.write(f"**हर मेंबर में प्रॉफिट बँटेगा:** ₹ {profit_per_member:.2f}")
            
        with f_qr_col:
            if admin_upi and fine_amount > 0:
                qr_img = generate_qr(admin_upi, "Admin", fine_amount)
                st.image(qr_img, width=200, caption="एडमिन को फाइन भेजें")
                
        if st.button("✅ फाइन जमा करें", use_container_width=True):
            st.session_state.ledger_transactions.append({
                "name": late_member,
                "date": str(datetime.date.today()),
                "विवरण": "लेट फाइन भुगतान",
                "credit": fine_amount,
                "debit": 0,
                "loan": 0,
                "commission": 0,
                "fine": fine_amount,
                "balance": fine_amount
            })
            st.success("✅ फाइन जमा हो गया और लेज़र में दर्ज कर लिया गया!")
    else:
        st.warning("⚠️ कोई मेंबर उपलब्ध नहीं है।")

# ----------------------------------------
# PAGE 6: MONTHLY REPORT & EXCEL EXPORT
# ----------------------------------------
elif st.session_state.page == "Report":
    st.header("📥 मंथली रिपोर्ट जनरेटर & डेटा बैकअप")
    
    report_month = st.selectbox("महीना चुनें", ["July 2026", "August 2026"])
    total_collection = 20000
    loan_receiver = st.session_state.current_receiver
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
