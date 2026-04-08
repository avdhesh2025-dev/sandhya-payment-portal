import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# पेज की सेटिंग
st.set_page_config(page_title="Sandhya ERP System", page_icon="🏢", layout="wide")

# मेनू का डिज़ाइन
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

# गूगल शीट कनेक्शन
sheet_url = "https://docs.google.com/spreadsheets/d/1K3ZeUuZbpB3FmUQlt2ryri_3su4EkLOqzS7uxUQYd1Y/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# डेटाबेस से रिटेलर्स की लिस्ट लाने का फंक्शन
@st.cache_data(ttl=30)
def get_retailer_list():
    try:
        df = conn.read(spreadsheet=sheet_url, worksheet="Retailers")
        df = df.dropna(how="all").fillna("")
        retailer_options = []
        for index, row in df.iterrows():
            prm = str(row.get("PRM ID", "")).split('.')[0]
            name = str(row.get("Retailer Name", ""))
            if prm and name:
                retailer_options.append(f"{prm} - {name}")
        return retailer_options
    except:
        return []

retailer_list = get_retailer_list()
dropdown_options = ["सर्च करने के लिए यहाँ टाइप करें..."] + retailer_list if retailer_list else ["डेटाबेस कनेक्ट नहीं हुआ"]

# साइडबार (मेनू)
st.sidebar.title("📲 संध्या इंटरप्राइजेज")
st.sidebar.markdown("---")
menu = st.sidebar.radio("मेनू चुनें:", ["📊 डैशबोर्ड (स्टॉक)", "➕ नया रिटेलर जोड़ें", "📦 माल / पेमेंट एंट्री", "📜 लेजर (खाता) देखें"])

# ---------------------------------------------------------
# 1. डैशबोर्ड (अब एरर बताएगा)
if menu == "📊 डैशबोर्ड (स्टॉक)":
    st.title("📊 लाइव इन्वेंट्री स्टॉक")
    try:
        # Inventory शीट से डेटा ला रहे हैं
        inv_df = conn.read(spreadsheet=sheet_url, worksheet="Inventory")
        inv_df = inv_df.dropna(how="all").fillna("")
        
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
        st.success("✅ आपकी Google Sheet से लाइव स्टॉक कनेक्ट हो गया है!")
    except Exception as e:
        st.error(f"❌ शीट से जुड़ने में टेक्निकल एरर आ रहा है: {e}")
        st.warning("कृपया चेक करें कि शीट में टैब का नाम बिल्कुल 'Inventory' है और कोई स्पेस नहीं है।")

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
                try:
                    df = conn.read(spreadsheet=sheet_url, worksheet="Retailers")
                    new_row = pd.DataFrame([{
                        "Retailer Name": str(r_name).strip().upper(),
                        "Mobile Number": str(r_mobile).strip(),
                        "PRM ID": str(r_prm).strip(),
                        "Location": str(r_loc).strip().upper(),
                        "Date Added": datetime.now().strftime("%d-%m-%Y")
                    }])
                    updated_df = pd.concat([df, new_row], ignore_index=True).fillna("")
                    updated_df = updated_df.astype(str)
                    
                    conn.update(spreadsheet=sheet_url, worksheet="Retailers", data=updated_df)
                    st.success(f"✅ रिटेलर {r_name} सफलतापूर्वक जुड़ गया है!")
                    st.balloons()
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"सेव नहीं हुआ। एरर: {e}")
            else:
                st.warning("कृपया नाम, मोबाइल नंबर और PRM ID जरूर भरें।")

# ---------------------------------------------------------
# 3. माल इशू / पेमेंट एंट्री
elif menu == "📦 माल / पेमेंट एंट्री":
    st.title("📦 स्टॉक आउट / पेमेंट लें")
    st.info("यह सेक्शन अगले स्टेप में लाइव होगा।")
    
# ---------------------------------------------------------
# 4. लेजर (खाता)
elif menu == "📜 लेजर (खाता) देखें":
    st.title("📜 रिटेलर का पूरा खाता")
    st.info("यह सेक्शन अंतिम स्टेप में लाइव होगा।")
