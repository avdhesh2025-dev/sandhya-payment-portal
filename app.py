import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import requests

# पेज की सेटिंग
st.set_page_config(page_title="Sandhya ERP System", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    div.row-widget.stRadio > div { flex-direction: column; }
    div.row-widget.stRadio > div > label {
        background-color: #f0f2f6; padding: 12px 15px; border-radius: 8px;
        border: 1px solid #d0d2d6; margin-bottom: 8px; cursor: pointer; font-weight: 500; transition: 0.3s;
    }
    div.row-widget.stRadio > div > label:hover { background-color: #e0e2e6; border-color: #b0b2b6; }
    </style>
""", unsafe_allow_html=True)

# 🛑 अपना चालू APPS SCRIPT वाला URL यहाँ डालें
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby_yV4nEMwrBODnkVh0x5DrVqcbj42iDMLNlX8M7QPrVGGMltoOfZhlid_gXlB0dwMvZQ/exec"

sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

@st.cache_data(ttl=30)
def get_retailers_data():
    try:
        df = pd.read_csv(retailers_csv).dropna(how="all").fillna("")
        ret_dict = {}
        for index, row in df.iterrows():
            prm = str(row.get("PRM ID", "")).split('.')[0]
            name = str(row.get("Retailer Name", ""))
            mobile = str(row.get("Mobile Number", "")).split('.')[0]
            if prm and name and prm != "nan":
                key = f"{prm} - {name}"
                ret_dict[key] = {"Name": name, "Mobile": mobile}
        return ret_dict
    except: return {}

retailers_data = get_retailers_data()
dropdown_options = ["सर्च करने के लिए यहाँ टाइप करें..."] + list(retailers_data.keys()) if retailers_data else ["सर्च करने के लिए यहाँ टाइप करें..."]

st.sidebar.title("📲 संध्या इंटरप्राइजेज")
st.sidebar.markdown("---")
menu = st.sidebar.radio("मेनू चुनें:", ["📊 डैशबोर्ड (स्टॉक)", "➕ नया रिटेलर जोड़ें", "📦 माल / पेमेंट एंट्री", "📜 लेजर (खाता) देखें", "💰 बकाया लिस्ट (All Dues)"])

# 1. डैशबोर्ड
if menu == "📊 डैशबोर्ड (स्टॉक)":
    st.title("📊 लाइव इन्वेंट्री स्टॉक")
    try:
        inv_df = pd.read_csv(inventory_csv).dropna(how="all").fillna("")
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
    except: st.error("स्टॉक लोड हो रहा है...")

# 2. नया रिटेलर जोड़ें
elif menu == "➕ नया रिटेलर जोड़ें":
    st.title("➕ नया रिटेलर जोड़ें")
    with st.form("add_retailer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            r_name = st.text_input("रिटेलर का नाम (Retailer Name)*")
            r_mobile = st.text_input("मोबाइल नंबर (Mobile Number)*", max_chars=10)
        with col2:
            r_prm = st.text_input("PRM ID* (अनिवार्य)")
            r_loc = st.text_input("लोकेशन (Location)")
        submit_retailer = st.form_submit_button("नया रिटेलर सेव करें")
        if submit_retailer and r_name and r_prm and r_mobile:
            payload = {"action": "add_retailer", "name": str(r_name).strip().upper(), "mobile": str(r_mobile).strip(), "prm": str(r_prm).strip(), "location": str(r_loc).strip().upper(), "date": datetime.now().strftime("%d-%m-%Y")}
            res = requests.post(WEBHOOK_URL, json=payload)
            if res.text == "Success":
                st.success(f"✅ रिटेलर {r_name} सेव हो गया!")
                st.cache_data.clear()

# 3. माल इशू / पेमेंट एंट्री
elif menu == "📦 माल / पेमेंट एंट्री":
    st.title("📦 स्टॉक आउट / पेमेंट लें")
    t_date = st.date_input("तारीख", datetime.now())
    t_prm = st.selectbox("रिटेलर खोजें (PRM ID या नाम टाइप करें)*", options=dropdown_options)
    col1, col2 = st.columns(2)
    with col1:
        t_type = st.selectbox("क्या एंट्री करनी है?", ["Jio Phone", "SIM Card", "Etop Recharge", "पेमेंट (Payment Received)"])
        fse = st.selectbox("एंट्री करने वाला (FSE)", ["Ravindra Sharma", "Lal Babu Das", "Self"])
    with col2:
        t_qty = 0; t_amount = 0.0
        if t_type == "SIM Card": t_qty = st.number_input("मात्रा (SIM)", min_value=1)
        elif t_type in ["Etop Recharge", "पेमेंट (Payment Received)"]: t_amount = st.number_input("राशि ₹", min_value=1.0)
        else:
            t_qty = st.number_input("मात्रा (Phone)", min_value=1)
            t_rate = st.number_input("रेट ₹", min_value=0.0)
            t_amount = t_qty * t_rate
            st.info(f"कुल राशि: ₹{t_amount}")
        txn_id = st.text_input("Transaction ID")
    if st.button("🚀 एंट्री सेव करें और WhatsApp भेजें", use_container_width=True):
        if t_prm != "सर्च करने के लिए यहाँ टाइप करें...":
            r_name = retailers_data[t_prm]["Name"]; r_mob = retailers_data[t_prm]["Mobile"]
            amt_out = t_amount if t_type != "पेमेंट (Payment Received)" else 0
            amt_in = t_amount if t_type == "पेमेंट (Payment Received)" else 0
            payload = {"action": "add_txn", "date": t_date.strftime("%d-%m-%Y"), "r_name": r_name, "r_mob": r_mob, "type": t_type, "qty": t_qty, "amt_out": amt_out, "amt_in": amt_in, "fse": fse, "txn_id": txn_id}
            res = requests.post(WEBHOOK_URL, json=payload)
            if res.text == "Success":
                st.success("✅ सेव हो गया!"); st.balloons(); st.cache_data.clear()
                msg = f"*🧾 संध्या इंटरप्राइजेज - रसीद*\nदिनांक: {t_date.strftime('%d-%m-%Y')}\nरिटेलर: {r_name}\nआइटम: {t_type}\nराशि: ₹{t_amount}\n🙏 धन्यवाद!"
                st.markdown(f"### [🟢 WhatsApp भेजें](https://wa.me/91{r_mob}?text={urllib.parse.quote(msg)})", unsafe_allow_html=True)

# 4. लेजर देखें
elif menu == "📜 लेजर (खाता) देखें":
    st.title("📜 रिटेलर का खाता")
    search_prm = st.selectbox("रिटेलर चुनें:", options=dropdown_options)
    if search_prm != "सर्च करने के लिए यहाँ टाइप करें...":
        ledger_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
        r_name = retailers_data[search_prm]["Name"]
        user_ledger = ledger_df[ledger_df['Retailer Name'] == r_name].copy()
        user_ledger['Amount Out (Debit)'] = pd.to_numeric(user_ledger['Amount Out (Debit)'], errors='coerce').fillna(0)
        user_ledger['Amount In (Credit)'] = pd.to_numeric(user_ledger['Amount In (Credit)'], errors='coerce').fillna(0)
        user_ledger['Balance'] = (user_ledger['Amount Out (Debit)'] - user_ledger['Amount In (Credit)']).cumsum()
        st.dataframe(user_ledger, use_container_width=True, hide_index=True)
        bal = user_ledger['Amount Out (Debit)'].sum() - user_ledger['Amount In (Credit)'].sum()
        st.warning(f"कुल बकाया: ₹{bal}")

# 5. 💰 बकाया लिस्ट (ALL DUES) - यह आपका नया फीचर है
elif menu == "💰 बकाया लिस्ट (All Dues)":
    st.title("💰 पूरे बिज़नेस की बकाया लिस्ट")
    if st.button("🔄 लिस्ट अपडेट करें"):
        try:
            ledger_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
            summary = []
            for key, val in retailers_data.items():
                name = val["Name"]
                u_data = ledger_df[ledger_df['Retailer Name'] == name]
                debit = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
                credit = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
                dues = debit - credit
                if dues != 0:
                    summary.append({"रिटेलर": name, "मोबाइल": val["Mobile"], "बकाया राशि (Dues)": dues})
            
            summary_df = pd.DataFrame(summary)
            if not summary_df.empty:
                st.dataframe(summary_df.sort_values(by="बकाया राशि (Dues)", ascending=False), use_container_width=True, hide_index=True)
                st.error(f"💸 बाज़ार में कुल फंसा हुआ पैसा: ₹{summary_df['बकाया राशि (Dues)'].sum()}")
                
                csv = summary_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 बकाया लिस्ट डाउनलोड करें", csv, "Total_Dues.csv", "text/csv")
            else: st.success("सबका हिसाब बराबर है!")
        except: st.error("डेटा लोड नहीं हो पाया।")
