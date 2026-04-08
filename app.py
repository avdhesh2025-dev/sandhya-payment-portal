import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
import requests

# 1. पेज की सेटिंग (Sidebar छुपाने के साथ)
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# 💎 प्रीमियम लुक के लिए CSS (ग्लोबल)
st.markdown("""
    <style>
    /* ऐप का बैकग्राउंड */
    .stApp { background-color: #f4f7f6; }
    
    /* साइडबार और ऊपर का मेनू आइकॉन छुपाना */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
    
    /* 🌟 प्रीमियम हेडर */
    .app-header {
        background: linear-gradient(135deg, #141e30 0%, #243b55 100%);
        color: white;
        padding: 35px 20px;
        border-radius: 16px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    .app-header h1 { font-size: 2.4rem; font-weight: 700; margin-bottom: 5px; color: #ffffff;}
    .app-header p { font-size: 1.1rem; font-weight: 300; opacity: 0.8; margin: 0;}
    
    /* 🎴 प्रीमियम कार्ड (बटन) का डिज़ाइन */
    .stButton > button {
        height: 75px;
        background: #ffffff;
        color: #1e293b;
        border: 1.5px solid #e2e8f0;
        border-radius: 14px;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 10px;
    }
    .stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.08);
        border-color: #3b82f6;
        color: #3b82f6;
    }
    .stButton > button:active {
        transform: translateY(0px);
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

# रिटेलर डिक्शनरी बनाना
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

# नेविगेशन के लिए सेशन स्टेट
if "current_page" not in st.session_state:
    st.session_state.current_page = "HOME"

def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- 🌟 APP HEADER ---
st.markdown('<div class="app-header"><h1>🏢 संध्या इंटरप्राइजेज</h1><p>Smart Business Management System</p></div>', unsafe_allow_html=True)

# --- 🏠 HOME PAGE (प्रीमियम ग्रिड - पूरी चौड़ाई के साथ) ---
if st.session_state.current_page == "HOME":
    st.markdown("### 📌 मुख्य मेनू")
    st.write("") # थोड़ा स्पेस
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 लाइव स्टॉक (Stock)", use_container_width=True): go_to("STOCK")
        if st.button("➕ नया रिटेलर (Add)", use_container_width=True): go_to("ADD_RETAILER")
        if st.button("📜 खाता रिपोर्ट (Ledger)", use_container_width=True): go_to("LEDGER")

    with col2:
        if st.button("💰 आज की वसूली (Collection)", use_container_width=True): go_to("COLLECTION")
        if st.button("📦 माल / पेमेंट एंट्री", use_container_width=True): go_to("ENTRY")
        if st.button("💸 बकाया लिस्ट (Dues)", use_container_width=True): go_to("DUES")

# --- 📊 1. STOCK PAGE ---
elif st.session_state.current_page == "STOCK":
    if st.button("🔙 वापस मेनू पर जाएं", use_container_width=True): go_to("HOME")
    st.header("📊 लाइव इन्वेंट्री स्टॉक")
    if inv_df is not None:
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
    else: st.error("डेटा लोड नहीं हुआ।")

# --- 💰 2. TODAY COLLECTION ---
elif st.session_state.current_page == "COLLECTION":
    if st.button("🔙 वापस मेनू पर जाएं", use_container_width=True): go_to("HOME")
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
                            p_fse = st.selectbox("FSE", ["Ravindra Sharma", "Lal Babu Das", "Self"], key=f"fse_{name}")
                            if st.form_submit_button("पेमेंट सेव करें", use_container_width=True):
                                payload = {
                                    "action": "add_txn", 
                                    "date": date.today().strftime("%d-%m-%Y"), 
                                    "r_name": name, "r_mob": mobile, 
                                    "type": f"Payment ({p_mode})", 
                                    "qty": 0, "amt_out": 0, "amt_in": p_amt, 
                                    "fse": p_fse, "txn_id": f"Direct_{p_mode}"
                                }
                                requests.post(WEBHOOK_URL, json=payload)
                                st.success(f"✅ {name} का ₹{p_amt} जमा हो गया!")
                                st.cache_data.clear()

# --- 📦 3. ENTRY PAGE (सिर्फ यहाँ 3D डिज़ाइन लागू होगा) ---
elif st.session_state.current_page == "ENTRY":
    # 🎴 सिर्फ इस पेज के लिए 3D और हिलने वाला (Wobble) एनीमेशन
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
            border: none !important;
            border-radius: 12px !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            box-shadow: 0 6px 0 #d1d9e6, 0 10px 15px rgba(0,0,0,0.1) !important;
            border-left: 6px solid #007bff !important;
            position: relative !important;
            top: 0 !important;
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
    
    if st.button("🔙 वापस मेनू पर जाएं", use_container_width=True): go_to("HOME")
    st.header("📦 स्टॉक आउट / पेमेंट लें")
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
            requests.post(WEBHOOK_URL, json=payload)
            st.success("✅ सेव हो गया!"); st.cache_data.clear()
            msg = f"*🧾 संध्या इंटरप्राइजेज*\nदिनांक: {t_date.strftime('%d-%m-%Y')}\nरिटेलर: {r_name}\nआइटम: {t_type}\nराशि: ₹{t_amount}\n🙏 धन्यवाद!"
            st.markdown(f"### [🟢 WhatsApp भेजें](https://wa.me/91{r_mob}?text={urllib.parse.quote(msg)})", unsafe_allow_html=True)

# --- ➕ 4. ADD RETAILER ---
elif st.session_state.current_page == "ADD_RETAILER":
    if st.button("🔙 वापस मेनू पर जाएं", use_container_width=True): go_to("HOME")
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
elif st.session_state.current_page == "LEDGER":
    if st.button("🔙 वापस मेनू पर जाएं", use_container_width=True): go_to("HOME")
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
elif st.session_state.current_page == "DUES":
    if st.button("🔙 वापस मेनू पर जाएं", use_container_width=True): go_to("HOME")
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
