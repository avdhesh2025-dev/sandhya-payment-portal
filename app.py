import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
import re
from PIL import Image, ImageOps, ImageEnhance

# 1. Page Configuration & UI
st.set_page_config(page_title="Cyber Safe Payment Portal", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main .block-container { 
        background-color: #ffffff; padding: 2rem; border-radius: 15px; 
        max-width: 850px; box-shadow: 0px 10px 40px rgba(0,0,0,0.1); margin: auto;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.05); border-radius: 8px !important;
        background-color: #f8fafc !important; border: 1px solid #cbd5e1 !important;
        font-weight: bold; font-size: 16px !important;
    }
    .red-alert { background-color: #fef2f2; color: #dc2626; padding: 15px; border-left: 6px solid #dc2626; border-radius: 8px; font-weight: bold; margin-bottom: 20px; }
    .green-alert { background-color: #f0fdf4; color: #16a34a; padding: 15px; border-left: 6px solid #16a34a; border-radius: 8px; font-weight: bold; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# Webhook Details
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# 🟢 ADVANCED X-RAY PROCESSING AI
def extract_data_advanced(img):
    if not HAS_OCR: return {}
    
    # STEP 1: X-RAY PRE-PROCESSING (Cleans screen reflections)
    img = img.convert('L') # GrayScale
    img = ImageOps.autocontrast(img) # Contrast badhao
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0) # Sharpness badhao
    
    # STEP 2: Read with Scattered Text Logic
    text = pytesseract.image_to_string(img, config='--psm 11')
    res = {}

    # 1. Date/Time
    dt_match = re.search(r'(\d{1,2}:\d{2}\s*[APM]+\s*on\s*\d{1,2}\s*[A-Za-z]+\s*\d{4})', text, re.IGNORECASE)
    if dt_match: res['date'] = dt_match.group(1).replace("on", "").strip()

    # 2. UTR (12 Digits)
    utr_match = re.search(r'\b(\d{12})\b', text)
    if utr_match: res['utr'] = utr_match.group(1)

    # 3. Amount (Look for ₹ or comma)
    amt_match = re.findall(r'[₹Rs]\s*([0-9,]{2,10})', text)
    if amt_match: res['amount'] = float(amt_match[-1].replace(',', ''))

    # 4. SENDER 4-DIGIT (The "Debited" Section Logic)
    lower_text = text.lower()
    if "debited" in lower_text:
        # 'debited from' ke baad waala hissa hi scan karo
        start_scan = lower_text.find("debited")
        target_text = text[start_scan : start_scan + 200] 
        nums = re.findall(r'\b(\d{4})\b', target_text)
        # Year aur amount filter karo
        valid = [n for n in nums if n not in ['2024','2025','2026','2027']]
        if valid: res['sender'] = valid[0]

    # Fallback if Debited logic fails
    if 'sender' not in res:
        blocked = re.findall(r'(\d{4})@', text)
        nums = re.findall(r'\b(\d{4})\b', text)
        clean = [n for n in nums if n not in ['2024','2025','2026','2027'] and n not in blocked]
        if clean: res['sender'] = clean[-1]

    return res

# Database Load
@st.cache_data(ttl=1)
def load_db(name, cols):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={name}&cb={int(time.time())}"
    try:
        df = pd.read_csv(url).dropna(how="all").fillna("")
        df.columns = [str(c).replace(" ", "").strip() for c in df.columns]
        return df
    except: return pd.DataFrame(columns=cols)

st.session_state.auth_retailers = load_db("Authorized_Retailers", ["RetailerName", "Mobile", "Auth_UPI"])
st.session_state.payment_ledger = load_db("Payment_Ledger", ["Date", "RetailerName", "Amount", "Mode", "SenderUPI_Mobile", "Status", "Reference"])

# Header
st.markdown("<div style='background: linear-gradient(90deg, #b91c1c 0%, #ef4444 100%); padding: 25px; border-radius: 12px; text-align: center; color: white; margin-bottom: 25px;'><h1 style='margin:0; font-size: 32px;'>🛡️ CYBER-SAFE PAYMENT PORTAL</h1><p style='margin:5px 0 0 0; font-size: 16px;'>Sandhya Enterprises - Smart Verification</p></div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💰 Register Payment", "📋 Ledger", "🛡️ Retailers"])

with tab1:
    if st.button("🔄 Sync Sheet"): st.rerun()
    up_file = st.file_uploader("Upload Slip Screenshot", type=['png', 'jpg', 'jpeg'])
    
    if up_file:
        with st.spinner("AI X-Ray Scanning..."):
            extracted = extract_data_advanced(Image.open(up_file))
            st.session_state.up_amt = extracted.get('amount', 0.0)
            st.session_state.up_utr = extracted.get('utr', '')
            st.session_state.up_snd = extracted.get('sender', '')
            st.session_state.up_dat = extracted.get('date', datetime.now().strftime("%d-%m-%Y %I:%M %p"))

    with st.form("main_form"):
        f_date = st.text_input("📅 Entry Date*", value=st.session_state.get('up_dat', datetime.now().strftime("%d-%m-%Y %I:%M %p")))
        c1, c2 = st.columns(2)
        with c1:
            sel_ret = st.selectbox("👤 Select Retailer*", ["-- Select --"] + st.session_state.auth_retailers["RetailerName"].tolist())
            f_amt = st.number_input("Amount (Rs)*", value=float(st.session_state.get('up_amt', 0.0)))
            f_rem = st.selectbox("📝 Remark*", ["eTop", "JPB", "Other"])
        with c2:
            st.write("💳 **Payment: UPI / Online**")
            f_snd = st.text_input("Sender Bank 4-Digit*", value=st.session_state.get('up_snd', ''))
            f_utr = st.text_input("UTR Number*", value=st.session_state.get('up_utr', ''))
            
        if st.form_submit_button("🔍 VERIFY & SAVE", use_container_width=True, type="primary"):
            if sel_ret == "-- Select --" or f_amt <= 0:
                st.error("❌ नाम और अमाउंट ज़रूरी है।")
            else:
                auth_row = st.session_state.auth_retailers[st.session_state.auth_retailers["RetailerName"] == sel_ret].iloc[0]
                is_safe = f_snd in str(auth_row["Auth_UPI"]) or f_snd in str(auth_row["Mobile"])
                status = "Verified (Safe)" if is_safe else "UNVERIFIED (Danger)"
                
                payload = {"sheet_name": "Payment_Ledger", "Date": f_date, "RetailerName": sel_ret, "Amount": f_amt, "Mode": "UPI", "SenderUPI_Mobile": f_snd, "Status": status, "Reference": f"{f_rem} (UTR: {f_utr})"}
                requests.post(WEBHOOK_URL, json=payload, timeout=10)
                
                if is_safe: st.markdown("<div class='green-alert'>✅ SAFE PAYMENT: एक्सेल में सेव हो गया।</div>", unsafe_allow_html=True)
                else: st.markdown(f"<div class='red-alert'>🚨 ALERT: यह नंबर {f_snd} रजिस्टर्ड लिस्ट में नहीं है!</div>", unsafe_allow_html=True)
                time.sleep(2)
                st.rerun()

with tab2:
    st.dataframe(st.session_state.payment_ledger, use_container_width=True)

with tab3:
    st.write("Manage Authorized Retailers here...")
