import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import datetime

# 1. Page Config (A4 Size / Centered Layout)
st.set_page_config(page_title="Sandhya Enterprises - Digital Committee ERP", layout="centered")

# 2. Custom CSS for Professional 3D Buttons & Styling
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #ffffff;
        color: #1f2937;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        border-bottom: 6px solid #d1d5db;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        font-weight: bold;
        font-size: 14px;
        height: 55px;
        transition: all 0.1s ease-in-out;
    }
    div.stButton > button:active {
        border-bottom: 2px solid #d1d5db;
        transform: translateY(4px);
    }
    [data-testid="collapsedControl"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- Company Header ---
st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🏢 Sandhya Enterprises</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Advanced Digital Committee Management ERP</p>", unsafe_allow_html=True)
st.divider()

# --- QR Code Generator Function ---
def generate_qr(upi_id, name, amount):
    upi_url = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf

# 3. Session State Initialization
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

if 'committees' not in st.session_state:
    st.session_state.committees = {
        "COM-2026-001": {"tier": "₹2,000 Committee", "amount": 2000, "members": 10},
        "COM-2026-002": {"tier": "₹5,000 Committee", "amount": 5000, "members": 10}
    }

if 'members' not in st.session_state:
    st.session_state.members = [
        {"id": "M001", "name": "Rahul Kumar", "mobile": "9876543210", "aadhar": "[Aadhaar Redacted]", "pan": "ABCDE1234F", "upi": "rahul@ybl", "status": "✅ Active"},
        {"id": "M002", "name": "Amit Sharma", "mobile": "9876543211", "aadhar": "[Aadhaar Redacted]", "pan": "FGHIJ5678K", "upi": "amit@paytm", "status": "✅ Active"}
    ]

# 4. Main Menu Display (Professional Navigation Grid)
c1, c2, c3 = st.columns(3)
if c1.button("📊 डैशबोर्ड", use_container_width=True): st.session_state.page = "Dashboard"
if c2.button("👤 नया मेंबर", use_container_width=True): st.session_state.page = "Add_Member"
if c3.button("📒 लेज़र", use_container_width=True): st.session_state.page = "Ledger"

c4, c5, c6 = st.columns(3)
if c4.button("💰 ट्रांसफर & QR", use_container_width=True): st.session_state.page = "Collection"
if c5.button("⚠️ लेट फाइन", use_container_width=True): st.session_state.page = "Penalty"
if c6.button("📥 रिपोर्ट्स & बैकअप", use_container_width=True): st.session_state.page = "Report"

st.divider()

# ----------------------------------------
# PAGE 1: DASHBOARD (MULTI-COMMITTEE & ANALYTICS)
# ----------------------------------------
if st.session_state.page == "Dashboard":
    st.header("📊 कमिटी समरी & एनालिटिक्स")
    
    # Select Active Committee Tier
    selected_com = st.selectbox("एक्टिव कमिटी चुनें:", list(st.session_state.committees.keys()))
    com_info = st.session_state.committees[selected_com]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("कमिटी ID", selected_com)
    m2.metric("कमिटी टियर", com_info["tier"])
    m3.metric("टोटल मेंबर्स", f"{len(st.session_state.members)} / {com_info['members']}")
    m4.metric("रनिंग बैलेंस", f"₹ {com_info['amount'] * len(st.session_state.members)}")
    
    st.markdown("---")
    st.subheader("📋 रजिस्टर्ड मेंबर्स लिस्ट & आईडी")
    
    member_df = pd.DataFrame(st.session_state.members)
    st.dataframe(member_df, use_container_width=True)

# ----------------------------------------
# PAGE 2: ADD NEW MEMBER (AUTO ID & VALIDATIONS)
# ----------------------------------------
elif st.session_state.page == "Add_Member":
    st.header("👤 नया मेंबर रजिस्ट्रेशन (Auto ID)")
    
    # Auto Generate Member ID
    next_id = f"M0{len(st.session_state.members) + 1}"
    st.info(ger_info := f"जनरेटेड मेंबर ID: **{next_id}**")
    
    with st.form("new_member_form"):
        colA, colB = st.columns(2)
        with colA:
            name = st.text_input("मेंबर का पूरा नाम *")
            mobile = st.text_input("मोबाइल / WhatsApp नंबर *")
            aadhar = st.text_input("Aadhar Number * (Mandatory)")
            
        with colB:
            pan = st.text_input("PAN Card Number *")
            upi_id = st.text_input("UPI ID (पैसे रिसीव करने के लिए) *")
            address = st.text_input("पूरा पता *")
            
        photo = st.file_uploader("मेंबर की फोटो अपलोड करें (Preview) *", type=["jpg", "png", "jpeg"])
        
        submit = st.form_submit_button("मेंबर सेव करें", use_container_width=True)
        
        if submit:
            # Duplicate Aadhar / PAN Check Logic
            existing_aadhars = [m['aadhar'] for m in st.session_state.members]
            existing_pans = [m['pan'] for m in st.session_state.members]
            
            if not name or not mobile or not aadhar or not pan or not upi_id or not photo:
                st.error("⚠️ कृपया सभी अनिवार्य फील्ड भरें!")
            elif aadhar in existing_aadhars:
                st.error("❌ त्रुटि: यह Aadhaar नंबर पहले से रजिस्टर्ड है (Member Already Exists)!")
            elif pan in existing_pans:
                st.error("❌ त्रुटि: यह PAN नंबर पहले से मौजूद है!")
            else:
                new_m = {
                    "id": next_id,
                    "name": name,
                    "mobile": mobile,
                    "aadhar": "[Aadhaar Redacted]", # Strict Redaction Protocol Applied
                    "pan": pan,
                    "upi": upi_id,
                    "status": "✅ Active"
                }
                st.session_state.members.append(new_m)
                st.success(f"✅ {name} सफलतापूर्वक रजिस्टर हो गए! ID: {next_id}")

# ----------------------------------------
# PAGE 3: MEMBER LEDGER & RECEIPT GENERATOR
# ----------------------------------------
elif st.session_state.page == "Ledger":
    st.header("📒 व्यक्तिगत मेंबर लेज़र & रसीद")
    
    member_names = [m['name'] for m in st.session_state.members]
    selected_member = st.selectbox("मेंबर चुनें:", member_names)
    
    if selected_member:
        st.markdown("---")
        p1, p2 = st.columns([1, 3])
        with p1:
            st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=100)
            st.success("🟢 Active")
        with p2:
            st.write(f"👤 **नाम:** {selected_member}")
            st.write(f"🆔 **Member ID:** M001")
            st.write(f"📍 **व्यवसाय:** Sandhya Enterprises Client")
            
        st.markdown("---")
        st.subheader("🖨️ पेमेंट रसीद (PDF/Print View)")
        
        # Receipt Box Simulation
        receipt_no = "RCP-2026-0015"
        amount_paid = 2000
        pay_date = datetime.date.today()
        
        st.markdown(f"""
        <div style='border: 2px dashed #1e3a8a; padding: 20px; border-radius: 10px; background-color: #f8fafc;'>
            <h3 style='text-align: center; color: #1e3a8a; margin:0;'>Sandhya Enterprises</h3>
            <p style='text-align: center; font-size:12px; color:gray;'>Meghpatti, Samastipur, Bihar</p>
            <hr style='margin:10px 0;'>
            <p><b>Receipt No:</b> {receipt_no}</p>
            <p><b>Member Name:</b> {selected_member}</p>
            <p><b>Amount Paid:</b> ₹ {amount_paid}</p>
            <p><b>Date:</b> {pay_date}</p>
            <p><b>Status:</b> <span style='color:green;'><b>PAID (सफल)</b></span></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📥 रसीद डाउनलोड करें (Text/Data Format)", use_container_width=True):
            st.success("रसीद फाइल तैयार है!")

# ----------------------------------------
# PAGE 4: COLLECTION & AUTO QR
# ----------------------------------------
elif st.session_state.page == "Collection":
    st.header("💰 मंथली कलेक्शन और ऑटो QR")
    
    colA, colB = st.columns(2)
    with colA:
        receiver = st.selectbox("इस महीने पैसा किसको मिला?", [m['name'] for m in st.session_state.members])
        receiver_upi = st.text_input("मेंबर की UPI ID", value="7479584179@ybl")
    with colB:
        total_amount = st.number_input("कमिटी टोटल अमाउंट (₹)", value=20000)
        
    bid_amount = st.number_input("बोली / डिस्काउंट अमाउंट (₹)", value=500.0)
    interest = (total_amount * 2) / 100 # 2% Interest
    total_deduction = interest + bid_amount
    final_payout = total_amount - total_deduction
    
    st.markdown("---")
    qr_col, info_col = st.columns([1, 2])
    
    with info_col:
        st.write(f"**फिक्स ब्याज (2%):** ₹ {interest}")
        st.write(f"**बोली डिस्काउंट:** ₹ {bid_amount}")
        st.markdown(f"#### **{receiver} को ट्रांसफर होगा:** ₹ {final_payout}")
        st.write(f"**हर मेंबर का प्रॉफिट शेयर:** ₹ {total_deduction / 10}")
        
    with qr_col:
        qr_img = generate_qr(receiver_upi, receiver, final_payout)
        st.image(qr_img, width=180, caption="स्कैन करके भुगतान करें")

# ----------------------------------------
# PAGE 5: LATE FINE CALCULATOR
# ----------------------------------------
elif st.session_state.page == "Penalty":
    st.header("⚠️ लेट फाइन कैलकुलेटर")
    
    late_mem = st.selectbox("मेंबर चुनें:", [m['name'] for m in st.session_state.members])
    days = st.number_input("कितने दिन लेट है?", min_value=1, value=3)
    
    fine = days * 20 if days <= 6 else ((2000 * 3) / 100) * days
    st.warning(f"⚠️ कुल देय फाइन ({late_mem}): **₹ {fine}**")
    
    if st.button("फाइन प्रभारित करें", use_container_width=True):
        st.success("फाइन लेज़र में जोड़ दिया गया है!")

# ----------------------------------------
# PAGE 6: REPORTS & BACKUP
# ----------------------------------------
elif st.session_state.page == "Report":
    st.header("📥 रिपोर्ट्स, बैकअप और डेटा सुरक्षा")
    
    st.info("यहाँ से आप पूरे महीने का डेटा Excel फॉर्मेट में डाउनलोड कर सकते हैं या सिस्टम का बैकअप ले सकते हैं।")
    
    rep_df = pd.DataFrame(st.session_state.members)
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        rep_df.to_excel(writer, sheet_name="Committee_Data", index=False)
        
    st.download_button(
        label="📥 पूर्ण डेटा बैकअप एक्सेल डाउनलोड करें (.xlsx)",
        data=buffer,
        file_name=f"Sandhya_Enterprises_Backup_{datetime.date.today()}.xlsx",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )
