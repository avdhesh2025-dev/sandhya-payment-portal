import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import urllib.parse
import requests
import time

# 1. Page Configuration (No Sidebar)
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# 💎 Global CSS Design (3D Effects & English UI)
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    .app-header {
        background: linear-gradient(135deg, #0047AB 0%, #00c6ff 100%);
        color: white; padding: 25px 20px; border-radius: 16px;
        text-align: center; margin-top: 10px; margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    .app-header h1 { font-size: 2.4rem; font-weight: 700; margin-bottom: 5px; color: #ffffff;}
    .app-header p { font-size: 1.1rem; font-weight: 300; opacity: 0.8; margin: 0;}
    .urgent-card {
        background-color: #fff5f5; border-left: 5px solid #ff4b4b;
        padding: 15px; border-radius: 10px; margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stDataFrame, .stSelectbox, .stNumberInput, .stTextInput, .stDateInput {
        background-color: white; border-radius: 10px; padding: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* 3D Wobble Effect for Entry Button */
    .wobble-btn > div > button {
        background-color: #ffffff !important; color: #1a1a1a !important; border: none !important; border-radius: 12px !important;
        font-size: 18px !important; font-weight: 700 !important; box-shadow: 0 6px 0 #d1d9e6 !important;
        border-left: 6px solid #007bff !important; transition: 0.2s; height: 60px !important;
    }
    .wobble-btn > div > button:hover { top: -3px; box-shadow: 0 9px 0 #d1d9e6 !important; border-left: 6px solid #00c6ff !important; }
    
    /* 🔥 KHATABOOK STYLE CSS FOR DUES PAGE 🔥 */
    .kb-header-container { display: flex; justify-content: space-between; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px;}
    .kb-box { width: 48%; text-align: center; }
    .kb-box h4 { font-size: 15px; color: #6b7280; margin: 0; font-weight: 500; }
    .kb-give { color: #15803d; font-size: 24px; font-weight: bold; margin: 5px 0 0 0; }
    .kb-get { color: #b91c1c; font-size: 24px; font-weight: bold; margin: 5px 0 0 0; }
    .kb-divider { width: 1px; background: #e5e7eb; }
    /* Streamlit Expander styling to look like Khatabook List */
    .streamlit-expanderHeader { background-color: white; border-radius: 8px; font-size: 16px; font-weight: bold; border: 1px solid #f3f4f6;}
    </style>
""", unsafe_allow_html=True)

# 🛑 CONFIGURATION (Google Sheet URL)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyH_oGxKbNZQj2azNOR0FgkLyAKxBfaAoE0Yo3DHmRpNOFZczJRayBhPd056SGUVWbxWQ/exec"
sheet_id = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
retailers_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Retailers"
inventory_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Inventory"
ledger_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Ledger"

def clean_prm_id(val):
    s = str(val).strip()
    if not s or s.lower() == 'nan': return ""
    try: return str(int(float(s)))
    except: return s.split('.')[0].replace(" ", "").upper()

@st.cache_data(ttl=5)
def load_data():
    try:
        cb = int(time.time())
        ret_df = pd.read_csv(f"{retailers_csv}&cb={cb}").dropna(how="all").fillna("")
        inv_df = pd.read_csv(f"{inventory_csv}&cb={cb}").dropna(how="all").fillna("")
        led_df = pd.read_csv(f"{ledger_csv}&cb={cb}").dropna(how="all").fillna("")
        led_df['DateObj'] = pd.to_datetime(led_df['Date'], format='%d-%m-%Y', errors='coerce')
        return ret_df, inv_df, led_df
    except: return None, None, None

ret_df, inv_df, led_df = load_data()

retailers_data = {}; prm_mapping = {}; dropdown_options = ["Type here to search..."]
if ret_df is not None:
    for _, row in ret_df.iterrows():
        prm = str(row.get("PRM ID", "")).split('.')[0].strip()
        name = str(row.get("Retailer Name", "")).strip()
        mob = str(row.get("Mobile Number", "")).split('.')[0].strip()
        m_prm = clean_prm_id(row.get("PRM ID", ""))
        if m_prm and name:
            retailers_data[f"{prm} - {name}"] = {"Name": name, "Mobile": mob, "PRM": prm}
            prm_mapping[m_prm] = {"Name": name, "Mobile": mob}
            dropdown_options.append(f"{prm} - {name}")

if "current_page" not in st.session_state: st.session_state.current_page = "HOME"

def go_to(page): 
    st.session_state.current_page = page

st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Smart Management System</p></div>', unsafe_allow_html=True)

# --- 🏠 HOME PAGE ---
if st.session_state.current_page == "HOME":
    if st.button("🔄 Refresh System Data", use_container_width=True):
        st.cache_data.clear(); st.rerun()
        
    st.markdown("""<style>
    .stButton > button { height: 75px; background: #ffffff; color: #1e293b; border: 1.5px solid #e2e8f0; border-radius: 14px; font-size: 18px; font-weight: 600; margin-bottom: 15px;}
    .stButton > button:hover { border-color: #3b82f6; color: #3b82f6; box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    </style>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Live Stock", use_container_width=True): go_to("STOCK"); st.rerun()
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD_RETAILER"); st.rerun()
        if st.button("📜 Ledger Report", use_container_width=True): go_to("LEDGER"); st.rerun()
        if st.button("📂 Bulk Entry (Excel)", use_container_width=True): go_to("BULK"); st.rerun()
    with col2:
        if st.button("💰 Today's Collection", use_container_width=True): go_to("COLLECTION"); st.rerun()
        if st.button("📦 Stock / Payment Entry", use_container_width=True): go_to("ENTRY"); st.rerun()
        if st.button("💸 Dues List (Khatabook)", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("🚨 Urgent Recovery", use_container_width=True): go_to("URGENT"); st.rerun()

# --- 📊 1. STOCK ---
elif st.session_state.current_page == "STOCK":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("📊 Live Inventory Stock")
    if inv_df is not None: st.dataframe(inv_df, use_container_width=True, hide_index=True)

# --- 💰 2. TODAY COLLECTION ---
elif st.session_state.current_page == "COLLECTION":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("💸 Today's Collection")
    
    if ret_df is not None and led_df is not None:
        total_market_dues = 0
        today_date_str = date.today().strftime("%d-%m-%Y")
        
        for _, row in ret_df.iterrows():
            name = row["Retailer Name"]
            u_led = led_df[led_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_led['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_led['Amount In (Credit)'], errors='coerce').sum()
            if dues > 0: total_market_dues += dues
                
        # 🟢 SMART FILTER: Only show REAL collections, exclude "Opening Advance"
        today_led = led_df[led_df['Date'] == today_date_str].copy()
        today_led['Amount In (Credit)'] = pd.to_numeric(today_led['Amount In (Credit)'], errors='coerce').fillna(0)
        today_collections = today_led[(today_led['Amount In (Credit)'] > 0) & (~today_led['Product/Service'].astype(str).str.contains('Opening', case=False, na=False))]
        today_collection_sum = today_collections['Amount In (Credit)'].sum()
        
        box1, box2 = st.columns(2)
        box1.error(f"### 🚩 Total Market Dues\n# ₹ {total_market_dues:,.2f}")
        box2.success(f"### 📥 Today's Collection\n# ₹ {today_collection_sum:,.2f}")
        
        # 🟢 Arrow box for details
        if not today_collections.empty:
            with st.expander("🔽 View Today's Collection Details (Kisne kya entry ki)"):
                cols = [c for c in ['Retailer Name', 'Product/Service', 'Amount In (Credit)', 'FSE Name'] if c in today_collections.columns]
                if not cols: cols = today_collections.columns.drop('DateObj', errors='ignore')
                st.dataframe(today_collections[cols], use_container_width=True, hide_index=True)
        else:
            with st.expander("🔽 View Today's Collection Details (Kisne kya entry ki)"):
                st.info("No collections recorded yet for today.")
                
        st.markdown("<hr>", unsafe_allow_html=True)
        
        for _, row in ret_df.iterrows():
            name, mob = row["Retailer Name"], str(row["Mobile Number"]).split('.')[0]
            u_led = led_df[led_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_led['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_led['Amount In (Credit)'], errors='coerce').sum()
            if dues > 0:
                with st.expander(f"👤 {name} | 🚩 Dues: ₹{dues}"):
                    st.markdown(f"### [📞 Call](tel:{mob})")
                    with st.form(f"col_{_}"):
                        p_amt = st.number_input("Amount", min_value=1.0)
                        p_mode = st.selectbox("Payment Mode", ["Cash", "Online"], key=f"mode_{_}")
                        f_n = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"], key=f"fse_{_}")
                        f_p = st.text_input("PIN", type="password", key=f"pin_{_}")
                        if st.form_submit_button("Save"):
                            if (f_n=="Avdhesh Kumar" and f_p=="9557") or (f_n=="Babloo kumar singh" and f_p=="2081"):
                                payload = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": name, "r_mob": mob, "type": f"Collection ({p_mode})", "qty": 0, "amt_out": 0, "amt_in": p_amt, "fse": f_n, "txn_id": "DIRECT"}
                                try: requests.post(WEBHOOK_URL, json=payload)
                                except: pass
                                st.success("✅ Saved!"); st.cache_data.clear()
                            else: st.error("❌ Wrong PIN")

# --- 📦 3. ENTRY PAGE ---
elif st.session_state.current_page == "ENTRY":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("📦 Stock / Payment Entry")
    t_date = st.date_input("Date", date.today())
    t_prm = st.selectbox("Select Retailer*", options=dropdown_options)
    col1, col2 = st.columns(2)
    with col1:
        t_type = st.selectbox("Entry Type", ["Etop Transfer", "Payment Received", "JPB V4", "Sim Card"])
        fse = st.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
        fse_pin = st.text_input("Enter PIN", type="password")
    with col2:
        t_qty, t_amt = 0, 0.0
        p_mode = "" 
        if t_type == "Etop Transfer":
            etop_opt = st.selectbox("Amount ₹", ["5000", "3000", "2000", "1500", "500", "Manual"])
            t_amt = float(etop_opt) if etop_opt != "Manual" else st.number_input("Enter Amount", min_value=1.0)
            
        elif t_type == "Payment Received":
            p_mode = st.selectbox("Payment Mode (Cash/Online)", ["Cash", "Online"])
            t_amt = st.number_input("Enter Amount", min_value=1.0, value=None)
            
        elif t_type == "JPB V4":
            t_qty = st.number_input("Qty", min_value=1); rate = st.number_input("Rate", min_value=1.0)
            t_amt = t_qty * rate
        elif t_type == "Sim Card":
            t_qty = st.number_input("Qty", min_value=1)
        txn_id = st.text_input("Remark / Txn ID")

    st.markdown('<div class="wobble-btn">', unsafe_allow_html=True)
    if st.button("🚀 Save and Send WhatsApp", use_container_width=True):
        if (fse=="Avdhesh Kumar" and fse_pin=="9557") or (fse=="Babloo kumar singh" and fse_pin=="2081"):
            if t_prm != "Type here to search...":
                r_name = retailers_data[t_prm]["Name"]; r_mob = retailers_data[t_prm]["Mobile"]
                final_type = f"{t_type} ({p_mode})" if t_type == "Payment Received" else t_type
                payload = {"action":"add_txn","date":t_date.strftime("%d-%m-%Y"),"r_name":r_name, "r_mob":r_mob, "type":final_type,"qty":t_qty,"amt_out":t_amt if t_type!="Payment Received" else 0,"amt_in":t_amt if t_type=="Payment Received" else 0,"fse":fse,"txn_id":txn_id}
                
                try: requests.post(WEBHOOK_URL, json=payload)
                except: pass
                st.success("✅ Entry Saved Successfully!"); st.cache_data.clear()
                msg = urllib.parse.quote(f"*Sandhya Enterprises*\nRetailer: {r_name}\nItem: {final_type}\nAmount: ₹{t_amt}")
                st.markdown(f"### [🟢 Send WhatsApp](https://wa.me/91{r_mob}?text={msg})")
            else: st.error("Please Select a Retailer")
        else: st.error("❌ Invalid PIN")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ➕ 4. ADD RETAILER ---
elif st.session_state.current_page == "ADD_RETAILER":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("➕ Add Single Retailer")
    with st.form("add_r", clear_on_submit=True):
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            n = st.text_input("Retailer Name*")
            m = st.text_input("Mobile Number*")
        with c_a2:
            p = st.text_input("PRM ID*")
            loc = st.text_input("Location (Address)")
            
        if st.form_submit_button("Save Retailer"):
            if n and p and m:
                payload = {"action":"add_retailer","name":n.upper(),"mobile":m,"prm":p,"location":loc.upper(),"date":date.today().strftime("%d-%m-%Y")}
                try: requests.post(WEBHOOK_URL, json=payload)
                except: pass
                st.success("✅ Retailer Added Successfully!"); st.cache_data.clear()
            else: st.error("❌ Name, Mobile and PRM ID are required")
    
    st.markdown("---")
    st.header("📂 Bulk Retailer Upload")
    up = st.file_uploader("Upload Excel: Name, PRM, Details, DUSE, ADVANCE", type=["xlsx","csv"])
    if up:
        df_up = pd.read_excel(up) if up.name.endswith('xlsx') else pd.read_csv(up)
        df_up.columns = [' '.join(str(col).upper().split()) for col in df_up.columns]
        st.dataframe(df_up, use_container_width=True)
        if st.button("🚀 Process Bulk Upload"):
            prog = st.progress(0)
            for i, row in df_up.iterrows():
                b_name = str(row.get("RETAILER NAME", "")).strip().upper()
                b_prm = clean_prm_id(row.get("PRM ID", "")); b_mob = clean_prm_id(row.get("DETAILS", ""))
                b_dues = float(str(row.get("DUSE", 0)).replace(',','')); b_adv = float(str(row.get("ADVANCE", 0)).replace(',',''))
                if b_name:
                    try: requests.post(WEBHOOK_URL, json={"action":"add_retailer","name":b_name,"mobile":b_mob,"prm":b_prm,"location":"BULK","date":date.today().strftime("%d-%m-%Y")})
                    except: pass
                    time.sleep(0.5)
                    if b_dues > 0: 
                        try: requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":b_name,"r_mob":b_mob,"type":"Opening Dues","qty":0,"amt_out":b_dues,"amt_in":0,"fse":"SYSTEM","txn_id":"OPENING"})
                        except: pass
                        time.sleep(0.5)
                    if b_adv > 0: 
                        try: requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":b_name,"r_mob":b_mob,"type":"Opening Advance","qty":0,"amt_out":0,"amt_in":b_adv,"fse":"SYSTEM","txn_id":"OPENING"})
                        except: pass
                        time.sleep(0.5)
                prog.progress((i+1)/len(df_up))
            st.success("✅ Bulk Upload Success!"); st.cache_data.clear()

# --- 📜 5. LEDGER ---
elif st.session_state.current_page == "LEDGER":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("📜 Ledger Report")
    search = st.selectbox("Select Retailer", options=dropdown_options)
    if search != "Type here to search...":
        r_name = retailers_data[search]["Name"]
        f_led = led_df[led_df['Retailer Name'] == r_name].sort_values(by='DateObj')
        st.dataframe(f_led.drop(columns=['DateObj']), use_container_width=True, hide_index=True)
        st.download_button("📥 Excel Download", f_led.to_csv(index=False).encode('utf-8-sig'), f"{r_name}_Ledger.csv")

# --- 💸 6. DUES REMINDERS (🔥 KHATABOOK INTERACTIVE UI 🔥) ---
elif st.session_state.current_page == "DUES":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    st.header("📖 Khatabook (Touch to Open Ledger)")
    
    total_dene_hain = 0
    total_milenge = 0
    dues_list = []
    adv_list = []
    
    for key, val in retailers_data.items():
        name = val["Name"]
        mob = val["Mobile"]
        u_data = led_df[led_df['Retailer Name'] == name]
        d = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
        c = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
        balance = d - c
        
        if balance > 0: 
            total_milenge += balance
            dues_list.append({"Name": name, "Mobile": mob, "Balance": balance})
        elif balance < 0: 
            total_dene_hain += abs(balance)
            last_credit = u_data[pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce') > 0].tail(1)
            reason = last_credit['Product/Service'].values[0] if not last_credit.empty else "Advance"
            adv_list.append({"Name": name, "Mobile": mob, "Balance": abs(balance), "Reason": reason})
            
    # Khatabook Header Boxes
    st.markdown(f'''
        <div class="kb-header-container">
            <div class="kb-box">
                <h4>Aapko dene hain (Advance)</h4>
                <p class="kb-give">₹ {total_dene_hain:,.0f}</p>
            </div>
            <div class="kb-divider"></div>
            <div class="kb-box">
                <h4>Aapko Milenge (Dues)</h4>
                <p class="kb-get">₹ {total_milenge:,.0f}</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # INTERACTIVE KHATABOOK LISTS
    tab1, tab2 = st.tabs(["🔴 Aapko Milenge (Dues)", "🟢 Aapko Dene Hain (Advance)"])
    
    with tab1:
        if not dues_list: st.success("No dues pending!")
        for item in dues_list:
            # 🟢 Touch to Open Expander (Looks like Khatabook row)
            with st.expander(f"🔴 {item['Name']}  |  ₹ {item['Balance']:,.0f}  |  {item['Mobile']}"):
                msg = urllib.parse.quote(f"Dear Partner, your pending dues are ₹{item['Balance']}. Please clear your payment. Regards, Sandhya Enterprises.")
                st.markdown(f"[📲 Send WhatsApp Reminder](https://wa.me/91{item['Mobile']}?text={msg})")
                
                st.markdown("### 📝 Ledger (Aapne Diye / Aapko Mile)")
                u_data = led_df[led_df['Retailer Name'] == item['Name']].copy()
                show_df = u_data[['Date', 'Product/Service', 'Amount Out (Debit)', 'Amount In (Credit)']].fillna(0)
                show_df.columns = ['Date', 'Item', 'Aapne Diye', 'Aapko Mile']
                st.dataframe(show_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("### ⚡ Add Entry / Collection")
                with st.form(f"kb_form_dues_{item['Name']}", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    t_type = col_a.selectbox("Type", ["Payment Received", "Etop Transfer", "JPB V4", "Sim Card"])
                    p_mode = col_b.selectbox("Mode (If Payment)", ["Cash", "Online"])
                    
                    col_c, col_d = st.columns(2)
                    t_amt = col_c.number_input("Amount ₹", min_value=0.0)
                    t_qty = col_d.number_input("Qty (if JPB/SIM)", min_value=0)
                    
                    col_e, col_f = st.columns(2)
                    f_n = col_e.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
                    f_p = col_f.text_input("PIN", type="password")
                    txn_id = st.text_input("Remark")

                    if st.form_submit_button("Save Entry"):
                        if (f_n=="Avdhesh Kumar" and f_p=="9557") or (f_n=="Babloo kumar singh" and f_p=="2081"):
                            final_type = f"{t_type} ({p_mode})" if t_type == "Payment Received" else t_type
                            amt_out = t_amt if t_type != "Payment Received" else 0
                            amt_in = t_amt if t_type == "Payment Received" else 0
                            
                            payload = {"action":"add_txn", "date":date.today().strftime("%d-%m-%Y"), "r_name":item['Name'], "r_mob":item['Mobile'], "type":final_type, "qty":t_qty, "amt_out":amt_out, "amt_in":amt_in, "fse":f_n, "txn_id":txn_id}
                            try: requests.post(WEBHOOK_URL, json=payload)
                            except: pass
                            st.success("✅ Saved Successfully!"); st.cache_data.clear()
                        else:
                            st.error("❌ Wrong PIN")

    with tab2:
        if not adv_list: st.info("No advance balances.")
        for item in adv_list:
            with st.expander(f"🟢 {item['Name']}  |  Advance: ₹ {item['Balance']:,.0f}  |  Item: {item['Reason']}"):
                st.markdown("### 📝 Ledger (Aapne Diye / Aapko Mile)")
                u_data = led_df[led_df['Retailer Name'] == item['Name']].copy()
                show_df = u_data[['Date', 'Product/Service', 'Amount Out (Debit)', 'Amount In (Credit)']].fillna(0)
                show_df.columns = ['Date', 'Item', 'Aapne Diye', 'Aapko Mile']
                st.dataframe(show_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("### ⚡ Add Entry / Collection")
                with st.form(f"kb_form_adv_{item['Name']}", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    t_type = col_a.selectbox("Type", ["Etop Transfer", "Payment Received", "JPB V4", "Sim Card"])
                    p_mode = col_b.selectbox("Mode (If Payment)", ["Cash", "Online"])
                    
                    col_c, col_d = st.columns(2)
                    t_amt = col_c.number_input("Amount ₹", min_value=0.0)
                    t_qty = col_d.number_input("Qty (if JPB/SIM)", min_value=0)
                    
                    col_e, col_f = st.columns(2)
                    f_n = col_e.selectbox("FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
                    f_p = col_f.text_input("PIN", type="password")
                    txn_id = st.text_input("Remark")

                    if st.form_submit_button("Save Entry"):
                        if (f_n=="Avdhesh Kumar" and f_p=="9557") or (f_n=="Babloo kumar singh" and f_p=="2081"):
                            final_type = f"{t_type} ({p_mode})" if t_type == "Payment Received" else t_type
                            amt_out = t_amt if t_type != "Payment Received" else 0
                            amt_in = t_amt if t_type == "Payment Received" else 0
                            
                            payload = {"action":"add_txn", "date":date.today().strftime("%d-%m-%Y"), "r_name":item['Name'], "r_mob":item['Mobile'], "type":final_type, "qty":t_qty, "amt_out":amt_out, "amt_in":amt_in, "fse":f_n, "txn_id":txn_id}
                            try: requests.post(WEBHOOK_URL, json=payload)
                            except: pass
                            st.success("✅ Saved Successfully!"); st.cache_data.clear()
                        else:
                            st.error("❌ Wrong PIN")

# --- 📂 7. BULK ENTRY (JIO ETOP) ---
elif st.session_state.current_page == "BULK":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("📂 Jio Bulk Etop (Auto-Amount Match)")
    up_j = st.file_uploader("Upload Jio Export Excel", type=["xlsx","csv"])
    if up_j:
        df_j = pd.read_excel(up_j) if up_j.name.endswith('xlsx') else pd.read_csv(up_j)
        df_j.columns = [' '.join(str(col).split()) for col in df_j.columns]
        st.dataframe(df_j, use_container_width=True)
        f_n = st.selectbox("Select FSE", ["Avdhesh Kumar", "Babloo kumar singh"])
        f_p = st.text_input("PIN", type="password")
        if st.button("🚀 Match & Upload Data"):
            if (f_n=="Avdhesh Kumar" and f_p=="9557") or (f_n=="Babloo kumar singh" and f_p=="2081"):
                prog = st.progress(0)
                for i, row in df_j.iterrows():
                    prm = clean_prm_id(row.get("Partner PRM ID", ""))
                    if prm in prm_mapping:
                        amt = float(str(row.get("Transfer Amount", 0)).replace(',',''))
                        
                        if amt == 5150: final_amt = 5000
                        elif amt == 3090: final_amt = 3000
                        elif amt == 2060: final_amt = 2000
                        elif amt == 1545: final_amt = 1500
                        elif amt == 100: final_amt = 100
                        elif amt == 200: final_amt = 200
                        elif amt == 500: final_amt = 500
                        else: final_amt = amt 

                        try: requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":prm_mapping[prm]['Name'],"r_mob":prm_mapping[prm]['Mobile'],"type":"Etop Transfer","qty":0,"amt_out":final_amt,"amt_in":0,"fse":f_n,"txn_id":str(row.get("Order ID",""))})
                        except: pass
                        time.sleep(0.5)
                    prog.progress((i+1)/len(df_j))
                st.success("✅ Done!"); st.cache_data.clear()

# --- 🚨 8. URGENT RECOVERY ---
elif st.session_state.current_page == "URGENT":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to("HOME"); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.error("### 🚨 Urgent Recovery Panel")
    f_n = st.selectbox("Select FSE", ["Babloo kumar singh", "Avdhesh Kumar"])
    f_p = st.text_input("PIN", type="password")
    
    if (f_p=="2081" and f_n=="Babloo kumar singh") or (f_p=="9557" and f_n=="Avdhesh Kumar"):
        now = datetime.now()
        u_list = []
        
        for key, val in retailers_data.items():
            name = val["Name"]
            u_data = led_df[led_df['Retailer Name'] == name]
            total_debit = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
            total_credit = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
            net_dues = total_debit - total_credit
            
            if net_dues > 0:
                is_urgent = False; u_reason = ""; u_date = ""
                for _, row in u_data.iterrows():
                    r_date = row['DateObj']
                    if pd.notnull(r_date):
                        row_text = str(row.values) 
                        if "Etop" in row_text and (now - r_date) > timedelta(hours=24):
                            is_urgent = True; u_reason = "Etop > 24 Hrs"; u_date = row['Date']; break
                        elif "JPB" in row_text and (now - r_date) > timedelta(days=15):
                            is_urgent = True; u_reason = "JPB V4 > 15 Days"; u_date = row['Date']; break
                            
                if is_urgent:
                    u_list.append({"Retailer": name, "Amount": net_dues, "Date": u_date, "Reason": u_reason})
                    st.markdown(f"""<div class="urgent-card"><b>👤 {name}</b> | 💰 ₹{net_dues}<br><b>⚠️ Alert:</b> {u_reason} (Since {u_date})</div>""", unsafe_allow_html=True)
                    with st.form(f"r_{name}"):
                        rsn = st.text_input("Reason for delay")
                        if st.form_submit_button("Submit Reason"):
                            try: requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":name,"type":f"Urgent Alert: {rsn}","txn_id":"URGENT","fse":f_n,"amt_in":0,"amt_out":0,"qty":0})
                            except: pass
                            st.success("✅ Reason Recorded!"); st.cache_data.clear()
                            
        if u_list:
            st.download_button("📥 Excel Download Urgent List", pd.DataFrame(u_list).to_csv(index=False).encode('utf-8-sig'), "Urgent_Recovery.csv")
        else:
            st.success("✅ No Urgent Recovery Dues Found!")
