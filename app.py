import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import io

# ==============================================================================
# 1. PAGE CONFIG & MODERN ULTRA-PRO GLASSMORPHISM DESIGN
# ==============================================================================
st.set_page_config(
    page_title="Jio Distributor SaaS ERP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
/* 🌟 ULTRA-PRO DYNAMIC GRADIENT BACKGROUND */
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], [data-testid="stMain"] { 
    background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 40%, #e0e7ff 75%, #f1f5f9 100%) !important;
    color: #0f172a;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 🌟 GLOBAL TYPOGRAPHY */
.stMarkdown p, .stMetric label, [data-testid="stText"], label, .stDataFrame td, .stDataFrame th {
    font-size: 15px !important;
    font-weight: 700 !important; 
    color: #0f172a; 
}
h1, h2, h3, h4, h5 { 
    font-weight: 900 !important; 
    letter-spacing: -0.5px;
    color: #0f172a;
}

/* 🌟 LIQUID TRANSPARENT INPUT FIELDS */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stDateInput input {
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 12px !important;
    border: 2px solid #cbd5e1 !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.03) !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
    background: #ffffff !important;
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
}

/* 🌟 3D HERO BANNER */
.hero-banner {
    background: linear-gradient(135deg, #091e42 0%, #1e3a8a 50%, #2563eb 100%);
    padding: 24px 28px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-bottom: 6px solid #0a1128;
    box-shadow: 0 16px 32px rgba(30, 58, 138, 0.25);
    color: #ffffff;
    margin-bottom: 22px;
}
.hero-title {
    font-size: 28px;
    font-weight: 900;
    margin: 0 0 6px 0;
    color: #ffffff !important;
    text-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
.hero-subtitle {
    font-size: 14px;
    font-weight: 600;
    color: #bfdbfe !important;
    margin: 0;
}

/* 🌟 SECTION HEADERS */
.section-header {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 12px 18px;
    border-radius: 14px;
    border-bottom: 4px solid #000000;
    color: #ffffff !important;
    font-weight: 800;
    font-size: 17px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 18px 0 14px 0;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.15);
}

/* 🌟 GLASS CONTAINER CARDS */
.glass-card {
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-bottom: 4px solid #cbd5e1;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.04);
    margin-bottom: 18px;
}

/* 🌟 METRIC WIDGETS */
.metric-card {
    text-align: center;
    padding: 16px 12px;
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    border-bottom: 5px solid #2563eb;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
    margin-bottom: 12px;
}
.metric-card-danger {
    border-bottom: 5px solid #dc2626 !important;
    background: #fef2f2 !important;
}
.metric-card-success {
    border-bottom: 5px solid #16a34a !important;
    background: #f0fdf4 !important;
}
.metric-card h4 {
    margin: 0;
    font-size: 13px;
    font-weight: 800;
    color: #64748b;
    text-transform: uppercase;
}
.metric-card h2 {
    margin: 6px 0 0 0;
    font-size: 26px;
    font-weight: 900;
    color: #0f172a;
}

/* 🌟 PAYMENT SLIP CARD */
.slip-box {
    background: #ffffff;
    border: 2px dashed #2563eb;
    border-radius: 16px;
    padding: 22px;
    margin-top: 15px;
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.08);
}

/* 🌟 ACTION BUTTONS (WHATSAPP & CALL) */
.btn-wa {
    display: inline-block;
    background-color: #25D366;
    color: white !important;
    font-weight: 800;
    padding: 8px 14px;
    border-radius: 10px;
    text-decoration: none;
    box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3);
    margin-right: 8px;
}
.btn-call {
    display: inline-block;
    background-color: #0284c7;
    color: white !important;
    font-weight: 800;
    padding: 8px 14px;
    border-radius: 10px;
    text-decoration: none;
    box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# 2. THREAD-SAFE DATABASE SETUP WITH AUTOMATIC MIGRATION
# ==============================================================================
DB_FILE = 'jio_saas_erp.db'

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with conn:
        # 1. Users Table (Multi-Tenant SaaS)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                business_name TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                valid_until DATE NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Auto-migrate missing columns in users if existing DB was from older version
        c = conn.cursor()
        c.execute("PRAGMA table_info(users)")
        u_cols = [r[1] for r in c.fetchall()]
        if 'business_name' not in u_cols:
            c.execute("ALTER TABLE users ADD COLUMN business_name TEXT DEFAULT ''")
        if 'phone' not in u_cols:
            c.execute("ALTER TABLE users ADD COLUMN phone TEXT DEFAULT ''")
        if 'status' not in u_cols:
            c.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active'")
        if 'created_at' not in u_cols:
            c.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

        # 2. Module 1: Auto-refill & Retailer Ledger
        conn.execute('''
            CREATE TABLE IF NOT EXISTS auto_refill_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dist_id INTEGER NOT NULL,
                retailer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                amount_given REAL DEFAULT 0.0,
                amount_received REAL DEFAULT 0.0,
                payment_mode TEXT DEFAULT 'Cash',
                remarks TEXT,
                date TEXT NOT NULL
            )
        ''')

        # Migrate old 'ledger' data if it exists from previous version
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ledger'")
        if c.fetchone():
            c.execute("SELECT COUNT(*) FROM auto_refill_ledger")
            if c.fetchone()[0] == 0:
                try:
                    c.execute("""
                        INSERT INTO auto_refill_ledger (dist_id, retailer_name, phone, amount_given, amount_received, date)
                        SELECT dist_id, retailer_name, phone, given, received, date FROM ledger
                    """)
                except Exception:
                    pass

        # 3. Commission Settings Table & Auto-Migration
        conn.execute('''
            CREATE TABLE IF NOT EXISTS commission_settings (
                dist_id INTEGER PRIMARY KEY,
                fse_sim_rate REAL DEFAULT 15.0,
                fse_mnp_rate REAL DEFAULT 50.0,
                fse_recharge_pct REAL DEFAULT 1.0,
                fse_daily_da REAL DEFAULT 100.0,
                airfiber_rate REAL DEFAULT 150.0,
                idu_rate REAL DEFAULT 40.0,
                stb_rate REAL DEFAULT 30.0,
                odu_rate REAL DEFAULT 50.0
            )
        ''')

        # Auto-migrate commission_settings columns
        c.execute("PRAGMA table_info(commission_settings)")
        cs_cols = [r[1] for r in c.fetchall()]
        if 'fse_sim_rate' not in cs_cols:
            c.execute("ALTER TABLE commission_settings ADD COLUMN fse_sim_rate REAL DEFAULT 15.0")
        if 'fse_mnp_rate' not in cs_cols:
            c.execute("ALTER TABLE commission_settings ADD COLUMN fse_mnp_rate REAL DEFAULT 50.0")
        if 'fse_recharge_pct' not in cs_cols:
            c.execute("ALTER TABLE commission_settings ADD COLUMN fse_recharge_pct REAL DEFAULT 1.0")
        if 'fse_daily_da' not in cs_cols:
            c.execute("ALTER TABLE commission_settings ADD COLUMN fse_daily_da REAL DEFAULT 100.0")
        if 'airfiber_rate' not in cs_cols:
            if 'airfiber' in cs_cols:
                c.execute("ALTER TABLE commission_settings ADD COLUMN airfiber_rate REAL DEFAULT 150.0")
                c.execute("UPDATE commission_settings SET airfiber_rate = airfiber WHERE airfiber IS NOT NULL")
            else:
                c.execute("ALTER TABLE commission_settings ADD COLUMN airfiber_rate REAL DEFAULT 150.0")
        if 'idu_rate' not in cs_cols:
            if 'idu' in cs_cols:
                c.execute("ALTER TABLE commission_settings ADD COLUMN idu_rate REAL DEFAULT 40.0")
                c.execute("UPDATE commission_settings SET idu_rate = idu WHERE idu IS NOT NULL")
            else:
                c.execute("ALTER TABLE commission_settings ADD COLUMN idu_rate REAL DEFAULT 40.0")
        if 'stb_rate' not in cs_cols:
            if 'stb' in cs_cols:
                c.execute("ALTER TABLE commission_settings ADD COLUMN stb_rate REAL DEFAULT 30.0")
                c.execute("UPDATE commission_settings SET stb_rate = stb WHERE stb IS NOT NULL")
            else:
                c.execute("ALTER TABLE commission_settings ADD COLUMN stb_rate REAL DEFAULT 30.0")
        if 'odu_rate' not in cs_cols:
            if 'odu' in cs_cols:
                c.execute("ALTER TABLE commission_settings ADD COLUMN odu_rate REAL DEFAULT 50.0")
                c.execute("UPDATE commission_settings SET odu_rate = odu WHERE odu IS NOT NULL")
            else:
                c.execute("ALTER TABLE commission_settings ADD COLUMN odu_rate REAL DEFAULT 50.0")

        # 4. Module 2: FSE / DAB Payout Entries
        conn.execute('''
            CREATE TABLE IF NOT EXISTS fse_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dist_id INTEGER NOT NULL,
                staff_name TEXT NOT NULL,
                phone TEXT,
                sim_count INTEGER DEFAULT 0,
                mnp_count INTEGER DEFAULT 0,
                recharge_amount REAL DEFAULT 0.0,
                daily_da REAL DEFAULT 0.0,
                total_payout REAL NOT NULL,
                date TEXT NOT NULL,
                remarks TEXT
            )
        ''')

        # 5. Module 3: AirFiber Payout Entries
        conn.execute('''
            CREATE TABLE IF NOT EXISTS airfiber_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dist_id INTEGER NOT NULL,
                staff_name TEXT NOT NULL,
                phone TEXT,
                installations_count INTEGER DEFAULT 0,
                rate_per_inst REAL NOT NULL,
                incentive REAL DEFAULT 0.0,
                total_payout REAL NOT NULL,
                date TEXT NOT NULL,
                remarks TEXT
            )
        ''')

        # 6. Module 4: Device Recovery Entries (IDU / STB / ODU)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS recovery_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dist_id INTEGER NOT NULL,
                staff_name TEXT NOT NULL,
                phone TEXT,
                idu_count INTEGER DEFAULT 0,
                stb_count INTEGER DEFAULT 0,
                odu_count INTEGER DEFAULT 0,
                idu_rate REAL NOT NULL,
                stb_rate REAL NOT NULL,
                odu_rate REAL NOT NULL,
                total_payout REAL NOT NULL,
                date TEXT NOT NULL,
                remarks TEXT
            )
        ''')

        # Seed Super Admin if not exists
        c.execute("SELECT id FROM users WHERE role='admin'")
        if not c.fetchone():
            c.execute('''
                INSERT INTO users (username, password, role, business_name, phone, valid_until, status)
                VALUES ('avdhesh_admin', 'admin123', 'admin', 'Sandhya Enterprises Tech HQ', '9876543210', '2099-12-31', 'active')
            ''')
    conn.close()

init_db()

# Safe Commission Rates Loader (Guaranteed no IndexError)
def get_commission_rates(dist_id):
    defaults = {
        'fse_sim_rate': 15.0,
        'fse_mnp_rate': 50.0,
        'fse_recharge_pct': 1.0,
        'fse_daily_da': 100.0,
        'airfiber_rate': 150.0,
        'idu_rate': 40.0,
        'stb_rate': 30.0,
        'odu_rate': 50.0
    }
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM commission_settings WHERE dist_id=?", (dist_id,))
    row = c.fetchone()
    
    if not row:
        c.execute('''
            INSERT OR REPLACE INTO commission_settings 
            (dist_id, fse_sim_rate, fse_mnp_rate, fse_recharge_pct, fse_daily_da, airfiber_rate, idu_rate, stb_rate, odu_rate)
            VALUES (?, 15.0, 50.0, 1.0, 100.0, 150.0, 40.0, 30.0, 50.0)
        ''', (dist_id,))
        conn.commit()
        rates = defaults.copy()
    else:
        rates = {}
        row_keys = row.keys() if hasattr(row, 'keys') else []
        for k, def_val in defaults.items():
            if k in row_keys and row[k] is not None:
                try:
                    rates[k] = float(row[k])
                except (ValueError, TypeError):
                    rates[k] = def_val
            else:
                rates[k] = def_val
        # Support legacy column name 'airfiber' if 'airfiber_rate' is default
        if 'airfiber' in row_keys and row['airfiber'] is not None and rates['airfiber_rate'] == 150.0:
            try:
                rates['airfiber_rate'] = float(row['airfiber'])
            except Exception:
                pass
    conn.close()
    return rates

# ==============================================================================
# 3. AUTHENTICATION & SESSION MANAGEMENT
# ==============================================================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'business_name' not in st.session_state:
    st.session_state['business_name'] = ""

def login_page():
    st.markdown("""
        <div class="hero-banner" style="text-align:center; max-width: 580px; margin: 40px auto 20px auto;">
            <div style="font-size: 40px; margin-bottom: 8px;">🏢⚡</div>
            <h1 class="hero-title">JIO DISTRIBUTOR ERP</h1>
            <p class="hero-subtitle">Sandhya Enterprises Cloud SaaS Network • Multi-Tenant Enterprise</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🔐 Secure Distributor Login")
            uname = st.text_input("Username (यूजरनेम)", placeholder="Enter your username")
            upass = st.text_input("Password (पासवर्ड)", type="password", placeholder="Enter your password")

            if st.button("🚀 ENTER DASHBOARD", type="primary", use_container_width=True):
                if not uname or not upass:
                    st.warning("⚠️ कृपया यूजरनेम और पासवर्ड दोनों दर्ज करें।")
                else:
                    conn = get_db()
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, upass))
                    user = c.fetchone()
                    conn.close()

                    if user:
                        # Extract fields safely
                        user_keys = user.keys() if hasattr(user, 'keys') else []
                        u_role = user['role']
                        u_status = user['status'] if 'status' in user_keys else 'active'
                        u_biz = user['business_name'] if 'business_name' in user_keys else ''
                        u_valid = user['valid_until']

                        is_active = (u_status == 'active')
                        valid_date = datetime.strptime(u_valid, '%Y-%m-%d').date()
                        today = datetime.now().date()

                        if u_role == 'admin' or (is_active and valid_date >= today):
                            st.session_state['logged_in'] = True
                            st.session_state['user_id'] = user['id']
                            st.session_state['role'] = u_role
                            st.session_state['username'] = user['username']
                            st.session_state['business_name'] = u_biz or user['username']
                            st.success(f"✅ स्वागत है, {st.session_state['business_name']}!")
                            st.rerun()
                        elif not is_active:
                            st.error("🚫 आपका खाता निष्क्रिय (Deactivated) कर दिया गया है। कृपया अवधेश जी से संपर्क करें।")
                        else:
                            days_expired = (today - valid_date).days
                            st.error(f"⌛ आपका 1 महीने का सब्सक्रिप्शन {days_expired} दिन पहले समाप्त हो चुका है ({u_valid})।\nकृपया बैंक/UPI में रीचार्ज पेमेंट भेजकर अवधेश जी से रिन्यू कराएं।")
                    else:
                        st.error("❌ अमान्य यूजरनेम या पासवर्ड!")
            st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 4. SUPER ADMIN CONTROL PANEL (AVDHESH CONTROL)
# ==============================================================================
def admin_panel():
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-title">⚙️ SUPER ADMIN CONTROL HUB (AVDHESH)</h1>
            <p class="hero-subtitle">Distributor Account Provisioning, 30-Day Validity, Payment Activation & Multi-Tenant Control</p>
        </div>
    """, unsafe_allow_html=True)

    conn = get_db()
    c = conn.cursor()

    # Admin KPI Overview
    c.execute("SELECT COUNT(*) FROM users WHERE role='distributor'")
    total_dist = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE role='distributor' AND valid_until >= date('now') AND status='active'")
    active_dist = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE role='distributor' AND (valid_until < date('now') OR status='suspended')")
    expired_dist = c.fetchone()[0]

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
            <div class="metric-card">
                <h4>👥 कुल डिस्ट्रीब्यूटर्स (Total Clients)</h4>
                <h2>{total_dist}</h2>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
            <div class="metric-card metric-card-success">
                <h4>🟢 एक्टिव सब्सक्राइबर्स (Active & Valid)</h4>
                <h2 style="color:#16a34a;">{active_dist}</h2>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
            <div class="metric-card metric-card-danger">
                <h4>🔴 एक्सपायर्ड / पेंडिंग (Expired / Due)</h4>
                <h2 style="color:#dc2626;">{expired_dist}</h2>
            </div>
        """, unsafe_allow_html=True)

    tab_manage, tab_add, tab_settings = st.tabs(["📋 Distributor Client Roster", "➕ Add New Distributor (1-Month Pass)", "🔐 Admin Profile"])

    with tab_add:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### ➕ नया डिस्ट्रीब्यूटर ऐप ऑनबोर्ड करें (New Distributor App)")
        st.caption("जब कोई डिस्ट्रीब्यूटर पैसे दे, यहाँ से उनका नया अकाउंट बनाएं। डिफ़ॉल्ट वैलिडिटी 30 दिन रहेगी।")

        c1, c2 = st.columns(2)
        new_username = c1.text_input("Username (लॉगिन आईडी)", placeholder="e.g. dist_patna_rajesh")
        new_password = c2.text_input("Password (पासवर्ड)", value="jio1234")

        c3, c4 = st.columns(2)
        biz_name = c3.text_input("Agency / Business Name", placeholder="e.g. Rajesh Telecom Agency")
        phone_no = c4.text_input("Distributor Contact Phone", placeholder="e.g. 9876543210")

        validity_days = st.number_input("Validity Period (दिन)", min_value=1, max_value=365, value=30)

        if st.button("💾 डिस्ट्रीब्यूटर ऐप एक्टिवेट करें (Create App)", type="primary"):
            if not new_username or not new_password:
                st.error("यूजरनेम और पासवर्ड जरूरी हैं!")
            else:
                expiry_date = (datetime.now() + timedelta(days=validity_days)).strftime('%Y-%m-%d')
                try:
                    c.execute('''
                        INSERT INTO users (username, password, role, business_name, phone, valid_until, status)
                        VALUES (?, ?, 'distributor', ?, ?, ?, 'active')
                    ''', (new_username.strip(), new_password.strip(), biz_name.strip(), phone_no.strip(), expiry_date))
                    new_dist_id = c.lastrowid

                    # Seed default commission rates
                    c.execute('''
                        INSERT OR REPLACE INTO commission_settings 
                        (dist_id, fse_sim_rate, fse_mnp_rate, fse_recharge_pct, fse_daily_da, airfiber_rate, idu_rate, stb_rate, odu_rate)
                        VALUES (?, 15.0, 50.0, 1.0, 100.0, 150.0, 40.0, 30.0, 50.0)
                    ''', (new_dist_id,))
                    conn.commit()
                    st.success(f"🎉 डिस्ट्रीब्यूटर '{new_username}' का अकाउंट सफलतापूर्वक बन गया! वैलिडिटी: {expiry_date} तक।")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("❌ इस यूजरनेम का डिस्ट्रीब्यूटर पहले से मौजूद है! दूसरा नाम चुनें।")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_manage:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🏢 डिस्ट्रीब्यूटर लिस्ट एवं 1-क्लिक रीचार्ज/रिन्यूअल (+30 Days)")
        
        df_dist = pd.read_sql_query("""
            SELECT id, username, business_name, phone, valid_until, status, created_at 
            FROM users WHERE role='distributor' ORDER BY id DESC
        """, conn)

        if df_dist.empty:
            st.info("अभी कोई डिस्ट्रीब्यूटर दर्ज नहीं है। 'Add New Distributor' टैब से बनाएं।")
        else:
            for idx, row in df_dist.iterrows():
                valid_date = datetime.strptime(row['valid_until'], '%Y-%m-%d').date()
                today = datetime.now().date()
                days_left = (valid_date - today).days

                status_color = "#16a34a" if (days_left >= 0 and row['status'] == 'active') else "#dc2626"
                status_text = f"ACTIVE ({days_left} दिन बाकी)" if days_left >= 0 else f"EXPIRED ({abs(days_left)} दिन पहले)"
                if row['status'] == 'suspended':
                    status_text = "SUSPENDED / BLOCKED"
                    status_color = "#ea580c"

                with st.expander(f"🏢 {row['business_name'] or row['username']} (ID: {row['id']}) — Status: {status_text}"):
                    ec1, ec2, ec3, ec4 = st.columns(4)
                    ec1.write(f"**Username:** `{row['username']}`")
                    ec2.write(f"**Phone:** `{row['phone'] or 'N/A'}`")
                    ec3.write(f"**Valid Till:** `{row['valid_until']}`")
                    ec4.markdown(f"**Account Status:** <span style='color:{status_color}; font-weight:900;'>{status_text}</span>", unsafe_allow_html=True)

                    btn_c1, btn_c2, btn_c3 = st.columns(3)
                    with btn_c1:
                        if st.button(f"⚡ +30 दिन रिन्यू करें (पेमेंट आ गया)", key=f"renew_{row['id']}"):
                            base_date = max(today, valid_date)
                            new_expiry = (base_date + timedelta(days=30)).strftime('%Y-%m-%d')
                            c.execute("UPDATE users SET valid_until=?, status='active' WHERE id=?", (new_expiry, row['id']))
                            conn.commit()
                            st.success(f"✅ {row['username']} का अकाउंट 30 दिन के लिए रिन्यू कर दिया गया! नई तारीख: {new_expiry}")
                            st.rerun()

                    with btn_c2:
                        toggle_label = "🔴 सस्पेंड (Block) करें" if row['status'] == 'active' else "🟢 अनब्लॉक (Activate) करें"
                        new_state = 'suspended' if row['status'] == 'active' else 'active'
                        if st.button(toggle_label, key=f"toggle_{row['id']}"):
                            c.execute("UPDATE users SET status=? WHERE id=?", (new_state, row['id']))
                            conn.commit()
                            st.rerun()

                    with btn_c3:
                        if st.button("🗑️ डिलीट करें", key=f"del_{row['id']}"):
                            c.execute("DELETE FROM users WHERE id=?", (row['id'],))
                            c.execute("DELETE FROM auto_refill_ledger WHERE dist_id=?", (row['id'],))
                            c.execute("DELETE FROM commission_settings WHERE dist_id=?", (row['id'],))
                            c.execute("DELETE FROM fse_entries WHERE dist_id=?", (row['id'],))
                            c.execute("DELETE FROM airfiber_entries WHERE dist_id=?", (row['id'],))
                            c.execute("DELETE FROM recovery_entries WHERE dist_id=?", (row['id'],))
                            conn.commit()
                            st.warning("खाता हटा दिया गया!")
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_settings:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🔐 सुपर एडमिन पासवर्ड बदलें")
        old_p = st.text_input("वर्तमान पासवर्ड", type="password")
        new_p = st.text_input("नया पासवर्ड", type="password")
        if st.button("पासवर्ड अपडेट करें"):
            c.execute("SELECT id FROM users WHERE username='avdhesh_admin' AND password=?", (old_p,))
            if c.fetchone():
                c.execute("UPDATE users SET password=? WHERE username='avdhesh_admin'", (new_p,))
                conn.commit()
                st.success("✅ एडमिन पासवर्ड बदल दिया गया!")
            else:
                st.error("पुराना पासवर्ड गलत है!")
        st.markdown('</div>', unsafe_allow_html=True)

    conn.close()

# ==============================================================================
# 5. DISTRIBUTOR APPLICATION PORTAL (CLIENT TENANT)
# ==============================================================================
def distributor_panel():
    dist_id = st.session_state['user_id']
    username = st.session_state['username']
    biz_name = st.session_state['business_name']

    conn = get_db()
    c = conn.cursor()

    # Check validity info
    c.execute("SELECT valid_until FROM users WHERE id=?", (dist_id,))
    user_row = c.fetchone()
    valid_until_str = user_row['valid_until'] if user_row else "2099-12-31"
    valid_date = datetime.strptime(valid_until_str, '%Y-%m-%d').date()
    days_remaining = (valid_date - datetime.now().date()).days

    # Top Hero Header
    st.markdown(f"""
        <div class="hero-banner">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <h1 class="hero-title">🏢 {biz_name.upper()}</h1>
                    <p class="hero-subtitle">Jio Authorized Distribution Enterprise Suite • Logged in as: <b>{username}</b></p>
                </div>
                <div style="background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.3); border-radius:12px; padding:8px 16px; text-align:right;">
                    <div style="font-size:12px; color:#bfdbfe; font-weight:700;">VALIDITY REMAINING</div>
                    <div style="font-size:18px; color:#ffffff; font-weight:900;">⚡ {days_remaining} Days (Till {valid_until_str})</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    st.sidebar.markdown(f"### 📱 {biz_name}")
    st.sidebar.info(f"📅 वैधता: **{valid_until_str}**\n⏳ बाकी दिन: **{days_remaining} दिन**")
    
    app_menu = st.sidebar.radio(
        "मोड्यूल चुनें (Select Module)",
        [
            "1. 📒 Auto-refill & Retailer Ledger",
            "2. 👥 FSE / DAB Payout & Slip",
            "3. 🌐 AirFiber Commission",
            "4. 📦 Recovery (IDU / STB / ODU)",
            "5. ⚙️ Commission Rate Settings"
        ]
    )

    # Load Commission Rates Safely (Guaranteed no IndexError)
    rates = get_commission_rates(dist_id)

    # --------------------------------------------------------------------------
    # MODULE 1: AUTO-REFILL & RETAILER LEDGER (उधार - जमा और रिमाइंडर)
    # --------------------------------------------------------------------------
    if "1. 📒 Auto-refill" in app_menu:
        st.markdown('<div class="section-header">📒 1. AUTO-REFILL & RETAILER BALANCE LEDGER (उधार-जमा खाता)</div>', unsafe_allow_html=True)

        # Overview Metrics for Auto-Refill
        c.execute("SELECT SUM(amount_given), SUM(amount_received) FROM auto_refill_ledger WHERE dist_id=?", (dist_id,))
        sums = c.fetchone()
        total_given = sums[0] if (sums and sums[0]) else 0.0
        total_received = sums[1] if (sums and sums[1]) else 0.0
        total_market_due = total_given - total_received

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>💸 कुल ऑटो-रिफिल दिया (Given)</h4>
                    <h2>₹ {total_given:,.2f}</h2>
                </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
                <div class="metric-card metric-card-success">
                    <h4>💰 कुल कैश/खाते में मिला (Received)</h4>
                    <h2 style="color:#16a34a;">₹ {total_received:,.2f}</h2>
                </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
                <div class="metric-card metric-card-danger">
                    <h4>⚠️ मार्केट में बकाया बाकी (Net Due)</h4>
                    <h2 style="color:#dc2626;">₹ {total_market_due:,.2f}</h2>
                </div>
            """, unsafe_allow_html=True)

        tab_entry, tab_report, tab_quick_reminder = st.tabs(["➕ नई एंट्री दर्ज करें (New Entry)", "📊 रिटेलर खाता रिपोर्ट व डाउनलोड", "💬 तुरंत पेमेंट रिमाइंडर भेजें"])

        with tab_entry:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0;'>➕ ऑटो-रिफिल / पेमेंट एंट्री जोड़ें</h4>", unsafe_allow_html=True)
            
            with st.form("auto_refill_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                r_name = col1.text_input("रिटेलर का नाम (Retailer Name)*", placeholder="जैसे: राजेश मोबाइल, शर्मा टेलीकॉम")
                r_phone = col2.text_input("व्हाट्सएप / मोबाइल नंबर (10 Digit Phone)*", placeholder="जैसे: 9876543210")

                col3, col4, col5 = st.columns(3)
                given_amt = col3.number_input("ऑटो-रिफिल दिया (Amount Given ₹)", min_value=0.0, step=100.0, value=0.0)
                recv_amt = col4.number_input("कैश / अकाउंट में मिला (Amount Received ₹)", min_value=0.0, step=100.0, value=0.0)
                pay_mode = col5.selectbox("पेमेंट माध्यम (Mode)", ["Cash (नकद)", "PhonePe / GPay / UPI", "Bank Account Transfer", "Pending / None"])

                remarks = st.text_input("रिमार्क्स / नोट (Remarks)", placeholder="e.g. Morning 10AM lapu refill")
                submit_entry = st.form_submit_button("🚀 खाता में सेव करें (Save Ledger Entry)", type="primary")

                if submit_entry:
                    if not r_name.strip():
                        st.error("कृपया रिटेलर का नाम दर्ज करें!")
                    elif given_amt == 0 and recv_amt == 0:
                        st.warning("कृपया दिया गया या प्राप्त हुआ अमाउंट भरें!")
                    else:
                        clean_phone = ''.join(filter(str.isdigit, r_phone))
                        date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
                        c.execute('''
                            INSERT INTO auto_refill_ledger (dist_id, retailer_name, phone, amount_given, amount_received, payment_mode, remarks, date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (dist_id, r_name.strip(), clean_phone, given_amt, recv_amt, pay_mode, remarks.strip(), date_str))
                        conn.commit()
                        net_diff = given_amt - recv_amt
                        st.success(f"✅ एंट्री सेव हो गई! ({r_name} - बाकी बैलेंस बदलाव: ₹{net_diff:,.2f})")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_report:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📋 संपूर्ण रिटेलर लेजर रिपोर्ट (Detailed Ledger)")

            df_all = pd.read_sql_query(f"""
                SELECT id, retailer_name, phone, amount_given, amount_received, 
                       (amount_given - amount_received) as due_amount, payment_mode, remarks, date
                FROM auto_refill_ledger 
                WHERE dist_id={dist_id} 
                ORDER BY id DESC
            """, conn)

            if df_all.empty:
                st.info("अभी कोई ऑटो-रिफिल एंट्री दर्ज नहीं है।")
            else:
                search_q = st.text_input("🔍 रिटेलर खोजें (Search Retailer Name)", "")
                if search_q:
                    df_filtered = df_all[df_all['retailer_name'].str.contains(search_q, case=False, na=False)]
                else:
                    df_filtered = df_all

                st.dataframe(df_filtered, use_container_width=True, hide_index=True)

                csv_buffer = io.StringIO()
                df_filtered.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 रिपोर्ट एक्सेल / CSV डाउनलोड करें",
                    data=csv_buffer.getvalue(),
                    file_name=f"Jio_AutoRefill_Report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_quick_reminder:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📱 1-क्लिक व्हाट्सएप पेमेंट रिमाइंडर एवं डायरेक्ट कॉल")
            st.caption("नीचे प्रत्येक रिटेलर का कुल बकाया हिसाब है। आप एक क्लिक में व्हाट्सएप संदेश भेज सकते हैं या कॉल कर सकते हैं।")

            df_summary = pd.read_sql_query(f"""
                SELECT retailer_name, phone, 
                       SUM(amount_given) as total_given, 
                       SUM(amount_received) as total_received,
                       (SUM(amount_given) - SUM(amount_received)) as net_balance,
                       MAX(date) as last_txn_date
                FROM auto_refill_ledger 
                WHERE dist_id={dist_id}
                GROUP BY retailer_name
                HAVING net_balance > 0
                ORDER BY net_balance DESC
            """, conn)

            if df_summary.empty:
                st.success("🎉 बधाई हो! किसी भी रिटेलर का कोई बकाया (Due) बाकी नहीं है।")
            else:
                for idx, row in df_summary.iterrows():
                    ret_name = row['retailer_name']
                    ret_phone = row['phone']
                    balance = row['net_balance']
                    given = row['total_given']
                    recv = row['total_received']

                    reminder_msg = (
                        f"नमस्ते {ret_name} जी,\n\n"
                        f"यह *{biz_name}* (Jio Distributor) की तरफ से ऑटो-रिफिल बकाया पेमेंट का सूचना संदेश है:\n"
                        f"▪ कुल ऑटो-रिफिल दिया गया: ₹{given:,.2f}\n"
                        f"▪ कुल प्राप्त भुगतान: ₹{recv:,.2f}\n"
                        f"👉 *वर्तमान बकाया राशि (Remaining Due): ₹{balance:,.2f}*\n\n"
                        f"कृपया बकाया राशि आज ही कैश या यूपीआई/खाते में जमा कराने की कृपा करें। धन्यवाद!"
                    )
                    encoded_msg = urllib.parse.quote(reminder_msg)
                    wa_link = f"https://api.whatsapp.com/send?phone=91{ret_phone}&text={encoded_msg}" if ret_phone else "#"
                    call_link = f"tel:+91{ret_phone}" if ret_phone else "#"

                    with st.container():
                        st.markdown(f"""
                            <div style="background:#ffffff; border:1px solid #e2e8f0; border-left: 6px solid #dc2626; border-radius:14px; padding:16px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                                <div>
                                    <h4 style="margin:0; font-size:18px; color:#0f172a;">👤 {ret_name}</h4>
                                    <div style="color:#64748b; font-size:14px; margin-top:4px;">
                                        📞 फ़ोन: <b>{ret_phone or 'नंबर नहीं है'}</b> | कुल दिया: <b>₹{given:,.2f}</b> | मिला: <b>₹{recv:,.2f}</b>
                                    </div>
                                </div>
                                <div style="text-align:right; margin-top:8px;">
                                    <div style="font-size:20px; font-weight:900; color:#dc2626;">बकाया: ₹{balance:,.2f}</div>
                                    <div style="margin-top:8px;">
                                        {f'<a href="{wa_link}" target="_blank" class="btn-wa">💬 WhatsApp Reminder</a>' if ret_phone else ''}
                                        {f'<a href="{call_link}" class="btn-call">📞 Call Retailer</a>' if ret_phone else ''}
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # MODULE 2: FSE / DAB MANAGEMENT & PAYMENT SLIP
    # --------------------------------------------------------------------------
    elif "2. 👥 FSE / DAB Payout" in app_menu:
        st.markdown('<div class="section-header">👥 2. FSE / DAB / DSE STAFF PAYOUT & SLIP GENERATOR</div>', unsafe_allow_html=True)
        st.caption("अपने फ़ील्ड लड़कों (DAB/FSE) की दैनिक/मासिक एक्टिवेशन एंट्री करें और उनका आधिकारिक पेमेंट स्लिप बनाएं।")

        fse_sim = rates['fse_sim_rate']
        fse_mnp = rates['fse_mnp_rate']
        fse_rch = rates['fse_recharge_pct']
        fse_da = rates['fse_daily_da']

        st.info(f"⚙️ वर्तमान कमीशन दरें: **SIM Activation:** ₹{fse_sim:,.2f}/SIM | **MNP Port:** ₹{fse_mnp:,.2f}/Port | **Recharge:** {fse_rch:,.2f}% | **Daily DA:** ₹{fse_da:,.2f}/Day (दरें बदलने के लिए 'Commission Settings' मेनू में जाएं)")

        tab_calc, tab_history = st.tabs(["📝 नया FSE पेमेंट बनाएं (New Slip)", "📜 FSE पेमेंट इतिहास व रिपोर्ट"])

        with tab_calc:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fse_name = st.text_input("👷 FSE / DAB स्टाफ का नाम (Staff Name)*", placeholder="जैसे: राहुल कुमार, अमित सिंह")
            fse_phone = st.text_input("📱 मोबाइल नंबर (Mobile Number)", placeholder="जैसे: 9876543210")

            c1, c2 = st.columns(2)
            sim_done = c1.number_input("नया सिम एक्टिवेशन संख्या (SIM Qty)", min_value=0, step=1, value=0)
            mnp_done = c2.number_input("MNP (पोर्ट) संख्या (MNP Qty)", min_value=0, step=1, value=0)

            c3, c4 = st.columns(2)
            rch_done = c3.number_input("कुल रिचार्ज वॉल्यूम किया (Recharge Amount ₹)", min_value=0.0, step=100.0, value=0.0)
            days_da = c4.number_input("दैनिक भत्ता (DA Days)", min_value=0, step=1, value=1)

            entry_remarks = st.text_input("नोट / रिमार्क्स (Payment Remarks)", placeholder="e.g. October 2nd Week Payment")

            payout_sim = sim_done * fse_sim
            payout_mnp = mnp_done * fse_mnp
            payout_rch = (rch_done * fse_rch) / 100.0
            payout_da = days_da * fse_da
            grand_total = payout_sim + payout_mnp + payout_rch + payout_da

            st.markdown(f"""
                <div class="slip-box">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #e2e8f0; padding-bottom:10px;">
                        <div>
                            <h3 style="margin:0; color:#1e3a8a;">📄 JIO FSE / DAB PAYMENT SLIP</h3>
                            <div style="color:#64748b; font-size:13px; font-weight:700;">{biz_name.upper()} • DATE: {datetime.now().strftime('%d-%b-%Y')}</div>
                        </div>
                        <div style="text-align:right;">
                            <span style="background:#dbeafe; color:#1e40af; padding:6px 14px; border-radius:10px; font-weight:900; font-size:14px;">STAFF: {fse_name or 'N/A'}</span>
                        </div>
                    </div>
                    <div style="margin:16px 0; font-size:15px;">
                        <table style="width:100%; border-collapse:collapse;">
                            <tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:6px 0;">New SIM Activations ({sim_done} × ₹{fse_sim})</td><td style="text-align:right; font-weight:800;">₹ {payout_sim:,.2f}</td></tr>
                            <tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:6px 0;">MNP / Port ({mnp_done} × ₹{fse_mnp})</td><td style="text-align:right; font-weight:800;">₹ {payout_mnp:,.2f}</td></tr>
                            <tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:6px 0;">Recharge Commission ({fse_rch}% on ₹{rch_done:,.2f})</td><td style="text-align:right; font-weight:800;">₹ {payout_rch:,.2f}</td></tr>
                            <tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:6px 0;">Field DA / Allowance ({days_da} days × ₹{fse_da})</td><td style="text-align:right; font-weight:800;">₹ {payout_da:,.2f}</td></tr>
                            <tr style="font-size:18px; color:#16a34a; font-weight:900;"><td style="padding:10px 0;">कुल देय राशि (TOTAL PAYOUT)</td><td style="text-align:right;">₹ {grand_total:,.2f}</td></tr>
                        </table>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if st.button("💾 FSE पेमेंट डेटाबेस में सेव करें (Save & Record Payout)", type="primary"):
                if not fse_name.strip():
                    st.error("कृपया FSE स्टाफ का नाम लिखें!")
                else:
                    date_now = datetime.now().strftime('%Y-%m-%d %H:%M')
                    c.execute('''
                        INSERT INTO fse_entries (dist_id, staff_name, phone, sim_count, mnp_count, recharge_amount, daily_da, total_payout, date, remarks)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (dist_id, fse_name.strip(), fse_phone.strip(), sim_done, mnp_done, rch_done, payout_da, grand_total, date_now, entry_remarks))
                    conn.commit()
                    st.success(f"🎉 {fse_name} का पेमेंट रिकॉर्ड ₹{grand_total:,.2f} सफलतापूर्वक सेव हो गया!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_history:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📜 सभी FSE लड़कों का पेमेंट इतिहास")
            df_fse = pd.read_sql_query(f"""
                SELECT id, staff_name, phone, sim_count, mnp_count, recharge_amount, daily_da, total_payout, remarks, date 
                FROM fse_entries WHERE dist_id={dist_id} ORDER BY id DESC
            """, conn)

            if df_fse.empty:
                st.info("अभी कोई FSE पेमेंट रिकॉर्ड नहीं है।")
            else:
                st.dataframe(df_fse, use_container_width=True, hide_index=True)
                csv_fse = io.StringIO()
                df_fse.to_csv(csv_fse, index=False)
                st.download_button("📥 FSE रिपोर्ट डाउनलोड करें (CSV)", data=csv_fse.getvalue(), file_name=f"FSE_Payouts_{datetime.now().strftime('%Y%m%d')}.csv")
            st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # MODULE 3: AIRFIBER COMMISSION
    # --------------------------------------------------------------------------
    elif "3. 🌐 AirFiber Commission" in app_menu:
        st.markdown('<div class="section-header">🌐 3. JIO AIRFIBER INSTALLATION COMMISSION</div>', unsafe_allow_html=True)
        st.caption("AirFiber इंस्टॉलेशन के लिए लड़कों का कमीशन कैलकुलेट करें और रिकॉर्ड सुरक्षित रखें।")

        af_rate = rates['airfiber_rate']
        st.info(f"⚙️ वर्तमान AirFiber कमीशन दर: **₹{af_rate:,.2f} प्रति इंस्टॉलेशन**")

        tab_af_entry, tab_af_hist = st.tabs(["📝 नया AirFiber पेमेंट", "📜 AirFiber पेमेंट रिकॉर्ड्स"])

        with tab_af_entry:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            af_staff = st.text_input("👷 AirFiber इंजीनियर / फील्ड स्टाफ का नाम*", placeholder="जैसे: विकास कुमार")
            af_phone = st.text_input("📱 मोबाइल नंबर", placeholder="e.g. 9876543210")

            c1, c2 = st.columns(2)
            inst_count = c1.number_input("कुल इंस्टॉलेशन की संख्या (Installations Done)", min_value=0, step=1, value=1)
            incentive = c2.number_input("अतिरिक्त प्रोत्साहन / बोनस (Incentive / Bonus ₹)", min_value=0.0, step=50.0, value=0.0)

            total_af_payout = (inst_count * af_rate) + incentive

            st.markdown(f"""
                <div class="slip-box">
                    <h3 style="margin:0; color:#1e3a8a;">⚡ JIO AIRFIBER COMMISSION SLIP</h3>
                    <div style="font-size:13px; color:#64748b; font-weight:700;">{biz_name} • Technician: <b>{af_staff or 'N/A'}</b></div>
                    <div style="margin:14px 0;">
                        ▪ कुल इंस्टॉलेशन: <b>{inst_count} nos × ₹{af_rate} = ₹{inst_count * af_rate:,.2f}</b><br/>
                        ▪ इंसेंटिव / बोनस: <b>₹{incentive:,.2f}</b>
                    </div>
                    <h2 style="color:#16a34a; margin:0;">कुल पे-आउट: ₹{total_af_payout:,.2f}</h2>
                </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 AirFiber पेमेंट सेव करें", type="primary"):
                if not af_staff.strip():
                    st.error("स्टाफ का नाम दर्ज करें!")
                else:
                    date_now = datetime.now().strftime('%Y-%m-%d %H:%M')
                    c.execute('''
                        INSERT INTO airfiber_entries (dist_id, staff_name, phone, installations_count, rate_per_inst, incentive, total_payout, date, remarks)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (dist_id, af_staff.strip(), af_phone.strip(), inst_count, af_rate, incentive, total_af_payout, date_now, 'AirFiber installation'))
                    conn.commit()
                    st.success(f"✅ AirFiber पेमेंट ₹{total_af_payout:,.2f} सेव हो गया!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_af_hist:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            df_af = pd.read_sql_query(f"SELECT * FROM airfiber_entries WHERE dist_id={dist_id} ORDER BY id DESC", conn)
            if df_af.empty:
                st.info("कोई AirFiber रिकॉर्ड नहीं मिला।")
            else:
                st.dataframe(df_af, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # MODULE 4: RECOVERY COMMISSION (IDU / STB / ODU)
    # --------------------------------------------------------------------------
    elif "4. 📦 Recovery" in app_menu:
        st.markdown('<div class="section-header">📦 4. JIO RECOVERY COMMISSION (IDU / STB / ODU)</div>', unsafe_allow_html=True)
        st.caption("कस्टमर से रिकवर किए गए IDU, STB, एवं ODU डिवाइस के आधार पर लड़कों का कमीशन पे-आउट बनाएं।")

        idu_r = rates['idu_rate']
        stb_r = rates['stb_rate']
        odu_r = rates['odu_rate']

        st.info(f"⚙️ रिकवरी कमीशन दरें: **IDU:** ₹{idu_r:,.2f}/Unit | **STB:** ₹{stb_r:,.2f}/Unit | **ODU:** ₹{odu_r:,.2f}/Unit")

        tab_rec_entry, tab_rec_hist = st.tabs(["📝 नया रिकवरी पे-आउट बनाएं", "📜 रिकवरी इतिहास"])

        with tab_rec_entry:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            rec_staff = st.text_input("👷 रिकवरी फील्ड बॉय का नाम*", placeholder="जैसे: सतीश कुमार")
            rec_phone = st.text_input("📱 मोबाइल नंबर", placeholder="e.g. 9876543210")

            c1, c2, c3 = st.columns(3)
            idu_c = c1.number_input("IDU (Indoor Unit) संख्या", min_value=0, step=1, value=0)
            stb_c = c2.number_input("STB (Set-Top Box) संख्या", min_value=0, step=1, value=0)
            odu_c = c3.number_input("ODU (Outdoor Unit) संख्या", min_value=0, step=1, value=0)

            total_rec = (idu_c * idu_r) + (stb_c * stb_r) + (odu_c * odu_r)

            st.markdown(f"""
                <div class="slip-box">
                    <h3 style="margin:0; color:#1e3a8a;">📦 JIO DEVICE RECOVERY SLIP</h3>
                    <div style="font-size:13px; color:#64748b; font-weight:700;">{biz_name} • Staff: <b>{rec_staff or 'N/A'}</b></div>
                    <div style="margin:14px 0; font-size:15px;">
                        ▪ IDU Recovered: <b>{idu_c} nos × ₹{idu_r:,.2f} = ₹{idu_c * idu_r:,.2f}</b><br/>
                        ▪ STB Recovered: <b>{stb_c} nos × ₹{stb_r:,.2f} = ₹{stb_c * stb_r:,.2f}</b><br/>
                        ▪ ODU Recovered: <b>{odu_c} nos × ₹{odu_r:,.2f} = ₹{odu_c * odu_r:,.2f}</b>
                    </div>
                    <h2 style="color:#16a34a; margin:0;">कुल रिकवरी पेमेंट: ₹{total_rec:,.2f}</h2>
                </div>
            """, unsafe_allow_html=True)

            if st.button("💾 रिकवरी पेमेंट सेव करें (Save Record)", type="primary"):
                if not rec_staff.strip():
                    st.error("स्टाफ का नाम भरें!")
                else:
                    date_now = datetime.now().strftime('%Y-%m-%d %H:%M')
                    c.execute('''
                        INSERT INTO recovery_entries (dist_id, staff_name, phone, idu_count, stb_count, odu_count, idu_rate, stb_rate, odu_rate, total_payout, date, remarks)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (dist_id, rec_staff.strip(), rec_phone.strip(), idu_c, stb_c, odu_c, idu_r, stb_r, odu_r, total_rec, date_now, 'Device Recovery'))
                    conn.commit()
                    st.success(f"✅ रिकवरी पेमेंट ₹{total_rec:,.2f} सफलतापूर्वक सेव हो गया!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_rec_hist:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            df_rec = pd.read_sql_query(f"SELECT * FROM recovery_entries WHERE dist_id={dist_id} ORDER BY id DESC", conn)
            if df_rec.empty:
                st.info("कोई रिकवरी रिकॉर्ड नहीं मिला।")
            else:
                st.dataframe(df_rec, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # MODULE 5: COMMISSION RATE SETTINGS
    # --------------------------------------------------------------------------
    elif "5. ⚙️ Commission Rate" in app_menu:
        st.markdown('<div class="section-header">⚙️ 5. DISTRIBUTOR CUSTOM COMMISSION SETTINGS</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### अपने अनुसार कमीशन रेट्स सेट करें (Custom Rates for your Business)")
        st.caption("प्रत्येक डिस्ट्रीब्यूटर अपने शहर और स्टाफ के अनुसार अपनी अलग-अलग दरें तय कर सकता है।")

        st.markdown("#### 1. FSE / DAB Commission Rates")
        rc1, rc2, rc3, rc4 = st.columns(4)
        new_sim_r = rc1.number_input("SIM Activation Rate (₹)", value=float(rates['fse_sim_rate']))
        new_mnp_r = rc2.number_input("MNP Port Rate (₹)", value=float(rates['fse_mnp_rate']))
        new_rch_p = rc3.number_input("Recharge Margin (%)", value=float(rates['fse_recharge_pct']))
        new_da_r = rc4.number_input("Daily DA / Petrol (₹)", value=float(rates['fse_daily_da']))

        st.markdown("#### 2. AirFiber & Recovery Device Rates")
        rc5, rc6, rc7, rc8 = st.columns(4)
        new_af_r = rc5.number_input("AirFiber Installation (₹)", value=float(rates['airfiber_rate']))
        new_idu_r = rc6.number_input("IDU Recovery (₹)", value=float(rates['idu_rate']))
        new_stb_r = rc7.number_input("STB Recovery (₹)", value=float(rates['stb_rate']))
        new_odu_r = rc8.number_input("ODU Recovery (₹)", value=float(rates['odu_rate']))

        if st.button("💾 नए रेट्स अपडेट करें (Save All Rates)", type="primary"):
            c.execute('''
                INSERT OR REPLACE INTO commission_settings 
                (dist_id, fse_sim_rate, fse_mnp_rate, fse_recharge_pct, fse_daily_da, airfiber_rate, idu_rate, stb_rate, odu_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dist_id, new_sim_r, new_mnp_r, new_rch_p, new_da_r, new_af_r, new_idu_r, new_stb_r, new_odu_r))
            conn.commit()
            st.success("✅ आपके सभी कमीशन रेट्स अपडेट हो गए हैं! अब से सभी नए पे-आउट इसी दर से बनेंगे।")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    conn.close()

# ==============================================================================
# 6. APPLICATION ROUTING & CONTROLLER
# ==============================================================================
if not st.session_state['logged_in']:
    login_page()
else:
    # Sidebar Logout & Account Card
    with st.sidebar:
        st.markdown(f"**लॉगिन उपयोगकर्ता:** `{st.session_state['username']}`")
        st.markdown(f"**रोल:** `{st.session_state['role'].upper()}`")
        if st.button("🚪 सुरक्षित लॉगआउट (LOGOUT)", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.divider()

    # Route based on role
    if st.session_state['role'] == 'admin':
        admin_panel()
    else:
        distributor_panel()
