import streamlit as st
import pandas as pd
from datetime import datetime
import time
import re
import requests

# FPDF for Bill Generation
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# 1. Page Configuration & A4 CSS Design
st.set_page_config(page_title="Jio Phone Service & Sales", page_icon="📱", layout="wide")

st.markdown("""
    <style>
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.1);
        max-width: 900px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 WEBHOOK AND SHEET ID
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzclpA2vXlcwScmEYvAjmOye2pYYr3yDnx6OnrlXVEHer7HxG9lrSKdrW1l6-ckABnbpQ/exec"
SHEET_ID = "https://docs.google.com/spreadsheets/d/17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM/edit?usp=sharing"
# ==========================================

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=ServiceDB"

@st.cache_data(ttl=2)
def load_data():
    try:
        cb = int(time.time())
        df = pd.read_csv(f"{csv_url}&cb={cb}").dropna(how="all").fillna("")
        if df.empty or 'ID' not in df.columns:
            return pd.DataFrame(columns=["ID", "Date", "MFRNAME", "Model", "IMEI", "MRP", "EAN", "SRNO", "Retailer", "Problem", "Action", "Status"])
        return df
    except:
        return pd.DataFrame(columns=["ID", "Date", "MFRNAME", "Model", "IMEI", "MRP", "EAN", "SRNO", "Retailer", "Problem", "Action", "Status"])

# 2. Database Initialization
if 'service_db' not in st.session_state:
    st.session_state.service_db = load_data()

# 🟢 SALES DATABASE
if 'sales_db' not in st.session_state:
    st.session_state.sales_db = pd.DataFrame(columns=["Date", "MFRNAME", "Model", "IMEI", "MRP", "EAN", "SRNO", "Retailer"])

if 'scan_key' not in st.session_state:
    st.session_state.scan_key = 0

if 'last_bill_data' not in st.session_state:
    st.session_state.last_bill_data = None

# PDF BILL GENERATOR
def generate_service_bill(data, bill_type="Service"):
    if not HAS_FPDF: return None
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, "SANDHYA ENTERPRISES", ln=True, align='C')
    pdf.set_font("Arial", 'B', 11)
    
    title = "Jio Phone Service Receipt" if bill_type == "Service" else "Jio Phone Sales/Dispatch Invoice"
    pdf.cell(0, 6, title, ln=True, align='C')
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, "Register office: Rosera Road, Meghpatti, Samastipur, Bihar", ln=True, align='C')
    pdf.cell(0, 5, "Contact: 7479584179 | Email: smp.sandhya02@gmail.com", ln=True, align='C')
    pdf.line(10, 38, 200, 38)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 10)
    def print_row(col1, col2):
        pdf.cell(60, 8, col1, border=1)
        pdf.set_font("Arial", '', 10)
        clean_col2 = str(col2).encode('latin-1', 'ignore').decode('latin-1')
        pdf.cell(0, 8, f" {clean_col2}", border=1, ln=True)
        pdf.set_font("Arial", 'B', 10)

    if bill_type == "Service":
        print_row("Receipt ID:", data.get('ID', ''))
    
    print_row("Date & Time:", data['Date'])
    print_row("Retailer Name:", data['Retailer'])
    print_row("IMEI Number:", data['IMEI'])
    print_row("Model Number:", data['Model'])
    print_row("Manufacturer:", data.get('MFRNAME', 'UNITED TELELINKS'))
    
    if bill_type == "Service":
        prob_clean = str(data['Problem']).split(' (')[0]
        act_clean = str(data['Action']).split(' (')[0]
        status_clean = str(data['Status']).split(' (')[0]
        print_row("Reported Problem:", prob_clean)
        print_row("Requested Action:", act_clean)
        print_row("Current Status:", status_clean)
    else:
        print_row("MRP:", data['MRP'])
        print_row("Transaction:", "New Phone Dispatched to Retailer")

    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, "This is a computer generated document.", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# 3. Main Header UI
st.markdown("""
    <div style='background: linear-gradient(135deg, #0b57d0 0%, #00c6ff 100%); padding: 20px; border-radius: 12px; text-align: center; color: white; margin-bottom: 20px;'>
        <h1 style='margin:0; font-size: 32px; font-weight: 900;'>📱 JIO PHONE - PORTAL</h1>
        <p style='margin:5px 0 0 0; font-size: 16px; font-weight: 600;'>Sales & Service Management</p>
    </div>
""", unsafe_allow_html=True)

# 4. Dashboard Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛒 New Sale (सेल)", "🛠️ Service Return (सर्विस)", "⏳ Pending", "✅ History", "📂 Data & Bills"])

# ==========================================
# TAB 1: NEW SALE (नया फ़ोन बेचना)
# ==========================================
with tab1:
    st.markdown("### 🛒 New Sale (Retailer Dispatch)")
    st.info("💡 **नया फ़ोन बेचना:** जब आप किसी रिटेलर को नया फ़ोन देते हैं, तो यहाँ उसकी एंट्री करें। इससे यह IMEI हमेशा के लिए उस रिटेलर के नाम पर आपके ऐप में सेव हो जाएगा।")
    
    sale_qr_data = st.text_input("📷 Scanned Box Data (Paste/Scan Here)", placeholder="डब्बे का 4-कोना या बारकोड स्कैन करें...", key=f"sale_scan_{st.session_state.scan_key}")
    
    parsed_sale = { "MFRNAME": "", "MODELNO": "", "IMEI": "", "MRP": "", "EAN": "", "SRNO": "" }
    
    if sale_qr_data:
        if "<IMEI>" in sale_qr_data.upper() or "<?XML" in sale_qr_data.upper():
            for key in parsed_sale.keys():
                match = re.search(f'<{key}>(.*?)</{key}>', sale_qr_data, re.IGNORECASE)
                if match: parsed_sale[key] = match.group(1)
        elif ',' in sale_qr_data:
            parts = sale_qr_data.split(',')
            if len(parts) >= 5:
                parsed_sale["MODELNO"] = parts[0]; parsed_sale["IMEI"] = parts[1]; parsed_sale["MRP"] = parts[2]; parsed_sale["EAN"] = parts[3]; parsed_sale["SRNO"] = parts[4]
        else:
            parsed_sale["IMEI"] = sale_qr_data
            
    with st.form("sale_form"):
        sale_retailer = st.text_input("👤 Retailer Name (किस रिटेलर को बेच रहे हैं?)*")
        
        c1, c2 = st.columns(2)
        with c1:
            sale_imei = st.text_input("IMEI Number*", value=parsed_sale["IMEI"])
            sale_model = st.text_input("Model Number", value=parsed_sale["MODELNO"])
            sale_mfr = st.text_input("MFRNAME", value=parsed_sale["MFRNAME"])
        with c2:
            sale_mrp = st.text_input("MRP (₹)", value=parsed_sale["MRP"])
            sale_srno = st.text_input("Serial No", value=parsed_sale["SRNO"])
            sale_ean = st.text_input("EAN Code", value=parsed_sale["EAN"])
            
        submit_sale = st.form_submit_button("💾 Save Sale & Assign to Retailer", type="primary", use_container_width=True)
        
        if submit_sale:
            if not sale_retailer or not sale_imei:
                st.error("❌ Retailer Name aur IMEI Number jaruri hai!")
            else:
                new_sale = {
                    "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                    "MFRNAME": sale_mfr, "Model": sale_model, "IMEI": sale_imei,
                    "MRP": sale_mrp, "EAN": sale_ean, "SRNO": sale_srno, "Retailer": sale_retailer.upper()
                }
                st.session_state.sales_db = pd.concat([st.session_state.sales_db, pd.DataFrame([new_sale])], ignore_index=True)
                st.success(f"✅ IMEI {sale_imei} successfully assigned to {sale_retailer.upper()}!")
                st.session_state.scan_key += 1
                time.sleep(1)
                st.rerun()

# ==========================================
# TAB 2: SERVICE RETURN (सर्विस वापसी)
# ==========================================
with tab2:
    st.markdown("### 🛠️ Service Entry (Return / Faulty)")
    st.info("💡 **खराब फ़ोन की वापसी:** रिटेलर का नाम और IMEI चुनें। फ़ोन का मॉडल, MRP और 'बिक्री की तारीख' खुद आ जाएगी।")
    
    entry_method = st.radio("डिवाइस खोजने का तरीका चुनें:", ["🔍 Smart Search (रिटेलर से खोजें)", "📷 Scanner / Paste (स्कैन या पेस्ट)"])
    
    parsed_data = { "MFRNAME": "", "MODELNO": "", "IMEI": "", "MRP": "", "EAN": "", "SRNO": "", "SALE_DATE": "" }
    auto_retailer_name = ""

    # 1. SMART SEARCH LOGIC (फ्रॉम Sales DB)
    if entry_method == "🔍 Smart Search (रिटेलर से खोजें)":
        if st.session_state.sales_db.empty:
            st.warning("⚠️ अभी तक कोई फ़ोन नहीं बेचा गया है। पहले '🛒 New Sale' में जाकर फ़ोन बेचें या 'Data & Bills' टैब में पुरानी एक्सेल डालें।")
        else:
            # 🟢 SMART COLUMN FINDER (It will catch columns no matter what they are named)
            def get_val(row, possible_names):
                for col in row.index:
                    if any(p in str(col).upper() for p in possible_names):
                        val = str(row[col])
                        return val if val.lower() != 'nan' else ""
                return ""

            ret_cols = [c for c in st.session_state.sales_db.columns if 'RETAILER' in str(c).upper() or 'NAME' in str(c).upper()]
            imei_cols = [c for c in st.session_state.sales_db.columns if 'IMEI' in str(c).upper()]
            
            if ret_cols and imei_cols:
                retailer_list = st.session_state.sales_db[ret_cols[0]].dropna().unique().tolist()
                colA, colB = st.columns(2)
                with colA:
                    selected_ret = st.selectbox("👤 Select Retailer*", ["-- Select --"] + sorted(retailer_list))
                
                if selected_ret != "-- Select --":
                    auto_retailer_name = selected_ret
                    ret_data = st.session_state.sales_db[st.session_state.sales_db[ret_cols[0]] == selected_ret]
                    imei_list = ret_data[imei_cols[0]].dropna().astype(str).tolist()
                    
                    with colB:
                        selected_imei = st.selectbox("📱 Select Phone IMEI*", ["-- Select --"] + imei_list)
                        
                    if selected_imei != "-- Select --":
                        match_row = ret_data[ret_data[imei_cols[0]].astype(str) == selected_imei].iloc[0]
                        
                        parsed_data["IMEI"] = selected_imei
                        parsed_data["MODELNO"] = get_val(match_row, ["MODEL"])
                        parsed_data["MFRNAME"] = get_val(match_row, ["MFRNAME", "MANUFACTURER"])
                        parsed_data["MRP"] = get_val(match_row, ["MRP", "PRICE", "RATE"])
                        parsed_data["SRNO"] = get_val(match_row, ["SRNO", "SERIAL"])
                        parsed_data["EAN"] = get_val(match_row, ["EAN"])
                        parsed_data["SALE_DATE"] = get_val(match_row, ["DATE", "TIME"])
                        
                        st.success("✅ Device Found in Sales Record! Details Auto-Filled.")

    # 2. SCAN OR PASTE LOGIC
    elif entry_method == "📷 Scanner / Paste (स्कैन या पेस्ट)":
        qr_data = st.text_input("📷 Scanned Data (Paste Here)", key=f"qr_manual_srv_{st.session_state.scan_key}")
        if qr_data:
            if "<IMEI>" in qr_data.upper() or "<?XML" in qr_data.upper():
                for key in parsed_data.keys():
                    if key != "SALE_DATE":
                        match = re.search(f'<{key}>(.*?)</{key}>', qr_data, re.IGNORECASE)
                        if match: parsed_data[key] = match.group(1)
            elif ',' in qr_data:
                parts = qr_data.split(',')
                if len(parts) >= 5:
                    parsed_data["MODELNO"] = parts[0]; parsed_data["IMEI"] = parts[1]; parsed_data["MRP"] = parts[2]; parsed_data["EAN"] = parts[3]; parsed_data["SRNO"] = parts[4]
            else:
                parsed_data["IMEI"] = qr_data

        if parsed_data["IMEI"] and not st.session_state.sales_db.empty:
            search_imei = str(parsed_data["IMEI"]).strip()
            imei_cols = [c for c in st.session_state.sales_db.columns if 'IMEI' in str(c).upper()]
            ret_cols = [c for c in st.session_state.sales_db.columns if 'RETAILER' in str(c).upper() or 'NAME' in str(c).upper()]
            date_cols = [c for c in st.session_state.sales_db.columns if 'DATE' in str(c).upper()]
            
            if imei_cols and ret_cols:
                match_df = st.session_state.sales_db[st.session_state.sales_db[imei_cols[0]].astype(str).str.strip() == search_imei]
                if not match_df.empty:
                    auto_retailer_name = str(match_df.iloc[0][ret_cols[0]])
                    st.success(f"🤖 Retailer Auto-Found from Sales Record: **{auto_retailer_name}**")
                    if date_cols:
                        parsed_data["SALE_DATE"] = str(match_df.iloc[0][date_cols[0]])

    # 🟢 SHOW SALE DATE (WARRANTY CHECK)
    if parsed_data["SALE_DATE"]:
        st.info(f"📅 **Sale Date (यह फ़ोन कब बेचा गया था):** {parsed_data['SALE_DATE']}")

    # SERVICE FORM
    with st.form("service_form"):
        st.markdown("### 📋 Phone Details")
        c1, c2 = st.columns(2)
        with c1:
            imei_in = st.text_input("IMEI Number*", value=parsed_data["IMEI"])
            model_in = st.text_input("Model Number", value=parsed_data["MODELNO"])
        with c2:
            mrp_in = st.text_input("MRP (₹)", value=parsed_data["MRP"])
            retailer = st.text_input("👤 Retailer Name*", value=auto_retailer_name)

        st.markdown("---")
        st.markdown("### 🛠️ Service Information")
        problem = st.selectbox("⚠️ Phone Problem*", ["-- Select --", "Damage / Broken (टूटा/डैमेज है)", "Battery Issue (बैटरी ख़राब)", "Software Dead (सॉफ्टवेयर डेड)", "Display Broken (डिस्प्ले टूटा है)", "Keypad Issue (कीपैड ख़राब)", "Charging Issue (चार्ज नहीं हो रहा)", "Other (अन्य)"])
        action = st.radio("🔄 Action Required*", ["Replace with New Phone (नया बदल कर देना है)", "Repair Same Phone (वही ठीक करके देना है)"])
        status = st.radio("📦 Current Status*", ["Pending (फ़ोन अभी पेंडिंग है)", "Delivered (दे दिया गया है)"])

        submit = st.form_submit_button("💾 Save Service Entry", type="primary", use_container_width=True)

        if submit:
            if problem == "-- Select --" or not retailer or not imei_in:
                st.error("❌ Retailer Name, IMEI, and Problem are required.")
            else:
                new_id = f"JIO-{(len(st.session_state.service_db) if not st.session_state.service_db.empty else 0)+1:04d}"
                new_data = {
                    "action": "add", "ID": new_id, "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                    "MFRNAME": parsed_data["MFRNAME"], "Model": model_in, 
                    "IMEI": imei_in, "MRP": mrp_in, 
                    "EAN": parsed_data["EAN"], "SRNO": parsed_data["SRNO"],
                    "Retailer": retailer.upper(), "Problem": problem, "Action": action, 
                    "Status": "Pending" if "Pending" in status else "Delivered"
                }
                st.session_state.service_db = pd.concat([st.session_state.service_db, pd.DataFrame([new_data])], ignore_index=True)
                
                try:
                    if WEBHOOK_URL != "यहाँ_अपना_नया_WEBHOOK_URL_डालें":
                        requests.post(WEBHOOK_URL, json=new_data, timeout=3)
                except: pass 
                
                st.success("✅ Service Entry Saved! Go to 'Data & Bills' tab to print bill.")

# ==========================================
# TAB 3 & 4: PENDING AND HISTORY
# ==========================================
with tab3:
    st.markdown("### ⏳ Pending Action Board")
    if st.session_state.service_db.empty:
        st.info("🎉 Good Job! No pending phones right now.")
    else:
        pending_df = st.session_state.service_db[st.session_state.service_db["Status"].astype(str).str.contains("Pending", case=False, na=False)]
        if pending_df.empty: st.info("🎉 Good Job! No pending phones right now.")
        else:
            for idx, row in pending_df.iterrows():
                st.markdown(f"<div style='border:1px solid #f87171; padding:15px; border-radius:10px; background:#fef2f2; margin-bottom:10px;'><b>👤 {row['Retailer']}</b> | IMEI: {row['IMEI']}<br>Problem: {row['Problem']}</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("### ✅ Delivered / Completed Phones")
    if not st.session_state.service_db.empty:
        delivered_df = st.session_state.service_db[st.session_state.service_db["Status"].astype(str).str.contains("Delivered", case=False, na=False)]
        st.dataframe(delivered_df[["ID", "Date", "Retailer", "IMEI", "Problem", "Action"]], hide_index=True, use_container_width=True)
    else:
        st.info("No completed services yet.")

# ==========================================
# TAB 5: DATA, BILLS & UPLOADS
# ==========================================
with tab5:
    st.markdown("### 🖨️ Re-Print Bill / Invoice")
    search_imei = st.text_input("🔍 Enter IMEI Number to generate Bill:")
    if st.button("Print Service Bill", type="primary"):
        if search_imei and not st.session_state.service_db.empty:
            result = st.session_state.service_db[st.session_state.service_db['IMEI'].astype(str).str.contains(search_imei, na=False)]
            if not result.empty:
                st.success("✅ Record Found!")
                if HAS_FPDF:
                    pdf_bytes = generate_service_bill(result.iloc[0].to_dict(), "Service")
                    st.download_button("📥 Download Service Bill (PDF)", data=pdf_bytes, file_name=f"Jio_Service_{search_imei}.pdf", mime="application/pdf")
            else: st.error("❌ Not found in Service DB.")
            
    st.markdown("---")
    st.markdown("### 📊 Your Sales Database (Current Session)")
    if not st.session_state.sales_db.empty:
        st.dataframe(st.session_state.sales_db, use_container_width=True)
        csv = st.session_state.sales_db.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Sales Record (Excel)", data=csv, file_name="Jio_Sales_Record.csv", mime="text/csv", use_container_width=True)
    else:
        st.info("No sales data yet. Sell a phone in 'New Sale' tab or upload past records below.")
        
    st.markdown("---")
    st.markdown("### 📂 Upload Old Sales Data (Optional)")
    uploaded_file = st.file_uploader("📥 Upload old Sales Excel/CSV", type=["xlsx", "xls", "csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.session_state.sales_db = pd.concat([st.session_state.sales_db, df], ignore_index=True)
            st.success("✅ Past Data Loaded Successfully!")
        except Exception as e: st.error(f"Error: {e}")
