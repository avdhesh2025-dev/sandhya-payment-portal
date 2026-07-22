import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import datetime
import requests
import hashlib
import urllib.parse

# ==========================================
# 1. CONFIGURATION & FULL DISPLAY LAYOUT
# ==========================================
st.set_page_config(page_title="Sandhya ERP - Digital Committee", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100% !important;
    }
    div.stButton > button {
        background-color: #ffffff;
        color: #1f2937;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        border-bottom: 6px solid #d1d5db;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        font-weight: bold;
        font-size: 15px;
        height: 50px;
        transition: all 0.1s ease-in-out;
    }
    div.stButton > button:active {
        border-bottom: 2px solid #d1d5db;
        transform: translateY(4px);
    }
    </style>
""", unsafe_allow_html=True)

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyO1X1iG-49QvgFDlPBQKFnw7is6HrbCFBLZOXqFxrpKH6aLXytvnolinxnfX6WpnVIJA/exec"
ADMIN_HASH = hashlib.sha256("9557".encode()).hexdigest()

# ==========================================
# 2. DATA SYNC & HELPERS
# ==========================================
@st.cache_data(ttl=1)
def load_data_from_sheet():
    try:
        response = requests.get(APPS_SCRIPT_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.sidebar.error(f"⚠️ Sheet Sync Error: {e}")
    return []

def save_ledger_txns(txns_list):
    st.session_state.ledger.extend(txns_list)
    try:
        payload = {"action": "add_ledger_bulk", "data": txns_list}
        requests.post(APPS_SCRIPT_URL, json=payload, timeout=5)
    except Exception as e:
        st.error(f"⚠️ लेज़र शीट में सेव नहीं हो पाया: {e}")

def generate_qr(upi_id, name, amount=None):
    upi_url = f"upi://pay?pa={upi_id}&pn={urllib.parse.quote(name)}&cu=INR"
    if amount: upi_url += f"&am={amount}"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf

def get_whatsapp_link(message):
    encoded_msg = urllib.parse.quote(message)
    return f"https://wa.me/?text={encoded_msg}"

# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================
if 'auth_status' not in st.session_state: st.session_state.auth_status = False
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
                "father_name": str(row.get('Father Name') or row.get('father_name', '-')),
                "mobile": str(row.get('Mobile') or row.get('mobile', '')),
                "dob": str(row.get('DOB') or row.get('dob', '-')),
                "gender": str(row.get('Gender') or row.get('gender', '-')),
                "aadhaar": "[Aadhaar Redacted]",
                "pan": str(row.get('PAN') or row.get('pan', '')),
                "upi": str(row.get('UPI ID') or row.get('upi', '')),
                "address": str(row.get('Address') or row.get('address', '')),
                "status": "Active", "photo": None
            })

if 'ledger' not in st.session_state: st.session_state.ledger = [] 
if 'active_loans' not in st.session_state: st.session_state.active_loans = {}

# ==========================================
# 4. SECURE LOGIN
# ==========================================
if not st.session_state.auth_status:
    st.title("🔒 Sandhya Enterprises - सिक्योर लॉगिन")
    with st.form("login_form"):
        username = st.text_input("यूज़रनेम (admin)")
        password = st.text_input("पासवर्ड (9557)", type="password")
        if st.form_submit_button("लॉगिन करें", use_container_width=True):
            if username == "admin" and hashlib.sha256(password.encode()).hexdigest() == ADMIN_HASH:
                st.session_state.auth_status = True
                st.rerun()
            else:
                st.error("❌ गलत विवरण!")
    st.stop()

# ==========================================
# 5. NAVIGATION MENUS
# ==========================================
st.sidebar.title("🏢 Sandhya ERP")
st.sidebar.info("📌 नियम: 50 सदस्य | ₹2000 महीना | ₹10 मेंटेनेंस | 2% ब्याज")

if st.sidebar.button("🔄 डेटा सिंक & रिफ्रेश", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("🚪 लॉग आउट", use_container_width=True): 
    st.session_state.auth_status = False
    st.rerun()

st.sidebar.markdown("---")
menu_opts = ["📊 डैशबोर्ड", "👤 नया मेंबर जोड़ें", "📂 मेंबर प्रोफाइल & लेज़र", "💰 कमिटी विनर (लोन पास)", "💸 मंथली कलेक्शन & EMI (QR)"]
choice = st.sidebar.radio("मेनू चुनें:", menu_opts)

# ==========================================
# 6. PAGES LOGIC
# ==========================================

if choice == "👤 नया मेंबर जोड़ें":
    st.header("👤 नया मेंबर रजिस्ट्रेशन (यूनिक चेक)")
    with st.form("add_member"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("पूरा नाम *")
            father_name = st.text_input("पिता का नाम *")
            mobile = st.text_input("मोबाइल नंबर *")
            dob = st.date_input("जन्म तिथि (DOB)")
            gender = st.selectbox("लिंग", ["Male", "Female", "Other"])
        with c2:
            aadhaar = st.text_input("Aadhar Number (12 Digits) *")
            pan = st.text_input("PAN Card Number *")
            upi_id = st.text_input("UPI ID (पैसे प्राप्त करने के लिए) *")
            address = st.text_area("पूरा पता *")
            
        photo = st.file_uploader("Passport Size Photo", type=["jpg", "png"])
        
        if st.form_submit_button("मेंबर ऐड करें", use_container_width=True):
            if not name or not mobile or not aadhaar or not pan or not father_name:
                st.error("⚠️ कृपया सभी (*) अनिवार्य फील्ड भरें!")
            else:
                existing_mobiles = [m['mobile'] for m in st.session_state.members_db]
                existing_pans = [m['pan'].upper() for m in st.session_state.members_db]
                
                if mobile in existing_mobiles:
                    st.error("❌ यह मोबाइल नंबर पहले से रजिस्टर्ड है!")
                elif pan.upper() in existing_pans:
                    st.error("❌ यह PAN नंबर पहले से मौजूद है!")
                else:
                    new_mem = {
                        "id": f"SE{len(st.session_state.members_db)+1:04d}",
                        "name": name, "father_name": father_name, "mobile": mobile,
                        "aadhaar": "[Aadhaar Redacted]", "pan": pan.upper(), "upi": upi_id,
                        "address": address, "dob": str(dob), "gender": gender,
                        "photo": photo, "status": "Active" 
                    }
                    
                    payload = {
                        "member_id": new_mem["id"], "name": name, "father_name": father_name, 
                        "mobile": mobile, "dob": str(dob), "gender": gender, "aadhaar": "[Aadhaar Redacted]",
                        "pan": pan.upper(), "upi": upi_id, "address": address
                    }
                    try: requests.post(APPS_SCRIPT_URL, json=payload, timeout=5)
                    except: pass
                    
                    st.session_state.members_db.append(new_mem)
                    st.success(f"✅ {name} कमिटी में सफलतापूर्वक जुड़ गए हैं!")

elif choice == "📂 मेंबर प्रोफाइल & लेज़र":
    st.header("📂 मेंबर प्रोफाइल & लेज़र पासबुक")
    if not st.session_state.members_db:
        st.warning("कोई मेंबर नहीं है।")
    else:
        mem_names = [m['name'] for m in st.session_state.members_db]
        selected_name = st.selectbox("प्रोफाइल देखने के लिए मेंबर चुनें:", mem_names)
        
        member_idx = next(i for i, m in enumerate(st.session_state.members_db) if m['name'] == selected_name)
        mem = st.session_state.members_db[member_idx]
        
        st.markdown("---")
        c1, c2, c3 = st.columns([1,2,2])
        with c1:
            if mem.get('photo'): st.image(mem['photo'], width=120)
            else: st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=120)
            
            # Defaulter toggle (If inactive, removed from loan eligibility)
            is_active = st.toggle("✅ Active Member", value=(mem['status'] == "Active"))
            new_status = "Active" if is_active else "Defaulter (Inactive)"
            
            if mem['status'] != new_status:
                st.session_state.members_db[member_idx]['status'] = new_status
                st.rerun()
            
            if new_status == "Active": st.success("Active Member")
            else: st.error("❌ Defaulter (QR बंद)")

        with c2:
            st.write(f"**नाम:** {mem['name']}")
            st.write(f"**पिता:** {mem['father_name']}")
            st.write(f"**मोबाइल:** {mem['mobile']}")
        with c3:
            st.write(f"**Aadhar:** [Aadhaar Redacted]") 
            st.write(f"**PAN:** {mem['pan']}")
            st.write(f"**UPI ID:** {mem['upi']}")
            
        st.markdown("<br>", unsafe_allow_html=True)

        my_txns = [t for t in st.session_state.ledger if t['name'] == mem['name']]
        total_deposited = sum(t['amount'] for t in my_txns if t['type'] in ['Monthly Deposit', 'EMI Paid'])
        profit_earned = sum(t['amount'] for t in my_txns if t['type'] == 'Profit Share')
        total_fine_paid = sum(t['amount'] for t in my_txns if t['type'] == 'Fine Paid')
        total_taken = sum(t['amount'] for t in my_txns if t['type'] == 'Loan Taken')
        
        net_savings = total_deposited + profit_earned

        st.subheader("📊 व्यक्तिगत लेज़र (Ledger)")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("कुल जमा किया", f"₹ {total_deposited}")
        col2.metric("प्रॉफिट मिला", f"₹ {profit_earned}")
        col3.metric("कुल बचत (Running Balance)", f"₹ {net_savings}")
        col4.metric("कमिटी से लिया (लोन)", f"₹ {total_taken}")
        col5.metric("लेट फाइन भरा", f"₹ {total_fine_paid}")
        
        if mem['name'] in st.session_state.active_loans:
            loan_info = st.session_state.active_loans[mem['name']]
            st.warning(f"⚠️ **एक्टिव लोन (EMI चल रही है):** ₹ {loan_info['emi']} प्रति माह | बचे हुए महीने: {loan_info['months_left']}")

        if my_txns:
            st.dataframe(pd.DataFrame(my_txns)[['date', 'desc', 'type', 'amount']], use_container_width=True)

elif choice == "💰 कमिटी विनर (लोन पास)":
    st.header("🏆 कमिटी विनर (लोन पास करें)")
    st.info("विजेता की कुल बचत (Running Balance) को टोटल पूल से माइनस करके बचे हुए अमाउंट पर 2% ब्याज से EMI बनाई जाएगी।")
    
    if not st.session_state.members_db:
        st.warning("मेंबर मौजूद नहीं हैं।")
    else:
        eligible_members = [m for m in st.session_state.members_db if m['status'] == "Active"]
        defaulters = [m['name'] for m in st.session_state.members_db if m['status'] != "Active"]
        if defaulters:
            st.error(f"❌ Defaulter सदस्य (इनका QR और लोन बंद है): {', '.join(defaulters)}")
            
        winner_name = st.selectbox("कमिटी विजेता चुनें:", [m['name'] for m in eligible_members])
        
        winner_txns = [t for t in st.session_state.ledger if t['name'] == winner_name]
        winner_savings = sum(t['amount'] for t in winner_txns if t['type'] in ['Monthly Deposit', 'EMI Paid']) + sum(t['amount'] for t in winner_txns if t['type'] == 'Profit Share')
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        total_pool = len(st.session_state.members_db) * 2000
        
        net_loan_principal = total_pool - winner_savings
        
        with c1:
            st.write(f"**कमिटी का कुल फंड (50 x 2000):** ₹ {total_pool}")
            st.success(f"**विजेता की कुल बचत (माइनस होगी):** - ₹ {winner_savings}")
            st.error(f"**एक्चुअल लोन अमाउंट (बचत कटने के बाद):** ₹ {net_loan_principal}")
            tenure = st.selectbox("लोन की अवधि चुनें (महीने)", [6, 12, 18, 24])
            interest_rate = 2.0 
            
        with c2:
            monthly_interest = (net_loan_principal * interest_rate) / 100
            monthly_principal = net_loan_principal / tenure
            emi = round(monthly_principal + monthly_interest, 2)
            
            st.info(f"**प्रति माह 2% ब्याज:** ₹ {monthly_interest}")
            st.warning(f"**विजेता की नई EMI:** ₹ {emi} (अगले {tenure} महीनों तक)")

        if st.button("✅ लोन पास करें और EMI सेट करें", use_container_width=True):
            st.session_state.active_loans[winner_name] = {
                "principal": net_loan_principal,
                "emi": emi,
                "months_left": tenure,
                "monthly_interest": monthly_interest
            }
            
            new_txns = [{
                "name": winner_name, "date": str(datetime.date.today()), 
                "desc": f"{tenure} महीने के लिए कमिटी उठाई (बचत काटकर)", "type": "Loan Taken", "amount": net_loan_principal
            }]
            save_ledger_txns(new_txns)
            st.success(f"✅ {winner_name} का लोन पास हो गया और EMI ₹ {emi} सेट कर दी गई है!")

elif choice == "💸 मंथली कलेक्शन & EMI (QR)":
    st.header("💸 मंथली कलेक्शन, मेंटेनेंस चार्ज & डायनामिक पेमेंट QR")
    
    date_today = st.date_input("आज की तारीख", datetime.date.today())
    due_date = datetime.date(date_today.year, date_today.month, 5)
    days_late = (date_today - due_date).days if (date_today - due_date).days > 0 else 0
    st.info(f"**मंथली ड्यू डेट:** 5 तारीख (रात 9 बजे तक मान्य) | **लेट दिन:** {days_late}")
    
    if st.session_state.members_db:
        st.subheader("✅ कलेक्शन एंट्री & QR")
        col_name = st.selectbox("पैसा जमा करने वाले मेंबर का नाम:", [m['name'] for m in st.session_state.members_db])
        
        # Check if member is defaulter
        mem_obj = next(m for m in st.session_state.members_db if m['name'] == col_name)
        if mem_obj['status'] != "Active":
            st.error("⚠️ यह मेंबर Defaulter (Inactive) है! इनका QR जनरेट नहीं होगा जब तक इन्हें Active न किया जाए। पात्र नहीं हैं। हल्दी/फाइन चेक करें।")
        else:
            is_emi_payer = col_name in st.session_state.active_loans
            base_due = 2000
            maintenance_fee = 10 # Admin maintenance charge
            
            if is_emi_payer:
                loan_details = st.session_state.active_loans[col_name]
                total_payable = loan_details['emi']
                pay_type = "EMI Paid"
                st.warning(f"⚠️ **लोन एक्टिव है!** इस मेंबर की EMI: **₹ {total_payable}** + मेंटेनेंस: **₹ {maintenance_fee}**")
            else:
                total_payable = base_due
                pay_type = "Monthly Deposit"
                st.success(f"✅ **नॉर्मल मेंबर:** बेस अमाउंट: **₹ {total_payable}** + मेंटेनेंस: **₹ {maintenance_fee}**")
                
            # Fine calculation rules: 1-6 days = Rs 20/day, 7+ days = 3% of total due
            fine_amount = 0
            if days_late > 0:
                if days_late <= 6:
                    fine_amount = days_late * 20
                    st.error(f"लेट फाइन ({days_late} दिन x ₹20): ₹ {fine_amount}")
                else:
                    fine_amount = ((total_payable + maintenance_fee) * 3) / 100
                    st.error(f"7+ दिन लेट! टोटल अमाउंट का 3% फाइन = ₹ {fine_amount}")
                    
            actual_total = total_payable + maintenance_fee + fine_amount
            st.markdown("---")
            st.subheader("📲 डायनामिक पेमेंट QR कोड")
            
            admin_upi = st.text_input("पैसे प्राप्त करने वाला UPI ID (एडमिन/कमिटी):", value="admin@ybl")
            actual_paid = st.number_input("वास्तव में कितना पैसा लिया जा रहा है?", value=float(actual_total))
            
            qr_col, txt_col = st.columns([1, 2])
            with qr_col:
                if admin_upi:
                    pay_qr = generate_qr(admin_upi, f"Committee-{col_name}", actual_paid)
                    st.image(pay_qr, width=180)
            with txt_col:
                st.info(f"**{col_name}** के लिए जनरेटेड QR\n- कमिटी/EMI: ₹{total_payable}\n- एडमिन मेंटेनेंस: ₹{maintenance_fee}\n- लेट फाइन: ₹{fine_amount}\n\n**कुल योग: ₹{actual_total}**")
            
            if st.button("✅ पेमेंट कन्फर्म करें और लेज़र में जोड़ें", use_container_width=True):
                txns_to_save = []
                # 1. Main Deposit / EMI
                txns_to_save.append({
                    "name": col_name, "date": str(date_today), "desc": f"महीने का पेमेंट (कमिटी/EMI)", 
                    "type": pay_type, "amount": total_payable
                })
                # 2. Admin Maintenance (₹10)
                txns_to_save.append({
                    "name": col_name, "date": str(date_today), "desc": f"सिस्टम मेंटेनेंस चार्ज (एडमिन फंड)", 
                    "type": "Maintenance", "amount": maintenance_fee
                })
                # 3. Fine if any
                if fine_amount > 0:
                    txns_to_save.append({
                        "name": col_name, "date": str(date_today), "desc": f"{days_late} दिन का लेट फाइन", 
                        "type": "Fine Paid", "amount": fine_amount
                    })
                
                # Deduct month from loan tenure
                if is_emi_payer:
                    st.session_state.active_loans[col_name]['months_left'] -= 1
                    if st.session_state.active_loans[col_name]['months_left'] <= 0:
                        del st.session_state.active_loans[col_name]
                        st.balloons()
                        st.success("🎉 बधाई हो! लोन पूरी तरह चुकता हो गया है।")
                    
                # 🌟 AUTOMATED PROFIT DISTRIBUTION ENGINE
                # Interest from EMI + Fine goes to all active members excluding active loan takers
                profit_generated = 0
                if is_emi_payer: profit_generated += st.session_state.active_loans.get(col_name, loan_details)['monthly_interest']
                if fine_amount > 0: profit_generated += fine_amount
                    
                if profit_generated > 0:
                    eligible = [m['name'] for m in st.session_state.members_db if m['name'] not in st.session_state.active_loans and m['status'] == "Active"]
                    if eligible:
                        per_head = profit_generated / len(eligible)
                        for emp in eligible:
                            txns_to_save.append({
                                "name": emp, "date": str(date_today), "desc": f"प्रॉफिट शेयर (Source: {col_name})", 
                                "type": "Profit Share", "amount": round(per_head, 2)
                            })
                        st.success(f"✅ कुल प्रॉफिट ₹ {profit_generated} सभी {len(eligible)} योग्य सदस्यों में बराबर बाँट दिया गया है!")
                
                save_ledger_txns(txns_to_save)
                st.success("✅ पेमेंट सफलतापूर्वक लेज़र और Google Sheet में सेव हो गया!")

elif choice == "📊 डैशबोर्ड":
    st.header("📊 कमिटी समरी & एनालिटिक्स")
    t_mems = len(st.session_state.members_db)
    act_loans = len(st.session_state.active_loans)
    defaulters = len([m for m in st.session_state.members_db if m['status'] != 'Active'])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("कुल मेंबर्स", t_mems)
    c2.metric("चल रहे लोन (EMI)", act_loans)
    c3.metric("डिफॉल्टर (Inactive)", defaulters)
    
    st.markdown("---")
    st.subheader("हाल के लेन-देन (Google Sheet Synced)")
    if st.session_state.ledger:
        recent = pd.DataFrame(st.session_state.ledger).iloc[::-1].head(10)
        st.dataframe(recent, use_container_width=True)
    else:
        st.info("अभी कोई लेन-देन रिकॉर्ड नहीं हुआ है।")
