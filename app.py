import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import urllib.parse
import requests
import time

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# 1. Page Configuration (No Sidebar)
st.set_page_config(page_title="Sandhya ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# SESSION STATES FOR SUCCESS POPUP & SOUND
if "show_success" not in st.session_state:
    st.session_state.show_success = False

# 🟢 PROFESSIONAL SUCCESS POPUP & SOUND 🟢
if st.session_state.show_success:
    st.toast("✅ Transaction Successfully!", icon="✅")
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    st.session_state.show_success = False # Reset immediately so it only plays once

# 💎 Global CSS Design (3D Effects & Mobile Fixes)
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
    
    /* 🔥 KHATABOOK SUPER 3D BOX CSS 🔥 */
    .kb-header-container { display: flex; justify-content: space-around; align-items: center; background: transparent; padding: 10px 0 20px 0; margin-bottom: 15px; }
    .kb-box { width: 44%; text-align: center; background: #ffffff; border: 1px solid #eaeaea; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); padding: 25px 15px; transition: all 0.2s ease; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .kb-divider { width: 1px; height: 80px; background: #e5e7eb; }
    .kb-box:hover { box-shadow: 0 10px 25px rgba(0,0,0,0.2); transform: translateY(-3px); }
    .kb-box h4 { font-size: 14px; color: #6b7280; margin: 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;}
    .kb-give { color: #15803d; font-size: 24px; font-weight: bold; margin: 8px 0 0 0; }
    .kb-get { color: #b91c1c; font-size: 24px; font-weight: bold; margin: 8px 0 0 0; }

    /* 📝 KHATABOOK INSIDE LEDGER CSS */
    .kb-ledger-row { display: flex; justify-content: space-between; border-bottom: 1px solid #f3f4f6; background: white; align-items: center;}
    .kb-ledger-left { width: 40%; padding: 12px 15px; }
    .kb-ledger-mid { width: 30%; text-align: right; color: #b91c1c; font-weight: 700; background: #fff5f5; padding: 12px 15px; font-size: 16px; border-left: 1px solid #f9fafb; height: 100%;}
    .kb-ledger-right { width: 30%; text-align: right; color: #15803d; font-weight: 700; background: white; padding: 12px 15px; font-size: 16px; border-left: 1px solid #f9fafb; height: 100%;}
    .kb-ledger-date { font-size: 12px; color: #6b7280; font-weight: 500; margin-bottom: 2px;}
    .kb-ledger-bal { font-size: 11px; color: #9ca3af; margin-bottom: 4px;}
    .kb-ledger-item { font-size: 15px; color: #1f2937; font-weight: 600; text-transform: capitalize;}
    
    /* 💎 RETAILER LIST 3D CARD CSS 💎 */
    div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 12px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.06) !important; background-color: #ffffff !important; border: 1px solid #eaeaea !important; padding: 5px 10px !important; margin-bottom: 10px !important; transition: 0.3s; }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover { box-shadow: 0 8px 20px rgba(0,0,0,0.12) !important; transform: translateY(-2px); border-color: #0b57d0 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] .stButton > button { height: auto !important; min-height: 20px !important; background: transparent !important; border: none !important; box-shadow: none !important; color: #1f2937 !important; font-size: 16px !important; font-weight: 700 !important; padding: 0 !important; margin: 0 !important; justify-content: flex-start !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] .stButton > button:hover { color: #0b57d0 !important; }
    
    /* 📱 MOBILE GRID FIX (Force Buttons Side-By-Side) */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 10px !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 0% !important;
            min-width: 0 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# 🛑 CONFIGURATION
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

def create_pdf(r_name, r_mob, bal, r_data):
    if not HAS_FPDF: return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 8, "Sandhya Enterprises", ln=True, align='C')
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 6, "Jio Authorities Distributor", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, "Register office: Rosera Rod Meghpatti City Samastipur Bihar 848117", ln=True, align='C')
    pdf.cell(0, 5, "GSTIN: 10GQZPK8313P1Z1  |  PAN: GQZPK8313P", ln=True, align='C')
    pdf.cell(0, 5, "Email: smp.sandhya02@gmail.com  |  Avdhesh Kumar: 7479584179", ln=True, align='C')
    pdf.line(10, 43, 200, 43)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 6, f"Retailer: {r_name}", ln=False)
    pdf.cell(0, 6, f"Mobile: {r_mob}", ln=True, align='R')
    bal_str = f"Total Dues: Rs {bal:,.0f}" if bal >= 0 else f"Advance Balance: Rs {abs(bal):,.0f}"
    pdf.cell(0, 8, bal_str, ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(25, 8, "Date", border=1)
    pdf.cell(75, 8, "Particulars", border=1)
    pdf.cell(30, 8, "Aapne Diye", border=1)
    pdf.cell(30, 8, "Aapko Mile", border=1)
    pdf.cell(30, 8, "Balance", border=1)
    pdf.ln()
    pdf.set_font("Arial", '', 9)
    for r in r_data:
        pdf.cell(25, 8, str(r['date']), border=1)
        pdf.cell(75, 8, str(r['item'])[:40], border=1)
        d_val = f"{r['debit']:,.0f}" if r['debit'] > 0 else "-"
        c_val = f"{r['credit']:,.0f}" if r['credit'] > 0 else "-"
        pdf.cell(30, 8, d_val, border=1)
        pdf.cell(30, 8, c_val, border=1)
        pdf.cell(30, 8, f"{r['bal']:,.0f}", border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

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

# 🟢 FILTER EMPLOYEES OUT FROM RETAILER LIST
valid_ret_df = None
if ret_df is not None:
    if "Location" in ret_df.columns:
        valid_ret_df = ret_df[ret_df['Location'].astype(str).str.upper() != 'EMPLOYEE']
    else:
        valid_ret_df = ret_df

retailers_data = {}; prm_mapping = {}; dropdown_options = ["Type here to search..."]
if valid_ret_df is not None:
    for _, row in valid_ret_df.iterrows():
        prm = str(row.get("PRM ID", "")).split('.')[0].strip()
        name = str(row.get("Retailer Name", "")).strip()
        mob = str(row.get("Mobile Number", "")).split('.')[0].strip()
        m_prm = clean_prm_id(row.get("PRM ID", ""))
        if m_prm and name:
            retailers_data[f"{prm} - {name}"] = {"Name": name, "Mobile": mob, "PRM": prm}
            prm_mapping[m_prm] = {"Name": name, "Mobile": mob}
            dropdown_options.append(f"{prm} - {name}")

# SESSION STATES (Login System)
if "current_page" not in st.session_state: st.session_state.current_page = "LOGIN"
if "role" not in st.session_state: st.session_state.role = None
if "emp_name" not in st.session_state: st.session_state.emp_name = ""
if "emp_pin" not in st.session_state: st.session_state.emp_pin = ""
if "kb_retailer" not in st.session_state: st.session_state.kb_retailer = None
if "kb_action" not in st.session_state: st.session_state.kb_action = None

def get_home(): return "HOME" if st.session_state.get("role") == "Admin" else "EMP_HOME"

def go_to(page): 
    st.session_state.current_page = page
    st.session_state.kb_retailer = None

st.markdown('<div class="app-header"><h1>🏢 Sandhya Enterprises</h1><p>Smart Management System</p></div>', unsafe_allow_html=True)

# 🟢 FSE LIST & PIN VERIFICATION LOGIC
fse_list = ["Avdhesh Kumar", "Babloo kumar singh"]
if ret_df is not None and "Location" in ret_df.columns:
    emp_names = ret_df[ret_df['Location'].astype(str).str.upper() == 'EMPLOYEE']['Retailer Name'].tolist()
    fse_list = list(set(fse_list + emp_names))

if st.session_state.get("role") == "Employee":
    fse_list = [st.session_state.emp_name]

def verify_pin(f_n, f_p):
    if f_n == "Avdhesh Kumar" and f_p == "9557": return True
    if f_n == "Babloo kumar singh" and f_p == "2081": return True
    if st.session_state.get("role") == "Employee" and f_p == st.session_state.emp_pin: return True
    return False

# --- 🔐 0. LOGIN PAGE ---
if st.session_state.current_page == "LOGIN":
    tab1, tab2 = st.tabs(["🔑 Secure Login", "📝 Employee Registration"])
    
    with tab1:
        with st.container(border=True):
            st.markdown("### 🔐 User Login")
            log_mob = st.text_input("Mobile Number (10 Digits)")
            log_pin = st.text_input("4-Digit PIN", type="password")
            if st.button("Login securely", use_container_width=True):
                if log_mob == "7479584179" and log_pin == "9557":
                    st.session_state.role = "Admin"; go_to("HOME"); st.rerun()
                elif log_mob == "7254972081" and log_pin == "2081":
                    st.session_state.role = "Employee"; st.session_state.emp_name = "Babloo kumar singh"; st.session_state.emp_pin = "2081"; go_to("EMP_HOME"); st.rerun()
                else:
                    emp_found = False
                    if ret_df is not None and "Location" in ret_df.columns:
                        emps = ret_df[ret_df['Location'].astype(str).str.upper() == 'EMPLOYEE']
                        for _, r in emps.iterrows():
                            m = str(r.get("Mobile Number", "")).split('.')[0].strip()
                            p = str(r.get("PRM ID", "")).replace("EMP_", "").strip()
                            if log_mob == m and log_pin == p:
                                st.session_state.role = "Employee"
                                st.session_state.emp_name = str(r.get("Retailer Name", ""))
                                st.session_state.emp_pin = p
                                emp_found = True
                                go_to("EMP_HOME"); st.rerun()
                                break
                    if not emp_found: st.error("❌ Invalid Mobile Number or PIN!")

    with tab2:
        with st.container(border=True):
            st.markdown("### 📝 New Employee Reg")
            reg_name = st.text_input("Employee Name*")
            reg_mob = st.text_input("Mobile Number (10 Digits)*")
            reg_pin = st.text_input("Create 4-Digit PIN*", type="password", max_chars=4)
            if st.button("Register & Create ID", use_container_width=True):
                if len(reg_mob) == 10 and len(reg_pin) == 4 and reg_name:
                    payload = {"action":"add_retailer","name":reg_name.upper(),"mobile":reg_mob,"prm":f"EMP_{reg_pin}","location":"EMPLOYEE","date":date.today().strftime("%d-%m-%Y")}
                    try: requests.post(WEBHOOK_URL, json=payload)
                    except: pass
                    st.session_state.show_success = True
                    st.cache_data.clear()
                    st.rerun()
                else: st.error("⚠️ Mobile must be 10 digits and PIN must be 4 digits!")

# --- 🏠 1. ADMIN HOME PAGE ---
elif st.session_state.current_page == "HOME":
    c1, c2 = st.columns([4,1])
    if c1.button("🔄 Refresh System Data"): st.cache_data.clear(); st.rerun()
    if c2.button("🚪 Logout"): st.session_state.role = None; go_to("LOGIN"); st.rerun()
        
    st.markdown("""<style>
    .stButton > button { height: 75px; background: #ffffff; color: #1e293b; border: 1.5px solid #e2e8f0; border-radius: 14px; font-size: 18px; font-weight: 600; margin-bottom: 15px;}
    .stButton > button:hover { border-color: #3b82f6; color: #3b82f6; box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    </style>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Live Stock & FSE Sim", use_container_width=True): go_to("STOCK"); st.rerun()
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD_RETAILER"); st.rerun()
        if st.button("📜 Ledger Report", use_container_width=True): go_to("LEDGER"); st.rerun()
        if st.button("📂 Bulk Entry (Excel)", use_container_width=True): go_to("BULK"); st.rerun()
    with col2:
        if st.button("💰 Today's Collection", use_container_width=True): go_to("COLLECTION"); st.rerun()
        if st.button("📦 Stock / Payment Entry", use_container_width=True): go_to("ENTRY"); st.rerun()
        if st.button("💸 Khatabook (3D)", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("🚨 Urgent Recovery", use_container_width=True): go_to("URGENT"); st.rerun()

# --- 👨‍💼 1.1 EMPLOYEE HOME PAGE ---
elif st.session_state.current_page == "EMP_HOME":
    c1, c2 = st.columns([4, 1])
    c1.success(f"### 👋 Welcome, {st.session_state.emp_name}")
    if c2.button("🚪 Logout"): st.session_state.role = None; go_to("LOGIN"); st.rerun()
    
    st.markdown("""<style>.stButton > button { height: 75px; background: #ffffff; color: #1e293b; border: 1.5px solid #e2e8f0; border-radius: 14px; font-size: 18px; font-weight: 600; margin-bottom: 15px;}</style>""", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💸 Khatabook (3D)", use_container_width=True): go_to("DUES"); st.rerun()
        if st.button("➕ Add Retailer", use_container_width=True): go_to("ADD_RETAILER"); st.rerun()
    with col2:
        if st.button("🚨 Urgent Recovery", use_container_width=True): go_to("URGENT"); st.rerun()
        if st.button("📦 My Sim Card Stock", use_container_width=True): go_to("STOCK"); st.rerun()

# --- 📊 2. STOCK (INVENTORY & FSE SIM BILLING) ---
elif st.session_state.current_page == "STOCK":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to(get_home()); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    
    q_col = None
    if led_df is not None:
        for c in ['Qty', 'Quantity', 'QTY', 'quantity']:
            if c in led_df.columns:
                q_col = c; break
                
    fse_col = None
    if led_df is not None:
        for c in ['FSE Name', 'FSE', 'fse', 'Fse Name']:
            if c in led_df.columns:
                fse_col = c; break

    if st.session_state.role == "Admin":
        st.header("📊 Inventory & FSE Sim Billing")
        tab1, tab2 = st.tabs(["📱 FSE Sim Billing & Stock", "📦 Live Inventory Stock"])
        
        with tab1:
            st.subheader("➕ Bill Sim Cards to FSE")
            with st.container(border=True):
                with st.form("fse_sim_bill_form", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    fse_sel = col_a.selectbox("Select FSE", fse_list)
                    sim_qty = col_b.number_input("Number of SIMs to Bill", min_value=1)
                    admin_pin = st.text_input("Admin PIN", type="password")
                    
                    if st.form_submit_button("Bill SIMs", use_container_width=True):
                        if admin_pin == "9557":
                            payload = {"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":fse_sel,"r_mob":"0000000000","type":"Sim Allocation","qty":sim_qty,"amt_out":0,"amt_in":0,"fse":"Admin","txn_id":"SIM_ALLOC"}
                            try: requests.post(WEBHOOK_URL, json=payload)
                            except: pass
                            st.session_state.show_success = True
                            st.cache_data.clear(); st.rerun()
                        else:
                            st.error("❌ Wrong Admin PIN")
                            
            st.markdown("---")
            st.subheader("📈 FSE Current Sim Stock")
            if q_col and led_df is not None:
                fse_stock_data = []
                for fse_n in fse_list:
                    alloc = pd.to_numeric(led_df[(led_df['Retailer Name'] == fse_n) & (led_df['Product/Service'] == 'Sim Allocation')][q_col], errors='coerce').sum()
                    dist = 0
                    if fse_col:
                        dist = pd.to_numeric(led_df[(led_df[fse_col] == fse_n) & (led_df['Product/Service'] == 'Sim Card')][q_col], errors='coerce').sum()
                    fse_stock_data.append({"FSE Name": fse_n, "Total Billed": int(alloc), "Distributed": int(dist), "Current Balance": int(alloc - dist)})
                st.dataframe(pd.DataFrame(fse_stock_data), use_container_width=True, hide_index=True)

        with tab2:
            if inv_df is not None: st.dataframe(inv_df, use_container_width=True, hide_index=True)

    elif st.session_state.role == "Employee":
        st.header("📦 My Sim Card Stock")
        emp_name = st.session_state.emp_name
        if q_col and led_df is not None:
            alloc = pd.to_numeric(led_df[(led_df['Retailer Name'] == emp_name) & (led_df['Product/Service'] == 'Sim Allocation')][q_col], errors='coerce').sum()
            dist = 0
            if fse_col:
                dist = pd.to_numeric(led_df[(led_df[fse_col] == emp_name) & (led_df['Product/Service'] == 'Sim Card')][q_col], errors='coerce').sum()
            cur_stock = alloc - dist
            
            st.markdown(f'''
            <div style="display: flex; justify-content: center; padding: 20px 0;">
                <div style="width: 100%; background: #ffffff; border: 1px solid #eaeaea; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); padding: 30px; text-align: center;">
                    <h4 style="font-size: 16px; color: #6b7280; margin: 0; font-weight: 600; text-transform: uppercase;">Current SIM Balance</h4>
                    <p style="color: #0b57d0; font-size: 56px; font-weight: bold; margin: 10px 0 0 0;">{int(cur_stock)}</p>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            st.info(f"**Total Received from Admin:** {int(alloc)}  |  **Total Distributed:** {int(dist)}")
            
            if fse_col:
                dist_df = led_df[(led_df[fse_col] == emp_name) & (led_df['Product/Service'] == 'Sim Card')].copy()
                if not dist_df.empty:
                    st.markdown("### 📝 Distributed SIM Details")
                    dist_df['Qty'] = pd.to_numeric(dist_df[q_col], errors='coerce')
                    show_df = dist_df[['Date', 'Retailer Name', 'Qty']]
                    st.dataframe(show_df, use_container_width=True, hide_index=True)
        else:
            st.warning("Quantity data not available yet.")

# --- 💰 3. TODAY COLLECTION ---
elif st.session_state.current_page == "COLLECTION":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to(get_home()); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("💸 Today's Collection")
    
    if valid_ret_df is not None and led_df is not None:
        total_market_dues = 0
        today_date_str = date.today().strftime("%d-%m-%Y")
        
        for _, row in valid_ret_df.iterrows():
            name = row["Retailer Name"]
            u_led = led_df[led_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_led['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_led['Amount In (Credit)'], errors='coerce').sum()
            if dues > 0: total_market_dues += dues
                
        today_led = led_df[led_df['Date'] == today_date_str].copy()
        today_led['Amount In (Credit)'] = pd.to_numeric(today_led['Amount In (Credit)'], errors='coerce').fillna(0)
        today_collections = today_led[(today_led['Amount In (Credit)'] > 0) & (~today_led['Product/Service'].astype(str).str.contains('Opening', case=False, na=False))]
        today_collection_sum = today_collections['Amount In (Credit)'].sum()
        
        box1, box2 = st.columns(2)
        box1.error(f"### 🚩 Total Market Dues\n# ₹ {total_market_dues:,.2f}")
        box2.success(f"### 📥 Today's Collection\n# ₹ {today_collection_sum:,.2f}")
        
        if not today_collections.empty:
            with st.expander("🔽 View Today's Collection Details"):
                cols = [c for c in ['Retailer Name', 'Product/Service', 'Amount In (Credit)', 'FSE Name', 'FSE'] if c in today_collections.columns]
                if not cols: cols = today_collections.columns.drop('DateObj', errors='ignore')
                st.dataframe(today_collections[cols], use_container_width=True, hide_index=True)
                
        st.markdown("<hr>", unsafe_allow_html=True)
        
        for _, row in valid_ret_df.iterrows():
            name, mob = row["Retailer Name"], str(row["Mobile Number"]).split('.')[0]
            u_led = led_df[led_df['Retailer Name'] == name]
            dues = pd.to_numeric(u_led['Amount Out (Debit)'], errors='coerce').sum() - pd.to_numeric(u_led['Amount In (Credit)'], errors='coerce').sum()
            if dues > 0:
                with st.expander(f"👤 {name} | 🚩 Dues: ₹{dues}"):
                    with st.form(f"col_{_}"):
                        p_amt = st.number_input("Amount", min_value=1.0)
                        p_mode = st.selectbox("Payment Mode", ["Cash", "Online"], key=f"mode_{_}")
                        f_n = st.selectbox("FSE", fse_list, key=f"fse_{_}")
                        f_p = st.text_input("PIN", type="password", key=f"pin_{_}")
                        if st.form_submit_button("Save"):
                            if verify_pin(f_n, f_p):
                                payload = {"action": "add_txn", "date": date.today().strftime("%d-%m-%Y"), "r_name": name, "r_mob": mob, "type": f"Collection ({p_mode})", "qty": 0, "amt_out": 0, "amt_in": p_amt, "fse": f_n, "txn_id": "DIRECT"}
                                try: requests.post(WEBHOOK_URL, json=payload)
                                except: pass
                                st.session_state.show_success = True
                                st.cache_data.clear(); st.rerun()
                            else: st.error("❌ Wrong PIN")

# --- 📦 4. ENTRY PAGE ---
elif st.session_state.current_page == "ENTRY":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to(get_home()); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("📦 Stock / Payment Entry")
    t_date = st.date_input("Date", date.today())
    t_prm = st.selectbox("Select Retailer*", options=dropdown_options)
    
    t_type = st.selectbox("Entry Type", ["Etop Transfer", "Payment Received", "JPB V4", "Sim Card"])
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        t_qty, t_amt = 0, 0.0
        p_mode = "" 
        
        with col1:
            fse = st.selectbox("FSE", fse_list)
            fse_pin = st.text_input("Enter PIN", type="password")
            
        with col2:
            if t_type == "Etop Transfer":
                etop_opt = st.selectbox("Amount ₹", ["5000", "3000", "2000", "1500", "500", "Manual"])
                t_amt = float(etop_opt) if etop_opt != "Manual" else st.number_input("Enter Amount", min_value=1.0)
            elif t_type == "Payment Received":
                p_mode = st.selectbox("Payment Mode (Cash/Online)", ["Cash", "Online"])
                t_amt = st.number_input("Enter Amount", min_value=1.0)
            elif t_type == "JPB V4":
                t_amt = st.number_input("Total Amount ₹", min_value=1.0)
                t_qty = st.number_input("Qty", min_value=1)
            elif t_type == "Sim Card":
                t_qty = st.number_input("Qty", min_value=1)
                
        txn_id = st.text_input("Remark / Txn ID")

    st.markdown('<div class="wobble-btn">', unsafe_allow_html=True)
    if st.button("🚀 Save Entry", use_container_width=True):
        if verify_pin(fse, fse_pin):
            if t_prm != "Type here to search...":
                r_name = retailers_data[t_prm]["Name"]; r_mob = retailers_data[t_prm]["Mobile"]
                final_type = f"{t_type} ({p_mode})" if t_type == "Payment Received" else t_type
                payload = {"action":"add_txn","date":t_date.strftime("%d-%m-%Y"),"r_name":r_name, "r_mob":r_mob, "type":final_type,"qty":t_qty,"amt_out":t_amt if t_type!="Payment Received" else 0,"amt_in":t_amt if t_type=="Payment Received" else 0,"fse":fse,"txn_id":txn_id}
                try: requests.post(WEBHOOK_URL, json=payload)
                except: pass
                st.session_state.show_success = True
                st.cache_data.clear(); st.rerun()
            else: st.error("Please Select a Retailer")
        else: st.error("❌ Invalid PIN")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ➕ 5. ADD RETAILER ---
elif st.session_state.current_page == "ADD_RETAILER":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to(get_home()); st.rerun()
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
                st.session_state.show_success = True
                st.cache_data.clear(); st.rerun()
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

# --- 📜 6. LEDGER ---
elif st.session_state.current_page == "LEDGER":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to(get_home()); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.header("📜 Ledger Report")
    search = st.selectbox("Select Retailer", options=dropdown_options)
    if search != "Type here to search...":
        r_name = retailers_data[search]["Name"]
        f_led = led_df[led_df['Retailer Name'] == r_name].sort_values(by='DateObj')
        st.dataframe(f_led.drop(columns=['DateObj']), use_container_width=True, hide_index=True)
        st.download_button("📥 Excel Download", f_led.to_csv(index=False).encode('utf-8-sig'), f"{r_name}_Ledger.csv")

# --- 💸 7. DUES REMINDERS (🔥 KHATABOOK UI - UNIFIED LIST) ---
elif st.session_state.current_page == "DUES":
    
    # CASE 1: SHOW UNIFIED LIST OF ALL RETAILERS
    if st.session_state.kb_retailer is None:
        c1, c2 = st.columns(2)
        if c1.button("🔙 Back Menu", use_container_width=True): go_to(get_home()); st.rerun()
        if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
        
        st.header("📖 Khatabook")
        
        total_dene_hain = 0; total_milenge = 0
        all_retailers_list = []
        
        for key, val in retailers_data.items():
            name = val["Name"]; mob = val["Mobile"]
            u_data = led_df[led_df['Retailer Name'] == name]
            d = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
            c = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
            balance = d - c
            
            if balance > 0: total_milenge += balance
            elif balance < 0: total_dene_hain += abs(balance)
                
            all_retailers_list.append({"Name": name, "Mobile": mob, "Balance": balance})
            
        def sort_retailers(r):
            if r['Balance'] > 0: return (0, -r['Balance']) 
            elif r['Balance'] < 0: return (1, r['Balance']) 
            else: return (2, 0) 
            
        all_retailers_list.sort(key=sort_retailers)
                
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
        
        search_opts = ["All Customers"] + [f"{r['Name']} - {r['Mobile']}" for r in all_retailers_list]
        selected_cust = st.selectbox("🔍 Customer search karein (Type Name or Mobile)...", search_opts)
        
        if selected_cust != "All Customers":
            sel_name = selected_cust.split(" - ")[0]
            filtered_list = [r for r in all_retailers_list if r['Name'] == sel_name]
        else:
            filtered_list = all_retailers_list
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if not filtered_list: st.info("No matching customers found.")
        
        for item in filtered_list:
            bal = item['Balance']
            if bal > 0: color = "#b91c1c"; status = "Pending"; amt_str = f"₹ {bal:,.0f}"
            elif bal < 0: color = "#15803d"; status = "Advance"; amt_str = f"₹ {abs(bal):,.0f}"
            else: color = "#4b5563"; status = "Settled"; amt_str = "₹ 0"
                
            with st.container(border=True):
                col1, col2 = st.columns([3, 2])
                with col1: 
                    if st.button(f"{item['Name']}", key=f"btn_all_{item['Name']}_{item['Mobile']}", use_container_width=True):
                        st.session_state.kb_retailer = item['Name']
                        st.rerun()
                    st.markdown(f"<div style='font-size:13px;color:#6b7280;margin-top:-5px;'>{item['Mobile']} • {status}</div>", unsafe_allow_html=True)
                with col2: 
                    if bal > 0:
                        msg = urllib.parse.quote(f"Dear Partner, your pending dues are ₹{bal}. Please clear your payment. Regards, Sandhya Enterprises.")
                        st.markdown(f"<div style='text-align:right;'><div style='font-size:18px;font-weight:bold;color:{color};'>{amt_str}</div><a href='https://wa.me/91{item['Mobile']}?text={msg}' target='_blank' style='font-size:12px;color:#2563eb;text-decoration:none;font-weight:bold;'>REMIND KARAYEIN ></a></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='text-align:right; margin-top:5px;'><div style='font-size:18px;font-weight:bold;color:{color};'>{amt_str}</div></div>", unsafe_allow_html=True)

    # CASE 2: SHOW SINGLE RETAILER KHATABOOK LEDGER VIEW
    else:
        kb_name = st.session_state.kb_retailer
        kb_mob = ""
        for k, v in retailers_data.items():
            if v["Name"] == kb_name: kb_mob = v["Mobile"]; break
            
        c1, c2 = st.columns([1, 4])
        if c1.button("⬅️ Back", use_container_width=True):
            st.session_state.kb_retailer = None
            st.session_state.kb_action = None
            st.rerun()
            
        st.markdown(f"""
        <div style="background-color: #0b57d0; padding: 15px; border-radius: 8px; display: flex; align-items: center; margin-bottom: 15px; margin-top: 15px;">
            <div style="width: 45px; height: 45px; border-radius: 50%; background-color: white; color: #0b57d0; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 20px; margin-right: 15px;">{kb_name[:2].upper()}</div>
            <div>
                <div style="color: white; font-size: 19px; font-weight: bold; margin-bottom:2px;">{kb_name}</div>
                <div style="color: rgba(255,255,255,0.8); font-size: 13px;">{kb_mob}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        u_data = led_df[led_df['Retailer Name'] == kb_name].copy()
        d = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
        c = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
        balance = d - c
        
        if balance > 0:
            st.markdown(f'''
            <div style="display: flex; justify-content: center; padding: 10px 0; margin-bottom: 15px;">
                <div style="width: 90%; background: #ffffff; border: 1px solid #eaeaea; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); padding: 25px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <h4 style="font-size: 14px; color: #6b7280; margin: 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Aapko Milenge</h4>
                    <p style="color: #b91c1c; font-size: 28px; font-weight: bold; margin: 8px 0 0 0;">₹ {balance:,.0f}</p>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        elif balance < 0:
            st.markdown(f'''
            <div style="display: flex; justify-content: center; padding: 10px 0; margin-bottom: 15px;">
                <div style="width: 90%; background: #ffffff; border: 1px solid #eaeaea; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); padding: 25px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <h4 style="font-size: 14px; color: #6b7280; margin: 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Aapko Dene Hain</h4>
                    <p style="color: #15803d; font-size: 28px; font-weight: bold; margin: 8px 0 0 0;">₹ {abs(balance):,.0f}</p>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
             st.markdown(f'''
            <div style="display: flex; justify-content: center; padding: 10px 0; margin-bottom: 15px;">
                <div style="width: 90%; background: #ffffff; border: 1px solid #eaeaea; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); padding: 25px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <h4 style="font-size: 14px; color: #6b7280; margin: 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Settled Balance</h4>
                    <p style="color: #4b5563; font-size: 28px; font-weight: bold; margin: 8px 0 0 0;">₹ 0</p>
                </div>
            </div>
            ''', unsafe_allow_html=True)           
            
        u_data = u_data.sort_values(by='DateObj', ascending=True) 
        running_bal = 0
        
        # 🟢 HTML FORMATTING FIXED FOR NO INDENTATION (Error-Free)
        ledger_html = "<div style='background:white; border-radius:8px; border:1px solid #e5e7eb; overflow:hidden; margin-bottom:15px; margin-top:10px;'>"
        ledger_html += "<div style='display:flex; font-size:11px; color:#6b7280; font-weight:600; padding:10px 15px; background:#f9fafb; border-bottom:1px solid #e5e7eb;'><div style='width:40%'>ENTRIES</div><div style='width:30%; text-align:right'>AAPNE DIYE</div><div style='width:30%; text-align:right'>AAPKO MILE</div></div>"
        
        rows_data = []
        for _, row in u_data.iterrows():
            debit = pd.to_numeric(row['Amount Out (Debit)'], errors='coerce')
            credit = pd.to_numeric(row['Amount In (Credit)'], errors='coerce')
            if pd.isna(debit): debit = 0
            if pd.isna(credit): credit = 0
            running_bal += (debit - credit)
            rows_data.append({'date': row['Date'], 'item': row['Product/Service'], 'debit': debit, 'credit': credit, 'bal': running_bal})
            
        for r in reversed(rows_data):
            d_str = f"₹ {r['debit']:,.0f}" if r['debit'] > 0 else ""
            c_str = f"₹ {r['credit']:,.0f}" if r['credit'] > 0 else ""
            # NO INDENTATION HERE TO AVOID MARKDOWN CODE BLOCK RENDERING
            ledger_html += f"<div class='kb-ledger-row'><div class='kb-ledger-left'><div class='kb-ledger-date'>{r['date']}</div><div class='kb-ledger-bal'>Bal. ₹ {r['bal']:,.0f}</div><div class='kb-ledger-item'>{r['item']}</div></div><div class='kb-ledger-mid'>{d_str}</div><div class='kb-ledger-right'>{c_str}</div></div>"
            
        ledger_html += "</div>"
        
        stmt_text = f"*Sandhya Enterprises - Ledger*\n👤 Retailer: {kb_name}\n"
        if balance > 0: stmt_text += f"💰 Total Dues: ₹{balance:,.0f}\n\n*Recent Entries:*\n"
        elif balance < 0: stmt_text += f"💰 Total Advance: ₹{abs(balance):,.0f}\n\n*Recent Entries:*\n"
        else: stmt_text += f"💰 Settled Balance: ₹0\n\n*Recent Entries:*\n"
        
        for r in rows_data[-5:]:
            act_str = f" Diye: {r['debit']:.0f}" if r['debit'] > 0 else (f" Mile: {r['credit']:.0f}" if r['credit'] > 0 else "")
            stmt_text += f"• {r['date']} | {r['item']} |{act_str} | Bal: ₹{r['bal']:,.0f}\n"
            
        stmt_text += "\nPlease clear your dues. Regards, Sandhya Enterprises."
        wa_link = f"https://wa.me/91{kb_mob}?text={urllib.parse.quote(stmt_text)}"
        
        st.markdown(f"<div style='text-align:center; margin-bottom:15px;'><a href='{wa_link}' target='_blank' style='display:inline-block; padding:10px 20px; background-color:#eff6ff; color:#0b57d0; font-weight:700; border-radius:20px; text-decoration:none; border:1px solid #bfdbfe; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>📲 Send WhatsApp Reminder (With Ledger)</a></div>", unsafe_allow_html=True)
        
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            if not HAS_FPDF:
                st.warning("⚠️ PDF banane ke liye requirements.txt me `fpdf` add karein.")
            else:
                pdf_bytes = create_pdf(kb_name, kb_mob, balance, rows_data)
                if pdf_bytes:
                    st.download_button(label="📄 Download PDF Ledger", data=pdf_bytes, file_name=f"{kb_name}_Ledger.pdf", mime="application/pdf", use_container_width=True)
        with dl_col2:
            st.download_button("📥 Download Excel Ledger", u_data[['Date', 'Product/Service', 'Amount Out (Debit)', 'Amount In (Credit)']].to_csv(index=False).encode('utf-8-sig'), f"{kb_name}_Ledger.csv", use_container_width=True)

        # RENDER HTML SAFELY
        st.markdown(ledger_html, unsafe_allow_html=True)
        
        b1, b2 = st.columns(2)
        if b1.button("🔴 AAPNE DIYE", use_container_width=True): st.session_state.kb_action = "diye"; st.rerun()
        if b2.button("🟢 AAPKO MILE", use_container_width=True): st.session_state.kb_action = "mile"; st.rerun()
            
        if st.session_state.kb_action == "diye":
            with st.form(f"diye_form", clear_on_submit=True):
                st.error("🔴 Aapne Diye (Stock Out)")
                t_type = st.selectbox("Type", ["Etop Transfer", "JPB V4", "Sim Card"], key="type_kb_diye")
                col_c, col_d = st.columns(2)
                t_qty, t_amt = 0, 0.0
                
                with col_c:
                    if t_type == "Etop Transfer":
                        etop_opt = st.selectbox("Amount ₹", ["5000", "3000", "2000", "1500", "500", "Manual"], key="kb_etop")
                        t_amt = float(etop_opt) if etop_opt != "Manual" else st.number_input("Enter Amount", min_value=1.0, key="kb_amt")
                    elif t_type == "JPB V4":
                        t_amt = st.number_input("Amount ₹", min_value=0.0)
                with col_d:
                    if t_type == "Sim Card" or t_type == "JPB V4":
                        t_qty = st.number_input("Qty", min_value=1)
                        
                col_e, col_f = st.columns(2)
                f_n = col_e.selectbox("FSE", fse_list)
                f_p = col_f.text_input("PIN", type="password")
                txn_id = st.text_input("Remark")
                
                if st.form_submit_button("Save Entry", use_container_width=True):
                    if verify_pin(f_n, f_p):
                        try: requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":kb_name,"r_mob":kb_mob,"type":t_type,"qty":t_qty,"amt_out":t_amt,"amt_in":0,"fse":f_n,"txn_id":txn_id})
                        except: pass
                        st.session_state.show_success = True
                        st.cache_data.clear(); st.session_state.kb_action = None; st.rerun()
                    else: st.error("❌ Wrong PIN")
                    
        elif st.session_state.kb_action == "mile":
            with st.form(f"mile_form", clear_on_submit=True):
                st.success("🟢 Aapko Mile (Payment Received)")
                p_mode = st.selectbox("Mode (Cash/Online)", ["Cash", "Online"])
                t_amt = st.number_input("Amount ₹", min_value=1.0)
                col_e, col_f = st.columns(2)
                f_n = col_e.selectbox("FSE", fse_list)
                f_p = col_f.text_input("PIN", type="password")
                txn_id = st.text_input("Remark")
                
                if st.form_submit_button("Save Entry", use_container_width=True):
                    if verify_pin(f_n, f_p):
                        try: requests.post(WEBHOOK_URL, json={"action":"add_txn","date":date.today().strftime("%d-%m-%Y"),"r_name":kb_name,"r_mob":kb_mob,"type":f"Payment Received ({p_mode})","qty":0,"amt_out":0,"amt_in":t_amt,"fse":f_n,"txn_id":txn_id})
                        except: pass
                        st.session_state.show_success = True
                        st.cache_data.clear(); st.session_state.kb_action = None; st.rerun()
                    else: st.error("❌ Wrong PIN")

# --- 📂 8. BULK ENTRY (JIO ETOP) ---
elif st.session_state.current_page == "BULK":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to(get_home()); st.rerun()
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
            if verify_pin(f_n, f_p):
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

# --- 🚨 9. URGENT RECOVERY (SMART FIX) ---
elif st.session_state.current_page == "URGENT":
    c1, c2 = st.columns(2)
    if c1.button("🔙 Back Menu", use_container_width=True): go_to(get_home()); st.rerun()
    if c2.button("🔄 Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.error("### 🚨 Urgent Recovery Panel")
    f_n = st.selectbox("Select FSE", fse_list)
    f_p = st.text_input("PIN", type="password")
    
    if verify_pin(f_n, f_p):
        now = datetime.now()
        u_list = []
        
        for key, val in retailers_data.items():
            name = val["Name"]
            u_data = led_df[led_df['Retailer Name'] == name]
            total_debit = pd.to_numeric(u_data['Amount Out (Debit)'], errors='coerce').sum()
            total_credit = pd.to_numeric(u_data['Amount In (Credit)'], errors='coerce').sum()
            net_dues = total_debit - total_credit
            
            if net_dues > 0:
                is_urgent = False
                u_reason = ""
                u_date = ""
                
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
                            st.session_state.show_success = True
                            st.cache_data.clear(); st.rerun()
                            
        if u_list:
            st.download_button("📥 Excel Download Urgent List", pd.DataFrame(u_list).to_csv(index=False).encode('utf-8-sig'), "Urgent_Recovery.csv")
        else:
            st.success("✅ No Urgent Recovery Dues Found!")
