import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
import re
from PIL import Image, ImageOps

# 1. Page Configuration & Professional 3D A4 Design
st.set_page_config(page_title="Cyber Safe Payment Portal", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main .block-container { 
        background-color: #ffffff; padding: 2rem 3rem; border-radius: 15px; 
        max-width: 850px; box-shadow: 0px 10px 40px rgba(0,0,0,0.2); margin: auto;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        box-shadow: inset 3px 3px 6px rgba(0,0,0,0.1); border-radius: 10px !important;
        background-color: #f0f4f8 !important; border: 1px solid #cbd5e1 !important;
        font-weight: bold; font-size: 18px !important; color: #1e293b !important;
    }
    .red-alert { background-color: #fff1f2; color: #be123c; padding: 20px; border-left: 8px solid #be123c; border-radius: 10px; font-weight: bold; font-size: 18px; margin-bottom: 25px; box-shadow: 2px 4px 10px rgba(0,0,0,0.1); }
    .green-alert { background-color: #f0fdf4; color: #15803d; padding: 20px; border-left: 8px solid #15803d; border-radius: 10px; font-weight: bold; font-size: 18px; margin-bottom: 25px; box-shadow: 2px 4px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 FIXED WEBHOOK AND SHEET ID
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
# ==========================================

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# 🟢 MAGIC LOGIC: TARGETED ZOOM SCANNING
def extract_magic_data(img):
    if not HAS_OCR: return {}
    
    # Image Cleanup
    img_gray = ImageOps.grayscale(img)
    full_text = pytesseract.image_to_string(img_gray, config='--psm 11')
    res = {}

    # 1. Extract UTR First (Anchor)
    utr_match = re.search(r'\b([0-9]{12})\b', full_text)
    if utr_match:
        res['utr'] = utr_match.group(1)
        
    # 2. Extract Date/Time
    dt_match = re.search(r'(\d{1,2}:\d{2}\s*[APM]+\s*on\s*\d{1,2}\s*[A-Za-z]+\s*\d{4})', full_text, re.IGNORECASE)
    if dt_match: res['date'] = dt_match.group(1).replace("on", "").strip()

    # 3. Extract Amount (Looking for ₹ or comma)
    amt_match = re.findall(r'[₹Rs]\s*([0-9,]{2,10})', full_text)
    if amt_match: res['amount'] = float(amt_match[-1].replace(',', ''))

    # 4. MAGIC FIX FOR DEBITED 4 DIGITS
    # Logic: Convert to pure numbers, block receiver IDs, take the last one
    blocked = re.findall(r'(\d{4})@', full_text) # Receiver ID like 8890
    nums = re.findall(r'\b(\d{4})\b', full_text)
    
    clean_nums = []
    for n in nums:
        if n in ['2024', '2025', '2026', '2027']: continue # Year filter
        if n in blocked: continue # Receiver filter
        if 'amount' in res and n == str(int(res['amount'])): continue # Amount filter
        clean_nums.append(n)

    if clean_nums:
        # Most PhonePe receipts list sender at the absolute bottom
        res['sender'] = clean_nums[-1]

    return res

# 🟢 DATABASE SYNC
@st.cache_data(ttl=1)
def sync_db(name, cols):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={name}&cb={int(time.time())}"
    try:
        df = pd.read_csv(url).dropna(how="all").fillna("")
        df.columns = [str(c).replace(" ", "").strip() for c in df.columns]
        return df
    except: return pd.DataFrame(columns=cols)

st.session_state.auth_retailers = sync_db("Authorized_Retailers", ["RetailerName", "Mobile", "Auth_UPI"])
st.session_state.payment_ledger = sync_db("Payment_Ledger", ["Date", "RetailerName", "Amount", "Mode", "SenderUPI_Mobile", "Status", "Reference"])

# Header
st.markdown("<div style='background: linear-gradient(90deg, #b91c1c 0%, #ef4444 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; margin-bottom: 30px;'><h1 style='margin:0; font-size: 36px;'>🛡️ CYBER-SAFE PAYMENT PORTAL</h1><p style='margin:5px 0 0 0; font-size: 18px;'>Sandhya Enterprises - Authorized Business Only</p></div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💰 Register Payment", "📋 Transaction Ledger", "🛡️ Manage Retailers"])

with tab1:
    if st.button("🔄 Sync with Google Sheet"): st.rerun()
    
    st.info("📸 **Magic OCR Activated:** स्लिप अपलोड करें। अब यह एक्सिस बैंक के लोगो को इग्नोर करके सीधा आपका नंबर पकड़ेगा।")
    up_file = st.file_uploader("Upload Slip", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    if up_file:
        with st.spinner("AI Magic Scanning..."):
            extracted = extract_magic_data(Image.open(up_file))
            if extracted:
                st.session_state.f_amt = extracted.get('amount', 0.0)
                st.session_state.f_utr = extracted.get('utr', '')
                st.session_state.f_snd = extracted.get('sender', '')
                st.session_state.f_dat = extracted.get('date', datetime.now().strftime("%d-%m-%Y %I:%M %p"))
                st.success("✅ स्लिप स्कैन हो गई! नीचे चेक करें।")

    with st.form("p_form"):
        f_date = st.text_input("📅 Date & Time*", value=st.session_state.get('f_dat', datetime.now().strftime("%d-%m-%Y %I:%M %p")))
        c1, c2 = st.columns(2)
        with c1:
            ret_list = ["-- Select Retailer --"] + st.session_state.auth_retailers["RetailerName"].tolist()
            sel_ret = st.selectbox("👤 Select Retailer*", ret_list)
            f_amt = st.number_input("Amount (Rs)*", value=float(st.session_state.get('f_amt', 0.0)))
            f_rem = st.selectbox("📝 Remark*", ["eTop", "JPB", "Other"])
        with c2:
            st.write("💳 **Payment: UPI / Online**")
            f_snd = st.text_input("Sender Bank 4-Ank*", value=st.session_state.get('f_snd', ''))
            f_utr = st.text_input("UTR Number*", value=st.session_state.get('f_utr', ''))
        
        if st.form_submit_button("🔍 VERIFY & SAVE TO SHEET", use_container_width=True, type="primary"):
            if sel_ret == "-- Select Retailer --" or f_amt <= 0:
                st.error("❌ कृपया नाम और अमाउंट चेक करें।")
            else:
                # Security Check
                auth_data = st.session_state.auth_retailers[st.session_state.auth_retailers["RetailerName"] == sel_ret].iloc[0]
                is_safe = f_snd in str(auth_data["Auth_UPI"]) or f_snd in str(auth_data["Mobile"])
                status = "Verified (Safe)" if is_safe else "UNVERIFIED (Danger)"
                
                payload = {"sheet_name": "Payment_Ledger", "Date": f_date, "RetailerName": sel_ret, "Amount": f_amt, "Mode": "UPI", "SenderUPI_Mobile": f_snd, "Status": status, "Reference": f"{f_rem} (UTR: {f_utr})"}
                
                requests.post(WEBHOOK_URL, json=payload, timeout=10)
                if not is_safe:
                    st.markdown(f"<div class='red-alert'>🚨 **RED ALERT:** यह पेमेंट {sel_ret} के रजिस्टर्ड नंबर से नहीं आया है!</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='green-alert'>✅ **SAFE PAYMENT:** डेटा सेव कर लिया गया है।</div>", unsafe_allow_html=True)
                time.sleep(2)
                st.rerun()

with tab2:
    st.dataframe(st.session_state.payment_ledger, use_container_width=True)

with tab3:
    with st.form("add_r"):
        n1, n2, n3 = st.columns(3)
        name = n1.text_input("Name")
        mob = n2.text_input("Mobile")
        upi = n3.text_input("Bank 4-Digit")
        if st.form_submit_button("Add Retailer"):
            requests.post(WEBHOOK_URL, json={"sheet_name": "Authorized_Retailers", "RetailerName": name.upper(), "Mobile": mob, "Auth_UPI": upi})
            st.rerun()
