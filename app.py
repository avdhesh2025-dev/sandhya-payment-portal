import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import requests

# पेज की सेटिंग
st.set_page_config(page_title="Sandhya ERP System", page_icon="🏢", layout="wide")

# मेनू और पेज का डिज़ाइन
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

# 🛑 आपका APPS SCRIPT वाला URL (फोटो से लिया गया)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby_yV4nEMwrBODnkVh0x5DrVqcbj42iDMLNlX8M7QPrVGGMltoOfZhlid_gXlB0dwMvZQ/exec"

# आपकी गूगल शीट के डायरेक्ट लिंक्स
sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

# डेटाबेस से रिटेलर्स की लिस्ट लाना
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
if retailers_data:
    dropdown_options = ["सर्च करने के लिए यहाँ टाइप करें..."] + list(retailers_data.keys())
else:
    dropdown_options = ["सर्च करने के लिए यहाँ टाइप करें..."]

# साइडबार (मेनू)
st.sidebar.title("📲 संध्या इंटरप्राइजेज")
st.sidebar.markdown("---")
menu = st.sidebar.radio("मेनू चुनें:", ["📊 डैशबोर्ड (स्टॉक)", "➕ नया रिटेलर जोड़ें", "📦 माल / पेमेंट एंट्री", "📜 लेजर (खाता) देखें"])

# ---------------------------------------------------------
# 1. डैशबोर्ड
if menu == "📊 डैशबोर्ड (स्टॉक)":
    st.title("📊 लाइव इन्वेंट्री स्टॉक")
    try:
        inv_df = pd.read_csv(inventory_csv)
        inv_df = inv_df.dropna(how="all").fillna("")
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error("स्टॉक लोड हो रहा है...")

# ---------------------------------------------------------
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
        
        if submit_retailer:
            if r_name and r_prm and r_mobile:
                payload = {
                    "action": "add_retailer",
                    "name": str(r_name).strip().upper(),
                    "mobile": str(r_mobile).strip(),
                    "prm": str(r_prm).strip(),
                    "location": str(r_loc).strip().upper(),
                    "date": datetime.now().strftime("%d-%m-%Y")
                }
                try:
                    res = requests.post(WEBHOOK_URL, json=payload)
                    if res.text == "Success":
                        st.success(f"✅ रिटेलर {r_name} सफलतापूर्वक सेव हो गया!")
                        st.balloons()
                        st.cache_data.clear()
                    else:
                        st.error(f"❌ सेव नहीं हुआ: {res.text}")
                except Exception as e:
                    st.error("❌ नेटवर्क एरर! कृपया इंटरनेट चेक करें।")
            else:
                st.warning("कृपया नाम, मोबाइल नंबर और PRM ID भरें।")

# ---------------------------------------------------------
# 3. माल इशू / पेमेंट एंट्री
elif menu == "📦 माल / पेमेंट एंट्री":
    st.title("📦 स्टॉक आउट / पेमेंट लें")
    with st.form("transaction_form", clear_on_submit=True):
        t_date = st.date_input("तारीख", datetime.now())
        t_prm = st.selectbox("रिटेलर खोजें (PRM ID या नाम टाइप करें)*", options=dropdown_options)
        
        col1, col2 = st.columns(2)
        with col1:
            t_type = st.selectbox("क्या एंट्री करनी है?", ["Jio Phone", "SIM Card", "Etop Recharge", "पेमेंट (Payment Received)"])
            t_qty = st.number_input("मात्रा (Quantity - SIM/Phone के लिए)", min_value=0)
            fse = st.selectbox("एंट्री करने वाला (FSE)", ["Ravindra Sharma", "Lal Babu Das", "Self"])
        with col2:
            t_amount = st.number_input("राशि (Amount ₹)", min_value=0.0, step=10.0)
            txn_id = st.text_input("Transaction ID (यदि हो)")
            
        submit_txn = st.form_submit_button("एंट्री सेव करें और स्टॉक अपडेट करें")

    if submit_txn:
        if t_prm == "सर्च करने के लिए यहाँ टाइप करें...":
            st.error("कृपया लिस्ट में से कोई रिटेलर चुनें!")
        else:
            r_name = retailers_data[t_prm]["Name"]
            r_mob = retailers_data[t_prm]["Mobile"]
            amt_out = t_amount if t_type != "पेमेंट (Payment Received)" else 0
            amt_in = t_amount if t_type == "पेमेंट (Payment Received)" else 0
            
            payload = {
                "action": "add_txn",
                "date": t_date.strftime("%d-%m-%Y"),
                "r_name": r_name,
                "r_mob": r_mob,
                "type": t_type,
                "qty": t_qty,
                "amt_out": amt_out,
                "amt_in": amt_in,
                "fse": fse,
                "txn_id": txn_id
            }
            try:
                res = requests.post(WEBHOOK_URL, json=payload)
                if res.text == "Success":
                    st.success(f"✅ {r_name} की एंट्री लेजर में सेव हो गई और स्टॉक अपडेट हो गया!")
                    st.balloons()
                    st.cache_data.clear()
                    
                    msg = f"संध्या इंटरप्राइजेज\nतारीख: {t_date.strftime('%d-%m-%Y')}\nरिटेलर: {r_name}\nआइटम: {t_type}\nमात्रा: {t_qty}\nराशि: ₹{t_amount}\nधन्यवाद!"
                    wa_url = f"https://wa.me/91{r_mob}?text={urllib.parse.quote(msg)}"
                    st.markdown(f"### [🟢 WhatsApp पर रसीद भेजने के लिए यहाँ क्लिक करें]({wa_url})", unsafe_allow_html=True)
                else:
                    st.error(f"❌ सेव नहीं हुआ: {res.text}")
            except:
                st.error("❌ नेटवर्क एरर! कृपया इंटरनेट चेक करें।")

# ---------------------------------------------------------
# 4. लेजर (खाता) देखें (नया और चालू)
elif menu == "📜 लेजर (खाता) देखें":
    st.title("📜 रिटेलर का पूरा खाता")
    search_prm = st.selectbox("रिटेलर का खाता देखने के लिए खोजें:", options=dropdown_options)
    
    if search_prm != "सर्च करने के लिए यहाँ टाइप करें...":
        try:
            # लेजर डेटा पढ़ना
            ledger_df = pd.read_csv(ledger_csv)
            ledger_df = ledger_df.dropna(how="all").fillna("")
            
            # रिटेलर का नाम निकालना
            r_name = retailers_data[search_prm]["Name"]
            
            # उस रिटेलर का डेटा फ़िल्टर करना
            user_ledger = ledger_df[ledger_df['Retailer Name'] == r_name]
            
            if not user_ledger.empty:
                st.markdown(f"### 👤 {r_name} का खाता")
                st.dataframe(user_ledger, use_container_width=True, hide_index=True)
                
                # कुल हिसाब जोड़ना
                total_out = pd.to_numeric(user_ledger['Amount Out (Debit)'], errors='coerce').sum()
                total_in = pd.to_numeric(user_ledger['Amount In (Credit)'], errors='coerce').sum()
                balance = total_out - total_in
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                col1.error(f"🔴 कुल माल दिया: ₹{total_out}")
                col2.success(f"🟢 कुल पैसा आया: ₹{total_in}")
                
                if balance > 0:
                    col3.warning(f"⚠️ बकाया (Dues): ₹{balance}")
                elif balance < 0:
                    col3.info(f"🔵 एडवांस (Advance): ₹{abs(balance)}")
                else:
                    col3.success(f"✅ बकाया: ₹0 (हिसाब बराबर)")
            else:
                st.info("इस रिटेलर की अभी कोई एंट्री नहीं है।")
        except Exception as e:
            st.error("लेजर लोड हो रहा है...")
