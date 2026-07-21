import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import datetime
import requests
import hashlib
import urllib.parse

# ==========================================
# 1. HELPER FUNCTIONS & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Sandhya ERP - Digital Committee", layout="centered", page_icon="🏢")

# Custom CSS
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

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw1cjdszgSRrSb8PlvupUVQTlea4e7dkvcCdDKJ-o8TssXJLmLRMBTJqBfhGhqcRjU-wg/exec"
ADMIN_HASH = hashlib.sha256("9557".encode()).hexdigest()

@st.cache_data(ttl=2)
def load_data_from_sheet():
    try:
        response = requests.get(APPS_SCRIPT_URL)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def generate_qr(upi_id, name, amount):
    upi_url = f"upi://pay?pa={upi_id}&pn={urllib.parse.quote(name)}&am={amount}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf

def get_whatsapp_link(mobile, message):
    encoded_msg = urllib.parse.quote(message)
    if not str(mobile).startswith("91"): mobile = f"91{mobile}"
    return f"https://wa.me/{mobile}?text={encoded_msg}"

def export_to_excel(df, sheet_name="Data"):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return buffer

# ==========================================
# 2. SESSION STATE (Crash-Proof)
# ==========================================
if 'auth_status' not in st.session_state: st.session_state.auth_status = False
if 'role' not in st.session_state: st.session_state.role = None
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

if 'members_db' not in st.session_state:
    raw_data = load_data_from_sheet()
    st.session_state.members_db = []
    for row in raw_data:
        m_name = row.get('Name') or row.get('name')
        if m_name:
            st.session_state.members_db.append({
                "id": str(row.get('Member ID') or row.get('member_id', 'SE0001')),
                "name": m_name,
                "mobile": str(row.get('Mobile') or row.get('mobile', '')),
                "identity_num": "[ID Redacted]",
                "pan": str(row.get('PAN') or row.get('pan', '')),
                "upi": str(row.get('UPI') or row.get('upi', '')),
                "address": str(row.get('Address') or row.get('address', '')),
                "reference": str(row.get('Reference') or row.get('reference', '')),
                "status": "✅ Active", "loan_status": "Clear", "photo": None,
                "dob": "-", "gender": "-", "nominee": "-", "bank_ac": "-"
            })

if 'payment_status' not in st.session_state:
    st.session_state.payment_status = {m['name']: "❌ Pending" for m in st.session_state.members_db}

if 'ledger_transactions' not in st.session_state: st.session_state.ledger_transactions = []
if 'current_receiver' not in st.session_state: st.session_state.current_receiver = "कोई नहीं (नया)"

# ==========================================
# 3. SECURE LOGIN SYSTEM
# ==========================================
if not st.session_state.auth_status:
    st.title("🔒 Sandhya Enterprises - सिक्योर लॉगिन")
    st.write("कृपया एडमिन पासवर्ड (9557) दर्ज करें।")
    
    with st.form("login_form"):
        role_select = st.selectbox("लॉगिन रोल:", ["Admin", "Staff", "Member"])
        username = st.text_input("यूज़रनेम (Admin के लिए: admin)")
        password = st.text_input("पासवर्ड (Admin के लिए: 9557)", type="password")
        if st.form_submit_button("लॉगिन करें", use_container_width=True):
            if role_select == "Admin" and username == "admin" and hashlib.sha256(password.encode()).hexdigest() == ADMIN_HASH:
                st.session_state.auth_status = True
                st.session_state.role = "Admin"
                st.session_state.user_name = "Avdhesh Kumar"
                st.success("✅ लॉगिन सफल!")
                st.rerun()
            elif role_select == "Staff" and password == "staff123":
                st.session_state.auth_status = True
                st.session_state.role = "Staff"
                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("❌ गलत यूज़रनेम या पासवर्ड!")
    st.stop()

# ==========================================
# 4. MAIN APP UI & MENUS
# ==========================================
st.sidebar.title("🏢 Sandhya ERP")
st.sidebar.success(f"👤 Logged in: {st.session_state.user_name} ({st.session_state.role})")
if st.sidebar.button("🔄 ऐप रिफ्रेश करें"): st.rerun()
if st.sidebar.button("🚪 सुरक्षित लॉग आउट"):
    st.session_state.auth_status = False
    st.rerun()

st.sidebar.markdown("---")
active_com = st.sidebar.selectbox("कमिटी टियर:", ["₹2,000 कमिटी (50 Members)", "₹5,000 कमिटी (50 Members)"])

st.title("💸 Digital Committee & ERP Manager")

# Menu Buttons
c1, c2, c3 = st.columns(3)
if c1.button("📊 डैशबोर्ड & चार्ट्स", use_container_width=True): st.session_state.page = "Dashboard"
if c2.button("👤 नया मेंबर", use_container_width=True): st.session_state.page = "Add_Member"
if c3.button("📒 लेज़र & एडिट", use_container_width=True): st.session_state.page = "Ledger"

c4, c5, c6 = st.columns(3)
if c4.button("💰 कलेक्शन & प्रॉफिट", use_container_width=True): st.session_state.page = "Collection"
if c5.button("⚠️ लेट फाइन", use_container_width=True): st.session_state.page = "Penalty"
if c6.button("📥 रिपोर्ट & बैकअप", use_container_width=True): st.session_state.page = "Report"
st.divider()

# ==========================================
# 5. PAGES LOGIC
# ==========================================
if st.session_state.page == "Dashboard":
    st.header("📊 कमिटी समरी & एनालिटिक्स")
    total_mem = len(st.session_state.members_db)
    txns = st.session_state.ledger_transactions
    total_coll = sum(t['credit'] for t in txns)
    total_loan = sum(t['loan'] for t in txns)
    run_bal = total_coll - total_loan
    
    # प्रत्येक मेंबर से ₹10 प्रति माह के हिसाब से एडमिन का कुल मेंटेनेंस फंड
    total_admin_maintenance = total_mem * 10
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("टोटल मेंबर्स", f"{total_mem} / 50")
    m2.metric("टोटल कलेक्शन", f"₹ {total_coll}")
    m3.metric("मार्केट लोन", f"₹ {total_loan}")
    m4.metric("एडमिन मेंटेनेंस फंड (₹10/सदस्य)", f"₹ {total_admin_maintenance}")
    
    st.markdown("---")
    colA, colB = st.columns(2)
    with colA:
        st.subheader("📈 कलेक्शन ट्रेंड")
        if len(txns) > 0:
            df_c = pd.DataFrame(txns)
            df_c['date'] = pd.to_datetime(df_c['date'])
            st.line_chart(df_c.groupby('date')['credit'].sum())
        else:
            st.info("डेटा उपलब्ध नहीं है।")
            
    with colB:
        st.subheader("🟢 पेमेंट स्टेटस")
        if len(st.session_state.payment_status) > 0:
            up_mem = st.selectbox("मेंबर चुनें:", list(st.session_state.payment_status.keys()))
            n_stat = st.radio("नया स्टेटस:", ["✅ Complete", "❌ Pending"], horizontal=True)
            if st.button("अपडेट करें"):
                st.session_state.payment_status[up_mem] = n_stat
                st.success("अपडेट हो गया!")
                st.rerun()
            st.dataframe(pd.DataFrame([{"मेंबर": k, "स्टेटस": v} for k, v in st.session_state.payment_status.items()]), use_container_width=True)

elif st.session_state.page == "Add_Member":
    st.header("👤 नया मेंबर रजिस्ट्रेशन")
    with st.form("add_mem_form", clear_on_submit=True):
        st.subheader("बेसिक जानकारी")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("पूरा नाम *")
            mobile = st.text_input("मोबाइल *")
            gender = st.selectbox("लिंग", ["Male", "Female"])
        with c2:
            dob = st.date_input("जन्म तिथि")
            nominee = st.text_input("नॉमिनी का नाम")
            
        st.subheader("KYC & बैंक डिटेल्स")
        c3, c4 = st.columns(2)
        with c3:
            identity = st.text_input("Aadhaar Number * (12 Digits)")
            pan = st.text_input("PAN Card *")
            address = st.text_area("पता *")
        with c4:
            upi_id = st.text_input("UPI ID *")
            bank_ac = st.text_input("बैंक अकाउंट नंबर")
            ref = st.selectbox("रेफरेंस *", ["Admin", "Self"])
            
        photo = st.file_uploader("फोटो अपलोड *", type=["jpg", "png"])
        if st.form_submit_button("डेटा सेव करें", use_container_width=True):
            if not name or not mobile or not identity or not pan or not address or not upi_id:
                st.error("⚠️ अनिवार्य (*) फील्ड भरें!")
            else:
                m_id = f"SE{len(st.session_state.members_db)+1:04d}"
                payload = {"member_id": m_id, "name": name, "mobile": mobile, "identity": "[ID Redacted]", "pan": pan, "upi": upi_id, "address": address, "reference": ref}
                try: requests.post(APPS_SCRIPT_URL, json=payload)
                except: pass
                
                st.session_state.members_db.append({
                    "id": m_id, "name": name, "mobile": mobile, "dob": str(dob), "gender": gender, 
                    "nominee": nominee, "identity_num": "[ID Redacted]", "pan": pan, "address": address, 
                    "bank_ac": bank_ac, "upi": upi_id, "reference": ref, "status": "✅ Active", "loan_status": "Clear", "photo": photo
                })
                st.session_state.payment_status[name] = "❌ Pending"
                
                # मंथली कमिटी जमा (₹2000) + सिस्टम मेंटेनेंस चार्ज (₹10 एडamin के लिए)
                st.session_state.ledger_transactions.append({"name": name, "date": str(datetime.date.today()), "विवरण": "मंथली जमा (₹2000) + मेंटेनेंस (₹10)", "credit": 2010, "debit": 0, "loan": 0, "commission": 0, "fine": 0, "balance": 2010})
                st.success(f"✅ {name} रजिस्टर्ड! ID: {m_id} (साथ में ₹10 मेंटेनेंस चार्ज जोड़ा गया)")

elif st.session_state.page == "Ledger":
    st.header("📒 व्यक्तिगत लेज़र & प्रोफाइल")
    if len(st.session_state.members_db) > 0:
        sel_mem = st.selectbox("मेंबर चुनें:", [m['name'] for m in st.session_state.members_db])
        md = next((m for m in st.session_state.members_db if m['name'] == sel_mem), None)
        
        if md:
            st.markdown("---")
            p1, p2, p3 = st.columns([1, 2, 2])
            with p1:
                if md.get('photo'): st.image(md['photo'], width=110)
                else: st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=110)
            with p2:
                st.write(f"👤 **नाम:** {md['name']}")
                st.write(f"📱 **मोबाइल:** {md['mobile']}")
                st.write(f"📍 **पता:** {md['address']}")
                wh_link = get_whatsapp_link(md['mobile'], f"Sandhya ERP: Hello {md['name']}, your payment is due.")
                st.markdown(f'[💬 WhatsApp पर मैसेज भेजें]({wh_link})')
            with p3:
                st.write(f"💳 **PAN:** {md['pan']}")
                st.write(f"🏦 **UPI:** {md['upi']}")
                st.write(f"👥 **नॉमिनी:** {md.get('nominee','-')}")
            
            with st.expander("✏️ प्रोफाइल एडिट (Update) करें"):
                with st.form(f"edit_{md['name']}"):
                    e_mob = st.text_input("मोबाइल", value=md['mobile'])
                    e_pan = st.text_input("PAN", value=md['pan'])
                    e_upi = st.text_input("UPI", value=md['upi'])
                    if st.form_submit_button("अपडेट करें"):
                        md['mobile'] = e_mob; md['pan'] = e_pan; md['upi'] = e_upi
                        try: requests.post(APPS_SCRIPT_URL, json={"action": "update", "member_id": md['id'], "name": md['name'], "mobile": e_mob, "pan": e_pan, "upi": e_upi, "reference": md['reference']})
                        except: pass
                        st.success("✅ अपडेट सफल!")
                        st.rerun()

            txns = [t for t in st.session_state.ledger_transactions if t['name'] == sel_mem]
            tc, tl, tcom = sum([t['credit'] for t in txns]), sum([t['loan'] for t in txns]), sum([t['commission'] for t in txns])
            nb = tc + tcom - sum([t['debit'] for t in txns])
            
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("कुल जमा", f"₹ {tc}"); f2.metric("लोन लिया", f"₹ {tl}"); f3.metric("प्रॉफिट/कमीशन", f"₹ {tcom}"); f4.metric("Net बैलेंस", f"₹ {nb}")
            
            with st.expander("➕ नया ट्रांज़ैक्शन जोड़ें"):
                with st.form(f"txn_{sel_mem}"):
                    c1, c2 = st.columns(2)
                    c_amt = c1.number_input("जमा (₹)", min_value=0.0, value=0.0)
                    d_amt = c2.number_input("भुगतान/लोन वापसी (₹)", min_value=0.0, value=0.0)
                    if st.form_submit_button("सेव करें"):
                        st.session_state.ledger_transactions.append({"name": sel_mem, "date": str(datetime.date.today()), "विवरण": "मैनुअल एंट्री", "credit": c_amt, "debit": d_amt, "loan": 0, "commission": 0, "fine": 0, "balance": nb + c_amt - d_amt})
                        st.success("✅ एंट्री जुड़ गई!"); st.rerun()

            st.subheader("💳 हिस्ट्री")
            if txns: st.dataframe(pd.DataFrame(txns), use_container_width=True)
            else: st.info("कोई एंट्री नहीं।")
    else:
        st.warning("⚠️ पहले मेंबर रजिस्टर करें।")

elif st.session_state.page == "Collection":
    st.header("💰 कमिटी डिस्ट्रीब्यूशन & प्रॉफिट शेयरिंग")
    st.info("नियम: 50 मेंबर्स × ₹2000 | 2% फिक्स ब्याज + बोली (डिस्काउंट) | प्रत्येक माह ₹10 सिस्टम मेंटेनेंस चार्ज एडमिन के लिए।")
    
    if len(st.session_state.members_db) > 0:
        loan_taker = st.selectbox("इस महीने कमिटी किसको मिली? (विजेता)", [m['name'] for m in st.session_state.members_db])
        
        colA, colB = st.columns(2)
        with colA:
            total_amount = st.number_input("टोटल अमाउंट (₹)", value=100000, step=10000)
            base_interest = st.number_input("फिक्स ब्याज (%)", value=2.0)
        with colB:
            boli_amount = st.number_input("बोली / डिस्काउंट (₹)", min_value=0.0, value=500.0, step=100.0)
            
        base_interest_amt = (total_amount * base_interest) / 100
        total_profit = base_interest_amt + boli_amount
        payout_amount = total_amount - total_profit
        
        total_members_count = len(st.session_state.members_db)
        per_member_profit = total_profit / total_members_count if total_members_count > 0 else 0
        
        st.markdown("---")
        st.write(f"📌 **बेस ब्याज (2%):** ₹ {base_interest_amt}")
        st.write(f"📌 **बोली (डिस्काउंट):** ₹ {boli_amount}")
        st.error(f"**टोटल कटा हुआ अमाउंट (कुल प्रॉफिट): ₹ {total_profit}**")
        st.success(f"💸 **{loan_taker} को ट्रांसफर होगा: ₹ {payout_amount}**")
        st.info(f"🎉 **सभी {total_members_count} मेंबर्स में प्रॉफिट बँटेगा: ₹ {per_member_profit:.2f} (प्रति मेंबर)**")
        
        if st.button("✅ कमिटी ट्रांसफर और प्रॉफिट डिस्ट्रीब्यूट करें"):
            st.session_state.current_receiver = loan_taker
            st.session_state.ledger_transactions.append({
                "name": loan_taker, "date": str(datetime.date.today()), "विवरण": "कमिटी उठाई (लोन)",
                "credit": 0, "debit": payout_amount, "loan": payout_amount, "commission": 0, "fine": 0, "balance": 0
            })
            
            for m in st.session_state.members_db:
                st.session_state.ledger_transactions.append({
                    "name": m['name'], "date": str(datetime.date.today()), "विवरण": f"कमिटी प्रॉफिट (विजेता: {loan_taker})",
                    "credit": 0, "debit": 0, "loan": 0, "commission": per_member_profit, "fine": 0, "balance": 0
                })
            
            st.success("✅ ट्रांसफर सफल! प्रॉफिट सभी मेंबर्स के लेज़र में जोड़ दिया गया है।")
    else:
        st.warning("⚠️ कृपया पहले मेंबर जोड़ें।")

elif st.session_state.page == "Penalty":
    st.header("⚠️ लेट फाइन (Penalty) कैलकुलेटर")
    st.info("नियम: 1 से 6 दिन लेट = ₹20/दिन | 7 दिन या उससे ज्यादा लेट = 3% मंथली पेनल्टी")
    
    if len(st.session_state.members_db) > 0:
        late_member = st.selectbox("लेट पेमेंट करने वाला मेंबर:", [m['name'] for m in st.session_state.members_db])
        monthly_due = st.number_input("मंथली जमा राशि (₹)", value=2000)
        days_late = st.number_input("कितने दिन लेट किया?", min_value=1, value=1)
        
        fine_amount = 0
        if 1 <= days_late <= 6:
            fine_amount = days_late * 20
            st.write(f"कैलकुलेशन: {days_late} दिन × ₹20 = ₹{fine_amount}")
        elif days_late >= 7:
            fine_amount = (monthly_due * 3) / 100
            st.write(f"कैलकुलेशन: 7+ दिन (₹{monthly_due} का 3%) = ₹{fine_amount}")
            
        st.error(f"**टोटल फाइन अमाउंट: ₹ {fine_amount}**")
        
        if st.button("✅ फाइन लेज़र में जोड़ें"):
            st.session_state.ledger_transactions.append({
                "name": late_member, "date": str(datetime.date.today()), "विवरण": f"{days_late} दिन का लेट फाइन",
                "credit": 0, "debit": fine_amount, "loan": 0, "commission": 0, "fine": fine_amount, "balance": 0
            })
            st.success(f"✅ {late_member} के खाते में ₹ {fine_amount} का फाइन जोड़ दिया गया है!")
    else:
        st.warning("⚠️ कोई मेंबर उपलब्ध नहीं है।")

elif st.session_state.page == "Report":
    st.header("📥 एक्सेल रिपोर्ट & बैकअप")
    if len(st.session_state.members_db) > 0:
        m_df = pd.DataFrame(st.session_state.members_db).drop(columns=['photo'], errors='ignore')
        t_df = pd.DataFrame(st.session_state.ledger_transactions)
        
        st.download_button("📥 मेंबर्स डेटा डाउनलोड करें", data=export_to_excel(m_df, "Members"), file_name=f"Members_{datetime.date.today()}.xlsx")
        st.download_button("📥 लेज़र/ट्रांज़ैक्शन डेटा डाउनलोड करें", data=export_to_excel(t_df, "Ledger"), file_name=f"Ledger_{datetime.date.today()}.xlsx")
    else:
        st.warning("कोई डेटा नहीं है।")
