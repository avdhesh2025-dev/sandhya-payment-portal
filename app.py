import streamlit as st
import pandas as pd
from datetime import datetime
import time
import re  # 🟢 Added Regex module to decode XML data

# 1. Page Configuration
st.set_page_config(page_title="Jio Phone Service", page_icon="📱", layout="centered")

# 2. Database Initialization
if 'service_db' not in st.session_state:
    st.session_state.service_db = pd.DataFrame(columns=[
        "ID", "Date", "Model", "IMEI", "MRP", "EAN", "SRNO",
        "Retailer", "Problem", "Action", "Status"
    ])

# 🟢 SMART FIX: Dynamic key counter to reset scanner without errors
if 'scan_key' not in st.session_state:
    st.session_state.scan_key = 0

# 3. Main Header UI
st.markdown("""
    <div style='background: linear-gradient(135deg, #0b57d0 0%, #00c6ff 100%); padding: 20px; border-radius: 12px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
        <h1 style='margin:0; font-size: 32px; font-weight: 900;'>📱 JIO PHONE SERVICE</h1>
        <p style='margin:5px 0 0 0; font-size: 16px; font-weight: 600;'>Return & Replacement Portal</p>
    </div>
""", unsafe_allow_html=True)

# 4. Single Dashboard Tabs
tab1, tab2, tab3 = st.tabs(["📝 New Scan & Entry", "⏳ Pending Phones", "✅ Delivered History"])

# ==========================================
# TAB 1: NEW ENTRY & LIVE BACK-CAMERA QR SCAN
# ==========================================
with tab1:
    st.markdown("### 🔍 Step 1: Scan QR Code")
    
    # स्कैन का तरीका
    scan_method = st.radio("स्कैन का तरीका चुनें:", ["📷 Live Mobile Camera (लाइव कैमरा)", "🔫 Scanner Machine (गन स्कैनर)"])
    
    qr_data = ""

    if scan_method == "📷 Live Mobile Camera (लाइव कैमरा)":
        st.info("👇 डब्बे में QR कोड लाएं। पीछे वाला कैमरा (Back Camera) अपने-आप स्कैन कर लेगा।")
        
        # 🟢 HTML/JS Scanner Code
        scanner_html = """
        <script src="https://unpkg.com/html5-qrcode"></script>
        <div id="reader" style="width: 100%; max-width: 400px; margin: auto; border: 4px solid #0b57d0; border-radius: 10px; overflow: hidden; background: #000;"></div>
        <script>
            const html5QrCode = new Html5Qrcode("reader");
            const config = { fps: 15, qrbox: { width: 220, height: 220 } };

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
                        document.getElementById('reader').innerHTML = '<div style="padding: 80px 0; text-align: center; color: #15803d; font-size: 24px; font-weight: bold; background: #dcfce7; height: 100%;">✅ Scan Successful! नीचे चेक करें 👇</div>';
                    });
                }, 
                (errorMessage) => { /* Ignore errors */ }
            ).catch(err => {
                document.getElementById('reader').innerHTML = '<div style="color:red; padding:20px; background:white;">Camera Error! Refresh page and allow permissions.</div>';
            });
        </script>
        """
        st.components.v1.html(scanner_html, height=350)
        
        qr_data = st.text_input("📷 Scanned Data (Auto-Fill)", key=f"qr_auto_{st.session_state.scan_key}")
        
    else:
        st.info("👇 नीचे क्लिक करें और मशीन से स्कैन करें।")
        qr_data = st.text_input("📷 Scanned Data (Auto-Fill)", placeholder="Scanner will type data here...", key=f"qr_manual_{st.session_state.scan_key}")

    # Reset Button
    if st.button("🔄 Reset Scanner / Clear Data"):
        st.session_state.scan_key += 1 
        st.rerun()

    # 🟢 NEW LOGIC: XML & Comma Decoder
    model_val = imei_val = mrp_val = ean_val = srno_val = ""
    
    if qr_data:
        # Check if data is in Jio's XML format
        if "<?xml" in qr_data or "<MODELNO>" in qr_data:
            try:
                # Using Regex to extract data from XML tags safely
                m_match = re.search(r'<MODELNO>(.*?)</MODELNO>', qr_data, re.IGNORECASE)
                i_match = re.search(r'<IMEI>(.*?)</IMEI>', qr_data, re.IGNORECASE)
                mrp_match = re.search(r'<MRP>(.*?)</MRP>', qr_data, re.IGNORECASE)
                e_match = re.search(r'<EAN>(.*?)</EAN>', qr_data, re.IGNORECASE)
                s_match = re.search(r'<SRNO>(.*?)</SRNO>', qr_data, re.IGNORECASE)

                model_val = m_match.group(1) if m_match else ""
                imei_val = i_match.group(1) if i_match else ""
                mrp_val = mrp_match.group(1) if mrp_match else ""
                ean_val = e_match.group(1) if e_match else ""
                srno_val = s_match.group(1) if s_match else ""
                
                if imei_val:
                    st.success("✅ Jio QR (XML) Successfully Decoded!")
                else:
                    st.error("⚠️ XML format detected, but IMEI not found.")
            except Exception as e:
                st.error(f"Error parsing XML: {e}")
                
        # Fallback if it's a simple comma-separated format
        elif ',' in qr_data:
            parts = qr_data.split(',')
            if len(parts) >= 5:
                model_val, imei_val, mrp_val, ean_val, srno_val = parts[0], parts[1], parts[2], parts[3], parts[4]
                st.success("✅ QR Code Successfully Read!")
            else:
                imei_val = qr_data 
                st.warning("⚠️ Scanner read the data, but format is unknown. Raw data filled in IMEI.")
        else:
            imei_val = qr_data
            st.warning("⚠️ Raw data filled in IMEI.")

    # FORM DETAILS
    with st.form("service_form"):
        st.markdown("### 📋 Step 2: Scanned Details (Read Only)")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Model Number", value=model_val, disabled=True)
            st.text_input("MRP", value=mrp_val, disabled=True)
            st.text_input("Serial No (SRNO)", value=srno_val, disabled=True)
        with c2:
            st.text_input("IMEI Number*", value=imei_val, disabled=True)
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
            ["Replace with New Phone (नया बदल कर देना है)", "Repair Same Phone (वही ठीक करके देना है)"]
        )
        
        status = st.radio(
            "📦 Current Status (स्टेटस क्या है?)*",
            ["Pending (फ़ोन अभी पेंडिंग है)", "Delivered (दे दिया गया है)"]
        )

        submit = st.form_submit_button("💾 Save Entry", type="primary", use_container_width=True)

        if submit:
            if problem == "-- Select --" or not retailer:
                st.error("❌ Please enter Retailer Name and select a Problem.")
            elif not imei_val:
                st.error("❌ Please Scan a valid QR Code first.")
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
                
                st.session_state.scan_key += 1
                time.sleep(1.5)
                st.rerun()

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
            
            c1, c2 = st.columns(2)
            if c1.button(f"✅ Mark Delivered", key=f"del_{row['ID']}", type="secondary", use_container_width=True):
                st.session_state.service_db.loc[st.session_state.service_db['ID'] == row['ID'], 'Status'] = "Delivered"
                st.success(f"{row['ID']} marked as Delivered!")
                time.sleep(1)
                st.rerun()
            if c2.button(f"🗑️ Delete", key=f"rm_{row['ID']}", use_container_width=True):
                st.session_state.service_db = st.session_state.service_db[st.session_state.service_db['ID'] != row['ID']]
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
