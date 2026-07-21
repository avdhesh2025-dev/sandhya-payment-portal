import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import datetime
import requests

# 1. Page Config (A4 Size / Centered Layout)
st.set_page_config(page_title="डिजिटल कमिटी - Sandhya Enterprises", layout="centered")

# 2. Custom CSS for 3D Buttons & Freeze Layout
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
        max-width: 800px;
        margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- Google Apps Script Web App URL ---
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw1cjdszgSRrSb8PlvupUVQTlea4e7dkvcCdDKJ-o8TssXJLmLRMBTJqBfhGhqcRjU-wg/exec"

# --- Google Sheet से डेटा लोड करने का फंक्शन ---
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

# 3. Session State Initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

if 'members_db' not in st.session_state:
    raw_data = load_data_from_sheet()
    st.session_state.members_db = []
    for row in raw_data:
        m_name = row.get('Name') or row.get('name')
        if m_name:
            st.session_state.members_db.append({
                "id": str(row.get('Member ID') or row.get('member_id', 'M01')),
                "name": m_name,
                "mobile": str(row.get('Mobile') or row.get('mobile', '')),
                "identity_num": "[ID Redacted]",
                "pan": str(row.get('PAN') or row.get('pan', '')),
                "upi": str(row.get('UPI') or row.get('upi', '')),
                "address": str(row.get('Address') or row.get('address', '')),
                "reference": str(row.get('Reference') or row.get('reference', '')),
                "status": "✅ Active",
                "loan_status": "Clear",
                "photo": None
            })

if 'payment_status' not in st.session_state:
    st.session_state.payment_status = {}
    for m in st.session_state.members_db:
        st.session_state.payment_status[m['name']] = "❌ Pending"

if 'ledger_transactions' not in st.session_state:
    st.session_state.ledger_transactions = []

if 'current_receiver' not in st.session_state:
    st.session_state.current_receiver = "कोई नहीं (नया)"

# ========================================
# LOGIN PAGE (PASSWORD: 9557)
# ========================================
if not st.session_state.authenticated:
    st.title("🔒 Sandhya Enterprises - सुरक्षित लॉगिन")
    st.write("कृपया आगे बढ़ने के लिए एडमिन पासवर्ड (9557) दर्ज करें।")
    
    with st.form("login_form"):
        entered_pass = st.text_input("एडमिन पासवर्ड:", type="password")
        login_btn = st.form_submit_button("लॉगिन करें", use_container_width=True)
        
        if login_btn:
            if entered_pass == "9557":
                st.session_state.authenticated = True
                st.success("✅ लॉगिन सफल!")
                st.rerun()
            else:
                st.error("❌ गलत पासवर्ड! कृपया सही पासवर्ड (9557) दर्ज करें।")
    st.stop()

# ========================================
# MAIN APP
# ========================================
st.sidebar.title("🔐 सिस्टम सेटिंग्स")
st.sidebar.success("रजिस्टर: एडमिन (Logged In)")

if st.sidebar.button("🔄 ऐप रिफ्रेश करें"):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("🚪 लॉग आउट करें"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📌 कमिटी टियर")
active_com = st.sidebar.selectbox("कमिटी चुनें:", ["₹2,000 कमिटी (10 लोग)", "₹5,000 कमिटी (10 लोग)", "₹10,000 कमिटी (10 लोग)"])

st.title("💸 Sandhya Enterprises - डिजिटल कमिटी मैनेजर")

c1, c2, c3 = st.columns(3)
if c1.button("📊 डैशबोर्ड", use_container_width=True): st.session_state.page = "Dashboard"
if c2.button("👤 नया मेंबर", use_container_width=True): st.session_state.page = "Add_Member"
if c3.button("📒 लेज़र & एडिट", use_container_width=True): st.session_state.page = "Ledger"

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
        st.info("⚠️ अभी कोई भी मेंबर रजिस्टर्ड नहीं है।")

# ----------------------------------------
# PAGE 2: ADD NEW MEMBER
# ----------------------------------------
elif st.session_state.page == "Add_Member":
    st.header("👤 नया मेंबर रजिस्ट्रेशन")
    
    with st.form("new_member_form", clear_on_submit=True):
        colA, colB = st.columns(2)
        with colA:
            name = st.text_input("मेंबर का पूरा नाम *")
            mobile = st.text_input("मोबाइल / WhatsApp नंबर *")
            identity_num = st.text_input("ID / Aadhar Number * (12 Digits)")
            pan = st.text_input("PAN Card Number *")
            
        with colB:
            upi_id = st.text_input("UPI ID *")
            address = st.text_area("पूरा पता (Village, Post, Dist, PIN) *")
            reference = st.selectbox("रेफरेंस / गारंटर *", ["-- चुनें --", "Admin"])
            
        photo = st.file_uploader("मेंबर की फोटो अपलोड करें *", type=["jpg", "png", "jpeg"])
        
        if photo is not None:
            st.image(photo, width=120, caption="फोटो प्रिव्यू")
            
        submit = st.form_submit_button("डेटा सेव करें और गूगल शीट में भेजें", use_container_width=True)
        
        if submit:
            if not name or not mobile or not identity_num or not pan or not address or not upi_id or reference == "-- चुनें --" or not photo:
                st.error("⚠️ कृपया सभी अनिवार्य फील्ड भरें!")
            else:
                member_id = f"M0{len(st.session_state.members_db) + 1}"
                
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
                    requests.post(APPS_SCRIPT_URL, json=payload)
                except:
                    pass
                
                new_member = {
                    "id": member_id, "name": name, "mobile": mobile, 
                    "identity_num": "[ID Redacted]", "pan": pan, "upi": upi_id, 
                    "address": address, "reference": reference, "status": "✅ Active",
                    "loan_status": "Clear", "photo": photo
                }
                st.session_state.members_db.append(new_member)
                st.session_state.payment_status[name] = "❌ Pending"
                st.success(f"✅ {name} सफलतापूर्वक रजिस्टर्ड हो गए! ID: {member_id}")

# ----------------------------------------
# PAGE 3: LEDGER & EDIT ENTRY OPTION
# ----------------------------------------
elif st.session_state.page == "Ledger":
    st.header("📒 व्यक्तिगत मेंबर लेज़र, प्रोफाइल & एडिट विकल्प")
    
    if len(st.session_state.members_db) > 0:
        member_names = [m['name'] for m in st.session_state.members_db]
        selected_member = st.selectbox("हिसाब या एडिट करने के लिए मेंबर चुनें:", member_names)
        
        m_details = next((m for m in st.session_state.members_db if m['name'] == selected_member), None)
        
        if m_details:
            st.markdown("---")
            p_col1, p_col2, p_col3 = st.columns([1, 2, 2])
            
            with p_col1:
                if m_details.get('photo') is not None:
                    st.image(m_details['photo'], width=110, caption="मेंबर फोटो")
                else:
                    st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=110)
                st.success(m_details['status'])
                
            with p_col2:
                st.write(f"👤 **नाम:** {m_details['name']}")
                st.write(f"📱 **मोबाइल:** {m_details['mobile']}")
                st.write(f"📍 **पता:** {m_details['address']}")
                
            with p_col3:
                st.write(f"🏛️ **ID:** [ID Redacted]")
                st.write(f"💳 **PAN:** {m_details['pan']}")
                st.write(f"🏦 **UPI:** {m_details['upi']}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- एडिट एंट्री/प्रोफाइल ऑप्शन (गूगल शीट सिंक के साथ) ---
            with st.expander("✏️ इस मेंबर की जानकारी एडिट (Edit) करें"):
                with st.form(f"edit_form_{selected_member}"):
                    edit_name = st.text_input("नाम बदलें", value=m_details['name'])
                    edit_mob = st.text_input("मोबाइल नंबर", value=m_details['mobile'])
                    edit_pan = st.text_input("PAN कार्ड", value=m_details['pan'])
                    edit_upi = st.text_input("UPI ID", value=m_details['upi'])
                    edit_addr = st.text_area("पूरा पता", value=m_details['address'])
                    
                    edit_submit = st.form_submit_button("गूगल शीट और ऐप में अपडेट करें")
                    if edit_submit:
                        m_details['name'] = edit_name
                        m_details['mobile'] = edit_mob
                        m_details['pan'] = edit_pan
                        m_details['upi'] = edit_upi
                        m_details['address'] = edit_addr
                        
                        # Google Sheet Update Request
                        try:
                            update_payload = {
                                "action": "update",
                                "member_id": m_details['id'],
                                "name": edit_name,
                                "mobile": edit_mob,
                                "pan": edit_pan,
                                "upi": edit_upi,
                                "reference": m_details['reference']
                            }
                            requests.post(APPS_SCRIPT_URL, json=update_payload)
                        except:
                            pass
                            
                        st.success(f"✅ {edit_name} की जानकारी गूगल शीट और ऐप दोनों में अपडेट हो गई है!")
                        st.rerun()

            member_txns = [t for t in st.session_state.ledger_transactions if t['name'] == selected_member]
            
            total_credit = sum([t['credit'] for t in member_txns])
            total_debit = sum([t['debit'] for t in member_txns])
            total_loan = sum([t['loan'] for t in member_txns])
            total_comm = sum([t['commission'] for t in member_txns])
            net_balance = total_credit - total_debit
            
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            f_col1.metric("कुल जमा (Credit)", f"₹ {total_credit}")
            f_col2.metric("कुल लोन लिया", f"₹ {total_loan}")
            f_col3.metric("कमीशन / प्रॉफिट", f"₹ {total_comm}")
            f_col4.metric("net बैलेंस", f"₹ {net_balance}")
                
            st.divider()
            
            with st.expander("➕ नया अमाउंट / लेज़र एंट्री जोड़ें"):
                with st.form(f"txn_form_{selected_member}"):
                    t_date = st.date_input("तारीख", datetime.date.today())
                    t_desc = st.text_input("विवरण (जैसे: मंथली किस्त, लोन वितरण)")
                    
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        c_amount = st.number_input("क्रेडिट / जमा (₹)", min_value=0.0, value=0.0)
                        l_amount = st.number_input("लोन लिया गया (₹)", min_value=0.0, value=0.0)
                        f_amount = st.number_input("फाइन / पेनल्टी (₹)", min_value=0.0, value=0.0)
                    with tc2:
                        d_amount = st.number_input("डेबिट / भुगतान (₹)", min_value=0.0, value=0.0)
                        comm_amount = st.number_input("कमीशन / प्रॉफिट (₹)", min_value=0.0, value=0.0)
                        
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
                        st.success("✅ लेज़र में एंट्री जोड़ दी गई है!")
                        st.rerun()

            st.subheader("💳 ट्रांज़ैक्शन हिस्ट्री")
            if len(member_txns) > 0:
                df_txn = pd.DataFrame(member_txns)
                df_txn = df_txn[['date', 'विवरण', 'credit', 'debit', 'loan', 'commission', 'fine', 'balance']]
                df_txn.columns = ['तारीख', 'विवरण', 'क्रेडिट (₹)', 'डेबिट (₹)', 'लोन (₹)', 'कमीशन (₹)', 'फाइन (₹)', 'बैलेंस (₹)']
                st.dataframe(df_txn, use_container_width=True)
            else:
                st.info("इस मेंबर की अभी कोई अतिरिक्त ट्रांज़ैक्शन एंट्री नहीं है।")
    else:
        st.warning("⚠️ लेज़र देखने के लिए पहले 'नया मेंबर' जोड़ें।")

# ----------------------------------------
# PAGE 4: COLLECTION & TRANSFER
# ----------------------------------------
elif st.session_state.page == "Collection":
    st.header("💰 मंथली कलेक्शन और लोन ट्रांसफर")
    if len(st.session_state.members_db) > 0:
        loan_taker = st.selectbox("इस महीने पैसा किसको मिला?", [m['name'] for m in st.session_state.members_db])
        if st.button("✅ ट्रांसफर दर्ज करें"):
            st.success(f"✅ {loan_taker} के ट्रांसफर की एंट्री हो गई है!")
    else:
        st.warning("⚠️ पहले मेंबर जोड़ें।")

# ----------------------------------------
# PAGE 5: LATE FINE (PENALTY)
# ----------------------------------------
elif st.session_state.page == "Penalty":
    st.header("⚠️ लेट फाइन कैलकुलेटर")
    st.info("यहाँ से फाइन कैलकुलेट कर सकते हैं।")

# ----------------------------------------
# PAGE 6: MONTHLY REPORT
# ----------------------------------------
elif st.session_state.page == "Report":
    st.header("📥 मंथली रिपोर्ट & बैकअप")
    st.info("यहाँ से एक्सेल रिपोर्ट डाउनलोड कर सकते हैं।")
