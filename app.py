import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
import re
from PIL import Image, ImageOps, ImageEnhance

# 1. Page Configuration & Professional 3D UI
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
    .red-alert { background-color: #fff1f2; color: #be123c; padding: 15px; border-left: 8px solid #be123c; border-radius: 10px; font-weight: bold; margin-bottom: 20px; }
    .green-alert { background-color: #f0fdf4; color: #15803d; padding: 15px; border-left: 8px solid #15803d; border-radius: 10px; font-weight: bold; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# Webhook & Sheet ID
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# 🟢 THE 10X LOGIC AI
def extract_smart_data(img):
    if not HAS_OCR: return {}
    
    # Pre-processing for better digit visibility
    img = img.convert('L')
    img = ImageOps.autocontrast(img)
    text = pytesseract.image_to_string(img, config='--psm 11')
    res = {}

    # 1. AMOUNT LOGIC: Find numbers with ₹ or commas, ignore small numbers like 2026
    amt_matches = re.findall(r'[₹Rs]?\s*([0-9,]{2,10})', text)
    if amt_matches:
        valid_amts = [float(a.replace(',', '')) for a in amt_matches if float(a.replace(',', '')) > 2027]
        if valid_amts: res['amount'] = valid_amts[-1]

    # 2. 10X LOGIC: Find 10 or more X followed by 4 digits
    # This specifically targets "XXXXXXXXXX9424"
    sender_match = re.search(r'[Xx\*]{8,15}\s*([0-9]{4})', text)
    if sender_match:
        res['sender'] = sender_match.group(1)
    else:
        # Fallback: Debited ke baad waala last 4 digit
        deb_idx = text.lower().find("debited")
        if deb_idx != -1:
            fours = re.findall(r'\b(\d{4})\b', text[deb_idx:])
            clean = [n for n in fours if n not in ['2024','2025','2026','2027']]
            if clean: res['sender'] = clean[-1]

    # 3. UTR & DATE
    utr_match = re.search(r'\b([0-9]{12})\b', text)
    if utr_match: res['utr'] = utr_match.group(1)
    
    dt_match = re.search(r'(\d{1,2}:\d{2}\s*[APM]+\s*on\s*\d{1,2}\s*[A-Za-z]+\s*\d{4})', text, re.IGNORECASE)
    if dt_match: res['date'] = dt_match.group(1).replace("on", "").strip()

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

# Header UI
st.markdown("<div style='background: linear-gradient(90deg, #b91c1c 0%, #ef4444 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; margin-bottom: 30px;'><h1 style='margin:0; font-size: 36px;'>🛡️ CYBER-SAFE PAYMENT PORTAL</h1><p style='margin:5px 0 0 0; font-size: 18px;'>Sandhya Enterprises - 10X Logic Active</p></div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💰 Register Payment", "📋 Ledger", "🛡️ Retailers"])

with tab1:
    if st.button("🔄 Sync Sheet"): st.rerun()
    up_file = st.file_uploader("Upload PhonePe Slip", type=['png', 'jpg', 'jpeg'])
    
    if up_file:
        with st.spinner("10X Scanning..."):
            extracted = extract_smart_data(Image.open(up_file))
            st.session_state.ex = extracted
            st.success("✅ स्लिप स्कैन हो गई!")

    with st.form("main_form"):
        e = st.session_state.get('ex', {})
        f_date = st.text_input("📅 Date*", value=e.get('date', datetime.now().strftime("%d-%m-%Y %I:%M %p")))
        c1, c2 = st.columns(2)
        with c1:
            sel_ret = st.selectbox("👤 Retailer*", ["-- Select --"] + st.session_state.auth_retailers["RetailerName"].tolist())
            f_amt = st.number_input("Amount (Rs)*", value=float(e.get('amount', 0.0)))
            f_rem = st.selectbox("📝 Remark*", ["eTop", "JPB", "Other"])
        with c2:
            st.write("💳 **Mode: Online**")
            f_snd = st.text_input("Sender Bank 4-Ank*", value=e.get('sender', ''))
            f_utr = st.text_input("UTR Number*", value=e.get('utr', ''))
            
        if st.form_submit_button("🔍 VERIFY & SAVE", use_container_width=True, type="primary"):
            if sel_ret == "-- Select --" or f_amt <= 0:
                st.error("❌ नाम और अमाउंट ज़रूरी है।")
            else:
                auth_row = st.session_state.auth_retailers[st.session_state.auth_retailers["RetailerName"] == sel_ret].iloc[0]
                is_safe = f_snd in str(auth_row["Auth_UPI"]) or f_snd in str(auth_row["Mobile"])
                status = "Verified (Safe)" if is_safe else "UNVERIFIED (Danger)"
                
                payload = {"sheet_name": "Payment_Ledger", "Date": f_date, "RetailerName": sel_ret, "Amount": f_amt, "Mode": "UPI", "SenderUPI_Mobile": f_snd, "Status": status, "Reference": f"{f_rem} (UTR: {f_utr})"}
                requests.post(WEBHOOK_URL, json=payload, timeout=10)
                
                if is_safe: st.markdown("<div class='green-alert'>✅ SAFE: एंट्री एक्सेल में सेव हो गई।</div>", unsafe_allow_html=True)
                else: st.markdown(f"<div class='red-alert'>🚨 ALERT: नंबर {f_snd} रजिस्टर्ड लिस्ट में नहीं है!</div>", unsafe_allow_html=True)
                time.sleep(2)
                st.rerun()

with tab2:
    st.dataframe(st.session_state.payment_ledger, use_container_width=True)

with tab3:
    st.dataframe(st.session_state.auth_retailers, use_container_width=True)
