import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
from streamlit_gsheets import GSheetsConnection

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

# आपकी नई गूगल शीट का लिंक
sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"

# डेटाबेस से रिटेलर्स लाने का फंक्शन
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
        st.error(f"❌ स्टॉक लोड नहीं हुआ: {e}")

# ---------------------------------------------------------
# 2. नया रिटेलर जोड़ें (अब Error 400 नहीं आएगा)
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
                    # डेटा पढ़ना और खाली लाइनें हटाना
                    df = conn.read(spreadsheet=sheet_url, worksheet="Retailers")
                    df = df.dropna(how="all") 
                    
                    new_row = pd.DataFrame([{
                        "Retailer Name": str(r_name).strip().upper(),
                        "Mobile Number": str(r_mobile).strip(),
                        "PRM ID": str(r_prm).strip(),
                        "Location": str(r_loc).strip().upper(),
                        "Date Added": datetime.now().strftime("%d-%m-%Y")
                    }])
                    
                    if not df.empty:
                        updated_df = pd.concat([df, new_row], ignore_index=True)
                    else:
                        updated_df = new_row
                        
                    updated_df = updated_df.fillna("").astype(str)
                    conn.update(spreadsheet=sheet_url, worksheet="Retailers", data=updated_df)
                    
                    st.success(f"✅ रिटेलर {r_name} सफलतापूर्वक सेव हो गया!")
                    st.balloons()
                    st.cache_data.clear()
                except Exception as e:
                    st.error("❌ एरर: कृपया सुनिश्चित करें कि नई शीट के 'Retailers' टैब में ऊपर हेडिंग लिखी हुई हैं।")
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
            st.error("कृपया लिस्ट में से कोई रिटेलर चुनें! (अगर लिस्ट नहीं आ रही है, तो पहले नया रिटेलर जोड़ें)")
        else:
            try:
                r_name = retailers_data[t_prm]["Name"]
                r_mob = retailers_data[t_prm]["Mobile"]
                
                amt_out = t_amount if t_type != "पेमेंट (Payment Received)" else 0
                amt_in = t_amount if t_type == "पेमेंट (Payment Received)" else 0
                
                # 1. Ledger में सेव करना
                ledger_df = conn.read(spreadsheet=sheet_url, worksheet="Ledger")
                ledger_df = ledger_df.dropna(how="all")
                
                new_txn = pd.DataFrame([{
                    "Date": t_date.strftime("%d-%m-%Y"),
                    "Retailer Name": r_name,
                    "Mobile Number": r_mob,
                    "Product/Service": t_type,
                    "Quantity": str(t_qty),
                    "Amount Out (Debit)": str(amt_out),
                    "Amount In (Credit)": str(amt_in),
                    "Balance": "", 
                    "Collected By": fse,
                    "Transaction ID": txn_id
                }])
                
                if not ledger_df.empty:
                    updated_ledger = pd.concat([ledger_df, new_txn], ignore_index=True)
                else:
                    updated_ledger = new_txn
                    
                updated_ledger = updated_ledger.fillna("").astype(str)
                conn.update(spreadsheet=sheet_url, worksheet="Ledger", data=updated_ledger)
                
                # 2. Inventory (स्टॉक) अपडेट करना
                prod_map = {"Jio Phone": "JIO PHONE BHARAT", "SIM Card": "SIM CARD", "Etop Recharge": "Etop BALANCE"}
                if t_type in prod_map:
                    inv_df = conn.read(spreadsheet=sheet_url, worksheet="Inventory")
                    prod_name = prod_map[t_type]
                    deduct_val = t_amount if t_type == "Etop Recharge" else t_qty
                    
                    if deduct_val > 0:
                        for idx, row in inv_df.iterrows():
                            if str(row.get("Product Name", "")).strip() == prod_name:
                                issued = float(row.get("Stock Issued", 0) or 0) + float(deduct_val)
                                inv_df.at[idx, "Stock Issued"] = issued
                                opening = float(row.get("Opening Stock", 0) or 0)
                                added = float(row.get("Stock Added", 0) or 0)
                                inv_df.at[idx, "Current Stock"] = opening + added - issued
                        conn.update(spreadsheet=sheet_url, worksheet="Inventory", data=inv_df.fillna("").astype(str))
                
                st.success(f"✅ {r_name} की एंट्री लेजर में सेव हो गई और स्टॉक अपडेट हो गया!")
                st.balloons()
                st.cache_data.clear()
                
                msg = f"संध्या इंटरप्राइजेज\nतारीख: {t_date.strftime('%d-%m-%Y')}\nरिटेलर: {r_name}\nआइटम: {t_type}\nमात्रा: {t_qty}\nराशि: ₹{t_amount}\nधन्यवाद!"
                msg_encoded = urllib.parse.quote(msg)
                wa_url = f"https://wa.me/91{r_mob}?text={msg_encoded}"
                st.markdown(f"### [🟢 WhatsApp पर रसीद भेजने के लिए यहाँ क्लिक करें]({wa_url})", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ एंट्री सेव नहीं हो पाई। चेक करें कि Ledger टैब में हेडिंग्स सही हैं। एरर: {e}")

# ---------------------------------------------------------
# 4. लेजर (खाता)
elif menu == "📜 लेजर (खाता) देखें":
    st.title("📜 रिटेलर का पूरा खाता")
    st.info("यह आखिरी सेक्शन हम अगले स्टेप में चालू करेंगे!")
