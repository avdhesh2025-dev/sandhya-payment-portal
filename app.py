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

# Custom CSS for Mobile friendly & Excel look
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #ffffff;
        color: #1f2937;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
        font-weight: bold;
        font-size: 14px;
        height: 50px;
        transition: all 0.1s ease-in-out;
    }
    div.stButton > button:active {
        background-color: #f3f4f6;
    }
    .main { padding-top: 1rem; }
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

def get_whatsapp_link(mobile, message):
    encoded_msg = urllib.parse.quote(message)
    if not str(mobile).startswith("91") and mobile != "": mobile = f"91{mobile}"
    return f"https://wa.me/{mobile}?text={encoded_msg}"

# ==========================================
# 2. SESSION STATE
# ==========================================
if 'auth_status' not in st.session_state: st.session_state.auth_status = False
if 'role' not in st.session_state: st.session_state.role = None
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
                "identity_num": "[Aadhaar Redacted]",
                "pan": str(row.get('PAN') or row.get('pan', '')),
                "upi": str(row.get('UPI') or row.get('upi', '')),
                "address": str(row.get('Address') or row.get('address', '')),
                "status": "✅ Active"
            })

# Tracking dictionary for who paid this month
if 'payment_status' not in st.session_state:
    st.session_state.payment_status = {m['name']: "❌ Pending" for m in st.session_state.members_db}

if 'ledger_transactions' not in st.session_state: st.session_state.ledger_transactions = []

# ==========================================
# 3. LOGIN
# ==========================================
if not st.session_state.auth_status:
    st.title("🔒 सिक्योर लॉगिन")
    with st.form("login_form"):
        username = st.text_input("यूज़रनेम (admin)")
        password = st.text_input("पासवर्ड (9557)", type="password")
        if st.form_submit_button("लॉगिन करें", use_container_width=True):
            if username == "admin" and hashlib.sha256(password.encode()).hexdigest() == ADMIN_HASH:
                st.session_state.auth_status = True
                st.session_state.role = "Admin"
                st.rerun()
            else:
                st.error("❌ गलत विवरण!")
    st.stop()

# ==========================================
# 4. MENUS (MOBILE FRIENDLY)
# ==========================================
st.sidebar.title("🏢 Sandhya ERP")
if st.sidebar.button("🔄 रिफ्रेश"): st.rerun()
if st.sidebar.button("🚪 लॉग आउट"):
    st.session_state.auth_status = False
    st.rerun()

st.markdown("### 💸 Digital Committee Manager")

# Mobile optimized menu - 2 buttons per row
c1, c2 = st.columns(2)
if c1.button("📊 डैशबोर्ड", use_container_width=True): st.session_state.page = "Dashboard"
if c2.button("📱 कलेक्शन & QR", use_container_width=True): st.session_state.page = "Collection"

c3, c4 = st.columns(2)
if c3.button("📝 Excel लेज़र", use_container_width=True): st.session_state.page = "Ledger"
if c4.button("👤 नया मेंबर", use_container_width=True): st.session_state.page = "Add_Member"

st.divider()

# ==========================================
# 5. PAGES
# ==========================================

if st.session_state.page == "Dashboard":
    st.header("📊 समरी")
    total_mem = len(st.session_state.members_db)
    txns = st.session_state.ledger_transactions
    total_coll = sum(t['credit'] for t in txns)
    total_loan = sum(t['debit'] for t in txns)
    run_bal = total_coll - total_loan
    
    m1, m2 = st.columns(2)
    m1.metric("टोटल मेंबर्स", f"{total_mem} / 50")
    m2.metric("एडमिन फंड (₹10/सदस्य)", f"₹ {total_mem * 10}")
    
    m3, m4 = st.columns(2)
    m3.metric("कुल जमा", f"₹ {total_coll}")
    m4.metric("रनिंग बैलेंस", f"₹ {run_bal}")

# ----------------------------------------------------
# 🌟 नया फीचर: कलेक्शन & QR मास्टर हब 
# ----------------------------------------------------
elif st.session_state.page == "Collection":
    st.header("📱 कलेक्शन, QR & पेमेंट ट्रैकिंग")
    st.info("यहाँ से विनर का QR बनाएँ, ग्रुप में शेयर करें और स्क्रीनशॉट आने पर टिक करें।")
    
    if len(st.session_state.members_db) > 0:
        # 1. विजेता चुनें
        winner_name = st.selectbox("इस महीने किसको पैसा देना है? (विजेता चुनें)", [m['name'] for m in st.session_state.members_db])
        winner_details = next((m for m in st.session_state.members_db if m['name'] == winner_name), None)
        
        c1, c2 = st.columns(2)
        winner_upi = c1.text_input("विजेता का UPI ID", value=winner_details['upi'] if winner_details else "")
        amount_to_collect = c2.number_input("प्रति मेंबर कलेक्शन (₹)", value=2000)
        
        if winner_upi:
            st.markdown("### 📷 पेमेंट QR कोड")
            qr_col, text_col = st.columns([1, 1.5])
            with qr_col:
                qr_img = generate_qr(winner_upi, winner_name)
                st.image(qr_img, width=180, caption=f"पेमेंट करें: {winner_name}")
            
            with text_col:
                st.success(f"**UPI ID:** {winner_upi}")
                # WhatsApp Share Message
                msg = f"नमस्कार, इस महीने की कमिटी *{winner_name}* को जा रही है।\nकृपया *₹{amount_to_collect}* इस UPI पर भेजें: {winner_upi}\n\nपेमेंट के बाद मुझे *स्क्रीनशॉट* जरूर भेजें ताकि मैं सिस्टम में आपका नाम अपडेट कर सकूँ।"
                wa_link = get_whatsapp_link("", msg) # Empty mobile opens contact list picker in WhatsApp
                st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; border-radius:8px; padding:10px; border:none; width:100%;">💬 ग्रुप/मेंबर्स को WhatsApp पर QR और मैसेज भेजें</button></a>', unsafe_allow_html=True)

        st.divider()
        
        # 2. स्क्रीनशॉट ट्रैकिंग (Excel Like Status Checker)
        st.subheader("✅ पेमेंट स्क्रीनशॉट ट्रैकिंग")
        st.write("जिनका स्क्रीनशॉट आ जाए, उनके आगे 'Paid' टिक करें:")
        
        # Convert dictionary to DataFrame for easy editing
        status_list = [{"Name": k, "Status": v == "✅ Paid"} for k, v in st.session_state.payment_status.items()]
        df_status = pd.DataFrame(status_list)
        
        # Data Editor for quick ticking
        edited_status = st.data_editor(
            df_status, 
            column_config={"Name": "मेंबर का नाम", "Status": st.column_config.CheckboxColumn("पैसा आ गया? (Tick)")},
            disabled=["Name"],
            hide_index=True,
            use_container_width=True
        )
        
        # Save button for status
        if st.button("स्टेटस सेव करें", use_container_width=True):
            for index, row in edited_status.iterrows():
                st.session_state.payment_status[row["Name"]] = "✅ Paid" if row["Status"] else "❌ Pending"
            st.success("✅ सभी मेंबर्स का पेमेंट स्टेटस अपडेट हो गया!")

    else:
        st.warning("⚠️ पहले मेंबर रजिस्टर करें।")

# ----------------------------------------------------
# 🌟 नया फीचर: EXCEL जैसा बैंक लेज़र
# ----------------------------------------------------
elif st.session_state.page == "Ledger":
    st.header("📝 Excel लेज़र (पासबुक एंट्री)")
    
    if len(st.session_state.members_db) > 0:
        sel_mem = st.selectbox("अकाउंट (फाइल) खोलने के लिए मेंबर चुनें:", [m['name'] for m in st.session_state.members_db])
        st.info("💡 **टिप:** नीचे दी गई शीट बिल्कुल Excel की तरह काम करती है। सबसे नीचे खाली लाइन (Row) में क्लिक करके आप सीधे नई एंट्री कर सकते हैं या पुरानी एंट्री बदल सकते हैं।")
        
        # Filter transactions for this member
        member_txns = [t for t in st.session_state.ledger_transactions if t['name'] == sel_mem]
        
        # Create a DataFrame
        if len(member_txns) > 0:
            df_txns = pd.DataFrame(member_txns)
        else:
            # Empty structure if no txns
            df_txns = pd.DataFrame(columns=["name", "date", "विवरण", "credit", "debit", "balance"])
            
        # Clean up columns for display
        display_df = df_txns[["date", "विवरण", "credit", "debit", "balance"]].copy()
        
        # 🌟 MAGIC: st.data_editor allows Excel-like adding and editing of rows
        edited_df = st.data_editor(
            display_df,
            num_rows="dynamic", # Allows adding/deleting rows!
            column_config={
                "date": st.column_config.DateColumn("तारीख", format="YYYY-MM-DD"),
                "विवरण": st.column_config.TextColumn("विवरण (Note)"),
                "credit": st.column_config.NumberColumn("जमा (Credit)", min_value=0.0, format="₹ %f"),
                "debit": st.column_config.NumberColumn("निकासी (Debit)", min_value=0.0, format="₹ %f"),
                "balance": st.column_config.NumberColumn("बैलेंस", format="₹ %f")
            },
            use_container_width=True,
            height=300
        )
        
        # Save the Excel edits back to the main database
        if st.button("💾 लेज़र में बदलाव सेव करें", use_container_width=True):
            # First, remove old transactions for this member
            st.session_state.ledger_transactions = [t for t in st.session_state.ledger_transactions if t['name'] != sel_mem]
            
            # Reconstruct and add the edited transactions
            for index, row in edited_df.iterrows():
                # Handling empty rows that might be added
                if pd.notna(row.get('date')) and pd.notna(row.get('विवरण')): 
                    st.session_state.ledger_transactions.append({
                        "name": sel_mem,
                        "date": str(row['date'])[:10], # format date string
                        "विवरण": str(row['विवरण']),
                        "credit": float(row['credit']) if pd.notna(row['credit']) else 0.0,
                        "debit": float(row['debit']) if pd.notna(row['debit']) else 0.0,
                        "balance": float(row['balance']) if pd.notna(row['balance']) else 0.0
                    })
            st.success("✅ फाइल (लेज़र) में डेटा सफलता से सेव हो गया!")
            st.rerun()
            
    else:
        st.warning("⚠️ पहले मेंबर रजिस्टर करें।")

elif st.session_state.page == "Add_Member":
    st.header("👤 नया मेंबर रजिस्ट्रेशन")
    with st.form("add_mem_form", clear_on_submit=True):
        name = st.text_input("पूरा नाम *")
        mobile = st.text_input("मोबाइल नंबर *")
        upi_id = st.text_input("UPI ID (कमिटी का पैसा लेने के लिए) *")
        identity = st.text_input("Aadhaar Number * (12 Digits)")
        pan = st.text_input("PAN Card")
        address = st.text_area("पूरा पता")
            
        if st.form_submit_button("मेंबर सेव करें", use_container_width=True):
            if not name or not mobile or not upi_id:
                st.error("⚠️ नाम, मोबाइल और UPI ID अनिवार्य हैं!")
            else:
                m_id = f"SE{len(st.session_state.members_db)+1:04d}"
                st.session_state.members_db.append({
                    "id": m_id, "name": name, "mobile": mobile, 
                    "identity_num": "[Aadhaar Redacted]", "pan": pan, 
                    "address": address, "upi": upi_id, "status": "✅ Active"
                })
                st.session_state.payment_status[name] = "❌ Pending"
                st.session_state.ledger_transactions.append({
                    "name": name, "date": str(datetime.date.today()), "विवरण": "रजिस्ट्रेशन & मेंटेनेंस", "credit": 2010.0, "debit": 0.0, "balance": 2010.0
                })
                st.success(f"✅ {name} जुड़ गए!")
