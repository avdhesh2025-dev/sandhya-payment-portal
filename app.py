import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
import re
from PIL import Image

# 1. Page Style & Layout
st.set_page_config(page_title="Cyber Safe Payment Portal", page_icon="🛡️", layout="wide")

# 🟢 3D & A4 Size CSS
st.markdown("""
    <style>
    /* A4 Size Paper Look */
    .main .block-container { 
        background-color: #ffffff; 
        padding: 2rem 3rem; 
        border-radius: 12px; 
        max-width: 850px; /* A4 Width */
        box-shadow: 0px 10px 30px rgba(0,0,0,0.15); /* Paper Shadow */
        margin: auto;
    }
    /* 3D Input Boxes */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.1), inset -2px -2px 5px rgba(255,255,255,0.7) !important;
        border-radius: 8px !important;
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: bold;
    }
    /* Disabled (Read-Only) Boxes Style */
    input:disabled {
        color: #1e3a8a !important;
        -webkit-text-fill-color: #1e3a8a !important;
        background-color: #e2e8f0 !important;
    }
    .red-alert { background-color: #fef2f2; color: #dc2626; padding: 15px; border-left: 5px solid #dc2626; border-radius: 5px; font-weight: bold; margin-bottom: 20px;}
    .green-alert { background-color: #f0fdf4; color: #166534; padding: 15px; border-left: 5px solid #166534; border-radius: 5px; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 WEBHOOK AND SHEET ID
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
# ==========================================

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# 🟢 ADVANCED SMART FILTER (Debited From Logic)
def extract_details_from_image(img):
    if not HAS_OCR: return {}
    img = img.convert('L')
    text = pytesseract.image_to_string(img)
    details = {}
    
    # 1. DATE & TIME (e.g., 07:41 PM on 27 Apr 2026)
    date_match = re.search(r'([0-9]{1,2}:[0-9]{2}\s*[APM]+\s*on\s*[0-9]{1,2}\s*[A-Za-z]+\s*[0-9]{4})', text, re.IGNORECASE)
    if date_match:
        details['date'] = date_match.group(1).replace("on", "").strip()
    
    # 2. SENDER 4 DIGITS & AMOUNT (Strictly from "Debited from")
    debited_section = ""
    if "Debited from" in text or "Debited" in text:
        start_idx = text.find("Debited")
        debited_section = text[start_idx:]
        
        # Amount inside Debited section
        amt_match = re.search(r'₹\s*([0-9,]+)', debited_section)
        if amt_match:
            try: details['amount'] = amt_match.group(1).replace(',', '')
            except: pass
            
        # Sender 4 digits inside Debited section
        sender_match = re.search(r'[X\*]{4,}([0-9]{4})', debited_section)
        if sender_match:
            details['sender'] = sender_match.group(1)
            
    # Fallbacks (If Debited from word is blurry)
    if 'amount' not in details:
        amts = re.findall(r'₹\s*([0-9,]+)', text)
        if amts: details['amount'] = amts[-1].replace(',', '')
    if 'sender' not in details:
        acc_matches = re.findall(r'[X\*]{4,}([0-9]{4})', text)
        if acc_matches: details['sender'] = acc_matches[-1]
        
    # 3. UTR / TRANSACTION ID
    utr_match = re.search(r'UTR.*?([0-9]{12})', text, re.IGNORECASE)
    if utr_match: details['utr'] = utr_match.group(1)
    else:
        t_match = re.search(r'(T[0-9]{15,})', text)
        if t_match: details['utr'] = t_match.group(1)
        
    return details

# 🟢 DATA LOADER
@st.cache_data(ttl=1)
def load_data_from_sheet(sheet_name, expected_columns):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&cb={int(time.time())}"
    try:
        df = pd.read_csv(url).dropna(how="all").fillna("")
        if not df.empty:
            df.columns = [str(c).replace(" ", "").strip() for c in df.columns]
            return df
    except: pass 
    return pd.DataFrame(columns=expected_columns)

st.session_state.auth_retailers = load_data_from_sheet("Authorized_Retailers", ["RetailerName", "Mobile", "Auth_UPI"])
st.session_state.payment_ledger = load_data_from_sheet("Payment_Ledger", ["Date", "RetailerName", "Amount", "Mode", "SenderUPI_Mobile", "Status", "Reference"])

# Session states for UI
if 'auto_amt' not in st.session_state: st.session_state.auto_amt = ""
if 'auto_utr' not in st.session_state: st.session_state.auto_utr = ""
if 'auto_sender' not in st.session_state: st.session_state.auto_sender = ""
if 'auto_date' not in st.session_state: st.session_state.auto_date = ""
if 'alert_msg' not in st.session_state: st.session_state.alert_msg = ""
if 'alert_type' not in st.session_state: st.session_state.alert_type = ""

# Header
st.markdown("""
    <div style='background: linear-gradient(90deg, #b91c1c 0%, #ef4444 100%); padding: 25px; border-radius: 10px; text-align: center; color: white; margin-bottom: 25px;'>
        <h1 style='margin:0; font-size: 34px; font-weight: 800;'>🛡️ CYBER-SAFE PAYMENT PORTAL</h1>
        <p style='margin:5px 0 0 0; font-size: 16px;'>Sandhya Enterprises - Smart OCR Verification</p>
    </div>
""", unsafe_allow_html=True)

if st.button("🔄 Sync Data with Google Sheet"):
    st.cache_data.clear()
    st.rerun()

tab1, tab2, tab3 = st.tabs(["💰 Register Payment", "📋 Transaction Ledger", "🛡️ Manage Authorized Retailers"])

with tab1:
    st.markdown("### 💰 New Payment Entry & Verification")
    
    if st.session_state.alert_msg:
        if st.session_state.alert_type == "success":
            st.markdown(f"<div class='green-alert'>{st.session_state.alert_msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='red-alert'>{st.session_state.alert_msg}</div>", unsafe_allow_html=True)
        st.session_state.alert_msg = ""
        st.session_state.alert_type = ""
    
    if st.session_state.auth_retailers.empty:
        st.warning("⚠️ अभी कोई अधिकृत (Authorized) रिटेलर लिस्ट नहीं है।")
    else:
        st.info("📸 **Smart Auto-Fill:** यहाँ पेमेंट स्लिप अपलोड करें, ऐप खुद डेटा पढ़ेगा और डब्बों को 'Lock' कर देगा!")
        uploaded_slip = st.file_uploader("Upload Payment Screenshot (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_slip is not None:
            image = Image.open(uploaded_slip)
            colA, colB = st.columns([1, 2])
            with colA:
                st.image(image, caption="Uploaded Slip", use_column_width=True)
            with colB:
                with st.spinner("फोटो पढ़ रहा हूँ (Debited from...)..."):
                    extracted = extract_details_from_image(image)
                    if extracted:
                        st.success("✅ स्लिप से डेटा निकाल लिया गया है!")
                        st.session_state.auto_amt = str(extracted.get('amount', ''))
                        st.session_state.auto_utr = extracted.get('utr', '')
                        st.session_state.auto_sender = extracted.get('sender', '')
                        st.session_state.auto_date = extracted.get('date', datetime.now().strftime("%d-%m-%Y %I:%M %p"))
                    else:
                        st.warning("⚠️ फोटो साफ़ नहीं है, कृपया हाथ से भरें।")

        with st.form("payment_form"):
            # READ-ONLY DATE
            curr_date = st.session_state.auto_date if st.session_state.auto_date else datetime.now().strftime("%d-%m-%Y %I:%M %p")
            entry_date = st.text_input("📅 Date & Time (Auto)*", value=curr_date, disabled=True)
            
            col1, col2 = st.columns(2)
            with col1:
                ret_col = "RetailerName" if "RetailerName" in st.session_state.auth_retailers.columns else st.session_state.auth_retailers.columns[0]
                retailer_list = ["-- Select Retailer --"] + st.session_state.auth_retailers[ret_col].astype(str).tolist()
                
                selected_retailer = st.selectbox("👤 Select Retailer (Editable)*", retailer_list)
                
                # READ-ONLY AMOUNT
                amount = st.text_input("Amount Received (Rs) [Locked]*", value=st.session_state.auto_amt, disabled=True)
                
                # JPB / eTop Options (Editable)
                remark_type = st.selectbox("📝 Remark / Purpose (Editable)*", ["eTop", "JPB", "Other"])
                if remark_type == "Other":
                    purpose = st.text_input("Type Other Purpose*")
                else:
                    purpose = remark_type
                
            with col2:
                # FIXED ONLINE
                st.info("💳 Payment Mode: UPI / Online (Fixed)")
                pay_mode = "UPI / Online" 
                
                # READ-ONLY SENDER
                sender_detail = st.text_input("Sender Bank ke 4 Ank [Locked]*", value=st.session_state.auto_sender, disabled=True)
                
                # READ-ONLY UTR
                utr_number = st.text_input("UTR Number / Transaction ID [Locked]*", value=st.session_state.auto_utr, disabled=True)
                
            if st.form_submit_button("🔍 Verify & Save Payment", type="primary", use_container_width=True):
                if selected_retailer == "-- Select Retailer --" or not amount:
                    st.error("❌ कृपया रिटेलर का नाम चुनें और स्लिप स्कैन करें।")
                elif not sender_detail or not utr_number:
                    st.error("❌ स्लिप से UTR और Sender के 4 अंक नहीं मिले!")
                elif remark_type == "Other" and not purpose:
                    st.error("❌ कृपया Other Purpose टाइप करें।")
                else:
                    auth_data = st.session_state.auth_retailers[st.session_state.auth_retailers[ret_col] == selected_retailer].iloc[0]
                    
                    auth_upi = str(auth_data.get("Auth_UPI", "")).strip().lower()
                    auth_mobile = str(auth_data.get("Mobile", "")).strip()
                    entered_sender = str(sender_detail).strip().lower()
                    
                    # Verification Logic
                    if entered_sender == auth_upi or entered_sender == auth_mobile or entered_sender in auth_upi:
                        status = "Verified (Safe)"
                        alert_type_val = "success"
                        alert_msg_text = f"✅ <b>SAFE PAYMENT:</b> यह पेमेंट {selected_retailer} के पक्के अकाउंट से आया है। (Data Saved!)"
                    else:
                        status = "UNVERIFIED (Danger)"
                        alert_type_val = "danger"
                        alert_msg_text = f"🚨 <b>RED ALERT:</b> सावधान! यह पेमेंट {selected_retailer} के पक्के नंबर से नहीं आया है! (Authorized: {auth_upi} | Received: {sender_detail}) (Record Saved!)"

                    final_reference = f"{purpose} (UTR: {utr_number})"

                    new_payment = {
                        "sheet_name": "Payment_Ledger",
                        "Date": entry_date,
                        "RetailerName": selected_retailer,
                        "Amount": amount,
                        "Mode": pay_mode,
                        "SenderUPI_Mobile": sender_detail,
                        "Status": status,
                        "Reference": final_reference
                    }
                    
                    try: requests.post(WEBHOOK_URL, json=new_payment, timeout=10)
                    except: pass
                    
                    st.session_state.alert_msg = alert_msg_text
                    st.session_state.alert_type = alert_type_val
                    st.session_state.auto_amt = ""
                    st.session_state.auto_utr = ""
                    st.session_state.auto_sender = ""
                    st.session_state.auto_date = ""
                    st.cache_data.clear()
                    st.rerun()

with tab2:
    st.markdown("### 📋 Transaction History")
    if st.session_state.payment_ledger.empty:
        st.info("Abhi koi transaction nahi hai.")
    else:
        df_to_show = st.session_state.payment_ledger.copy()
        if "Status" in df_to_show.columns:
            def highlight_danger(val):
                return 'background-color: #fef2f2; color: #dc2626; font-weight: bold;' if 'UNVERIFIED' in str(val) else ''
            try: styled_df = df_to_show.style.map(highlight_danger, subset=['Status'])
            except: styled_df = df_to_show.style.applymap(highlight_danger, subset=['Status'])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.dataframe(df_to_show, use_container_width=True)

with tab3:
    st.markdown("### 🛡️ Add Authorized Retailer")
    with st.form("add_retailer"):
        c1, c2, c3 = st.columns(3)
        new_ret_name = c1.text_input("Retailer Name*")
        new_ret_mob = c2.text_input("Mobile Number*")
        new_ret_upi = c3.text_input("Authorized UPI ya Bank A/C ke 4 Ank*")
        
        if st.form_submit_button("➕ Save to Google Sheet"):
            if new_ret_name and new_ret_mob and new_ret_upi:
                new_ret = {
                    "sheet_name": "Authorized_Retailers",
                    "RetailerName": new_ret_name.upper(), 
                    "Mobile": new_ret_mob, 
                    "Auth_UPI": new_ret_upi.lower()
                }
                try: requests.post(WEBHOOK_URL, json=new_ret, timeout=10)
                except: pass
                st.success(f"✅ {new_ret_name} added!")
                st.cache_data.clear()
                time.sleep(1.5)
                st.rerun()
