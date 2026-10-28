import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIG & ULTRA-PRO 3D GLASSMORPHISM STYLES (FROM YOUR DESIGN)
# ==========================================
st.set_page_config(page_title="Jio Distributor SaaS", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
/* 🌟 ULTRA-PRO ANIMATED MESH GRADIENT BACKGROUND */
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], [data-testid="stMain"] { 
    background: linear-gradient(-45deg, #e0e7ff, #f8fafc, #dbeafe, #f1f5f9, #ede9fe) !important;
    color: #0f172a;
    font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
}
/* 🌟 GLOBAL TYPOGRAPHY */
.stMarkdown p, .stMetric label, [data-testid="stText"], label, .stDataFrame td, .stDataFrame th {
    font-size: 16px !important;
    font-weight: 800 !important; 
    color: #0f172a; 
}
h1, h2, h3, h4, h5 { font-weight: 900 !important; letter-spacing: 0.5px; }

/* 🌟 LIQUID TRANSPARENT INPUT FIELDS */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stDateInput input {
    background: rgba(255, 255, 255, 0.94) !important;
    border-radius: 12px !important;
    border: 2px solid rgba(148, 163, 184, 0.45) !important;
    box-shadow: inset 2px 2px 6px rgba(0,0,0,0.04) !important;
    color: #0f172a !important;
    font-weight: 900 !important;
    font-size: 16px !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
    background: #ffffff !important;
    border-color: #2563eb !important;
    box-shadow: 0 0 10px rgba(37, 99, 235, 0.25) !important;
}

/* 🌟 3D HERO WELCOME BANNER */
.welcome-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%) !important;
    padding: 24px 22px !important;
    border-radius: 20px !important;
    border: 2px solid rgba(255, 255, 255, 0.5) !important;
    border-bottom: 7px solid #090d16 !important;
    box-shadow: 0 14px 28px rgba(30, 58, 138, 0.28), inset 0 4px 15px rgba(255,255,255,0.25) !important;
    text-align: center !important;
    margin-bottom: 18px !important;
}
.welcome-text { color: #ffffff !important; font-size: 30px !important; font-weight: 900 !important; text-shadow: 2px 3px 0px #0f172a, 4px 6px 12px rgba(0,0,0,0.5) !important; margin: 0 0 8px 0 !important; }
.welcome-subtext { color: #93c5fd !important; font-size: 15px !important; font-weight: 800 !important; margin: 0 !important; }

/* 🌟 SECTION HEADERS */
.section-3d-header {
    background: linear-gradient(145deg, #0f172a, #1e3a8a, #2563eb);
    padding: 14px 18px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-bottom: 5px solid #090d16;
    color: #ffffff !important;
    font-weight: 900 !important;
    font-size: 20px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(30, 58, 138, 0.3);
    margin-bottom: 16px;
    text-transform: uppercase;
}

/* 🌟 STANDARD GLASS CARDS (For Forms) */
.pos-box, [data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.82) !important;
    border: 1px solid rgba(255, 255, 255, 0.95) !important;
    border-bottom: 5px solid rgba(148, 163, 184, 0.35) !important;
    border-radius: 18px !important;
    padding: 18px !important;
    box-shadow: 0 8px 20px rgba(0,0,0,0.05) !important;
    margin-bottom: 16px !important;
}

/* 🌟 PREMIUM 3D METRIC CARDS */
.glass-metric {
    text-align: center;
    padding: 18px 12px;
    background: rgba(255, 255, 255, 0.85) !important;
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.95);
    border-bottom: 6px solid #cbd5e1;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06), inset 0 2px 5px rgba(255,255,255,0.9);
    margin-bottom: 14px;
}
.glass-metric h4 { margin: 0; font-weight: 900 !important; font-size: 14px !important; text-transform: uppercase; }
.glass-metric h2 { margin: 8px 0 0 0; font-weight: 900 !important; font-size: 28px !important; }

/* 🌟 TRANSPARENT GLASS BUTTONS */
.stButton button, [data-testid="stFormSubmitButton"] button {
    width: 100% !important;
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(148, 163, 184, 0.5) !important;
    border-bottom: 5px solid rgba(100, 116, 139, 0.65) !important;
    color: #0f172a !important;
    font-weight: 900 !important;
    font-size: 16px !important;
    padding: 12px 10px !important;
    border-radius: 14px !important;
    box-shadow: 0 5px 12px rgba(0,0,0,0.05) !important;
}
button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {
    background: linear-gradient(90deg, #1e3a8a, #2563eb, #3b82f6) !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    border-bottom: 5px solid #0f172a !important;
    color: white !important;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.35) !important;
}

/* 📊 DATA GRID TRANSPARENT */
[data-testid="stDataFrame"] {
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 2px solid #94a3b8 !important;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06) !important;
    background: rgba(255, 255, 255, 0.95) !important;
}
</style>""", unsafe_allow_html=True)


# ==========================================
# 2. DATABASE SETUP (Multi-Tenant SaaS)
# ==========================================
conn = sqlite3.connect('jio_saas_erp.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, valid_until DATE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ledger (id INTEGER PRIMARY KEY, dist_id INTEGER, retailer_name TEXT, phone TEXT, given REAL, received REAL, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS commission_settings (dist_id INTEGER PRIMARY KEY, airfiber REAL, idu REAL, stb REAL, odu REAL)''')
    
    # Create Super Admin
    c.execute("SELECT * FROM users WHERE role='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role, valid_until) VALUES ('avdhesh_admin', 'admin123', 'admin', '2099-12-31')")
    conn.commit()

init_db()

# ==========================================
# 3. AUTHENTICATION SYSTEM
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.markdown('<div class="welcome-box"><h2 class="welcome-text">🔐 SAAS LOGIN</h2><p class="welcome-subtext">Sandhya Enterprises Tech Network</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="pos-box">', unsafe_allow_html=True)
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    
    if st.button("🚀 SECURE LOGIN", type="primary"):
        c.execute("SELECT id, role, valid_until FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user:
            valid_until = datetime.strptime(user[2], '%Y-%m-%d').date()
            if valid_until >= datetime.now().date() or user[1] == 'admin':
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user[0]
                st.session_state['role'] = user[1]
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("🚫 Your subscription has expired! Please contact Avdhesh Sir.")
        else:
            st.error("❌ Invalid Credentials")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. SUPER ADMIN PANEL (Avdhesh Control)
# ==========================================
def admin_panel():
    st.markdown('<div class="section-3d-header">⚙️ SUPER ADMIN DASHBOARD (AVDHESH)</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="pos-box">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#1e3a8a; margin-top:0;'>➕ Add / Renew Distributor App</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    d_name = c1.text_input("Distributor Username (e.g. dist_rajesh)")
    d_pass = c2.text_input("Password")
    days = c3.number_input("Validity (Days)", min_value=1, value=30)
    
    if st.button("💾 Create / Renew Account", type="primary"):
        valid_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        c.execute("SELECT id FROM users WHERE username=?", (d_name,))
        if c.fetchone():
            c.execute("UPDATE users SET valid_until=?, password=? WHERE username=?", (valid_date, d_pass, d_name))
            st.success(f"✅ Renewed {d_name} till {valid_date}")
        else:
            c.execute("INSERT INTO users (username, password, role, valid_until) VALUES (?, ?, 'distributor', ?)", (d_name, d_pass, valid_date))
            st.success(f"✅ Created new app for {d_name}, valid till {valid_date}")
        conn.commit()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="pos-box">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#0f172a; margin-top:0;'>👥 Active Distributors List</h3>", unsafe_allow_html=True)
    df_users = pd.read_sql_query("SELECT id, username, valid_until FROM users WHERE role='distributor'", conn)
    st.dataframe(df_users, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. DISTRIBUTOR PANEL (Client SaaS App)
# ==========================================
def distributor_panel():
    st.sidebar.markdown(f"### 🏢 Welcome, {st.session_state['username']}")
    menu = st.sidebar.radio("Navigate Module", ["1. Auto-refill Ledger", "2. AirFiber & Recovery Setup"])
    dist_id = st.session_state['user_id']
    
    st.markdown(f'<div class="welcome-box"><h2 class="welcome-text">📱 DISTRIBUTOR ERP</h2><p class="welcome-subtext">{st.session_state["username"].upper()} DASHBOARD</p></div>', unsafe_allow_html=True)

    # --- Module 1: Auto-refill Ledger ---
    if menu == "1. Auto-refill Ledger":
        st.markdown('<div class="section-3d-header">📒 AUTO-REFILL & RETAILER LEDGER</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="pos-box">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        r_name = c1.text_input("👤 Retailer Name (e.g., Rajesh Mobile)")
        r_phone = c2.text_input("📱 WhatsApp Number")
        
        c3, c4 = st.columns(2)
        given = c3.number_input("💸 Auto-refill Given (Rs)", min_value=0.0)
        received = c4.number_input("💰 Cash/Account Received (Rs)", min_value=0.0)
        
        if st.button("🚀 SAVE LEDGER ENTRY", type="primary"):
            date_now = datetime.now().strftime('%Y-%m-%d %H:%M')
            c.execute("INSERT INTO ledger (dist_id, retailer_name, phone, given, received, date) VALUES (?, ?, ?, ?, ?, ?)", 
                      (dist_id, r_name, r_phone, given, received, date_now))
            conn.commit()
            st.success("✅ Entry Saved Successfully!")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="pos-box">', unsafe_allow_html=True)
        st.markdown("### 📊 Retailer Due Reports")
        df_ledger = pd.read_sql_query(f"SELECT retailer_name, phone, given, received, (given - received) as due_balance, date FROM ledger WHERE dist_id={dist_id}", conn)
        st.dataframe(df_ledger, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Module 2: AirFiber & Recovery Commission ---
    elif menu == "2. AirFiber & Recovery Setup":
        st.markdown('<div class="section-3d-header">🔧 FSE RECOVERY & COMMISSION LOGIC</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="pos-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#1e3a8a; margin-top:0;'>⚙️ Set Your Staff Commission Rates</h3>", unsafe_allow_html=True)
        c.execute(f"SELECT airfiber, idu, stb, odu FROM commission_settings WHERE dist_id={dist_id}")
        rates = c.fetchone() or (0.0, 0.0, 0.0, 0.0)
        
        r1, r2, r3, r4 = st.columns(4)
        af_rate = r1.number_input("AirFiber (₹)", value=rates[0])
        idu_rate = r2.number_input("IDU (₹)", value=rates[1])
        stb_rate = r3.number_input("STB (₹)", value=rates[2])
        odu_rate = r4.number_input("ODU (₹)", value=rates[3])
        
        if st.button("💾 UPDATE RATES", type="primary"):
            c.execute("REPLACE INTO commission_settings (dist_id, airfiber, idu, stb, odu) VALUES (?, ?, ?, ?, ?)", 
                      (dist_id, af_rate, idu_rate, stb_rate, odu_rate))
            conn.commit()
            st.success("✅ Rates Updated!")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="pos-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#0f172a; margin-top:0;'>📝 Daily FSE Payment Calculator</h3>", unsafe_allow_html=True)
        staff_name = st.text_input("👷 Staff Name")
        c5, c6, c7, c8 = st.columns(4)
        af_count = c5.number_input("AirFiber Qty", min_value=0)
        idu_count = c6.number_input("IDU Qty", min_value=0)
        stb_count = c7.number_input("STB Qty", min_value=0)
        odu_count = c8.number_input("ODU Qty", min_value=0)
        
        if st.button("🚀 GENERATE PAYMENT", type="primary"):
            total_payout = (af_count * af_rate) + (idu_count * idu_rate) + (stb_count * stb_rate) + (odu_count * odu_rate)
            
            st.markdown(f"""
            <div class='glass-metric' style='border-bottom: 6px solid #16a34a; background: linear-gradient(145deg, #f0fdf4, #dcfce7) !important;'>
                <h4 style='color:#166534 !important;'>✅ PAYMENT SLIP: {staff_name.upper()}</h4>
                <h2 style='color:#15803d !important;'>₹ {total_payout}</h2>
                <div style='font-size:13px; color:#166534; font-weight:800; margin-top:8px;'>
                    AirFiber: ₹{af_count * af_rate} | IDU: ₹{idu_count * idu_rate} | STB: ₹{stb_count * stb_rate} | ODU: ₹{odu_count * odu_rate}
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MAIN ROUTING
# ==========================================
if not st.session_state['logged_in']:
    login()
else:
    st.sidebar.button("🚪 LOGOUT", on_click=lambda: st.session_state.clear(), type="primary")
    if st.session_state['role'] == 'admin':
        admin_panel()
    else:
        distributor_panel()
