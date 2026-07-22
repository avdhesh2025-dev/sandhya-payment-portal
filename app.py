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
st.set_page_config(page_title="Sandhya ERP - Digital Committee", layout="wide", page_icon="🏢")

# 3D Button CSS & styling
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
        height: 50px;
        transition: all 0.1s ease-in-out;
    }
    div.stButton > button:active {
        border-bottom: 2px solid #d1d5db;
        transform: translateY(4px);
    }
    </style>
""", unsafe_allow_html=True)

# Admin Security
ADMIN_HASH = hashlib.sha256("9557".encode()).hexdigest()

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
# 2. SESSION STATE & DATABASE SETUP
# ==========================================
if 'auth_status' not in st.session_state: st.session_state.auth_status = False
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

if 'members_db' not in st.session_state:
    st.session_state.members_db = [] 
if 'ledger' not in st.session_state:
    st.session_state.ledger = [] 
if 'active_loans' not in st.session_state:
    st.session_state.active_loans = {} # Format: {name: {principal, emi, months_left, monthly_interest}}

# ==========================================
# 3. SECURE LOGIN
# ==========================================
if not st.session_state.auth_status:
    st.title("🔒 Sandhya Enterprises - सिक्योर लॉगिन")
    with st.form("login_form"):
        username = st.text_input("यूज़रनेम (admin)")
        password = st.text_input("पासवर्ड (9557)", type="password")
        if st.form_submit_button("लॉगिन करें"):
            if username == "admin" and hashlib.sha256(password.encode()).hexdigest() == ADMIN_HASH:
                st.session_state.auth_status = True
                st.rerun()
            else:
                st.error("❌ गलत विवरण!")
    st.stop()

# ==========================================
# 4. NAVIGATION MENUS
# ==========================================
st.sidebar.title("🏢 Sandhya ERP")
if st.sidebar.button("🔄 ऐप रिफ्रेश"): st.rerun()
if st.sidebar.button("🚪 लॉग आउट"): 
    st.session_state.auth_status = False
    st.rerun()

st.sidebar.markdown("---")
menu_opts = ["📊 डैशबोर्ड", "👤 नया मेंबर जोड़ें", "📂 मेंबर प्रोफाइल & लेज़र", "💰 कमिटी विनर (लोन पास)", "💸 मंथली कलेक्शन & EMI (QR)"]
choice = st.sidebar.radio("मेनू चुनें:", menu_opts)

# ==========================================
# 5. PAGE LOGIC
# ==========================================

# ------------------------------------------
# PAGE 1: ADD MEMBER
# ------------------------------------------
if choice == "👤 नया मेंबर जोड़ें":
    st.header("👤 नया मेंबर रजिस्ट्रेशन")
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
                existing_aadhaars = [m['aadhaar'] for m in st.session_state.members_db]
                
                if mobile in existing_mobiles: st.error("❌ यह मोबाइल नंबर पहले से जुड़ा हुआ है!")
                elif pan.upper() in existing_pans: st.error("❌ यह PAN नंबर पहले से मौजूद है!")
                elif aadhaar in existing_aadhaars: st.error("❌ यह Aadhar नंबर पहले से उपयोग में है!")
                else:
                    new_mem = {
                        "name": name, "father_name": father_name, "mobile": mobile,
                        "aadhaar": aadhaar, "pan": pan.upper(), "upi": upi_id,
                        "address": address, "dob": str(dob), "gender": gender,
                        "photo": photo, "status": "Active" 
                    }
                    st.session_state.members_db.append(new_mem)
                    st.success(f"✅ {name} कमिटी में सफलतापूर्वक जुड़ गए हैं!")

# ------------------------------------------
# PAGE 2: MEMBER PROFILE & LEDGER
# ------------------------------------------
elif choice == "📂 मेंबर प्रोफाइल & लेज़र":
    st.header("📂 मेंबर प्रोफाइल & लेज़र पासबुक")
    if not st.session_state.members_db:
        st.warning("कोई मेंबर नहीं है। पहले मेंबर जोड़ें।")
    else:
        mem_names = [m['name'] for m in st.session_state.members_db]
        selected_name = st.selectbox("प्रोफाइल देखने के लिए मेंबर चुनें:", mem_names)
        
        member_idx = next(i for i, m in enumerate(st.session_state.members_db) if m['name'] == selected_name)
        mem = st.session_state.members_db[member_idx]
        
        st.markdown("---")
        c1, c2, c3 = st.columns([1,2,2])
        with c1:
            if mem['photo']: st.image(mem['photo'], width=120)
            else: st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=120)
            
            is_active = st.toggle("✅ Active Member", value=(mem['status'] == "Active"))
            new_status = "Active" if is_active else "Defaulter (Inactive)"
            
            if mem['status'] != new_status:
                st.session_state.members_db[member_idx]['status'] = new_status
                st.rerun()
                
            if new_status == "Active": st.success(new_status)
            else: st.error("❌ " + new_status)

        with c2:
            st.write(f"**नाम:** {mem['name']}")
            st.write(f"**पिता:** {mem['father_name']}")
            st.write(f"**मोबाइल:** {mem['mobile']}")
            st.write(f"**DOB:** {mem['dob']}")
        with c3:
            st.write(f"**Aadhar:** [Aadhaar Redacted]") 
            st.write(f"**PAN:** {mem['pan']}")
            st.write(f"**UPI ID:** {mem['upi']}")
            st.write(f"**पता:** {mem['address']}")
            
        # 🌟 NEW FEATURE: SHOW ACTIVE LOAN & EMI DETAILS ON PROFILE
        st.markdown("<br>", unsafe_allow_html=True)
        if mem['name'] in st.session_state.active_loans:
            loan_info = st.session_state.active_loans[mem['name']]
            st.warning(f"⚠️ **एक्टिव लोन (EMI चल रही है):** इस मेंबर को हर महीने **₹ {loan_info['emi']}** जमा करने हैं। **बचे हुए महीने:** {loan_info['months_left']}")
        else:
            st.success("✅ **कोई लोन नहीं है।** (इस मेंबर को हर महीने सिर्फ बेस अमाउंट ₹2000 जमा करना है)")

        st.subheader("📊 व्यक्तिगत लेज़र (Ledger)")
        my_txns = [t for t in st.session_state.ledger if t['name'] == mem['name']]
        total_deposited = sum(t['amount'] for t in my_txns if t['type'] in ['Monthly Deposit', 'EMI Paid'])
        total_taken = sum(t['amount'] for t in my_txns if t['type'] == 'Loan Taken')
        total_fine_paid = sum(t['amount'] for t in my_txns if t['type'] == 'Fine Paid')
        profit_earned = sum(t['amount'] for t in my_txns if t['type'] == 'Profit Share')
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("कुल जमा किया (EMI/Monthly)", f"₹ {total_deposited}")
        col2.metric("कमिटी से लिया (लोन)", f"₹ {total_taken}")
        col3.metric("प्रॉफिट मिला", f"₹ {profit_earned}")
        col4.metric("लेट फाइन भरा", f"₹ {total_fine_paid}")
        
        if my_txns:
            st.dataframe(pd.DataFrame(my_txns)[['date', 'desc', 'type', 'amount']], use_container_width=True)
        else:
            st.info("अभी कोई लेन-देन नहीं हुआ है।")

# ------------------------------------------
# PAGE 3: COMMITTEE WINNER (LOAN PASS)
# ------------------------------------------
elif choice == "💰 कमिटी विनर (लोन पास)":
    st.header("🏆 कमिटी विनर (लोन पास करें)")
    st.info("यहाँ से उस मेंबर को चुनें जिसने इस महीने कमिटी उठाई है। सिस्टम उसका EMI सेट कर देगा।")
    
    if not st.session_state.members_db:
        st.warning("मेंबर मौजूद नहीं हैं।")
    else:
        eligible_members = [m for m in st.session_state.members_db if m['status'] == "Active"]
        defaulters = [m['name'] for m in st.session_state.members_db if m['status'] != "Active"]
        
        if defaulters:
            st.error(f"❌ Defaulter (लोन नहीं ले सकते): {', '.join(defaulters)}")
            
        winner_name = st.selectbox("कमिटी विजेता चुनें:", [m['name'] for m in eligible_members])
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        total_pool = len(st.session_state.members_db) * 2000
        with c1:
            st.write(f"**कमिटी का कुल फंड:** ₹ {total_pool}")
            tenure = st.selectbox("लोन की अवधि चुनें (महीने)", [6, 12, 18, 24])
            interest_rate = 2.0 
            
        with c2:
            monthly_interest = (total_pool * interest_rate) / 100
            monthly_principal = total_pool / tenure
            emi = round(monthly_principal + monthly_interest, 2)
            
            st.success(f"**प्रति माह 2% ब्याज:** ₹ {monthly_interest}")
            st.error(f"**विजेता की नई EMI:** ₹ {emi} (अगले {tenure} महीनों तक)")

        if st.button("✅ लोन पास करें और EMI सेट करें", use_container_width=True):
            st.session_state.active_loans[winner_name] = {
                "principal": total_pool,
                "emi": emi,
                "months_left": tenure,
                "monthly_interest": monthly_interest
            }
            
            st.session_state.ledger.append({
                "name": winner_name, "date": str(datetime.date.today()), 
                "desc": f"{tenure} महीने के लिए कमिटी उठाई", "type": "Loan Taken", "amount": total_pool
            })
            st.success(f"✅ {winner_name} का लोन पास हो गया और EMI ₹ {emi} सेट कर दी गई है!")

# ------------------------------------------
# PAGE 4: MONTHLY COLLECTION & DYNAMIC QR
# ------------------------------------------
elif choice == "💸 मंथली कलेक्शन & EMI (QR)":
    st.header("💸 मंथली कलेक्शन & डायनामिक पेमेंट QR")
    st.write("मेंबर का नाम चुनें, सिस्टम ऑटोमैटिक बताएगा कि उसे कितने पैसे देने हैं और उसी अमाउंट का QR जनरेट करेगा।")
    
    date_today = st.date_input("आज की तारीख", datetime.date.today())
    due_date = datetime.date(date_today.year, date_today.month, 5)
    days_late = (date_today - due_date).days if (date_today - due_date).days > 0 else 0
    
    st.info(f"**मंथली ड्यू डेट:** 5 तारीख | **लेट दिन:** {days_late}")
    
    if st.session_state.members_db:
        st.subheader("✅ कलेक्शन एंट्री & QR")
        col_name = st.selectbox("पैसा जमा करने वाले मेंबर का नाम:", [m['name'] for m in st.session_state.members_db])
        
        is_emi_payer = col_name in st.session_state.active_loans
        base_due = 2000
        
        if is_emi_payer:
            loan_details = st.session_state.active_loans[col_name]
            total_payable = loan_details['emi']
            pay_type = "EMI Paid"
            st.warning(f"⚠️ **लोन एक्टिव है!** इस मेंबर की EMI: **₹ {total_payable}** | बचे हुए महीने: **{loan_details['months_left']}**")
        else:
            total_payable = base_due
            pay_type = "Monthly Deposit"
            st.success(f"✅ **नॉर्मल मेंबर:** इस मेंबर का बेस अमाउंट: **₹ {total_payable}**")
            
        # Calculate Fine
        fine_amount = 0
        if days_late > 0:
            if days_late <= 6:
                fine_amount = days_late * 20
                st.error(f"लेट फाइन: {days_late} दिन x ₹20 = ₹ {fine_amount}")
            else:
                fine_amount = (total_payable * 3) / 100
                st.error(f"7+ दिन लेट! टोटल अमाउंट का 3% फाइन = ₹ {fine_amount}")
                
        # 🌟 NEW FEATURE: DYNAMIC QR CODE FOR INDIVIDUAL MEMBER DUE
        actual_total = total_payable + fine_amount
        st.markdown("---")
        st.subheader("📲 पेमेंट प्राप्त करें (QR Code)")
        
        admin_upi = st.text_input("पैसे प्राप्त करने वाला UPI ID (यहाँ अपना या कमिटी का UPI डालें):", value="admin@ybl")
        actual_paid = st.number_input("वास्तव में कितना पैसा लिया जा रहा है?", value=float(actual_total))
        
        qr_col, txt_col = st.columns([1, 2])
        with qr_col:
            if admin_upi:
                pay_qr = generate_qr(admin_upi, "Committee Collection", actual_paid)
                st.image(pay_qr, width=180)
        with txt_col:
            st.info(f"**मेंबर ({col_name}) से ₹ {actual_paid} कलेक्ट करें।**\n\nआप इस QR कोड को स्कैन करवाकर सीधे पेमेंट ले सकते हैं।")
        
        st.markdown("---")
        
        if st.button("✅ पेमेंट कन्फर्म करें और लेज़र में जोड़ें", use_container_width=True):
            # Record Payment
            st.session_state.ledger.append({
                "name": col_name, "date": str(date_today), "desc": f"महीने का पेमेंट", 
                "type": pay_type, "amount": total_payable
            })
            # Record Fine
            if fine_amount > 0:
                st.session_state.ledger.append({
                    "name": col_name, "date": str(date_today), "desc": f"{days_late} दिन का लेट फाइन", 
                    "type": "Fine Paid", "amount": fine_amount
                })
            
            # Reduce Month from EMI if applicable
            if is_emi_payer:
                st.session_state.active_loans[col_name]['months_left'] -= 1
                if st.session_state.active_loans[col_name]['months_left'] <= 0:
                    del st.session_state.active_loans[col_name] # Loan fully paid!
                    st.balloons()
                    st.success("🎉 बधाई हो! इस मेंबर का लोन पूरी तरह चुकता हो गया है।")
                
            # Profit Distribution
            profit_generated = 0
            if is_emi_payer: profit_generated += st.session_state.active_loans.get(col_name, loan_details)['monthly_interest']
            if fine_amount > 0: profit_generated += fine_amount
                
            if profit_generated > 0:
                eligible_for_profit = [m['name'] for m in st.session_state.members_db if m['name'] not in st.session_state.active_loans]
                if eligible_for_profit:
                    per_head_profit = profit_generated / len(eligible_for_profit)
                    for emp in eligible_for_profit:
                        st.session_state.ledger.append({
                            "name": emp, "date": str(date_today), 
                            "desc": f"प्रॉफिट शेयर (Source: {col_name})", 
                            "type": "Profit Share", "amount": round(per_head_profit, 2)
                        })
                    st.success(f"✅ पेमेंट सेव हुआ! और प्रॉफिट (₹ {profit_generated}) सभी योग्य मेंबर्स में बाँट दिया गया है।")
                else:
                    st.success("✅ पेमेंट सेव हुआ! (प्रॉफिट बांटने के लिए कोई योग्य मेंबर नहीं बचा)")
            else:
                st.success("✅ पेमेंट सफलतापूर्वक सेव हो गया!")

# ------------------------------------------
# DASHBOARD PAGE
# ------------------------------------------
elif choice == "📊 डैशबोर्ड":
    st.header("📊 कमिटी समरी")
    
    t_mems = len(st.session_state.members_db)
    act_loans = len(st.session_state.active_loans)
    defaulters = len([m for m in st.session_state.members_db if m['status'] != 'Active'])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("कुल मेंबर्स", t_mems)
    c2.metric("चल रहे लोन (EMI)", act_loans)
    c3.metric("डिफॉल्टर (Inactive)", defaulters)
    
    st.markdown("---")
    st.subheader("हाल के लेन-देन (Recent Transactions)")
    if st.session_state.ledger:
        recent = pd.DataFrame(st.session_state.ledger).iloc[::-1].head(10)
        st.dataframe(recent, use_container_width=True)
    else:
        st.write("कोई लेन-देन नहीं है।")
