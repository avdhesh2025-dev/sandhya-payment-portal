import streamlit as st
import pandas as pd
from datetime import datetime

# कैमरा स्कैनर के टूल्स लोड करने की कोशिश
try:
    from pyzbar.pyzbar import decode
    from PIL import Image
    HAS_SCANNER = True
except ImportError:
    HAS_SCANNER = False

# 1. Page Configuration
st.set_page_config(page_title="Jio Phone Service", page_icon="📱", layout="centered")

# 2. Database Initialization (Temporary memory)
if 'service_db' not in st.session_state:
    st.session_state.service_db = pd.DataFrame(columns=[
        "ID", "Date", "Model", "IMEI", "MRP", "EAN", "SRNO",
        "Retailer", "Problem", "Action", "Status"
    ])

# 3. Main Header UI
st.markdown("""
    <div style='background: linear-gradient(135deg, #0b57d0 0%, #00c6ff 100%); padding: 20px; border-radius: 12px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
        <h1 style='margin:0; font-size: 32px; font-weight: 900;'>📱 JIO PHONE SERVICE</h1>
        <p style='margin:5px 0 0 0; font-size: 16px; font-weight: 600;'>Sandhya Enterprises - Return & Replacement Portal</p>
    </div>
""", unsafe_allow_html=True)

# 4. Single Dashboard Tabs
tab1, tab2, tab3 = st.tabs(["📝 New Scan & Entry", "⏳ Pending Phones", "✅ Delivered History"])

# ==========================================
# TAB 1: NEW ENTRY & QR SCAN
# ==========================================
with tab1:
    st.markdown("### 🔍 Step 1: Scan QR Code")
    
    # स्कैन करने का तरीका चुनें
    scan_method = st.radio("स्कैन करने का तरीका (Select Scan Method):", ["📷 Mobile Camera (मोबाइल कैमरा)", "🔫 Scanner Machine (गन स्कैनर)"])
    
    qr_data = ""
    
    if scan_method == "📷 Mobile Camera (मोबाइल कैमरा)":
        if HAS_SCANNER:
            st.info("👇 'Browse files' पर क्लिक करें, 'Camera' चुनें और मोबाइल के असली कैमरे से साफ़ फोटो लें!")
            
            # HD Camera File Uploader
            img_file = st.file_uploader("📷 QR Code की फोटो लें", type=['png', 'jpg', 'jpeg'])
            
            if img_file is not None:
                try:
                    img = Image.open(img_file)
                    decoded = decode(img)
                    if decoded:
                        qr_data = decoded[0].data.decode('utf-8')
                        st.success("✅ QR Successfully Read!")
                    else:
                        st.error("❌ QR कोड पढ़ा नहीं जा सका। कृपया कैमरे को फोकस करके साफ़ फोटो लें।")
                except Exception as e:
                    st.error("Error processing image.")
        else:
            st.error("⚠️ कैमरा चालू करने के लिए GitHub में 'requirements.txt' के अंदर pyzbar और Pillow लिखना होगा।")
            
    else:
        st.info("👇 नीचे क्लिक करें और अपनी स्कैनर मशीन से स्कैन करें।")
        qr_data = st.text_input("🔫 Click here and Scan QR...", placeholder="Scanner will type data here automatically...")

    # Logic to auto-fill data based on scanned string
    model_val = imei_val = mrp_val = ean_val = srno_val = ""
    
    if qr_data:
        try:
            parts = qr_data.split(',')
            if len(parts) >= 5:
                model_val, imei_val, mrp_val, ean_val, srno_val = parts[0], parts[1], parts[2], parts[3], parts[4]
                st.success("✅ Scanned Successfully! Data Locked.")
            else:
                imei_val = qr_data 
                st.warning("⚠️ Unknown QR format. Filling raw data in IMEI box.")
        except:
            st.error("Error reading QR Data.")

    with st.form("service_form"):
        st.markdown("### 🔒 Step 2: Scanned Details (Read Only)")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Model Number", value=model_val, disabled=True)
            st.text_input("MRP", value=mrp_val, disabled=True)
            st.text_input("Serial No (SRNO)", value=srno_val, disabled=True)
        with c2:
            st.text_input("IMEI Number", value=imei_val, disabled=True)
            st.text_input("EAN", value=ean_val, disabled=True)

        st.markdown("---")
        st.markdown("### 🛠️ Step 3: Service Information")
        retailer = st.text_input("👤 Retailer Name (किस रिटेलर का फ़ोन है?)*")
        
        problem = st.selectbox(
            "⚠️ Phone Problem (फ़ोन में क्या दिक्कत है?)*",
            ["-- Select --", "Battery Issue (बैटरी ख़राब)", "Software Dead (सॉफ्टवेयर डेड)", "Display Broken (डिस्प्ले टूटा है)", "Keypad Issue (कीपैड ख़राब)", "Charging Issue (चार्ज नहीं हो रहा)", "Other (अन्य)"]
        )
        
        action = st.radio(
            "🔄 Action Required (क्या करना है?)*",
            ["Replace with New Phone (फ़ोन बदल कर नया देना है)", "Repair Same Phone (वही फ़ोन ठीक करके देना है)"]
        )
        
        status = st.radio(
            "📦 Current Status (स्टेटस क्या है?)*",
            ["Pending (फ़ोन अभी हमारे पास पेंडिंग है)", "Delivered (रिटेलर को दे दिया गया है)"]
        )

        submit = st.form_submit_button("💾 Save Entry", type="primary", use_container_width=True)

        if submit:
            if problem == "-- Select --" or not retailer:
                st.error("❌ Please enter Retailer Name and select a Problem.")
            elif not imei_val:
                st.error("❌ Please Scan the QR Code first before saving.")
            else:
                new_id = f"JIO-{len(st.session_state.service_db)+1:04d}"
                new_data = {
                    "ID": new_id, 
                    "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                    "Model": model_val, "IMEI": imei_val, "MRP": mrp_val, "EAN": ean_val, "SRNO": srno_val,
                    "Retailer": retailer.upper(), "Problem": problem, "Action": action, 
                    "Status": "Pending" if "Pending" in status else "Delivered"
                }
                
                st.session_state.service_db = pd.concat([st.session_state.service_db, pd.DataFrame([new_data])], ignore_index=True)
                st.success(f"🎉 Saved Successfully! ID: {new_id} is marked as **{new_data['Status']}**")

# ==========================================
# TAB 2: PENDING PHONES DASHBOARD
# ==========================================
with tab2:
    st.markdown("### ⏳ Pending Action Board")
    
    pending_df = st.session_state.service_db[st.session_state.service_db["Status"] == "Pending"]
    
    if pending_df.empty:
        st.info("🎉 Good Job! No pending phones right now.")
    else:
        st.error(f"🚨 You have {len(pending_df)} phone(s) pending for service!")
        
        for idx, row in pending_df.iterrows():
            st.markdown(f"""
                <div style='border: 1px solid #f87171; padding: 15px; border-radius: 10px; background: #fef2f2; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                    <div style='display: flex; justify-content: space-between;'>
                        <h4 style='color: #b91c1c; margin: 0;'>👤 Retailer: {row['Retailer']}</h4>
                        <span style='background: #b91c1c; color: white; padding: 3px 8px; border-radius: 5px; font-size: 12px;'>{row['ID']}</span>
                    </div>
                    <p style='margin: 8px 0 2px 0; color: #4b5563;'><b>📱 Model:</b> {row['Model']} | <b>IMEI:</b> {row['IMEI']}</p>
                    <p style='margin: 2px 0; color: #4b5563;'><b>⚠️ Problem:</b> {row['Problem']}</p>
                    <p style='margin: 2px 0; color: #1e3a8a;'><b>🛠️ Action:</b> {row['Action']}</p>
                    <p style='margin: 6px 0 0 0; font-size: 12px; color: #9ca3af;'>📅 Received On: {row['Date']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✅ Mark as Delivered (Done)", key=f"del_{row['ID']}", type="secondary", use_container_width=True):
                st.session_state.service_db.loc[st.session_state.service_db['ID'] == row['ID'], 'Status'] = "Delivered"
                st.success(f"{row['ID']} marked as Delivered!")
                st.rerun()

# ==========================================
# TAB 3: DELIVERED HISTORY
# ==========================================
with tab3:
    st.markdown("### ✅ Delivered / Completed Phones")
    
    delivered_df = st.session_state.service_db[st.session_state.service_db["Status"] == "Delivered"]
    
    if delivered_df.empty:
        st.info("No completed services yet.")
    else:
        st.dataframe(
            delivered_df[["ID", "Date", "Retailer", "IMEI", "Problem", "Action"]].sort_values("ID", ascending=False), 
            hide_index=True, 
            use_container_width=True
        )
        
        csv = delivered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Delivered History (Excel)",
            data=csv,
            file_name=f"Jio_Service_History_{datetime.now().strftime('%d-%m-%Y')}.csv",
            mime="text/csv",
            use_container_width=True
        )
