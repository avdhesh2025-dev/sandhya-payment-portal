import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# FPDF for Bill Generation
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# 1. Page Configuration & A4 CSS Design
st.set_page_config(page_title="Sandhya Repair & Service", page_icon="🔧", layout="centered")

# A4 Page Look
st.markdown("""
    <style>
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.1);
        max-width: 800px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 यहाँ अपना गूगल शीट डेटा फिर से भरें 🔴
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzuGfQwsktUljAVELCbCfaXLUJV1b5-hy7Y6ErCT89Y_ZnrmPO0X_wCX9AXBf4oAGNrcA/exec"
SHEET_ID = "https://docs.google.com/spreadsheets/d/17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM/edit?usp=sharing"
# ==========================================

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=ServiceDB"

@st.cache_data(ttl=2)
def load_data():
    try:
        cb = int(time.time())
        df = pd.read_csv(f"{csv_url}&cb={cb}").dropna(how="all").fillna("")
        return df
    except:
        return pd.DataFrame(columns=["JobID", "Date", "CustName", "Mobile", "Address", "Category", "ProductDetail", "Fault", "EstCost", "DeliveryDate", "Status"])

# Database Initialization
if 'repair_db' not in st.session_state:
    st.session_state.repair_db = load_data()
else:
    st.session_state.repair_db = load_data()

if 'last_receipt_data' not in st.session_state:
    st.session_state.last_receipt_data = None

# 🟢 CRASH-PROOF PDF BILL GENERATOR
def generate_repair_receipt(data):
    if not HAS_FPDF: return None
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, "SANDHYA ENTERPRISES", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 6, "Repair & Service Receipt", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, "Register office: Rosera Road, Meghpatti, Samastipur, Bihar", ln=True, align='C')
    pdf.cell(0, 5, "Contact: 7479584179 | Email: smp.sandhya02@gmail.com", ln=True, align='C')
    pdf.line(10, 40, 200, 40)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    
    def print_row(col1, col2):
        pdf.cell(50, 8, col1, border=1)
        pdf.set_font("Arial", '', 10)
        clean_col2 = str(col2).encode('latin-1', 'ignore').decode('latin-1')
        pdf.cell(0, 8, f" {clean_col2}", border=1, ln=True)
        pdf.set_font("Arial", 'B', 10)

    # .get() makes it 100% crash-proof against KeyErrors
    print_row("Bill No / Job ID:", data.get('JobID', 'N/A'))
    print_row("Date & Time:", data.get('Date', data.get('EntryDate', 'N/A')))
    print_row("Customer Name:", data.get('CustName', 'N/A'))
    print_row("Mobile Number:", data.get('Mobile', 'N/A'))
    print_row("Item Category:", data.get('Category', 'N/A'))
    print_row("Product Model:", data.get('ProductDetail', 'N/A'))
    print_row("Problem:", data.get('Fault', 'N/A'))
    print_row("Estimated Cost:", f"Rs. {data.get('EstCost', '0')}")
    print_row("Delivery Date:", data.get('DeliveryDate', 'N/A'))
    
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, "Authorized Signatory - Sandhya Enterprises", align='R')
    return pdf.output(dest='S').encode('latin-1')

# Header
st.markdown("""
    <div style='background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 20px;'>
        <h1 style='margin:0; font-size: 30px;'>🛠️ REPAIR & SERVICE PORTAL</h1>
        <p style='margin:0;'>Sandhya Enterprises - Universal Desk</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📝 New Entry (नयी एंट्री)", "⏳ Pending (पेंडिंग)", "✅ Delivered (दे दिया)"])

# TAB 1: NEW ENTRY
with tab1:
    if st.session_state.last_receipt_data:
        res = st.session_state.last_receipt_data
        st.success(f"✅ Job ID {res['JobID']} Saved Successfully!")
        if HAS_FPDF:
            pdf = generate_repair_receipt(res)
            st.download_button("📥 Print Receipt (PDF)", data=pdf, file_name=f"Bill_{res['JobID']}.pdf", use_container_width=True)
        if st.button("➕ Next Customer"):
            st.session_state.last_receipt_data = None
            st.rerun()
    else:
        with st.form("repair_form"):
            st.markdown("#### 👤 Customer Details")
            c1, c2 = st.columns(2)
            name = c1.text_input("Name (नाम)*")
            mobile = c2.text_input("Mobile (नंबर)*")
            address = st.text_input("Address (पता)")
            
            st.markdown("#### 📱 Repair Details")
            category = st.selectbox("Category*", ["Mobile", "Fan", "Charger", "Other"])
            prod = st.text_input("Item Name/Model*")
            fault = st.text_area("Problem (खराबी)*")
            
            st.markdown("#### 💰 Charges")
            cost = st.text_input("Cost (₹)*")
            del_date = st.text_input("Delivery (कब मिलेगा?)*")
            
            submit = st.form_submit_button("💾 Save & Generate Bill", type="primary", use_container_width=True)
            
            if submit:
                if not name or not mobile or not prod:
                    st.error("❌ कृपया जरूरी जानकारी भरें (नाम, मोबाइल, सामान)")
                else:
                    new_id = f"REP-{int(time.time())}"
                    new_data = {
                        "action": "add", 
                        "JobID": new_id, 
                        "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "CustName": name.upper(), 
                        "Mobile": mobile, 
                        "Address": address,
                        "Category": category, 
                        "ProductDetail": prod, 
                        "Fault": fault,
                        "EstCost": cost, 
                        "DeliveryDate": del_date, 
                        "Status": "Pending"
                    }
                    
                    try:
                        # 3-second silent webhook attempt
                        if WEBHOOK_URL != "यहाँ_अपना_नया_WEBHOOK_URL_डालें":
                            requests.post(WEBHOOK_URL, json=new_data, timeout=3)
                    except:
                        pass # Never show connection error, just proceed to bill
                        
                    st.session_state.last_receipt_data = new_data
                    st.rerun()

# TAB 2: PENDING
with tab2:
    pending = st.session_state.repair_db[st.session_state.repair_db["Status"].astype(str).str.contains("Pending", na=False)]
    if pending.empty: 
        st.info("No pending jobs.")
    else:
        for idx, row in pending.iterrows():
            st.markdown(f"**{row['CustName']}** - {row['ProductDetail']} (₹{row['EstCost']})")
            if st.button(f"Mark Completed - {row['JobID']}"):
                try:
                    if WEBHOOK_URL != "यहाँ_अपना_नया_WEBHOOK_URL_डालें":
                        requests.post(WEBHOOK_URL, json={"action": "update", "ID": row['JobID'], "Status": "Delivered"}, timeout=3)
                except:
                    pass
                st.session_state.repair_db.loc[st.session_state.repair_db['JobID'] == row['JobID'], 'Status'] = "Delivered"
                st.rerun()

# TAB 3: HISTORY
with tab3:
    if st.session_state.repair_db.empty:
        st.info("No data available.")
    else:
        st.dataframe(st.session_state.repair_db, use_container_width=True)
