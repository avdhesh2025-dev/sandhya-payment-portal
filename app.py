import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
import re
from PIL import Image

# 1. Page Style & Layout
st.set_page_config(page_title="Cyber Safe Payment Portal", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main .block-container { background-color: #f8fafc; padding: 2rem; border-radius: 12px; max-width: 900px; }
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

# 🟢 Tesseract OCR Setup
try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# 🟢 SMART FILTER: OCR EXTRACTION
def extract_details_from_image(img):
    if not HAS_OCR: return {}
    
    # Image ko thoda clear karne ke liye Grayscale me convert karte hain
    img = img.convert('L')
    text = pytesseract.image_to_string(img)
    details = {}
    
    # 1. AMOUNT: PhonePe me ₹ symbol ya comma wala bada number
    amt_match = re.search(r'[₹₹Rs]\s*([0-9,]+)', text, re.IGNORECASE)
    if not amt_match:
        # Fallback: Sirf 3,000 jaisa comma wala number dhoonde
        amt_match = re.search(r'\b([0-9]{1,2},[0-9]{3})\b', text)
        
    if amt_match:
        try:
            details['amount'] = float(amt_match.group(1).replace(',', ''))
        except: pass
        
    # 2. UTR / Transaction ID
    utr_match = re.search(r'UTR.*?([0-9]{12})', text, re.IGNORECASE)
    if not utr_match:
        utr_match = re.search(r'(?:T[0-9]{15,})', text) # PayTM/PhonePe Txn ID
    if not utr_match:
        utr_match = re.search(r'([0-9]{12})', text) # Koi bhi 12 digit
        
    if utr_match:
        # Pura match group nikalenge
        match_str = utr_match.group(1) if len(utr_match.groups()) > 0 and utr_match.group(1) else utr_match.group(0)
        details['utr'] = match_str.replace("T", "") # T hata kar clean number
        
    # 3. SENDER 4 DIGITS (Smart Logic)
    # PhonePe me 2 baar 'XXXX' aate hain. Sender ka aakhiri (Debited From) me hota hai.
    acc_matches = re.findall(r'[Xx\*]{4,}([0-9]{4})', text)
    if acc_matches:
        # -1 ka matlab hai sabse aakhiri wala uthana hai (Jo sender ka hota hai)
        details['sender'] = acc_matches[-1] 
        
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
if 'auto_amt' not in st.session_state: st.session_state.auto_amt = 0.0
if 'auto_utr' not in st.session_state: st.session_state.auto_utr = ""
if 'auto_sender' not in st.session_state: st.session_state.auto_sender = ""
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
    
    # 🟢 PERSISTENT ALERT MESSAGE LOGIC
    if st.session_state.alert_msg:
        if st.session_state.alert_type == "success":
            st.markdown(f"<div class='green-alert'>{st.session_state.alert_msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='red-alert'>{st.session_state.alert_msg}</div>", unsafe_allow_html=True)
        # Ek baar dikha kar clear kar denge taki hamesha na rahe
        st.session_state.alert_msg = ""
        st.session_state.alert_type = ""
    
    if st.session_state.auth_retailers.empty:
        st.warning("⚠️ अभी कोई अधिकृत (Authorized) रिटेलर लिस्ट नहीं है।")
    else:
        st.info("📸 **Smart Auto-Fill:** यहाँ पेमेंट स्लिप (Screenshot) अपलोड करें, बाकी डिटेल्स ऐप खुद भर लेगा!")
        uploaded_slip = st.file_uploader("Upload Payment Screenshot (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_slip is not None:
            image = Image.open(uploaded_slip)
            colA, colB = st.columns([1, 2])
            with colA:
                st.image(image, caption="Uploaded Slip", use_column_width=True)
            with colB:
                with st.spinner("फोटो पढ़ रहा हूँ..."):
                    extracted = extract_details_from_image(image)
                    if extracted:
                        st.success("✅ स्लिप से डेटा निकाल लिया गया है! नीचे डब्बों में चेक करें।")
                        st.session_state.auto_amt = extracted.get('amount', 0.0)
                        st.session_state.auto_utr = extracted.get('utr', '')
                        st.session_state.auto_sender = extracted.get('sender', '')
                    else:
                        st.warning("⚠️ फोटो साफ़ नहीं है या डेटा नहीं मिल पाया। कृपया हाथ से भरें।")

        with st.form("payment_form"):
            col1, col2 = st.columns(2)
            with col1:
                ret_col = "RetailerName" if "RetailerName" in st.session_state.auth_retailers.columns else st.session_state.auth_retailers.columns[0]
                retailer_list = ["-- Select Retailer --"] + st.session_state.auth_retailers[ret_col].astype(str).tolist()
                
                selected_retailer = st.selectbox("👤 Select Retailer*", retailer_list)
                amount = st.number_input("Amount Received (Rs)*", min_value=0.0, step=10.0, value=float(st.session_state.auto_amt))
                purpose = st.text_input("UTR Number / Reference*", value=st.session_state.auto_utr)
                
            with col2:
                pay_mode = st.selectbox("Payment Mode*", ["UPI / Online", "Bank Transfer", "Cash"])
                sender_detail = st.text_input("Sender UPI ya Bank ke Aakhiri 4 Ank (eg. 9424)*", value=st.session_state.auto_sender)
                
            if st.form_submit_button("🔍 Verify & Save Payment", type="primary", use_container_width=True):
                if selected_retailer == "-- Select Retailer --" or amount <= 0:
                    st.error("❌ कृपया रिटेलर का नाम और सही अमाउंट डालें।")
                elif pay_mode != "Cash" and (not sender_detail or not purpose):
                    st.error("❌ ऑनलाइन पेमेंट के लिए UTR और Sender detail जरूरी है!")
                else:
                    status = "Verified"
                    alert_msg_text = ""
                    alert_type_val = ""
                    
                    if pay_mode != "Cash":
                        auth_data = st.session_state.auth_retailers[st.session_state.auth_retailers[ret_col] == selected_retailer].iloc[0]
                        
                        auth_upi = str(auth_data.get("Auth_UPI", "")).strip().lower()
                        auth_mobile = str(auth_data.get("Mobile", "")).strip()
                        entered_sender = str(sender_detail).strip().lower()
                        
                        if entered_sender == auth_upi or entered_sender == auth_mobile or entered_sender in auth_upi:
                            status = "Verified (Safe)"
                            alert_type_val = "success"
                            alert_msg_text = f"✅ <b>SAFE PAYMENT:</b> यह पेमेंट {selected_retailer} के पक्के अकाउंट से आया है। (Data Saved!)"
                        else:
                            status = "UNVERIFIED (Danger)"
                            alert_type_val = "danger"
                            alert_msg_text = f"🚨 <b>RED ALERT:</b> सावधान! यह पेमेंट {selected_retailer} के पक्के नंबर से नहीं आया है! (Authorized: {auth_upi} | Received: {sender_detail}) (Record Saved in Ledger!)"
                    else:
                        status = "Cash (Safe)"
                        alert_type_val = "success"
                        alert_msg_text = "✅ Cash Payment Recorded & Saved!"

                    new_payment = {
                        "sheet_name": "Payment_Ledger",
                        "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": selected_retailer,
                        "Amount": amount,
                        "Mode": pay_mode,
                        "SenderUPI_Mobile": sender_detail if pay_mode != "Cash" else "Hand Cash",
                        "Status": status,
                        "Reference": purpose
                    }
                    
                    # 🟢 INCREASED TIMEOUT FOR SAVING RED ALERTS TO GOOGLE SHEET
                    try:
                        requests.post(WEBHOOK_URL, json=new_payment, timeout=10)
                    except: pass
                    
                    # Alert dikhane aur fields ko khali karne ka logic
                    st.session_state.alert_msg = alert_msg_text
                    st.session_state.alert_type = alert_type_val
                    st.session_state.auto_amt = 0.0
                    st.session_state.auto_utr = ""
                    st.session_state.auto_sender = ""
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
            try:
                styled_df = df_to_show.style.map(highlight_danger, subset=['Status'])
            except:
                styled_df = df_to_show.style.applymap(highlight_danger, subset=['Status'])
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
                try:
                    requests.post(WEBHOOK_URL, json=new_ret, timeout=10)
                except: pass
                st.success(f"✅ {new_ret_name} added!")
                st.cache_data.clear()
                time.sleep(1.5)
                st.rerun()
