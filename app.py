import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
import re
from PIL import Image, ImageOps, ImageEnhance

# 1. Page Style & 3D A4 Layout
st.set_page_config(page_title="Cyber Safe Payment Portal", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main .block-container { 
        background-color: #ffffff; padding: 2rem 3.5rem; border-radius: 15px; 
        max-width: 850px; box-shadow: 0px 15px 50px rgba(0,0,0,0.2); margin: auto;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        box-shadow: inset 3px 3px 6px rgba(0,0,0,0.1), 2px 2px 5px rgba(255,255,255,0.8) !important;
        border-radius: 10px !important; background-color: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important; font-weight: bold; font-size: 17px !important;
    }
    .red-alert { background-color: #fff1f2; color: #be123c; padding: 18px; border-left: 8px solid #be123c; border-radius: 10px; font-weight: bold; margin-bottom: 20px; }
    .green-alert { background-color: #f0fdf4; color: #15803d; padding: 18px; border-left: 8px solid #15803d; border-radius: 10px; font-weight: bold; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 API & GOOGLE SHEET CONFIG
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# 🟢 THE MAGIC SCANNER (10X & DEEP FILTER LOGIC)
def master_ocr_scan(img):
    if not HAS_OCR: return {}
    
    # Image Preparation
    gray = ImageOps.grayscale(img)
    inverted = ImageOps.invert(gray) # White text on black background for better scan
    
    # Double Scan for Accuracy
    text_normal = pytesseract.image_to_string(gray, config='--psm 11')
    text_inv = pytesseract.image_to_string(inverted, config='--psm 11')
    full_text = text_normal + " " + text_inv
    
    res = {}

    # 1. DATE & TIME
    dt = re.search(r'(\d{1,2}:\d{2}\s*[APM]+\s*on\s*\d{1,2}\s*[A-Za-z]+\s*\d{4})', full_text, re.IGNORECASE)
    if dt: res['date'] = dt.group(1).replace("on", "").strip()

    # 2. UTR (Strict 12 Digit)
    utr = re.search(r'\b(\d{12})\b', full_text)
    if utr: res['utr'] = utr.group(1)

    # 3. AMOUNT (Strict Rule: Must be > 2027 to avoid 'Year' confusion)
    amts = re.findall(r'[₹Rs]?\s*([0-9,]{2,10})', full_text)
    if amts:
        valid = [float(a.replace(',', '')) for a in amts if float(a.replace(',', '')) > 2027]
        if valid: res['amount'] = valid[-1]

    # 4. SENDER 4-DIGIT (The 10X Magic Logic)
    # Step A: Find 10X pattern (XXXXXXXXXX1234)
    sender_10x = re.search(r'[Xx\*]{6,15}\s*(\d{4})', full_text)
    if sender_10x:
        res['sender'] = sender_10x.group(1)
    else:
        # Step B: Filter Logic (Ignore Years, Receiver IDs, and Amounts)
        blocked = re.findall(r'(\d{4})@', full_text) # Receiver ID filter
        nums = re.findall(r'\b(\d{4})\b', full_text)
        clean = [n for n in nums if n not in ['2024','2025','2026','2027'] and n not in blocked]
        if 'amount' in res: clean = [n for n in clean if n != str(int(res['amount']))]
        if clean: res['sender'] = clean[-1]

    return res

# 🟢 DATABASE CONNECTION
@st.cache_data(ttl=1)
def load_db(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&cb={int(time.time())}"
    try:
        df = pd.read_csv(url).dropna(how="all").fillna("")
        df.columns = [str(c).replace(" ", "").strip() for c in df.columns]
        return df
    except: return pd.DataFrame()

# UI Initialization
st.session_state.auth_retailers = load_db("Authorized_Retailers")
st.session_state.payment_ledger = load_db("Payment_Ledger")

st.markdown("<div style='background: linear-gradient(90deg, #b91c1c 0%, #ef4444 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; margin-bottom: 30px;'><h1 style='margin:0; font-size: 34px;'>🛡️ CYBER-SAFE PAYMENT PORTAL</h1><p style='margin:5px 0 0 0; font-size: 17px;'>Sandhya Enterprises - Pro Business Control</p></div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💰 Register Payment", "📋 Ledger", "🛡️ Master Retailers"])

with tab1:
    if st.button("🔄 Sync Master Sheet"): st.rerun()
    
    st.info("📸 **Magic Scan Mode:** यहाँ स्लिप अपलोड करें। ऐप अब 10X लॉजिक से डेटा निकालेगा।")
    up_file = st.file_uploader("Upload PhonePe Slip", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    if up_file:
        with st.spinner("AI Deep Scanning..."):
            extracted = master_ocr_scan(Image.open(up_file))
            st.session_state.master_data = extracted
            st.success("✅ स्कैनिंग पूरी हुई! डेटा चेक करें।")

    with st.form("master_payment_form"):
        d = st.session_state.get('master_data', {})
        
        f_date = st.text_input("📅 Date & Time*", value=d.get('date', datetime.now().strftime("%d-%m-%Y %I:%M %p")))
        
        c1, c2 = st.columns(2)
        with c1:
            ret_list = ["-- Select --"] + st.session_state.auth_retailers["RetailerName"].tolist() if not st.session_state.auth_retailers.empty else ["-- Select --"]
            sel_ret = st.selectbox("👤 Select Retailer*", ret_list)
            f_amt = st.number_input("Amount (Rs)*", value=float(d.get('amount', 0.0)))
            f_rem = st.selectbox("📝 Remark*", ["eTop", "JPB", "Other"])
        with c2:
            st.write("💳 **Mode: UPI / Online**")
            f_snd = st.text_input("Sender Bank 4-Ank*", value=d.get('sender', ''))
            f_utr = st.text_input("UTR Number*", value=d.get('utr', ''))
            
        if st.form_submit_button("🔍 VERIFY & SAVE PAYMENT", use_container_width=True, type="primary"):
            if sel_ret == "-- Select --" or f_amt <= 0:
                st.error("❌ कृपया नाम और अमाउंट भरें।")
            else:
                # Security Match
                auth_row = st.session_state.auth_retailers[st.session_state.auth_retailers["RetailerName"] == sel_ret]
                if not auth_row.empty:
                    stored_acc = str(auth_row.iloc[0]["Auth_UPI"])
                    stored_mob = str(auth_row.iloc[0]["Mobile"])
                    is_safe = f_snd in stored_acc or f_snd in stored_mob
                else: is_safe = False
                
                status = "Verified (Safe)" if is_safe else "UNVERIFIED (Danger)"
                
                # Payload to Sheet
                payload = {"sheet_name": "Payment_Ledger", "Date": f_date, "RetailerName": sel_ret, "Amount": f_amt, "Mode": "UPI", "SenderUPI_Mobile": f_snd, "Status": status, "Reference": f"{f_rem} (UTR: {f_utr})"}
                requests.post(WEBHOOK_URL, json=payload, timeout=10)
                
                if is_safe: st.markdown("<div class='green-alert'>✅ SAFE: डेटा एक्सेल में सेव हो गया है।</div>", unsafe_allow_html=True)
                else: st.markdown(f"<div class='red-alert'>🚨 ALERT: यह सेंडर {f_snd} रजिस्टर्ड लिस्ट में नहीं मिला!</div>", unsafe_allow_html=True)
                time.sleep(2)
                st.rerun()

with tab2:
    st.dataframe(st.session_state.payment_ledger, use_container_width=True)

with tab3:
    st.dataframe(st.session_state.auth_retailers, use_container_width=True)
