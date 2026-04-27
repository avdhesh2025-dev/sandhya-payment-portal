import streamlit as st
import pandas as pd
from datetime import datetime
import time

# FPDF for Bill Generation
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# 1. Page Configuration & Clean CSS
st.set_page_config(page_title="Sandhya Repair & Service", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main .block-container {
        background-color: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        max-width: 1000px;
    }
    .stButton>button {
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Database Initialization
if 'repair_db' not in st.session_state:
    st.session_state.repair_db = pd.DataFrame(columns=[
        "JobID", "EntryDate", "CustName", "Mobile", "Address", 
        "Category", "ProductDetail", "Fault", "Resolution", 
        "EstCost", "DeliveryDate", "Status"
    ])

if 'last_receipt_data' not in st.session_state:
    st.session_state.last_receipt_data = None

# 3. PDF Receipt Generator
def generate_repair_receipt(data):
    if not HAS_FPDF: return None
    pdf = FPDF()
    pdf.add_page()
    
    # Company Header
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
        # Clean special/Hindi chars to prevent PDF crash
        clean_col2 = str(col2).encode('latin-1', 'ignore').decode('latin-1')
        pdf.cell(0, 8, f" {clean_col2}", border=1, ln=True)
        pdf.set_font("Arial", 'B', 10)

    # Job & Customer Info
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, " CUSTOMER DETAILS", border=1, ln=True, fill=True)
    print_row("Job ID / Bill No:", data['JobID'])
    print_row("Date & Time:", data['EntryDate'])
    print_row("Customer Name:", data['CustName'])
    print_row("Mobile Number:", data['Mobile'])
    print_row("Address:", data['Address'])
    
    pdf.ln(5)
    
    # Product & Repair Info
    pdf.cell(0, 8, " PRODUCT & REPAIR DETAILS", border=1, ln=True, fill=True)
    print_row("Product Category:", data['Category'])
    print_row("Product Name/Model:", data['ProductDetail'])
    print_row("Reported Fault:", data['Fault'])
    print_row("Proposed Solution:", data['Resolution'])
    print_row("Estimated Cost:", f"Rs. {data['EstCost']}")
    print_row("Est. Delivery Date:", data['DeliveryDate'])
    print_row("Current Status:", data['Status'])

    # Terms & Conditions
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 5, "Terms & Conditions:", ln=True)
    pdf.set_font("Arial", '', 8)
    pdf.cell(0, 5, "1. Please bring this receipt at the time of delivery.", ln=True)
    pdf.cell(0, 5, "2. Estimated cost may vary if additional internal damage is found.", ln=True)
    pdf.cell(0, 5, "3. We are not responsible for any data loss in mobile/laptops.", ln=True)
    
    pdf.ln(10)
    pdf.cell(0, 5, "Authorized Signatory", align='R')
    
    return pdf.output(dest='S').encode('latin-1')


# 4. Main UI Header
st.markdown("""
    <div style='background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); padding: 25px; border-radius: 10px; text-align: center; color: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h1 style='margin:0; font-size: 34px; font-weight: 800;'>🛠️ REPAIR & SERVICE DESK</h1>
        <p style='margin:5px 0 0 0; font-size: 16px;'>Sandhya Enterprises - Universal Service Portal</p>
    </div>
""", unsafe_allow_html=True)

# 5. Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 New Repair Entry", "⏳ Pending Jobs", "✅ Completed", "🖨️ Re-Print Bill"])

# ==========================================
# TAB 1: NEW REPAIR ENTRY
# ==========================================
with tab1:
    if st.session_state.last_receipt_data is not None:
        receipt_data = st.session_state.last_receipt_data
        st.success(f"🎉 Job Registered Successfully! Job ID: {receipt_data['JobID']}")
        
        if HAS_FPDF:
            pdf_bytes = generate_repair_receipt(receipt_data)
            st.download_button("📥 Download Repair Receipt (PDF)", data=pdf_bytes, file_name=f"Repair_Receipt_{receipt_data['JobID']}.pdf", mime="application/pdf", use_container_width=True)
            
        if st.button("➕ Create Another Entry", type="primary", use_container_width=True):
            st.session_state.last_receipt_data = None
            st.rerun()

    else:
        st.markdown("### 📝 Register New Repair Job")
        st.caption("कस्टमर और प्रोडक्ट की डिटेल्स भरें।")
        
        with st.form("new_repair_form"):
            st.markdown("#### 👤 Customer Information")
            c1, c2, c3 = st.columns([2, 1.5, 2])
            with c1:
                cust_name = st.text_input("Customer Name (कस्टमर का नाम)*", placeholder="E.g. Rahul Kumar")
            with c2:
                cust_mobile = st.text_input("Mobile Number (मोबाइल नंबर)*", placeholder="10 Digits")
            with c3:
                cust_address = st.text_input("Address (पता)", placeholder="Village / Area")
                
            st.markdown("---")
            st.markdown("#### 📱 Product & Fault Information")
            c4, c5 = st.columns(2)
            with c4:
                category = st.selectbox("Category (सामान क्या है?)*", ["-- Select --", "Mobile Phone (मोबाइल)", "Fan (पंखा)", "Charger / Adapter", "Home Appliance (टीवी/मिक्सर आदि)", "Other (अन्य)"])
                fault = st.text_area("Reported Fault (खराबी क्या है?)*", placeholder="E.g. Display broken, Touch not working, Coil burnt...")
            with c5:
                product_detail = st.text_input("Product Name/Model (मॉडल/कंपनी)*", placeholder="E.g. Samsung Galaxy M11, Usha Fan")
                resolution = st.text_area("Proposed Solution (क्या काम होगा?)*", placeholder="E.g. New display will be installed, Winding repair...")

            st.markdown("---")
            st.markdown("#### 💰 Cost & Delivery")
            c6, c7 = st.columns(2)
            with c6:
                est_cost = st.text_input("Estimated Cost (खर्चा कितना लगेगा - ₹)*", placeholder="E.g. 1500")
            with c7:
                est_delivery = st.text_input("Expected Delivery (कितने दिन में मिलेगा?)*", placeholder="E.g. 2 Days / Tomorrow 5 PM")

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("💾 Save Entry & Generate Bill", type="primary", use_container_width=True)

            if submit:
                if not cust_name or not cust_mobile or category == "-- Select --" or not product_detail or not fault:
                    st.error("❌ कृपया स्टार (*) वाले सभी जरूरी फील्ड भरें!")
                else:
                    new_id = f"REP-{datetime.now().strftime('%y%m')}-{(len(st.session_state.repair_db)+1):03d}"
                    new_data = {
                        "JobID": new_id,
                        "EntryDate": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "CustName": cust_name.upper(),
                        "Mobile": cust_mobile,
                        "Address": cust_address,
                        "Category": category.split(" ")[0],
                        "ProductDetail": product_detail,
                        "Fault": fault,
                        "Resolution": resolution,
                        "EstCost": est_cost,
                        "DeliveryDate": est_delivery,
                        "Status": "Pending (काम चल रहा है)"
                    }
                    
                    st.session_state.repair_db = pd.concat([st.session_state.repair_db, pd.DataFrame([new_data])], ignore_index=True)
                    st.session_state.last_receipt_data = new_data
                    st.rerun()

# ==========================================
# TAB 2: PENDING JOBS DASHBOARD
# ==========================================
with tab2:
    st.markdown("### ⏳ Pending Repairs")
    pending_df = st.session_state.repair_db[st.session_state.repair_db["Status"].str.contains("Pending")]
    
    if pending_df.empty:
        st.info("🎉 कोई पेंडिंग काम नहीं है!")
    else:
        st.warning(f"🚨 {len(pending_df)} सामान रिपेयर होने के लिए पेंडिंग हैं!")
        for idx, row in pending_df.iterrows():
            st.markdown(f"""
                <div style='border: 1px solid #f59e0b; padding: 15px; border-radius: 8px; background: #fffbeb; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                    <div style='display: flex; justify-content: space-between; border-bottom: 1px solid #fcd34d; padding-bottom: 8px; margin-bottom: 8px;'>
                        <h4 style='color: #b45309; margin: 0;'>👤 {row['CustName']} ({row['Mobile']})</h4>
                        <span style='background: #b45309; color: white; padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: bold;'>{row['JobID']}</span>
                    </div>
                    <p style='margin: 4px 0;'><b>📦 Item:</b> {row['ProductDetail']} | <b>🔧 Fault:</b> {row['Fault']}</p>
                    <p style='margin: 4px 0;'><b>💰 Cost:</b> ₹{row['EstCost']} | <b>⏰ Delivery:</b> {row['DeliveryDate']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            if c1.button(f"✅ Mark Delivered (कस्टमर को दे दिया)", key=f"del_{row['JobID']}", type="secondary", use_container_width=True):
                st.session_state.repair_db.loc[st.session_state.repair_db['JobID'] == row['JobID'], 'Status'] = "Delivered (दे दिया गया)"
                st.rerun()
            if c2.button(f"🗑️ Cancel/Delete Job", key=f"rm_{row['JobID']}", use_container_width=True):
                st.session_state.repair_db = st.session_state.repair_db[st.session_state.repair_db['JobID'] != row['JobID']]
                st.rerun()

# ==========================================
# TAB 3: COMPLETED / HISTORY
# ==========================================
with tab3:
    st.markdown("### ✅ Delivered History (हिसाब-किताब)")
    delivered_df = st.session_state.repair_db[st.session_state.repair_db["Status"].str.contains("Delivered")]
    
    if delivered_df.empty:
        st.info("अभी तक कोई काम डिलीवर नहीं हुआ है।")
    else:
        st.dataframe(delivered_df[["JobID", "Date", "CustName", "ProductDetail", "EstCost"]].rename(columns={"Date": "EntryDate"}), hide_index=True, use_container_width=True)
        csv = delivered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download History (Excel/CSV)", data=csv, file_name=f"Repair_History_{datetime.now().strftime('%d-%m-%Y')}.csv", mime="text/csv", use_container_width=True)

# ==========================================
# TAB 4: RE-PRINT BILL
# ==========================================
with tab4:
    st.markdown("### 🖨️ Search & Re-Print Bill")
    st.info("किसी भी कस्टमर का पुराना बिल निकालने के लिए उनका मोबाइल नंबर या Job ID डालें।")
    
    search_query = st.text_input("🔍 Enter Mobile Number OR Job ID:")
    if st.button("Search Details", type="primary"):
        if search_query and not st.session_state.repair_db.empty:
            # Search in Mobile or JobID
            result = st.session_state.repair_db[
                (st.session_state.repair_db['Mobile'].str.contains(search_imei, na=False)) | 
                (st.session_state.repair_db['JobID'].str.contains(search_imei, na=False, case=False))
            ]
            if not result.empty:
                st.success(f"✅ {len(result)} Record(s) Found!")
                for _, found_data in result.iterrows():
                    st.markdown(f"**Customer:** {found_data['CustName']} | **Item:** {found_data['ProductDetail']} | **Status:** {found_data['Status']}")
                    if HAS_FPDF:
                        pdf_bytes = generate_repair_receipt(found_data.to_dict())
                        st.download_button(f"📥 Download Bill ({found_data['JobID']})", data=pdf_bytes, file_name=f"Receipt_{found_data['JobID']}.pdf", mime="application/pdf", key=f"dl_{found_data['JobID']}")
            else:
                st.error("❌ कोई रिकॉर्ड नहीं मिला।")
        else:
            st.warning("कृपया मोबाइल नंबर या ID डालें।")
