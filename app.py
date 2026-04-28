import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
import re
from PIL import Image, ImageOps, ImageEnhance

# 1. Page Config
st.set_page_config(page_title="Payment Portal", layout="wide")

# Webhook & Sheet ID
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# 🟢 THE SUPER ANCHOR LOGIC
def extract_final_logic(img):
    if not HAS_OCR: return {}
    
    # Image Ko Clean Karna (Taaki Number Saaf Dikhe)
    img = img.convert('L')
    img = ImageOps.invert(img) # Background kaala aur text safed karne se OCR badhiya chalta hai
    text = pytesseract.image_to_string(img, config='--psm 6')
    res = {}

    # 1. UTR (Hamesha 12 ank ka hota hai)
    utr_match = re.search(r'\b(\d{12})\b', text)
    if utr_match:
        res['utr'] = utr_match.group(1)

    # 2. AMOUNT LOGIC (Bigger than 2027 and contains ₹/Rs or Decimals)
    amt_raw = re.findall(r'(?:₹|Rs\.?|Total Amount|Amount)\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
    if not amt_raw:
        amt_raw = re.findall(r'\b\d{3,7}\.\d{2}\b', text) # Search for XX.00 format
        
    if amt_raw:
        valid_amts = []
        for a in amt_raw:
            try:
                val = float(a.replace(',', ''))
                if val > 2027: valid_amts.append(val)
            except: continue
        if valid_amts: res['amount'] = valid_amts[0]

    # 3. 10X + 4 DIGIT ACCOUNT LOGIC (Direct Search)
    # PhonePe me aksar 'X' ka use account chhupane ke liye hota hai
    acc_match = re.search(r'[Xx\*]{4,}\s*(\d{4})', text)
    if acc_match:
        res['sender'] = acc_match.group(1)
    
    # 4. DATE LOGIC
    dt_match = re.search(r'(\d{1,2}:\d{2}\s*[APM]+)\s*on\s*(\d{1,2}\s*[A-Za-z]+\s*\d{4})', text, re.IGNORECASE)
    if dt_match:
        res['date'] = f"{dt_match.group(1)} {dt_match.group(2)}"

    return res

# --- DATABASE & UI ---
@st.cache_data(ttl=1)
def load_db(name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={name}&cb={int(time.time())}"
    try: return pd.read_csv(url).fillna("")
    except: return pd.DataFrame()

st.session_state.auth_retailers = load_db("Authorized_Retailers")
st.session_state.payment_ledger = load_db("Payment_Ledger")

st.title("🛡️ Cyber-Safe Payment Portal")

up_file = st.file_uploader("Upload Slip", type=['png', 'jpg', 'jpeg'])
if up_file:
    with st.spinner("Deep Scanning..."):
        data = extract_final_logic(Image.open(up_file))
        st.session_state.scanned = data
        st.success("Scanning Complete!")

with st.form("payment_form"):
    s = st.session_state.get('scanned', {})
    
    f_date = st.text_input("Date/Time", value=s.get('date', datetime.now().strftime("%I:%M %p %d %b %Y")))
    
    col1, col2 = st.columns(2)
    with col1:
        retailer = st.selectbox("Select Retailer", ["-- Select --"] + list(st.session_state.auth_retailers.get("RetailerName", [])))
        amount = st.number_input("Amount", value=float(s.get('amount', 0.0)))
    with col2:
        sender_acc = st.text_input("Sender Account (Last 4)", value=s.get('sender', ''))
        utr = st.text_input("UTR Number", value=s.get('utr', ''))

    if st.form_submit_button("SAVE & VERIFY"):
        if retailer != "-- Select --" and amount > 0:
            # Match Logic
            auth_data = st.session_state.auth_retailers[st.session_state.auth_retailers["RetailerName"] == retailer]
            stored_acc = str(auth_data["Auth_UPI"].values[0]) if not auth_data.empty else ""
            
            is_safe = sender_acc in stored_acc or sender_acc in str(auth_data["Mobile"].values[0])
            status = "Verified" if is_safe else "Unverified"
            
            payload = {"sheet_name": "Payment_Ledger", "Date": f_date, "RetailerName": retailer, "Amount": amount, "Mode": "UPI", "SenderUPI_Mobile": sender_acc, "Status": status, "Reference": f"UTR: {utr}"}
            requests.post(WEBHOOK_URL, json=payload)
            
            if is_safe: st.success("✅ Payment Saved & Verified!")
            else: st.warning(f"⚠️ Account {sender_acc} not matched with {retailer}!")
            time.sleep(1)
            st.rerun()
