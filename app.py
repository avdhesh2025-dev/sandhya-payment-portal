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

# 👉 आपका नया Google Apps Script URL यहाँ अपडेट कर दिया गया है 👈
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby7WHaNevFEemxTbL2FT9r05vhDxCywARHSfXy_xbwoQW6wInjeyn-Sih93zz7Vs2ZyVw/exec"

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
    st.session_state.members_db = [] # List of member dictionaries
if 'ledger' not in st.session_state:
    st.session_state.ledger = [] # Format: {name, date, desc, type(deposit/loan/fine/emi/profit), amount}
if 'active_loans' not in st.session_state:
    st.session_state.active_loans = {} # Track EMIs for members

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
# Navigation
menu_opts = ["📊 डैशबोर्ड", "👤 नया मेंबर जोड़ें", "📂 मेंबर प्रोफाइल & लेज़र", "💰 कमिटी विनर & QR", "💸 मंथली कलेक्शन & EMI"]
choice = st.sidebar.radio("मेनू चुनें:", menu_opts)

# ==========================================
# 5. PAGE LOGIC
# ==========================================

# ------------------------------------------
# PAGE 1: ADD MEMBER
# ------------------------------------------
if choice == "👤 नया मेंबर जोड़ें":
    st.header("👤 नया मेंबर रजिस्ट्रेशन (Unique Validation)")
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
                # 1. Unique Checks
                existing_mobiles = [m['mobile'] for m in st.session_state.members_db]
                existing_pans = [m['pan'].upper() for m in st.session_state.members_db]
                existing_aadhaars = [m['aadhaar'] for m in st.session_state.members_db]
                
                if mobile in existing_mobiles:
                    st.error("❌ यह मोबाइल नंबर पहले से जुड़ा हुआ है!")
                elif pan.upper() in existing_pans:
                    st.error("❌ यह PAN नंबर पहले से मौजूद है!")
                elif aadhaar in existing_aadhaars:
                    st.error("❌ यह Aadhar नंबर पहले से उपयोग में है!")
                else:
                    m_id = f"SE{len(st.session_state.members_db)+1:04d}"
                    new_mem = {
                        "id": m_id, "name": name, "father_name": father_name, "mobile": mobile,
                        "aadhaar": aadhaar, "pan": pan.upper(), "upi": upi_id,
                        "address": address, "dob": str(dob), "gender": gender,
                        "photo": photo, "status": "Active" # Active / Inactive(Defaulter)
                    }
                    
                    # 2. Google Sheet में डेटा भेजना
                    payload = {
                        "action": "add_member", "member_id": m_id, "name": name, 
                        "father_name": father_name, "mobile": mobile, "dob": str(dob), 
                        "gender": gender, "aadhaar": "[Aadhaar Redacted]", "pan": pan.upper(), 
                        "upi": upi_id, "address": address, "status": "Active"
                    }
                    try: requests.post(APPS_SCRIPT_URL, json=payload)
                    except: pass
                    
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
        # Display Dropdown to select member
        mem_names = [m['name'] for m in st.session_state.members_db]
        selected_name = st.selectbox("प्रोफाइल देखने के लिए मेंबर चुनें:", mem_names)
        
        # Find Member details
        member_idx = next(i for i, m in enumerate(st.session_state.members_db) if m['name'] == selected_name)
        mem = st.session_state.members_db[member_idx]
        
        st.markdown("---")
        c1, c2, c3 = st.columns([1,2,2])
        with c1:
            if mem['photo']: st.image(mem['photo'], width=120)
            else: st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=120)
            
            # Defaulter / Inactive Toggle
            is_active = st.toggle("✅ Active Member", value=(mem['status'] == "Active"))
            new_status = "Active" if is_active else "Defaulter (Inactive)"
            
            if mem['status'] != new_status:
                st.session_state.members_db[member_idx]['status'] = new_status
                st.rerun()
                
            if new_status == "Active":
                st.success(new_status)
            else:
                st.error("❌ " + new_status)

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
            
        st.subheader("📊 व्यक्तिगत लेज़र (Ledger)")
        # Calculate Ledger Math
        my_txns = [t for t in st.session_state.ledger if t['name'] == mem['name']]
        total_deposited = sum(t['amount'] for t in my_txns if t['type'] in ['Monthly Deposit', 'EMI Paid'])
        total_taken = sum(t['amount'] for t in my_txns if t['type'] == 'Loan Taken')
        total_fine_paid = sum(t['amount'] for t in my_txns if t['type'] == 'Fine Paid')
        profit_earned = sum(t['amount'] for t in my_txns if t['type'] == 'Profit Share')
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("कुल जमा किया", f"₹ {total_deposited}")
        col2.metric("कमिटी से लिया (लोन)", f"₹ {total_taken}")
        col3.metric("प्रॉफिट मिला", f"₹ {profit_earned}")
        col4.metric("लेट फाइन भरा", f"₹ {total_fine_paid}")
        
        if my_txns:
            st.dataframe(pd.DataFrame(my_txns)[['date', 'desc', 'type', 'amount']], use_container_width=True)
        else:
            st.info("अभी कोई लेन-देन नहीं हुआ है।")

# ------------------------------------------
# PAGE 3: COMMITTEE WINNER & QR GENERATOR
# ------------------------------------------
elif choice == "💰 कमिटी विनर & QR":
    st.header("🏆 कमिटी विनर (4 तारीख को QR शेयरिंग)")
    st.info("यहाँ से उस मेंबर को चुनें जिसे इस महीने पैसे देने हैं। सिस्टम उसका EMI बनाएगा और ग्रुप के लिए QR जनरेट करेगा।")
    
    if not st.session_state.members_db:
        st.warning("मेंबर मौजूद नहीं हैं।")
    else:
        # Only Active members can take the loan
        eligible_members = [m for m in st.session_state.members_db if m['status'] == "Active"]
        defaulters = [m['name'] for m in st.session_state.members_db if m['status'] != "Active"]
        
        if defaulters:
            st.error(f"❌ Defaulter (लोन नहीं ले सकते): {', '.join(defaulters)}")
            
        if eligible_members:
            winner_name = st.selectbox("कमिटी विजेता चुनें:", [m['name'] for m in eligible_members])
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            total_pool = len(st.session_state.members_db) * 2000
            with c1:
                st.write(f"**कमिटी का कुल फंड (Total Pool):** ₹ {total_pool}")
                tenure = st.selectbox("लोन की अवधि चुनें (महीने)", [6, 12, 18, 24])
                interest_rate = 2.0 # Fixed 2% per month
                
            with c2:
                # 2% per month interest
                monthly_interest = (total_pool * interest_rate) / 100
                monthly_principal = total_pool / tenure
                emi = monthly_principal + monthly_interest
                
                st.success(f"**प्रति माह 2% ब्याज:** ₹ {monthly_interest}")
                st.error(f"**विजेता की नई EMI:** ₹ {emi} (अगले {tenure} महीनों तक)")

            if st.button("✅ लोन पास करें और QR जनरेट करें", use_container_width=True):
                winner_upi = next(m['upi'] for m in eligible_members if m['name'] == winner_name)
                
                # Update Active Loan State
                st.session_state.active_loans[winner_name] = {
                    "principal": total_pool,
                    "emi": emi,
                    "months_left": tenure,
                    "monthly_interest": monthly_interest
                }
                
                # Ledger entry for taking loan
                entry = {
                    "name": winner_name, "date": str(datetime.date.today()), 
                    "desc": f"{tenure} महीने के लिए कमिटी उठाई", "type": "Loan Taken", "amount": total_pool
                }
                st.session_state.ledger.append(entry)
                
                # Google Sheet में भेजना
                try: 
                    requests.post(APPS_SCRIPT_URL, json={"action": "add_ledger", **entry})
                except: pass
                
                st.session_state.current_winner_qr = {
                    "name": winner_name, "upi": winner_upi, "amount": 2000 # 2000 to be sent by everyone
                }
                st.success("लोन पास हो गया है!")

            # Display QR Code if generated
            if hasattr(st.session_state, 'current_winner_qr'):
                qr_data = st.session_state.current_winner_qr
                st.divider()
                st.subheader(f"📲 {qr_data['name']} का पेमेंट QR")
                
                q_col, t_col = st.columns([1,2])
                with q_col:
                    img = generate_qr(qr_data['upi'], qr_data['name'], qr_data['amount'])
                    st.image(img, width=200)
                with t_col:
                    st.warning("⚠️ **ज़रूरी सूचना:** यह QR कोड 5 तारीख को रात 9:00 बजे तक ही मान्य है। उसके बाद पेमेंट करने पर फाइन लगेगा।")
                    wa_msg = f"इस महीने की कमिटी *{qr_data['name']}* को दी जा रही है।\nकृपया ₹2000 इस UPI पर भेजें: {qr_data['upi']}\n\n*ध्यान दें:* 5 तारीख रात 9 बजे से पहले स्क्रीनशॉट भेजें, अन्यथा फाइन लगेगा।"
                    link = get_whatsapp_link(wa_msg)
                    st.markdown(f'<a href="{link}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:8px; padding:10px; border:none;">💬 ग्रुप में WhatsApp पर भेजें</button></a>', unsafe_allow_html=True)
        else:
            st.warning("कोई भी एक्टिव मेंबर नहीं है जो लोन ले सके।")

# ------------------------------------------
# PAGE 4: MONTHLY COLLECTION, EMI & FINE
# ------------------------------------------
elif choice == "💸 मंथली कलेक्शन & EMI":
    st.header("💸 मंथली कलेक्शन (5 तारीख) & लेट फाइन")
    st.write("यहाँ से चेक करें कि किसने पैसे दिए, किसने EMI दी और किसने लेट किया।")
    
    date_today = st.date_input("आज की तारीख", datetime.date.today())
    # Assuming collection date is 5th of current month
    due_date = datetime.date(date_today.year, date_today.month, 5)
    days_late = (date_today - due_date).days if (date_today - due_date).days > 0 else 0
    
    st.info(f"**मंथली ड्यू डेट:** 5 तारीख | **आज के हिसाब से दिन लेट:** {days_late} दिन")
    
    if st.session_state.members_db:
        st.subheader("✅ कलेक्शन एंट्री")
        
        col_name = st.selectbox("पैसा जमा करने वाले का नाम:", [m['name'] for m in st.session_state.members_db])
        
        # Determine what this person has to pay
        is_emi_payer = col_name in st.session_state.active_loans
        base_due = 2000
        
        if is_emi_payer:
            loan_details = st.session_state.active_loans[col_name]
            total_payable = loan_details['emi']
            pay_type = "EMI Paid"
            st.warning(f"इस मेंबर पर लोन चल रहा है। इनकी इस महीने की EMI ₹ {total_payable} है।")
        else:
            total_payable = base_due
            pay_type = "Monthly Deposit"
            st.success(f"इस मेंबर को अपनी मंथली जमा राशि ₹ {total_payable} देनी है।")
            
        # Calculate Fine
        fine_amount = 0
        if days_late > 0:
            if days_late <= 6:
                fine_amount = days_late * 20
                st.error(f"लेट फाइन: {days_late} दिन x ₹20 = ₹ {fine_amount}")
            else:
                fine_amount = (total_payable * 3) / 100
                st.error(f"7+ दिन लेट! टोटल अमाउंट का 3% फाइन = ₹ {fine_amount}")
                
        actual_paid = st.number_input("वास्तव में कितना पैसा दिया?", value=float(total_payable + fine_amount))
        
        if st.button("पेमेंट कन्फर्म करें (लेज़र में जोड़ें)"):
            # 1. Record Main Payment
            entry1 = {"name": col_name, "date": str(date_today), "desc": f"महीने का पेमेंट", "type": pay_type, "amount": total_payable}
            st.session_state.ledger.append(entry1)
            try: requests.post(APPS_SCRIPT_URL, json={"action": "add_ledger", **entry1})
            except: pass
            
            # 2. Record Fine if collected
            if fine_amount > 0:
                entry2 = {"name": col_name, "date": str(date_today), "desc": f"{days_late} दिन का लेट फाइन", "type": "Fine Paid", "amount": fine_amount}
                st.session_state.ledger.append(entry2)
                try: requests.post(APPS_SCRIPT_URL, json={"action": "add_ledger", **entry2})
                except: pass
                
            # PROFIT DISTRIBUTION (Fine and Interest)
            profit_generated = 0
            if is_emi_payer:
                profit_generated += st.session_state.active_loans[col_name]['monthly_interest']
            if fine_amount > 0:
                profit_generated += fine_amount
                
            if profit_generated > 0:
                # Distribute equally among all EXCLUDING the active loan takers
                eligible_for_profit = [m['name'] for m in st.session_state.members_db if m['name'] not in st.session_state.active_loans]
                if eligible_for_profit:
                    per_head_profit = profit_generated / len(eligible_for_profit)
                    for emp in eligible_for_profit:
                        entry3 = {"name": emp, "date": str(date_today), "desc": f"ब्याज/फाइन का प्रॉफिट शेयर (Source: {col_name})", "type": "Profit Share", "amount": round(per_head_profit, 2)}
                        st.session_state.ledger.append(entry3)
                        try: requests.post(APPS_SCRIPT_URL, json={"action": "add_ledger", **entry3})
                        except: pass
                    st.success(f"✅ पेमेंट सेव हुआ! और प्रॉफिट (₹ {profit_generated}) सभी योग्य {len(eligible_for_profit)} मेंबर्स में बाँट दिया गया है।")
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
    st.subheader("हाल के लेन-देन")
    if st.session_state.ledger:
        # Show last 10 entries reversed
        recent = pd.DataFrame(st.session_state.ledger).iloc[::-1].head(10)
        st.dataframe(recent, use_container_width=True)
    else:
        st.write("कोई लेन-देन नहीं है।")
