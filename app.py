import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
import requests

# 1. पेज की सेटिंग और मोबाइल फ्रेंडली लुक
st.set_page_config(page_title="Sandhya ERP", page_icon="📲", layout="wide")

# प्रोफेशनल डिज़ाइन के लिए CSS
st.markdown("""
    <style>
    /* बैकग्राउंड और फोंट */
    .main { background-color: #f8f9fa; }
    
    /* मेनू कार्ड्स का डिज़ाइन */
    .menu-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;
        margin-bottom: 20px; border-left: 5px solid #007bff;
        transition: 0.3s; cursor: pointer;
    }
    .menu-card:hover { transform: translateY(-5px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }
    
    /* हेडर */
    .app-header {
        background: linear-gradient(90deg, #007bff, #00c6ff);
        color: white; padding: 20px; border-radius: 0 0 20px 20px;
        text-align: center; margin-bottom: 30px;
    }
    
    /* साइडबार छुपाना (क्योंकि हम कार्ड्स इस्तेमाल करेंगे) */
    [data-testid="stSidebar"] { display: none; }
    
    /* बटन स्टाइल */
    .stButton>button {
        width: 100%; border-radius: 10px; height: 50px;
        background-color: #007bff; color: white; border: none;
    }
    </style>
""", unsafe_allow_html=True)

# 🛑 आपका APPS SCRIPT URL
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby_yV4nEMwrBODnkVh0x5DrVqcbj42iDMLNlX8M7QPrVGGMltoOfZhlid_gXlB0dwMvZQ/exec"

sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

# डेटा लोड करने का फंक्शन
@st.cache_data(ttl=30)
def load_data():
    try:
        ret_df = pd.read_csv(retailers_csv).dropna(how="all").fillna("")
        inv_df = pd.read_csv(inventory_csv).dropna(how="all").fillna("")
        led_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
        return ret_df, inv_df, led_df
    except: return None, None, None

ret_df, inv_df, led_df = load_data()

# सेशन स्टेट में पेज को ट्रैक करना
if "current_page" not in st.session_state:
    st.session_state.current_page = "HOME"

def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- APP HEADER ---
st.markdown('<div class="app-header"><h1>📲 संध्या इंटरप्राइजेज</h1><p>स्मार्ट बिज़नेस मैनेजमेंट</p></div>', unsafe_allow_html=True)

# --- 🏠 HOME PAGE (प्रोफेशनल मेनू कार्ड्स) ---
if st.session_state.current_page == "HOME":
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 लाइव स्टॉक (Stock)"): go_to("STOCK")
        if st.button("➕ नया रिटेलर (Add)"): go_to("ADD_RETAILER")
        if st.button("📜 खाता (Ledger)"): go_to("LEDGER")

    with col2:
        if st.button("💰 वसूली (Collection)"): go_to("COLLECTION")
        if st.button("📦 माल / पेमेंट एंट्री"): go_to("ENTRY")
        if st.button("💸 बकाया लिस्ट (Reminders)"): go_to("DUES")

# --- 📊 1. STOCK PAGE ---
elif st.session_state.current_page == "STOCK":
    if st.button("🔙 मुख्य मेनू पर जाएं"): go_to("HOME")
    st.header("📊 लाइव इन्वेंट्री स्टॉक")
    if inv_df is not None:
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
    else: st.error("डेटा लोड नहीं हुआ।")

# --- 💰 2. TODAY COLLECTION ---
elif st.session_state.current_page == "COLLECTION":
    if st.button("🔙 मुख्य मेनू पर जाएं"): go_to("HOME")
    st.header("💸 आज की वसूली")
    
    if ret_df is not None and led_df is not None:
        for index, row in ret_df.iterrows():
            name = row["Retailer Name"]
            mobile = row["Mobile Number"]
            u_data = led_df[led_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
            
            if dues > 0:
                with st.expander(f"👤 {name} | 🚩 बकाया: ₹{dues}"):
                    st.markdown(f"### [📞 कॉल करें](tel:{mobile})")
                    p_amt = st.number_input(f"पेमेंट राशि", min_value=1.0, key=f"p_{name}")
                    if st.button(f"सेव करें {name}"):
                        payload = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": name, "r_mob": mobile, "type": "Payment (Cash)", "qty": 0, "amt_out": 0, "amt_in": p_amt, "fse": "FSE", "txn_id": "Collection"}
                        requests.post(WEBHOOK_URL, json=payload)
                        st.success("पेमेंट जमा हो गया!")
                        st.cache_data.clear()

# --- 📦 3. ENTRY PAGE ---
elif st.session_state.current_page == "ENTRY":
    if st.button("🔙 मुख्य मेनू पर जाएं"): go_to("HOME")
    st.header("📦 नई एंट्री करें")
    with st.form("entry_form"):
        t_prm = st.selectbox("रिटेलर चुनें", [f"{r['PRM ID']} - {r['Retailer Name']}" for i,r in ret_df.iterrows()])
        t_type = st.selectbox("क्या दिया?", ["Jio Phone", "SIM Card", "Etop Recharge", "पेमेंट"])
        t_qty = st.number_input("मात्रा", min_value=0)
        t_amt = st.number_input("राशि ₹", min_value=0.0)
        if st.form_submit_button("एंट्री सेव करें"):
            # एंट्री कोड (वही पुराना)
            st.success("एंट्री सफलतापूर्वक हो गई!")

# --- ➕ 4. ADD RETAILER ---
elif st.session_state.current_page == "ADD_RETAILER":
    if st.button("🔙 मुख्य मेनू पर जाएं"): go_to("HOME")
    st.header("➕ नया रिटेलर जोड़ें")
    # फॉर्म कोड (वही पुराना)

# --- 📜 5. LEDGER ---
elif st.session_state.current_page == "LEDGER":
    if st.button("🔙 मुख्य मेनू पर जाएं"): go_to("HOME")
    st.header("📜 रिटेलर खाता")
    # लेजर कोड (वही पुराना)

# --- 💸 6. DUES REMINDERS ---
elif st.session_state.current_page == "DUES":
    if st.button("🔙 मुख्य मेनू पर जाएं"): go_to("HOME")
    st.header("💸 बकाया लिस्ट और व्हाट्सएप")
    # बकाया लिस्ट कोड (वही पुराना)
