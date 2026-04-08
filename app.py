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
        df = pd.read_csv(retailers_csv)
        df = df.dropna(how="all").fillna("")
        ret_dict = {}
        for index, row in df.iterrows():
            prm = str(row.get("PRM ID", "")).split('.')[0]
            name = str(row.get("Retailer Name", ""))
            mobile = str(row.get("Mobile Number", "")).split('.')[0]
            if prm and name and prm != "nan":
                key = f"{prm} - {name}"
                ret_dict[key] = {"Name": name, "Mobile": mobile}
        return ret_dict
    except:
        return {}

retailers_data = get_retailers_data()
dropdown_options = ["सर्च करने के लिए यहाँ टाइप करें..."] + list(retailers_data.keys()) if retailers_data else ["सर्च करने के लिए यहाँ टाइप करें..."]

st.sidebar.title("📲 संध्या इंटरप्राइजेज")
st.sidebar.markdown("---")
menu = st.sidebar.radio("मेनू चुनें:", ["📊 डैशबोर्ड (स्टॉक)", "➕ नया रिटेलर जोड़ें", "📦 माल / पेमेंट एंट्री", "📜 लेजर (खाता) देखें"])

# 1. डैशबोर्ड
if menu == "📊 डैशबोर्ड (स्टॉक)":
    st.title("📊 लाइव इन्वेंट्री स्टॉक")
    try:
        inv_df = pd.read_csv(inventory_csv).dropna(how="all").fillna("")
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
    except:
        st.error("स्टॉक लोड हो रहा है...")

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
        t_qty = 0
        t_amount = 0.0
        
        # ऑटोमैटिक कैलकुलेशन बॉक्स
        if t_type == "SIM Card":
            t_qty = st.number_input("मात्रा (Quantity - SIM के लिए)", min_value=1)
            t_amount = 0.0
        elif t_type in ["Etop Recharge", "पेमेंट (Payment Received)"]:
            t_qty = 0
            t_amount = st.number_input("कुल राशि (Amount ₹)", min_value=1.0, step=10.0)
        else: # Jio Phone
            t_qty = st.number_input("मात्रा (Quantity - Phone के लिए)", min_value=1)
            t_rate = st.number_input("प्रति पीस रेट (Rate per piece ₹)", min_value=0.0, step=10.0)
            t_amount = t_qty * t_rate # गुणा हो गया
            st.info(f"कुल राशि (Total Amount): ₹{t_amount}")
            
        txn_id = st.text_input("Transaction ID (यदि हो)")

    st.markdown("---")
    submit_txn = st.button("🚀 एंट्री सेव करें और WhatsApp भेजें", use_container_width=True)

    if submit_txn:
        if t_prm == "सर्च करने के लिए यहाँ टाइप करें...":
            st.error("कृपया लिस्ट में से कोई रिटेलर चुनें!")
        else:
            r_name = retailers_data[t_prm]["Name"]
            r_mob = retailers_data[t_prm]["Mobile"]
            amt_out = t_amount if t_type != "पेमेंट (Payment Received)" else 0
            amt_in = t_amount if t_type == "पेमेंट (Payment Received)" else 0
            
            try:
                l_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
                u_ledger = l_df[l_df['Retailer Name'] == r_name]
                tot_out = pd.to_numeric(u_ledger['Amount Out (Debit)'], errors='coerce').sum()
                tot_in = pd.to_numeric(u_ledger['Amount In (Credit)'], errors='coerce').sum()
                old_bal = tot_out - tot_in
            except:
                old_bal = 0
                
            new_bal = old_bal + amt_out - amt_in

            payload = {"action": "add_txn", "date": t_date.strftime("%d-%m-%Y"), "r_name": r_name, "r_mob": r_mob, "type": t_type, "qty": t_qty, "amt_out": amt_out, "amt_in": amt_in, "fse": fse, "txn_id": txn_id}
            
            try:
                res = requests.post(WEBHOOK_URL, json=payload)
                if res.text == "Success":
                    st.success(f"✅ {r_name} की एंट्री लेजर में सेव हो गई!")
                    st.balloons()
                    
                    bal_text = f"बकाया (Dues): ₹{new_bal}" if new_bal >= 0 else f"एडवांस जमा: ₹{abs(new_bal)}"
                    msg = f"*🧾 संध्या इंटरप्राइजेज - रसीद*\n------------------------\n*दिनांक:* {t_date.strftime('%d-%m-%Y')}\n*रिटेलर:* {r_name}\n*आइटम:* {t_type}\n"
                    if t_qty > 0: msg += f"*मात्रा:* {t_qty} पीस\n"
                    if t_amount > 0: msg += f"*कुल राशि:* ₹{t_amount}\n"
                    msg += f"------------------------\n*कुल {bal_text}*\n*एंट्री द्वारा:* {fse}\n🙏 धन्यवाद!"
                    
                    wa_url = f"https://wa.me/91{r_mob}?text={urllib.parse.quote(msg)}"
                    st.markdown(f"### [🟢 WhatsApp पर डिजिटल रसीद भेजने के लिए यहाँ क्लिक करें]({wa_url})", unsafe_allow_html=True)
                else:
                    st.error(f"❌ सेव नहीं हुआ: {res.text}")
            except:
                st.error("❌ नेटवर्क एरर!")

# 4. लेजर (खाता) देखें
elif menu == "📜 लेजर (खाता) देखें":
    st.title("📜 रिटेलर का पूरा खाता")
    search_prm = st.selectbox("रिटेलर का खाता देखने के लिए खोजें:", options=dropdown_options)
    
    if search_prm != "सर्च करने के लिए यहाँ टाइप करें...":
        try:
            ledger_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
            r_name = retailers_data[search_prm]["Name"]
            user_ledger = ledger_df[ledger_df['Retailer Name'] == r_name].copy()
            
            if not user_ledger.empty:
                st.markdown(f"### 👤 {r_name} का खाता")
                
                user_ledger['DateObj'] = pd.to_datetime(user_ledger['Date'], format='%d-%m-%Y', errors='coerce')
                date_range = st.date_input("तारीख से फ़िल्टर करें (Start Date - End Date)", [])
                
                if len(date_range) == 2:
                    start_d, end_d = date_range
                    start_d = pd.to_datetime(start_d)
                    end_d = pd.to_datetime(end_d)
                    user_ledger = user_ledger[(user_ledger['DateObj'] >= start_d) & (user_ledger['DateObj'] <= end_d)]
                
                display_ledger = user_ledger.drop(columns=['DateObj'], errors='ignore')
                st.dataframe(display_ledger, use_container_width=True, hide_index=True)
                
                total_out = pd.to_numeric(display_ledger['Amount Out (Debit)'], errors='coerce').sum()
                total_in = pd.to_numeric(display_ledger['Amount In (Credit)'], errors='coerce').sum()
                balance = total_out - total_in
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                col1.error(f"🔴 कुल माल दिया: ₹{total_out}")
                col2.success(f"🟢 कुल पैसा आया: ₹{total_in}")
                
                if balance > 0: col3.warning(f"⚠️ कुल बकाया: ₹{balance}")
                elif balance < 0: col3.info(f"🔵 कुल एडवांस: ₹{abs(balance)}")
                else: col3.success(f"✅ हिसाब बराबर (₹0)")

                csv_data = display_ledger.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 लेजर डाउनलोड करें (Excel/CSV में)",
                    data=csv_data,
                    file_name=f"{r_name}_Ledger.csv",
                    mime="text/csv"
                )
                
                r_mob = retailers_data[search_prm]["Mobile"]
                summary_msg = f"*📊 संध्या इंटरप्राइजेज - लेजर समरी*\n*रिटेलर:* {r_name}\n*कुल माल लिया:* ₹{total_out}\n*कुल पेमेंट दिया:* ₹{total_in}\n*बाकी बकाया:* ₹{balance if balance > 0 else 0}\n*एडवांस:* ₹{abs(balance) if balance < 0 else 0}\n(पूरा हिसाब जानने के लिए डिस्ट्रीब्यूटर से संपर्क करें)"
                wa_ledger_url = f"https://wa.me/91{r_mob}?text={urllib.parse.quote(summary_msg)}"
                st.markdown(f"**[🟢 इस हिसाब को WhatsApp पर भेजें]({wa_ledger_url})**", unsafe_allow_html=True)

            else:
                st.info("इस रिटेलर की अभी कोई एंट्री नहीं है।")
        except Exception as e:
            st.error("लेजर लोड हो रहा है...")
