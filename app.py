import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import requests

# पेज की सेटिंग
st.set_page_config(page_title="Sandhya ERP System", page_icon="🏢", layout="wide")

# 🛑 अपना चालू APPS SCRIPT वाला URL यहाँ डालें
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby_yV4nEMwrBODnkVh0x5DrVqcbj42iDMLNlX8M7QPrVGGMltoOfZhlid_gXlB0dwMvZQ/exec"

sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
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
            if prm and name:
                ret_dict[f"{prm} - {name}"] = {"Name": name, "Mobile": mobile}
        return ret_dict
    except: return {}

retailers_data = get_retailers_data()

st.sidebar.title("📲 संध्या इंटरप्राइजेज")
menu = st.sidebar.radio("मेनू चुनें:", ["📊 डैशबोर्ड", "📦 नई एंट्री", "📜 लेजर देखें", "💰 बकाया लिस्ट (Bulk SMS)"])

# --- बकाया लिस्ट और बल्क मैसेजिंग सेक्शन ---
if menu == "💰 बकाया लिस्ट (Bulk SMS)":
    st.title("💰 बकाया वसूली (Bulk WhatsApp Reminder)")
    
    if st.button("🔄 सभी का बकाया चेक करें"):
        try:
            ledger_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
            summary = []
            
            for key, val in retailers_data.items():
                name = val["Name"]
                u_data = ledger_df[ledger_df['Retailer Name'] == name]
                debit = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
                credit = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
                dues = debit - credit
                
                if dues > 0: # सिर्फ उनका जिनका बकाया है
                    summary.append({"रिटेलर": name, "मोबाइल": val["Mobile"], "बकाया राशि": dues})
            
            summary_df = pd.DataFrame(summary)
            
            if not summary_df.empty:
                st.error(f"💸 कुल मार्केट बकाया: ₹{summary_df['बकाया राशि'].sum()}")
                
                # टेबल में दिखाने के लिए
                for index, row in summary_df.iterrows():
                    col1, col2, col3 = st.columns([2, 1, 2])
                    col1.write(f"**{row['रिटेलर']}**")
                    col2.write(f"₹{row['बकाया राशि']}")
                    
                    # 📩 व्हाट्सएप मैसेज ड्राफ्ट
                    msg = (
                        f"डियर पार्टनर,\n"
                        f"आज तक का आपका बकाया (DUSE) ₹{row['बकाया राशि']} है।\n"
                        f"यह DUSE JIO PHONE या Etop Balance का हो सकता है। आपसे अनुरोध है कि अपना बकाया आज ही कैश या ऑनलाइन पेमेंट कर दें।\n\n"
                        f"नोट: ज्यादा जानकारी के लिए कॉल करें।\n"
                        f"Regards,\nSANDHYA ENTERPRISES\nAvdhesh Kumar\n7479584179"
                    )
                    wa_link = f"https://wa.me/91{row['मोबाइल']}?text={urllib.parse.quote(msg)}"
                    col3.markdown(f"[📲 रिमाइंडर भेजें]({wa_link})")
                    st.divider()
            else:
                st.success("कोई बकाया नहीं है!")
        except:
            st.error("डेटा लोड नहीं हो पाया।")
