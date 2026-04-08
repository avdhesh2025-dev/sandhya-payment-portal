import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
import requests

# 1. पेज की सेटिंग (पुराना साइडबार)
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="wide")

# 💎 ग्लोबल डिज़ाइन (बाकी सब सादा और साफ़ रहेगा)
st.markdown("""
    <style>
    /* बैकग्राउंड */
    .main { background-color: #f0f2f5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* 🌟 प्रीमियम हेडर */
    .app-header {
        background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        border-bottom: 4px solid #00c6ff;
    }
    .app-header h1 { margin: 0; font-size: 2.2rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .app-header p { margin: 5px 0 0 0; font-size: 1rem; opacity: 0.9; }

    /* इनपुट बॉक्स डिज़ाइन */
    .stDataFrame, .stSelectbox, .stNumberInput, .stTextInput, .stDateInput {
        background-color: white;
        border-radius: 10px;
        padding: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 🛑 आपका APPS SCRIPT URL
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby_yV4nEMwrBODnkVh0x5DrVqcbj42iDMLNlX8M7QPrVGGMltoOfZhlid_gXlB0dwMvZQ/exec"

sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

@st.cache_data(ttl=30)
def load_data():
    try:
        ret_df = pd.read_csv(retailers_csv).dropna(how="all").fillna("")
        inv_df = pd.read_csv(inventory_csv).dropna(how="all").fillna("")
        led_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
        return ret_df, inv_df, led_df
    except: return None, None, None

ret_df, inv_df, led_df = load_data()

# रिटेलर ड्रॉपडाउन लिस्ट
retailers_data = {}
dropdown_options = ["सर्च करने के लिए यहाँ टाइप करें..."]
if ret_df is not None:
    for index, row in ret_df.iterrows():
        prm = str(row.get("PRM ID", "")).split('.')[0]
        name = str(row.get("Retailer Name", ""))
        mobile = str(row.get("Mobile Number", "")).split('.')[0]
        if prm and name and prm != "nan":
            retailers_data[f"{prm} - {name}"] = {"Name": name, "Mobile": mobile, "PRM": prm}
            dropdown_options.append(f"{prm} - {name}")

# --- 🌟 APP HEADER ---
st.markdown('<div class="app-header"><h1>🏢 संध्या इंटरप्राइजेज</h1><p>Smart Business Management System</p></div>', unsafe_allow_html=True)

# --- 📱 साइडबार मेनू ---
st.sidebar.title("📲 संध्या इंटरप्राइजेज")
st.sidebar.markdown("---")
menu = st.sidebar.radio("मेनू चुनें:", [
    "📊 डैशबोर्ड (स्टॉक)", 
    "💰 Today Collection", 
    "➕ नया रिटेलर जोड़ें", 
    "📦 माल / पेमेंट एंट्री", 
    "📜 लेजर (खाता) देखें", 
    "💸 बकाया लिस्ट (Bulk SMS)"
])

# --- 📊 1. STOCK PAGE ---
if menu == "📊 डैशबोर्ड (स्टॉक)":
    st.header("📊 लाइव इन्वेंट्री स्टॉक")
    if inv_df is not None:
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
    else: st.error("डेटा लोड नहीं हुआ।")

# --- 💰 2. TODAY COLLECTION ---
elif menu == "💰 Today Collection":
    st.header("💸 आज की वसूली (Today Collection)")
    st.info("यहाँ उन सभी रिटेलर्स की लिस्ट है जिनका बकाया है। आप सीधे कॉल कर सकते हैं और पेमेंट ले सकते हैं।")
    
    if ret_df is not None and led_df is not None:
        for index, row in ret_df.iterrows():
            name = row["Retailer Name"]
            mobile = row["Mobile Number"]
            u_data = led_df[led_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
            
            if dues > 0:
                with st.expander(f"👤 {name} | 🚩 बकाया: ₹{dues}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"### [📞 कॉल करें (Call)](tel:{mobile})")
                    
                    with c2:
                        with st.form(f"pay_form_{name}", clear_on_submit=True):
                            p_amt = st.number_input(f"पेमेंट राशि (₹)", min_value=1.0, key=f"amt_{name}")
                            p_mode = st.selectbox("पेमेंट मोड", ["Cash", "Online"], key=f"mode_{name}")
                            p_fse = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"], key=f"fse_{name}")
                            if st.form_submit_button("पेमेंट सेव करें", use_container_width=True):
                                payload = {
                                    "action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), 
                                    "r_name": name, "r_mob": mobile, "type": f"Payment ({p_mode})", 
                                    "qty": 0, "amt_out": 0, "amt_in": p_amt, "fse": p_fse, "txn_id": f"Direct_{p_mode}"
                                }
                                requests.post(WEBHOOK_URL, json=payload)
                                st.success(f"✅ {name} का ₹{p_amt} जमा हो गया!")
                                st.cache_data.clear()

# --- 📦 3. ENTRY PAGE (3D डिज़ाइन + नई एंट्री सेटिंग्स) ---
elif menu == "📦 माल / पेमेंट एंट्री":
    # 🎴 सिर्फ इस पेज के लिए 3D और हिलने वाला (Wobble) एनीमेशन
    st.markdown("""
        <style>
        .stButton>button {
            width: 100% !important;
            background-color: #ffffff !important;
            color: #1a1a1a !important;
            border: none !important;
            border-radius: 12px !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            box-shadow: 0 6px 0 #d1d9e6, 0 10px 15px rgba(0,0,0,0.1) !important;
            transition: all 0.2s ease-out !important;
            border-left: 6px solid #007bff !important;
            margin-bottom: 10px !important;
            position: relative;
            top: 0;
        }
        .stButton>button:hover {
            color: #007bff !important;
            border-left: 6px solid #00c6ff !important;
            top: -3px !important;
            box-shadow: 0 9px 0 #d1d9e6, 0 15px 20px rgba(0,0,0,0.15) !important;
            animation: wobble-hor-bottom 0.5s both !important;
        }
        .stButton>button:active {
            top: 4px !important;
            box-shadow: 0 2px 0 #d1d9e6, 0 5px 10px rgba(0,0,0,0.1) !important;
            animation: none !important;
        }
        @keyframes wobble-hor-bottom {
            0%, 100% { transform: translateX(0%); }
            15% { transform: translateX(-4px) rotate(-1deg); }
            30% { transform: translateX(3px) rotate(1deg); }
            45% { transform: translateX(-2px) rotate(-0.5deg); }
            60% { transform: translateX(1px) rotate(0.2deg); }
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("📦 स्टॉक आउट / पेमेंट लें")
    t_date = st.date_input("तारीख", date.today())
    t_prm = st.selectbox("रिटेलर चुनें*", options=dropdown_options)
    
    col1, col2 = st.columns(2)
    with col1:
        # 🟢 ड्रॉपडाउन में बदलाव
        t_type = st.selectbox("क्या एंट्री करनी है?", ["Etop Transfer", "Payment Received", "JPB V4", "Sim Card"])
        fse = st.selectbox("एंट्री करने वाला (FSE)", ["Avdhesh Kumar", "Babloo kumar singh"])
        fse_pin = st.text_input("4 अंकों का PIN डालें*", type="password", max_chars=4)

    with col2:
        t_qty = 0
        t_amount = 0.0
        p_mode = ""
        
        # 🟢 Etop Transfer सेटिंग्स
        if t_type == "Etop Transfer":
            etop_opt = st.selectbox("राशि चुनें ₹", ["5000", "3000", "2000", "1500", "500", "Manual"])
            if etop_opt == "Manual":
                t_amt_input = st.number_input("मैनुअल राशि भरें ₹", min_value=1.0, value=None, step=10.0)
                t_amount = t_amt_input if t_amt_input else 0.0
            else:
                t_amount = float(etop_opt)
        
        # 🟢 Payment Received सेटिंग्स (खाली बॉक्स)
        elif t_type == "Payment Received":
            p_mode = st.selectbox("पेमेंट मोड", ["Cash", "Online"])
            t_amt_input = st.number_input("राशि भरें ₹ (यहाँ टाइप करें)", min_value=1.0, value=None, step=10.0)
            t_amount = t_amt_input if t_amt_input else 0.0
        
        # 🟢 JPB V4 (Jio Phone)
        elif t_type == "JPB V4":
            t_qty = st.number_input("मात्रा (Piece)", min_value=1)
            t_rate_input = st.number_input("रेट ₹", min_value=0.0, value=None, step=10.0)
            if t_rate_input:
                t_amount = t_qty * t_rate_input
                st.info(f"कुल राशि: ₹{t_amount}")
            else:
                t_amount = 0.0
                
        # 🟢 Sim Card
        elif t_type == "Sim Card":
            t_qty = st.number_input("मात्रा (SIM)", min_value=1)
            t_amount = 0.0

        txn_id = st.text_input("Transaction ID (यदि हो)")

    if st.button("🚀 सेव करें और WhatsApp भेजें", use_container_width=True):
        # 🔴 PIN और एरर चेकिंग
        if t_prm == "सर्च करने के लिए यहाँ टाइप करें...":
            st.error("कृपया लिस्ट में से रिटेलर चुनें!")
        elif (t_type != "Sim Card") and (t_amount == 0.0 or t_amount is None):
            st.error("कृपया सही राशि भरें!")
        elif fse == "Avdhesh Kumar" and fse_pin != "9557":
            st.error("❌ Avdhesh Kumar के लिए PIN गलत है!")
        elif fse == "Babloo kumar singh" and fse_pin != "2081":
            st.error("❌ Babloo kumar singh के लिए PIN गलत है!")
        else:
            r_name = retailers_data[t_prm]["Name"]
            r_mob = retailers_data[t_prm]["Mobile"]
            
            # डेबिट और क्रेडिट सेट करना
            amt_out = t_amount if t_type != "Payment Received" else 0
            amt_in = t_amount if t_type == "Payment Received" else 0
            final_type = f"{t_type} ({p_mode})" if t_type == "Payment Received" else t_type
            
            payload = {"action": "add_txn", "date": t_date.strftime("%d-%m-%Y"), "r_name": r_name, "r_mob": r_mob, "type": final_type, "qty": t_qty, "amt_out": amt_out, "amt_in": amt_in, "fse": fse, "txn_id": txn_id}
            requests.post(WEBHOOK_URL, json=payload)
            st.success("✅ सफलतापूर्वक सेव हो गया!")
            st.cache_data.clear()
            msg = f"*🧾 संध्या इंटरप्राइजेज*\nदिनांक: {t_date.strftime('%d-%m-%Y')}\nरिटेलर: {r_name}\nआइटम: {final_type}\nराशि: ₹{t_amount}\n🙏 धन्यवाद!"
            st.markdown(f"### [🟢 WhatsApp रसीद भेजें](https://wa.me/91{r_mob}?text={urllib.parse.quote(msg)})", unsafe_allow_html=True)

# --- ➕ 4. ADD RETAILER ---
elif menu == "➕ नया रिटेलर जोड़ें":
    st.header("➕ नया रिटेलर जोड़ें")
    with st.form("add_retailer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            r_name = st.text_input("रिटेलर का नाम*")
            r_mobile = st.text_input("मोबाइल नंबर*", max_chars=10)
        with col2:
            r_prm = st.text_input("PRM ID*")
            r_loc = st.text_input("लोकेशन")
        if st.form_submit_button("सेव करें", use_container_width=True):
            if r_name and r_prm and r_mobile:
                payload = {"action": "add_retailer", "name": r_name.upper(), "mobile": r_mobile, "prm": r_prm, "location": r_loc.upper(), "date": datetime.now().strftime("%d-%m-%Y")}
                requests.post(WEBHOOK_URL, json=payload)
                st.success("सफलतापूर्वक सेव हो गया!"); st.cache_data.clear()

# --- 📜 5. LEDGER ---
elif menu == "📜 लेजर (खाता) देखें":
    st.header("📜 रिटेलर रिपोर्ट (खाता)")
    search_prm = st.selectbox("रिटेलर चुनें:", options=dropdown_options)
    
    if search_prm != "सर्च करने के लिए यहाँ टाइप करें...":
        try:
            r_name = retailers_data[search_prm]["Name"]
            led_df['DateObj'] = pd.to_datetime(led_df['Date'], format='%d-%m-%Y', errors='coerce')
            user_df = led_df[led_df['Retailer Name'] == r_name].sort_values(by='DateObj')

            st.markdown(f"### 👤 {r_name} का खाता")
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
                c1.download_button("📥 Excel डाउनलोड", f_df.to_csv(index=False).encode('utf-8-sig'), f"{r_name}_Ledger.csv", "text/csv", use_container_width=True)
                html = f"<h2>संध्या इंटरप्राइजेज</h2><b>रिटेलर:</b> {r_name}<br><b>अवधि:</b> {s_date} से {e_date}<br><br>" + f_df.drop(columns=['DateObj']).to_html(index=False)
                c2.download_button("📄 PDF (Report)", html.encode('utf-8-sig'), f"{r_name}_Report.html", "text/html", use_container_width=True)
        except: st.error("डेटा लोड नहीं हुआ।")

# --- 💸 6. DUES REMINDERS ---
elif menu == "💸 बकाया लिस्ट (Bulk SMS)":
    st.header("💰 बकाया वसूली लिस्ट (Bulk SMS)")
    
    if st.button("🔄 सभी का बकाया चेक करें", use_container_width=True):
        try:
            summary = []
            for key, val in retailers_data.items():
                name = val["Name"]
                u_data = led_df[led_df['Retailer Name'] == name]
                d = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
                c = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
                if (d - c) > 0: summary.append({"रिटेलर": name, "मोबाइल": val["Mobile"], "बकाया": d - c})
            
            s_df = pd.DataFrame(summary)
            if not s_df.empty:
                st.error(f"💸 कुल मार्केट बकाया: ₹{s_df['बकाया'].sum()}")
                st.dataframe(s_df, use_container_width=True, hide_index=True)
                for _, row in s_df.iterrows():
                    msg = f"डियर पार्टनर, आपका बकाया ₹{row['बकाया']} है। कृपया पेमेंट करें।"
                    st.markdown(f"**{row['रिटेलर']}** (₹{row['बकाया']}) -> [📲 रिमाइंडर भेजें](https://wa.me/91{row['मोबाइल']}?text={urllib.parse.quote(msg)})")
            else: st.success("कोई बकाया नहीं है!")
        except: st.error("एरर")
