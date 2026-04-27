import streamlit as st
import pandas as pd
from datetime import datetime
import time

# 1. Page Configuration
st.set_page_config(page_title="Jio Phone Service", page_icon="📱", layout="centered")

# 2. Database Initialization
if 'service_db' not in st.session_state:
    st.session_state.service_db = pd.DataFrame(columns=[
        "ID", "Date", "Model", "IMEI", "MRP", "EAN", "SRNO",
        "Retailer", "Problem", "Action", "Status"
    ])

# 🟢 SMART FIX: Catch QR Data from URL immediately (Bypasses Browser Security Blocks)
if 'qr_val' not in st.session_state:
    st.session_state.qr_val = ""

if "qr" in st.query_params:
    st.session_state.qr_val = st.query_params["qr"]
    st.query_params.clear()  # Clear URL link automatically
    time.sleep(0.5) # Give it half a second to settle
    st.rerun()

# 3. Main Header UI
st.markdown("""
    <div style='background: linear-gradient(135deg, #0b57d0 0%, #00c6ff 100%); padding: 20px; border-radius: 12px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
        <h1 style='margin:0; font-size: 30px; font-weight: 900;'>📱 JIO PHONE SERVICE</h1>
        <p style='margin:5px 0 0 0; font-size: 15px; font-weight: 600;'>Sandhya Enterprises - Live Return Portal</p>
    </div>
""", unsafe_allow_html=True)

# 4. Single Dashboard Tabs
tab1, tab2, tab3 = st.tabs(["📝 New Scan & Entry", "⏳ Pending Phones", "✅ Delivered History"])

# ==========================================
# TAB 1: NEW ENTRY & LIVE BACK-CAMERA QR SCAN
# ==========================================
with tab1:
    st.markdown("### 🔍 Step 1: Scan QR Code")
    
    qr_data = st.session_state.qr_val
    
    # 🟢 BACK-CAMERA LIVE SCANNER (URL REDIRECT METHOD)
    scanner_html = """
    <script src="https://unpkg.com/html5-qrcode"></script>
    <div id="reader" style="width: 100%; max-width: 400px; margin: auto; border: 4px solid #0b57d0; border-radius: 10px; overflow: hidden; background: #000;"></div>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const config = { fps: 15, qrbox: { width: 250, height: 250 } };

        // Forcing Back Camera
        html5QrCode.start({ facingMode: "environment" }, config, 
            (decodedText) => {
                // SUCCESS: Stop camera and Redirect with Data in URL (100% Reliable)
                html5QrCode.stop().then(() => {
                    document.getElementById('reader').innerHTML = '<div style="padding: 80px 0; text-align: center; color: #15803d; font-size: 24px; font-weight: bold; background: #dcfce7; height: 100%;">✅ Scan Captured! Loading...</div>';
                    
                    // Create an invisible link and click it to bypass iframe restrictions
                    const link = document.createElement('a');
                    link.href = "?qr=" + encodeURIComponent(decodedText);
                    link.target = "_top"; 
                    document.body.appendChild(link);
                    link.click();
                });
            }, 
            (errorMessage) => {
                // Ignore background scanning errors
            }
        ).catch(err => {
            document.getElementById('reader').innerHTML = '<div style="color:red; padding:20px; background:white;">Camera Access Denied or Back Camera Not Found.</div>';
        });
    </script>
    """
    
    # Show scanner only if nothing is scanned yet
    if not qr_data:
        st.info("👇 डब्बे में QR कोड लाएं। पीछे वाला कैमरा (Back Camera) अपने-आप स्कैन कर लेगा।")
        st.components.v1.html(scanner_html, height=380)
        
        st.markdown("---")
        st.markdown("**अगर कोड बहुत ख़राब है और स्कैन नहीं हो रहा, तो यहाँ हाथ से टाइप करें:**")
        manual_entry = st.text_input("IMEI Number (Manual Entry)")
        if st.button("Submit Manual Entry", type="secondary"):
            if manual_entry:
                st.session_state.qr_val = manual_entry
                st.rerun()
    else:
        st.success("✅ QR Code Data Successfully Captured!")
        if st.button("🔄 Retake Scan (दुबारा स्कैन करें)"):
            st.session_state.qr_val = ""
            st.rerun()

    # Logic to auto-fill data based on scanned string
    model_val = imei_val = mrp_val = ean_val = srno_val = ""
    
    if qr_data:
        try:
            parts = qr_data.split(',')
            if len(parts) >= 5:
                model_val, imei_val, mrp_val, ean_val, srno_val = parts[0], parts[1], parts[2], parts[3], parts[4]
            else:
                imei_val = qr_data 
                st.warning("⚠️ Scanner read the data, but it's not in standard Jio format. Raw data filled in IMEI.")
        except:
            st.error("Error reading QR Data.")

        # FORM DETAILS (Appears only after scan)
        with st.form("service_form"):
            st.markdown("### 📋 Step 2: Scanned Details (Editable)")
            c1, c2 = st.columns(2)
            with c1:
                model_in = st.text_input("Model Number", value=model_val)
                mrp_in = st.text_input("MRP", value=mrp_val)
                srno_in = st.text_input("Serial No (SRNO)", value=srno_val)
            with c2:
                imei_in = st.text_input("IMEI Number*", value=imei_val)
                ean_in = st.text_input("EAN", value=ean_val)

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
                elif not imei_in:
                    st.error("❌ Invalid IMEI Data.")
                else:
                    new_id = f"JIO-{len(st.session_state.service_db)+1:04d}"
                    new_data = {
                        "ID": new_id, 
                        "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "Model": model_in, "IMEI": imei_in, "MRP": mrp_in, "EAN": ean_in, "SRNO": srno_in,
                        "Retailer": retailer.upper(), "Problem": problem, "Action": action, 
                        "Status": "Pending" if "Pending" in status else "Delivered"
                    }
                    
                    st.session_state.service_db = pd.concat([st.session_state.service_db, pd.DataFrame([new_data])], ignore_index=True)
                    st.success(f"🎉 Saved Successfully! ID: {new_id} is marked as **{new_data['Status']}**")
                    
                    # Auto clear scanner input after save
                    st.session_state.qr_val = ""
                    time.sleep(2)
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
