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

# 1. Page Configuration
st.set_page_config(page_title="Jio Phone Service", page_icon="📱", layout="centered")

# ==========================================
# 🔴 यहाँ अपना नया WEBHOOK और SHEET ID डालें 🔴
# ==========================================
WEBHOOK_URL = "यहाँ_अपना_नया_WEBHOOK_URL_डालें"
SHEET_ID = "यहाँ_अपनी_नई_Google_Sheet_की_ID_डालें"
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

if 'sales_db' not in st.session_state:
    st.session_state.sales_db = pd.DataFrame()

if 'scan_key' not in st.session_state:
    st.session_state.scan_key = 0

if 'last_bill_data' not in st.session_state:
    st.session_state.last_bill_data = None

# PDF BILL GENERATOR FUNCTION
def generate_service_bill(data):
    if not HAS_FPDF: return None
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, "SANDHYA ENTERPRISES", ln=True, align='C')
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 6, "Jio Phone Service & Return Receipt", ln=True, align='C')
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

    print_row("Receipt ID:", data['ID'])
    print_row("Date & Time:", data['Date'])
    print_row("Retailer Name:", data['Retailer'])
    print_row("IMEI Number:", data['IMEI'])
    print_row("Model Number:", data['Model'])
    print_row("Manufacturer:", data['MFRNAME'])
    
    prob_clean = str(data['Problem']).split(' (')[0]
    act_clean = str(data['Action']).split(' (')[0]
    status_clean = str(data['Status']).split(' (')[0]

    print_row("Reported Problem:", prob_clean)
    print_row("Requested Action:", act_clean)
    print_row("Current Status:", status_clean)

    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, "This is a computer generated service receipt.", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')


# 3. Main Header UI
st.markdown("""
    <div style='background: linear-gradient(135deg, #0b57d0 0%, #00c6ff 100%); padding: 20px; border-radius: 12px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
        <h1 style='margin:0; font-size: 32px; font-weight: 900;'>📱 JIO PHONE SERVICE</h1>
        <p style='margin:5px 0 0 0; font-size: 16px; font-weight: 600;'>Return & Replacement Portal</p>
    </div>
""", unsafe_allow_html=True)

# 4. Dashboard Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 New Entry", "⏳ Pending", "✅ History", "🖨️ Re-Print Bill", "📂 Auto-Fill Setup"])

# ==========================================
# TAB 1: NEW ENTRY & LIVE SCANNER
# ==========================================
with tab1:
    if st.session_state.last_bill_data is not None:
        bill_data = st.session_state.last_bill_data
        st.success(f"🎉 Entry Saved Successfully! ID: {bill_data['ID']}")
        st.markdown(f"### 📄 Bill Generated for {bill_data['Retailer']}")
        
        if HAS_FPDF:
            pdf_bytes = generate_service_bill(bill_data)
            st.download_button(
                label="📥 Download Service Bill (PDF)",
                data=pdf_bytes,
                file_name=f"Jio_Bill_{bill_data['IMEI']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        if st.button("➕ Start New Scan & Entry", type="primary", use_container_width=True):
            st.session_state.last_bill_data = None
            st.session_state.scan_key += 1
            st.rerun()

    else:
        st.markdown("### 🔍 Step 1: Scan QR Code")
        scan_method = st.radio("स्कैन का तरीका चुनें:", ["📷 Live Mobile Camera (लाइव कैमरा)", "🔫 Scanner Machine (गन स्कैनर)"])
        
        qr_data = ""

        if scan_method == "📷 Live Mobile Camera (लाइव कैमरा)":
            st.info("💡 **TIP:** डब्बे के **4-कोने वाले चौकोर कोड** को इस लाल डब्बे के बीच में लाएं।")
            
            # 🟢 PERFECT SQUARE SCANNER FOR 4-CORNER DATA MATRIX
            scanner_html = """
            <script src="https://unpkg.com/html5-qrcode"></script>
            <div id="reader" style="width: 100%; max-width: 400px; margin: auto; border: 4px solid #0b57d0; border-radius: 10px; overflow: hidden; background: #000;"></div>
            <script>
                const html5QrCode = new Html5Qrcode("reader");
                // Square box to easily catch the 4-corner Data Matrix
                const config = { fps: 20, qrbox: { width: 250, height: 250 }, experimentalFeatures: { useBarCodeDetectorIfSupported: true } };
                function setNativeValue(element, value) {
                    const prototype = Object.getPrototypeOf(element);
                    const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
                    prototypeValueSetter.call(element, value);
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                }
                html5QrCode.start({ facingMode: "environment" }, config, 
                    (decodedText) => {
                        let inputs = window.parent.document.querySelectorAll('input[type="text"]');
                        inputs.forEach(inp => {
                            if(inp.getAttribute('aria-label') && inp.getAttribute('aria-label').includes('Scanned Data')) {
                                setNativeValue(inp, decodedText);
                            }
                        });
                        html5QrCode.stop().then(() => {
                            document.getElementById('reader').innerHTML = '<div style="padding: 80px 0; text-align: center; color: #15803d; font-size: 24px; font-weight: bold; background: #dcfce7; height: 100%;">✅ Code Caught! Scroll Down 👇</div>';
                        });
                    }, 
                    (errorMessage) => { /* Ignore errors */ }
                ).catch(err => {
                    document.getElementById('reader').innerHTML = '<div style="color:red; padding:20px; background:white;">Camera Error! Allow permissions.</div>';
                });
            </script>
            """
            st.components.v1.html(scanner_html, height=350)
            qr_data = st.text_input("📷 Scanned Data (Auto-Fill)", key=f"qr_auto_{st.session_state.scan_key}")
            
        else:
            qr_data = st.text_input("📷 Scanned Data (Auto-Fill)", placeholder="Scanner will type data here...", key=f"qr_manual_{st.session_state.scan_key}")

        if st.button("🔄 Reset Scanner / Clear Data"):
            st.session_state.scan_key += 1 
            st.rerun()

        parsed_data = { "MFRNAME": "", "MODELNO": "", "IMEI": "", "MRP": "", "EAN": "", "SRNO": "" }
        
        if qr_data:
            if "<IMEI>" in qr_data.upper() or "<?XML" in qr_data.upper():
                st.success("✅ 4-Kona Jio QR (XML) Successfully Decoded!")
                for key in parsed_data.keys():
                    match = re.search(f'<{key}>(.*?)</{key}>', qr_data, re.IGNORECASE)
                    if match: parsed_data[key] = match.group(1)
            elif ',' in qr_data:
                parts = qr_data.split(',')
                if len(parts) >= 5:
                    parsed_data["MODELNO"] = parts[0]; parsed_data["IMEI"] = parts[1]; parsed_data["MRP"] = parts[2]; parsed_data["EAN"] = parts[3]; parsed_data["SRNO"] = parts[4]
                    st.success("✅ Simple QR Code Successfully Read!")
                else:
                    parsed_data["IMEI"] = qr_data 
            else:
                parsed_data["IMEI"] = qr_data

        # AUTO-FILL RETAILER LOGIC
        auto_retailer_name = ""
        if parsed_data["IMEI"] and not st.session_state.sales_db.empty:
            search_imei = str(parsed_data["IMEI"]).strip()
            imei_cols = [c for c in st.session_state.sales_db.columns if 'IMEI' in str(c).upper()]
            ret_cols = [c for c in st.session_state.sales_db.columns if 'RETAILER' in str(c).upper() or 'NAME' in str(c).upper()]
            
            if imei_cols and ret_cols:
                match_df = st.session_state.sales_db[st.session_state.sales_db[imei_cols[0]].astype(str).str.strip() == search_imei]
                if not match_df.empty:
                    auto_retailer_name = str(match_df.iloc[0][ret_cols[0]])
                    st.success(f"🤖 Retailer Auto-Found in Database: **{auto_retailer_name}**")

        with st.form("service_form"):
            st.markdown("### 📋 Step 2: Scanned Details (Auto-Boxed)")
            st.text_input("Manufacturer Name (MFRNAME)", value=parsed_data["MFRNAME"], disabled=True)
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Model Number", value=parsed_data["MODELNO"])
                st.text_input("MRP", value=parsed_data["MRP"])
                st.text_input("Serial No (SRNO)", value=parsed_data["SRNO"])
            with c2:
                st.text_input("IMEI Number*", value=parsed_data["IMEI"])
                st.text_input("EAN", value=parsed_data["EAN"])

            st.markdown("---")
            st.markdown("### 🛠️ Step 3: Service Information & Options")
            
            retailer = st.text_input("👤 Retailer Name (किस रिटेलर का फ़ोन है?)*", value=auto_retailer_name)
            problem = st.selectbox("⚠️ Phone Problem (दिक्कत क्या है?)*", ["-- Select --", "Damage / Broken (टूटा/डैमेज है)", "Battery Issue (बैटरी ख़राब)", "Software Dead (सॉफ्टवेयर डेड)", "Display Broken (डिस्प्ले टूटा है)", "Keypad Issue (कीपैड ख़राब)", "Charging Issue (चार्ज नहीं हो रहा)", "Other (अन्य)"])
            action = st.radio("🔄 Action Required*", ["Replace with New Phone (नया बदल कर देना है)", "Repair Same Phone (वही ठीक करके देना है)"])
            status = st.radio("📦 Current Status*", ["Pending (फ़ोन अभी पेंडिंग है)", "Delivered (दे दिया गया है)"])

            submit = st.form_submit_button("💾 Save Entry & Print Bill", type="primary", use_container_width=True)

            if submit:
                if problem == "-- Select --" or not retailer:
                    st.error("❌ Please enter Retailer Name and select a Problem.")
                elif not parsed_data["IMEI"]:
                    st.error("❌ Please Scan a valid QR Code first.")
                else:
                    if st.session_state.service_db.empty: new_num = 1
                    else: new_num = len(st.session_state.service_db) + 1
                        
                    new_id = f"JIO-{new_num:04d}"
                    new_data = {
                        "action": "add", "ID": new_id, "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "MFRNAME": parsed_data["MFRNAME"], "Model": parsed_data["MODELNO"], 
                        "IMEI": parsed_data["IMEI"], "MRP": parsed_data["MRP"], 
                        "EAN": parsed_data["EAN"], "SRNO": parsed_data["SRNO"],
                        "Retailer": retailer.upper(), "Problem": problem, "Action": action, 
                        "Status": "Pending" if "Pending" in status else "Delivered"
                    }
                    
                    st.session_state.service_db = pd.concat([st.session_state.service_db, pd.DataFrame([new_data])], ignore_index=True)
                    st.session_state.last_bill_data = new_data
                    
                    # 🟢 FIX: SILENT WEBHOOK POST (No Timeout Errors on Screen)
                    try:
                        if WEBHOOK_URL != "यहाँ_अपना_नया_WEBHOOK_URL_डालें":
                            requests.post(WEBHOOK_URL, json=new_data, timeout=3) # Only waits 3 seconds
                    except: 
                        pass # Ignores error entirely so your app never hangs!
                    
                    st.rerun()

# ==========================================
# TAB 2: PENDING PHONES DASHBOARD
# ==========================================
with tab2:
    st.markdown("### ⏳ Pending Action Board")
    if st.session_state.service_db.empty:
        pending_df = pd.DataFrame()
    else:
        pending_df = st.session_state.service_db[st.session_state.service_db["Status"].astype(str).str.contains("Pending", case=False, na=False)]
    
    if pending_df.empty: st.info("🎉 Good Job! No pending phones right now.")
    else:
        st.error(f"🚨 You have {len(pending_df)} phone(s) pending for service!")
        for idx, row in pending_df.iterrows():
            st.markdown(f"""
                <div style='border: 1px solid #f87171; padding: 15px; border-radius: 10px; background: #fef2f2; margin-bottom: 10px;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <h4 style='color: #b91c1c; margin: 0;'>👤 {row['Retailer']}</h4>
                        <span style='background: #b91c1c; color: white; padding: 3px 8px; border-radius: 5px; font-size: 12px;'>{row['ID']}</span>
                    </div>
                    <p style='margin: 8px 0 2px 0; color: #4b5563;'><b>📱 Model:</b> {row['Model']} | <b>IMEI:</b> {row['IMEI']}</p>
                    <p style='margin: 2px 0; color: #4b5563;'><b>⚠️ Problem:</b> {row['Problem']}</p>
                    <p style='margin: 2px 0; color: #1e3a8a;'><b>🛠️ Action:</b> {row['Action']}</p>
                    <p style='margin: 6px 0 0 0; font-size: 12px; color: #9ca3af;'>📅 {row['Date']}</p>
                </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button(f"✅ Mark Delivered", key=f"del_{row['ID']}", type="secondary", use_container_width=True):
                st.session_state.service_db.loc[st.session_state.service_db['ID'] == row['ID'], 'Status'] = "Delivered"
                try:
                    if WEBHOOK_URL != "यहाँ_अपना_नया_WEBHOOK_URL_डालें":
                        requests.post(WEBHOOK_URL, json={"action":"update", "ID":row['ID'], "Status":"Delivered"}, timeout=3)
                except: pass
                st.rerun()
            if c2.button(f"🗑️ Delete", key=f"rm_{row['ID']}", use_container_width=True):
                st.session_state.service_db = st.session_state.service_db[st.session_state.service_db['ID'] != row['ID']]
                try:
                    if WEBHOOK_URL != "यहाँ_अपना_नया_WEBHOOK_URL_डालें":
                        requests.post(WEBHOOK_URL, json={"action":"delete", "ID":row['ID']}, timeout=3)
                except: pass
                st.rerun()

# ==========================================
# TAB 3: DELIVERED HISTORY
# ==========================================
with tab3:
    st.markdown("### ✅ Delivered / Completed Phones")
    if st.session_state.service_db.empty:
        delivered_df = pd.DataFrame()
    else:
        delivered_df = st.session_state.service_db[st.session_state.service_db["Status"].astype(str).str.contains("Delivered", case=False, na=False)]
    
    if delivered_df.empty: st.info("No completed services yet.")
    else:
        st.dataframe(delivered_df[["ID", "Date", "Retailer", "IMEI", "Problem", "Action"]].sort_values("ID", ascending=False), hide_index=True, use_container_width=True)
        csv = delivered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Delivered History (Excel)", data=csv, file_name=f"Jio_Service_History_{datetime.now().strftime('%d-%m-%Y')}.csv", mime="text/csv", use_container_width=True)

# ==========================================
# TAB 4: RE-PRINT BILL (SEARCH BY IMEI)
# ==========================================
with tab4:
    st.markdown("### 🖨️ Re-Print Old Bill")
    st.info("किसी भी पुराने फ़ोन का बिल दोबारा निकालने के लिए उसका IMEI नंबर डालें।")
    search_imei = st.text_input("🔍 Enter IMEI Number to Search:")
    if st.button("Search & Print Bill", type="primary"):
        if search_imei and not st.session_state.service_db.empty:
            result = st.session_state.service_db[st.session_state.service_db['IMEI'].astype(str).str.contains(search_imei, na=False)]
            if not result.empty:
                st.success("✅ Record Found!")
                found_data = result.iloc[0].to_dict()
                st.markdown(f"**Retailer:** {found_data['Retailer']} | **Status:** {found_data['Status']}")
                if HAS_FPDF:
                    pdf_bytes = generate_service_bill(found_data)
                    st.download_button("📥 Download Bill (PDF)", data=pdf_bytes, file_name=f"Jio_Bill_{found_data['IMEI']}.pdf", mime="application/pdf", use_container_width=True)
            else: st.error(f"❌ No record found for IMEI: {search_imei}")
        else: st.warning("Please enter an IMEI number first.")

# ==========================================
# TAB 5: AUTO-FILL SALES DATA SETUP
# ==========================================
with tab5:
    st.markdown("### 📂 Upload Sales Data (For Auto-Fill)")
    st.info("""
        **ऑटोमैटिक रिटेलर का नाम कैसे लाएं?**
        यहाँ अपनी उस Excel या CSV फाइल को अपलोड करें जिसमें आपने रिकॉर्ड रखा है कि कौन सा IMEI किस रिटेलर को बेचा गया है।
    """)
    uploaded_file = st.file_uploader("📥 Upload Sales/Dispatch Excel File", type=["xlsx", "xls", "csv"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)
            st.session_state.sales_db = df
            st.success(f"✅ Data Loaded Successfully! ({len(df)} Records Found)")
        except Exception as e: st.error(f"❌ Error reading file: {e}")
