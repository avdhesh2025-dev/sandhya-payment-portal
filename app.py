import streamlit as st
import pandas as pd
from datetime import datetime, date
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

# 🛑 आपका APPS SCRIPT URL
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
                ret_dict[key] = {"Name": name, "Mobile": mobile, "PRM": prm}
        return ret_dict
    except: return {}

retailers_data = get_retailers_data()
dropdown_options = ["सर्च करने के लिए यहाँ टाइप करें..."] + list(retailers_data.keys()) if retailers_data else ["सर्च करने के लिए यहाँ टाइप करें..."]

st.sidebar.title("📲 संध्या इंटरप्राइजेज")
st.sidebar.markdown("---")
# 🆕 'Today Collection' ऑप्शन यहाँ जोड़ दिया गया है
menu = st.sidebar.radio("मेनू चुनें:", ["📊 डैशबोर्ड (स्टॉक)", "💰 Today Collection", "➕ नया रिटेलर जोड़ें", "📦 माल / पेमेंट एंट्री", "📜 लेजर (खाता) देखें", "💰 बकाया लिस्ट (Bulk SMS)"])

# --- 1. डैशबोर्ड ---
if menu == "📊 डैशबोर्ड (स्टॉक)":
    st.title("📊 लाइव इन्वेंट्री स्टॉक")
    try:
        inv_df = pd.read_csv(inventory_csv).dropna(how="all").fillna("")
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
    except: st.error("स्टॉक लोड हो रहा है...")

# --- 🆕 2. Today Collection (New Option) ---
elif menu == "💰 Today Collection":
    st.title("💸 आज की वसूली (Today Collection)")
    st.info("यहाँ उन सभी रिटेलर्स की लिस्ट है जिनका बकाया है। आप सीधे कॉल कर सकते हैं और पेमेंट ले सकते हैं।")
    
    try:
        ledger_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
        for key, val in retailers_data.items():
            name = val["Name"]
            mobile = val["Mobile"]
            u_data = ledger_df[ledger_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
            
            if dues > 0:
                with st.expander(f"👤 {name} | 🚩 बकाया: ₹{dues}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"### [📞 कॉल करें](tel:{mobile})")
                    
                    with c2:
                        with st.form(f"pay_form_{name}", clear_on_submit=True):
                            p_amt = st.number_input(f"पेमेंट राशि (₹)", min_value=1.0, key=f"amt_{name}")
                            p_mode = st.selectbox("पेमेंट मोड", ["Cash", "Online"], key=f"mode_{name}")
                            p_fse = st.selectbox("FSE", ["Ravindra Sharma", "Lal Babu Das", "Self"], key=f"fse_{name}")
                            if st.form_submit_button("पेमेंट एंट्री सेव करें"):
                                payload = {
                                    "action": "add_txn", 
                                    "date": date.today().strftime("%d-%m-%Y"), 
                                    "r_name": name, "r_mob": mobile, 
                                    "type": f"Payment ({p_mode})", 
                                    "qty": 0, "amt_out": 0, "amt_in": p_amt, 
                                    "fse": p_fse, "txn_id": f"Direct_{p_mode}"
                                }
                                res = requests.post(WEBHOOK_URL, json=payload)
                                if res.text == "Success":
                                    st.success(f"✅ {name} का ₹{p_amt} जमा हो गया!")
                                    st.cache_data.clear()
    except: st.error("डेटा लोड करने में समस्या आई।")

# --- 3. नया रिटेलर जोड़ें ---
elif menu == "➕ नया रिटेलर जोड़ें":
    st.title("➕ नया रिटेलर जोड़ें")
    with st.form("add_retailer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            r_name = st.text_input("रिटेलर का नाम*")
            r_mobile = st.text_input("मोबाइल नंबर*", max_chars=10)
        with col2:
            r_prm = st.text_input("PRM ID*")
            r_loc = st.text_input("लोकेशन")
        if st.form_submit_button("सेव करें"):
            if r_name and r_prm and r_mobile:
                payload = {"action": "add_retailer", "name": r_name.upper(), "mobile": r_mobile, "prm": r_prm, "location": r_loc.upper(), "date": datetime.now().strftime("%d-%m-%Y")}
                res = requests.post(WEBHOOK_URL, json=payload)
                if res.text == "Success":
                    st.success("सफलतापूर्वक सेव हो गया!"); st.cache_data.clear()

# --- 4. माल / पेमेंट एंट्री ---
elif menu == "📦 माल / पेमेंट एंट्री":
    st.title("📦 स्टॉक आउट / पेमेंट लें")
    t_date = st.date_input("तारीख", date.today())
    t_prm = st.selectbox("रिटेलर चुनें*", options=dropdown_options)
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

    if st.button("🚀 सेव करें और WhatsApp भेजें", use_container_width=True):
        if t_prm != "सर्च करने के लिए यहाँ टाइप करें...":
            r_name = retailers_data[t_prm]["Name"]; r_mob = retailers_data[t_prm]["Mobile"]
            amt_out = t_amount if t_type != "पेमेंट (Payment Received)" else 0
            amt_in = t_amount if t_type == "पेमेंट (Payment Received)" else 0
            payload = {"action": "add_txn", "date": t_date.strftime("%d-%m-%Y"), "r_name": r_name, "r_mob": r_mob, "type": t_type, "qty": t_qty, "amt_out": amt_out, "amt_in": amt_in, "fse": fse, "txn_id": txn_id}
            res = requests.post(WEBHOOK_URL, json=payload)
            if res.text == "Success":
                st.success("✅ सेव हो गया!"); st.cache_data.clear()
                msg = f"*🧾 संध्या इंटरप्राइजेज*\nदिनांक: {t_date.strftime('%d-%m-%Y')}\nरिटेलर: {r_name}\nआइटम: {t_type}\nराशि: ₹{t_amount}\n🙏 धन्यवाद!"
                st.markdown(f"### [🟢 WhatsApp भेजें](https://wa.me/91{r_mob}?text={urllib.parse.quote(msg)})")

# --- 5. लेजर (अलग तारीख बॉक्स के साथ) ---
elif menu == "📜 लेजर (खाता) देखें":
    st.title("📜 रिटेलर रिपोर्ट (दो अलग तारीखें)")
    search_prm = st.selectbox("रिटेलर चुनें:", options=dropdown_options)
    
    if search_prm != "सर्च करने के लिए यहाँ टाइप करें...":
        try:
            ledger_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
            ledger_df['DateObj'] = pd.to_datetime(ledger_df['Date'], format='%d-%m-%Y', errors='coerce')
            r_name = retailers_data[search_prm]["Name"]
            user_df = ledger_df[ledger_df['Retailer Name'] == r_name].sort_values(by='DateObj')

            col_d1, col_d2 = st.columns(2)
            s_date = col_d1.date_input("शुरू (Start Date):", date.today().replace(day=1))
            e_date = col_d2.date_input("अंत (End Date):", date.today())
            
            if s_date <= e_date:
                f_df = user_df[(user_df['DateObj'].dt.date >= s_date) & (user_df['DateObj'].dt.date <= e_date)].copy()
                f_df['Amount Out (Debit)'] = pd.to_numeric(f_df['Amount Out (Debit)'], errors='coerce').fillna(0)
                f_df['Amount In (Credit)'] = pd.to_numeric(f_df['Amount In (Credit)'], errors='coerce').fillna(0)
                f_df['Balance'] = (f_df['Amount Out (Debit)'] - f_df['Amount In (Credit)']).cumsum()
                
                st.dataframe(f_df.drop(columns=['DateObj']), use_container_width=True, hide_index=True)
                t_out = f_df['Amount Out (Debit)'].sum()
                t_in = f_df['Amount In (Credit)'].sum()
                st.error(f"कुल डेबिट: ₹{t_out} | कुल क्रेडिट: ₹{t_in} | बकाया: ₹{t_out - t_in}")

                c1, c2 = st.columns(2)
                c1.download_button("📥 Excel डाउनलोड", f_df.to_csv(index=False).encode('utf-8-sig'), f"{r_name}_Ledger.csv", "text/csv")
                html = f"<h2>संध्या इंटरप्राइजेज</h2><b>रिटेलर:</b> {r_name}<br><b>अवधि:</b> {s_date} से {e_date}<br><br>" + f_df.drop(columns=['DateObj']).to_html(index=False)
                c2.download_button("📄 PDF (Report)", html.encode('utf-8-sig'), f"{r_name}_Report.html", "text/html")
        except: st.error("डेटा लोड नहीं हुआ।")

# --- 6. बकाया लिस्ट ---
elif menu == "💰 बकाया लिस्ट (Bulk SMS)":
    st.title("💰 बकाया वसूली लिस्ट")
    if st.button("🔄 सभी का बकाया चेक करें"):
        try:
            ledger_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
            summary = []
            for key, val in retailers_data.items():
                name = val["Name"]
                u_data = ledger_df[ledger_df['Retailer Name'] == name]
                d = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
                c = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
                if (d - c) > 0:
                    summary.append({"रिटेलर": name, "मोबाइल": val["Mobile"], "बकाया": d - c})
            
            s_df = pd.DataFrame(summary)
            if not s_df.empty:
                st.error(f"💸 कुल मार्केट बकाया: ₹{s_df['बकाया'].sum()}")
                st.dataframe(s_df, use_container_width=True, hide_index=True)
                for _, row in s_df.iterrows():
                    msg = f"डियर पार्टनर, आपका बकाया ₹{row['बकाया']} है। कृपया पेमेंट करें।"
                    st.markdown(f"**{row['रिटेलर']}** (₹{row['बकाया']}) -> [📲 रिमाइंडर भेजें](https://wa.me/91{row['मोबाइल']}?text={urllib.parse.quote(msg)})")
            else: st.success("कोई बकाया नहीं है!")
        except: st.error("एरर")
