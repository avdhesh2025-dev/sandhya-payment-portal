import streamlit as st
import pandas as pd

# 1. Page Config (A4 Size / Centered Layout)
st.set_page_config(page_title="डिजिटल कमिटी", layout="centered")

# 2. Custom CSS for 3D Buttons & Layout
st.markdown("""
    <style>
    /* 3D Button Style */
    div.stButton > button {
        background-color: #ffffff;
        color: #1f2937;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        border-bottom: 6px solid #d1d5db;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        font-weight: bold;
        font-size: 16px;
        height: 70px;
        transition: all 0.1s ease-in-out;
    }
    div.stButton > button:active {
        border-bottom: 2px solid #d1d5db;
        transform: translateY(4px);
    }
    /* Hide Sidebar completely if needed */
    [data-testid="collapsedControl"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# 3. Session State for Navigation (मेन स्क्रीन पर मेनू चलाने के लिए)
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

st.title("💸 डिजिटल कमिटी मैनेजर")

# 4. Main Menu Display (3D Boxes)
col1, col2, col3, col4 = st.columns(4)
if col1.button("📊 डैशबोर्ड", use_container_width=True): st.session_state.page = "Dashboard"
if col2.button("👤 नया मेंबर", use_container_width=True): st.session_state.page = "Add_Member"
if col3.button("📒 मेंबर लेज़र", use_container_width=True): st.session_state.page = "Ledger"
if col4.button("💰 कलेक्शन", use_container_width=True): st.session_state.page = "Collection"

st.divider()

# ----------------------------------------
# PAGE 1: DASHBOARD
# ----------------------------------------
if st.session_state.page == "Dashboard":
    st.header("📊 कमिटी समरी (Dashboard)")
    
    # Dashboard Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("टोटल मेंबर्स", "10 / 10")
    m2.metric("कमिटी के पास बैलेंस", "₹ 0")
    m3.metric("टोटल रनिंग बैलेंस", "₹ 20,000")
    m4.metric("वर्तमान लोन धारक", "अवधेश (Jul)")
    
    st.subheader("इस महीने का पेमेंट स्टेटस")
    # डमी डेटा
    status_data = pd.DataFrame({
        "मेंबर का नाम": ["Member 1", "Member 2", "Member 3", "Member 4"],
        "जमा राशि": ["₹2000", "₹2000", "₹0", "₹0"],
        "स्टेटस": ["✅ Complete", "✅ Complete", "❌ Pending", "❌ Pending"]
    })
    st.dataframe(status_data, use_container_width=True)

# ----------------------------------------
# PAGE 2: ADD NEW MEMBER
# ----------------------------------------
elif st.session_state.page == "Add_Member":
    st.header("👤 नया मेंबर रजिस्ट्रेशन")
    st.info("नोट: नीचे दिए गए सभी फील्ड भरना अनिवार्य (Mandatory) है।")
    
    with st.form("new_member_form"):
        colA, colB = st.columns(2)
        with colA:
            name = st.text_input("मेंबर का पूरा नाम *")
            mobile = st.text_input("मोबाइल / WhatsApp नंबर *")
            aadhar = st.text_input("Aadhar Number *")
            
        with colB:
            pan = st.text_input("PAN Card Number *")
            address = st.text_input("पूरा पता *")
            reference = st.selectbox("रेफरेंस / गारंटर (किसके थ्रू आए हैं) *", ["-- चुनें --", "Member 1", "Member 2", "Admin"])
            
        photo = st.file_uploader("मेंबर की फोटो अपलोड करें *", type=["jpg", "png", "jpeg"])
        
        submit = st.form_submit_button("डेटा सेव करें", use_container_width=True)
        
        if submit:
            # Mandatory Field Check (Validation)
            if not name or not mobile or not aadhar or not pan or not address or reference == "-- चुनें --" or not photo:
                st.error("⚠️ कृपया सभी अनिवार्य (*) फील्ड भरें और फोटो अपलोड करें!")
            else:
                st.success(f"✅ {name} का प्रोफाइल सफलतापूर्वक बन गया है!")

# ----------------------------------------
# PAGE 3: MEMBER LEDGER (PROFILE & HISTORY)
# ----------------------------------------
elif st.session_state.page == "Ledger":
    st.header("📒 व्यक्तिगत मेंबर लेज़र")
    
    selected_member = st.selectbox("हिसाब देखने के लिए मेंबर चुनें:", ["Member 1", "Member 2", "Member 3"])
    
    if selected_member:
        st.subheader("👤 प्रोफाइल डिटेल्स")
        p_col1, p_col2 = st.columns([1, 3])
        with p_col1:
            # डमी फोटो आइकॉन
            st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=120)
        with p_col2:
            st.write(f"**नाम:** {selected_member}")
            st.write("**मोबाइल:** 9876543210")
            st.write("**गारंटर:** Admin")
            st.write("**पता:** Meghpatti, Samastipur, Bihar")
            
        st.divider()
        st.subheader("💳 ट्रांज़ैक्शन हिस्ट्री (Credit / Debit)")
        
        # लेज़र का डमी डेटा
        ledger_data = pd.DataFrame({
            "तारीख": ["01-Jul", "05-Jul", "05-Jul", "05-Jul"],
            "विवरण": ["मंथली जमा", "लोन लिया", "ब्याज कटा", "प्रॉफिट मिला"],
            "क्रेडिट (आया)": ["₹ 2000", "₹ 20000", "-", "₹ 40"],
            "डेबिट (गया)": ["-", "-", "₹ 400", "-"],
            "बैलेंस": ["₹ 2000", "₹ -18000", "₹ -18400", "₹ -18360"]
        })
        st.dataframe(ledger_data, use_container_width=True)

# ----------------------------------------
# PAGE 4: COLLECTION & TRANSFER
# ----------------------------------------
elif st.session_state.page == "Collection":
    st.header("💰 मंथली कलेक्शन और ट्रांसफर")
    st.info("जिस मेंबर ने बोली लगाकर या अपनी बारी पर पैसा लिया है, उसकी एंट्री यहाँ करें।")
    
    loan_taker = st.selectbox("इस महीने पैसा किसको मिला?", ["Member 1", "Member 2", "Member 3"])
    total_amount = st.number_input("टोटल अमाउंट (₹)", value=20000)
    interest_rate = st.number_input("ब्याज / डिस्काउंट (%)", value=2.0)
    
    calculated_interest = (total_amount * interest_rate) / 100
    per_member_profit = calculated_interest / 10
    
    st.write(f"**कटा हुआ ब्याज:** ₹ {calculated_interest}")
    st.write(f"**हर मेंबर को प्रॉफिट बँटेगा:** ₹ {per_member_profit}")
    
    if st.button("कंप्लीट ट्रांसफर दर्ज करें", use_container_width=True):
        st.success(f"✅ {loan_taker} के लेज़र में ₹ {total_amount} डेबिट और ब्याज की एंट्री कर दी गई है!")
