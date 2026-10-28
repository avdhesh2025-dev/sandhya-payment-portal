import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import io

# ==============================================================================
# 1. PAGE CONFIG & MODERN ULTRA-PRO GLASSMORPHISM + KHATABOOK UI STYLES
# ==============================================================================
st.set_page_config(
    page_title="Jio Distributor SaaS ERP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
/* 🌟 GLOBAL BACKGROUND & TYPOGRAPHY */
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], [data-testid="stMain"] { 
    background: #f1f5f9 !important;
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
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 2px solid #cbd5e1 !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.03) !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
    background: #ffffff !important;
    border-color: #1565c0 !important;
    box-shadow: 0 0 0 3px rgba(21, 101, 192, 0.15) !important;
}

/* 🌟 3D HERO BANNER */
.hero-banner {
    background: linear-gradient(135deg, #091e42 0%, #1565c0 60%, #1e88e5 100%);
    padding: 20px 24px;
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-bottom: 5px solid #0a1128;
    box-shadow: 0 12px 28px rgba(21, 101, 192, 0.25);
    color: #ffffff;
    margin-bottom: 18px;
}
.hero-title {
    font-size: 26px;
    font-weight: 900;
    margin: 0 0 4px 0;
    color: #ffffff !important;
    text-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
.hero-subtitle {
    font-size: 13px;
    font-weight: 600;
    color: #bbdefb !important;
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
    font-size: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 16px 0 14px 0;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.12);
}

/* 🌟 GLASS CONTAINER CARDS */
.glass-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-bottom: 4px solid #cbd5e1;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
    margin-bottom: 18px;
}

/* 🌟 METRIC WIDGETS */
.metric-card {
    text-align: center;
    padding: 16px 12px;
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    border-bottom: 5px solid #1565c0;
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
    border: 2px dashed #1565c0;
    border-radius: 16px;
    padding: 22px;
    margin-top: 15px;
    box-shadow: 0 8px 24px rgba(21, 101, 192, 0.08);
}

/* ==============================================================================
   🌟 KHATABOOK AUTHENTIC STYLING (FROM USER SCREENSHOTS)
============================================================================== */
.kb-topbar {
    background: #0d47a1;
    color: white;
    padding: 14px 20px;
    border-radius: 16px 16px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.kb-summary-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    margin-bottom: 16px;
}
.kb-summary-split {
    display: flex;
    justify-content: space-around;
    text-align: center;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 12px;
}
.kb-summary-label {
    font-size: 13px;
    font-weight: 700;
    color: #64748b;
    margin-bottom: 4px;
}
.kb-summary-dene {
    font-size: 24px;
    font-weight: 900;
    color: #16a34a;
}
.kb-summary-milenge {
    font-size: 24px;
    font-weight: 900;
    color: #dc2626;
}
.kb-report-link {
    text-align: center;
    padding-top: 10px;
    font-size: 14px;
    font-weight: 800;
    color: #1565c0;
    cursor: pointer;
}

/* Khatabook Customer List Card */
.kb-customer-card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    padding: 14px 16px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    transition: all 0.15s ease-in-out;
}
.kb-customer-card:hover {
    border-color: #93c5fd;
    box-shadow: 0 4px 12px rgba(21, 101, 192, 0.08);
}
.kb-avatar {
    width: 44px;
    height: 44px;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    color: #1e3a8a;
    font-size: 15px;
    margin-right: 14px;
    position: relative;
    flex-shrink: 0;
}
.kb-avatar-dot {
    width: 10px;
    height: 10px;
    background: #dc2626;
    border: 2px solid white;
    border-radius: 50%;
    position: absolute;
    top: 0;
    right: 0;
}
.kb-customer-name {
    font-size: 15px;
    font-weight: 900;
    color: #0f172a;
    margin: 0 0 2px 0;
}
.kb-customer-time {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    margin: 0;
}
.kb-amount-due {
    font-size: 18px;
    font-weight: 900;
    color: #dc2626;
    text-align: right;
}
.kb-amount-advance {
    font-size: 18px;
    font-weight: 900;
    color: #16a34a;
    text-align: right;
}
.kb-amount-zero {
    font-size: 18px;
    font-weight: 900;
    color: #475569;
    text-align: right;
}
.kb-remind-link {
    color: #1565c0 !important;
    font-size: 12px;
    font-weight: 800;
    text-decoration: none;
    display: block;
    text-align: right;
    margin-top: 2px;
}

/* Floating Customer Add Button */
.kb-fab {
    background: linear-gradient(135deg, #be185d 0%, #9d174d 100%) !important;
    color: white !important;
    font-weight: 900 !important;
    font-size: 15px !important;
    padding: 12px 24px !important;
    border-radius: 30px !important;
    box-shadow: 0 8px 20px rgba(190, 24, 93, 0.35) !important;
    border: none !important;
    text-align: center;
    margin: 14px auto;
    display: inline-block;
}

/* Khatabook Passbook View */
.kb-passbook-banner {
    background: #0d47a1;
    color: white;
    padding: 16px 20px;
    border-radius: 16px;
    margin-bottom: 14px;
}
.kb-balance-pill-barabar {
    background: #ffffff;
    border-radius: 12px;
    padding: 14px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 14px;
}
.kb-action-bar {
    display: flex;
    justify-content: space-around;
    background: #ffffff;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #e2e8f0;
    margin-bottom: 16px;
}
.kb-action-item {
    text-align: center;
    color: #1e3a8a;
    font-size: 13px;
    font-weight: 800;
    text-decoration: none;
}

/* Khatabook Transaction Row */
.kb-txn-date-header {
    text-align: center;
    font-size: 12px;
    font-weight: 800;
    color: #64748b;
    margin: 18px 0 8px 0;
}
.kb-txn-row {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.kb-txn-bal {
    background: #f1f5f9;
    color: #475569;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 800;
    display: inline-block;
    margin-bottom: 4px;
}

/* Big Dual Buttons */
.btn-diye {
    background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%) !important;
    color: #ffffff !important;
    font-weight: 900 !important;
    font-size: 16px !important;
    padding: 14px !important;
    border-radius: 12px !important;
    border: none !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(185, 28, 28, 0.3) !important;
}
.btn-mile {
    background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important;
    color: #ffffff !important;
    font-weight: 900 !important;
    font-size: 16px !important;
    padding: 14px !important;
    border-radius: 12px !important;
    border: none !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(21, 128, 61, 0.3) !important;
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
                created_at TEXT DEFAULT ''
            )
        ''')

        # Auto-migrate missing columns safely
        c = conn.cursor()
        try:
            c.execute("PRAGMA table_info(users)")
            u_cols = [r[1] for r in c.fetchall()]
            if 'business_name' not in u_cols:
                c.execute("ALTER TABLE users ADD COLUMN business_name TEXT DEFAULT ''")
            if 'phone' not in u_cols:
                c.execute("ALTER TABLE users ADD COLUMN phone TEXT DEFAULT ''")
            if 'status' not in u_cols:
                c.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active'")
            if 'created_at' not in u_cols:
                c.execute("ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT ''")
                c.execute("UPDATE users SET created_at = datetime('now') WHERE created_at = '' OR created_at IS NULL")
        except Exception:
            pass

        # 2. Module 1: Auto-refill & Retailer Ledger (Khatabook Store)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS auto_refill_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dist_id INTEGER NOT NULL,
                retailer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                amount_given REAL DEFAULT 0.0,
                amount_received REAL DEFAULT 0.0,
                payment_mode TEXT DEFAULT 'Etop transfer',
                remarks TEXT DEFAULT '',
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

        try:
            c.execute("PRAGMA table_info(commission_settings)")
            cs_cols = [r[1] for r in c.fetchall()]
            cols_to_add = [
                ('fse_sim_rate', 'REAL', 15.0),
                ('fse_mnp_rate', 'REAL', 50.0),
                ('fse_recharge_pct', 'REAL', 1.0),
                ('fse_daily_da', 'REAL', 100.0),
                ('airfiber_rate', 'REAL', 150.0),
                ('idu_rate', 'REAL', 40.0),
                ('stb_rate', 'REAL', 30.0),
                ('odu_rate', 'REAL', 50.0)
            ]
            for col_name, col_type, def_val in cols_to_add:
                if col_name not in cs_cols:
                    try:
                        c.execute(f"ALTER TABLE commission_settings ADD COLUMN {col_name} {col_type} DEFAULT {def_val}")
                    except Exception:
                        pass
            
            # Map legacy column values if they exist
            legacy_mappings = [('airfiber', 'airfiber_rate'), ('idu', 'idu_rate'), ('stb', 'stb_rate'), ('odu', 'odu_rate')]
            for old_c, new_c in legacy_mappings:
                if old_c in cs_cols:
                    try:
                        c.execute(f"UPDATE commission_settings SET {new_c} = {old_c} WHERE {old_c} IS NOT NULL")
                    except Exception:
                        pass
        except Exception:
            pass

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
                INSERT INTO users (username, password, role, business_name, phone, valid_until, status, created_at)
                VALUES ('avdhesh_admin', 'admin123', 'admin', 'Sandhya Enterprises Tech HQ', '9876543210', '2099-12-31', 'active', datetime('now'))
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
        if 'airfiber' in row_keys and row['airfiber'] is not None and rates['airfiber_rate'] == 150.0:
            try:
                rates['airfiber_rate'] = float(row['airfiber'])
            except Exception:
                pass
    conn.close()
    return rates

# Helper to extract initials
def get_initials(name):
    clean = name.strip()
    if not clean:
        return "R"
    parts = clean.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return clean[:2].upper()

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
if 'kb_selected_retailer' not in st.session_state:
    st.session_state['kb_selected_retailer'] = None
if 'kb_action_mode' not in st.session_state:
    st.session_state['kb_action_mode'] = None  # 'diye' or 'mile' or None

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
                        INSERT INTO users (username, password, role, business_name, phone, valid_until, status, created_at)
                        VALUES (?, ?, 'distributor', ?, ?, ?, 'active', datetime('now'))
                    ''', (new_username.strip(), new_password.strip(), biz_name.strip(), phone_no.strip(), expiry_date))
                    new_dist_id = c.lastrowid

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
            "1. 📒 Auto-refill & Retailer Ledger (Khatabook)",
            "2. 👥 FSE / DAB Payout & Slip",
            "3. 🌐 AirFiber Commission",
            "4. 📦 Recovery (IDU / STB / ODU)",
            "5. ⚙️ Commission Rate Settings"
        ]
    )

    rates = get_commission_rates(dist_id)

    # --------------------------------------------------------------------------
    # MODULE 1: AUTHENTIC KHATABOOK AUTO-REFILL & RETAILER LEDGER
    # --------------------------------------------------------------------------
    if "1. 📒 Auto-refill" in app_menu:
        # Check if a customer is selected for Passbook Detail View (Image 2)
        selected_cust = st.session_state.get('kb_selected_retailer')

        # ======================================================================
        # VIEW A: KHATABOOK CUSTOMER PASSBOOK DETAIL (IMAGE 2)
        # ======================================================================
        if selected_cust:
            # Back Button
            if st.button("⬅️ Wapas (Sabhi Retailers List)", type="secondary"):
                st.session_state['kb_selected_retailer'] = None
                st.session_state['kb_action_mode'] = None
                st.rerun()

            # Fetch retailer info & transactions
            df_cust_txns = pd.read_sql_query(f"""
                SELECT id, retailer_name, phone, amount_given, amount_received, payment_mode, remarks, date
                FROM auto_refill_ledger
                WHERE dist_id={dist_id} AND retailer_name=?
                ORDER BY id ASC
            """, conn, params=(selected_cust,))

            # Calculate Running Balances
            if not df_cust_txns.empty:
                df_cust_txns['net'] = df_cust_txns['amount_given'] - df_cust_txns['amount_received']
                df_cust_txns['running_bal'] = df_cust_txns['net'].cumsum()
                current_bal = df_cust_txns['running_bal'].iloc[-1]
                cust_phone = df_cust_txns['phone'].iloc[-1]
            else:
                current_bal = 0.0
                cust_phone = ""

            initials = get_initials(selected_cust)

            # Top Customer Header (Like Khatabook Blue Header)
            st.markdown(f"""
                <div class="kb-topbar">
                    <div style="display:flex; align-items:center;">
                        <div class="kb-avatar" style="background:#ffffff; color:#0d47a1; margin-right:12px;">{initials}</div>
                        <div>
                            <div style="font-size:18px; font-weight:900;">{selected_cust.upper()} {cust_phone}</div>
                            <div style="font-size:12px; color:#bbdefb;">Settings Dekhein • Jio LAPU Retailer</div>
                        </div>
                    </div>
                    <div>
                        {f'<a href="tel:+91{cust_phone}" style="background:#ffffff; color:#0d47a1; padding:8px 14px; border-radius:10px; font-weight:900; text-decoration:none;">📞 Call</a>' if cust_phone else ''}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Balance Banner Card
            if current_bal == 0:
                bal_status_text = "Balance barabar"
                bal_color = "#16a34a"
                bal_icon = "✅"
            elif current_bal > 0:
                bal_status_text = "Aapko Milenge (Due)"
                bal_color = "#dc2626"
                bal_icon = "🔴"
            else:
                bal_status_text = "Aapko Dene Hain (Advance)"
                bal_color = "#16a34a"
                bal_icon = "🟢"

            st.markdown(f"""
                <div class="kb-balance-pill-barabar" style="border-left: 6px solid {bal_color}; margin-top:10px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:18px;">{bal_icon}</span>
                        <span style="font-size:17px; font-weight:900; color:{bal_color};">{bal_status_text}</span>
                    </div>
                    <div style="font-size:24px; font-weight:900; color:{bal_color};">
                        ₹ {abs(current_bal):,.2f}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Action Bar (Report, WhatsApp Reminder, SMS)
            reminder_text = (
                f"नमस्ते {selected_cust} जी,\n\n"
                f"यह *{biz_name}* (Jio Distributor) की तरफ से ऑटो-रिफिल बकाया पेमेंट का सूचना संदेश है:\n"
                f"👉 *वर्तमान बकाया राशि: ₹{current_bal:,.2f}*\n\n"
                f"कृपया बकाया राशि आज ही कैश या ऑनलाइन जमा कराने की कृपा करें। धन्यवाद!"
            )
            encoded_reminder = urllib.parse.quote(reminder_text)
            wa_reminder_url = f"https://api.whatsapp.com/send?phone=91{cust_phone}&text={encoded_reminder}" if cust_phone else "#"

            col_act1, col_act2, col_act3 = st.columns(3)
            with col_act1:
                # PDF / CSV Download Statement
                csv_passbook = io.StringIO()
                if not df_cust_txns.empty:
                    df_cust_txns[['date', 'payment_mode', 'amount_given', 'amount_received', 'running_bal', 'remarks']].to_csv(csv_passbook, index=False)
                st.download_button("📄 Report Download", data=csv_passbook.getvalue(), file_name=f"{selected_cust}_Ledger.csv", use_container_width=True)
            with col_act2:
                if cust_phone:
                    st.markdown(f'<a href="{wa_reminder_url}" target="_blank" style="text-align:center; display:block; background:#25D366; color:white; font-weight:800; padding:10px; border-radius:10px; text-decoration:none;">💬 Reminder (WhatsApp)</a>', unsafe_allow_html=True)
                else:
                    st.button("💬 Reminder (No Phone)", disabled=True, use_container_width=True)
            with col_act3:
                if cust_phone:
                    st.markdown(f'<a href="tel:+91{cust_phone}" style="text-align:center; display:block; background:#0284c7; color:white; font-weight:800; padding:10px; border-radius:10px; text-decoration:none;">📞 Phone Call</a>', unsafe_allow_html=True)
                else:
                    st.button("📞 Phone Call", disabled=True, use_container_width=True)

            st.divider()

            # Entry Form Trigger (When either Big Button is Clicked)
            action_mode = st.session_state.get('kb_action_mode')
            if action_mode in ['diye', 'mile']:
                is_diye = (action_mode == 'diye')
                form_title = "🔴 AAPNE DIYE ₹ (Auto-refill / E-top Diya)" if is_diye else "🟢 AAPKO MILE ₹ (Cash / AC Transfer Mila)"
                form_bg = "#fef2f2" if is_diye else "#f0fdf4"

                st.markdown(f"""
                    <div style="background:{form_bg}; border:2px solid {'#b91c1c' if is_diye else '#15803d'}; border-radius:16px; padding:18px; margin-bottom:16px;">
                        <h4 style="margin:0 0 10px 0; color:{'#b91c1c' if is_diye else '#15803d'}; font-weight:900;">{form_title}</h4>
                    </div>
                """, unsafe_allow_html=True)

                with st.form("khatabook_entry_form", clear_on_submit=True):
                    fe_c1, fe_c2 = st.columns(2)
                    entry_amt = fe_c1.number_input("राशि (Amount ₹)*", min_value=1.0, step=100.0, value=2000.0)
                    
                    if is_diye:
                        entry_mode = fe_c2.selectbox("माध्यम / टाइप (Entry Type)", ["Etop transfer", "Auto-refill", "Lapu Recharge", "SIM stock", "Other"])
                    else:
                        entry_mode = fe_c2.selectbox("माध्यम / टाइप (Payment Type)", ["AC transfer", "Cash", "PhonePe / GPay / UPI", "MNP scheme", "Bank Deposit"])

                    fe_c3, fe_c4 = st.columns(2)
                    entry_date_str = fe_c3.text_input("तारीख व समय (Date & Time)", value=datetime.now().strftime('%Y-%m-%d %I:%M %p'))
                    entry_rem = fe_c4.text_input("रिमार्क्स / नोट (Optional Remarks)", placeholder="e.g. Morning 10AM refill")

                    submit_entry = st.form_submit_button("💾 Save Entry", type="primary", use_container_width=True)
                    if submit_entry:
                        given_val = entry_amt if is_diye else 0.0
                        received_val = 0.0 if is_diye else entry_amt
                        c.execute('''
                            INSERT INTO auto_refill_ledger (dist_id, retailer_name, phone, amount_given, amount_received, payment_mode, remarks, date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (dist_id, selected_cust, cust_phone, given_val, received_val, entry_mode, entry_rem, entry_date_str))
                        conn.commit()
                        st.session_state['kb_action_mode'] = None
                        st.success("✅ एंट्री सफलतापूर्वक सेव हो गई!")
                        st.rerun()

            # Transaction History Table Grouped by Date (Exact Khatabook Passbook Layout)
            st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:#f8fafc; border-radius:10px; font-weight:900; font-size:13px; color:#475569; margin-bottom:10px; border:1px solid #e2e8f0;">
                    <div style="flex:2;">ENTRIES</div>
                    <div style="flex:1; text-align:right; color:#b91c1c;">AAPNE DIYE</div>
                    <div style="flex:1; text-align:right; color:#15803d;">AAPKO MILE</div>
                </div>
            """, unsafe_allow_html=True)

            if df_cust_txns.empty:
                st.info("इस रिटेलर के लिए अभी कोई लेनदेन दर्ज नहीं है। नीचे दिए गए बटनों से पहली एंट्री दर्ज करें।")
            else:
                # Reverse order for Passbook stream (latest on top)
                df_reversed = df_cust_txns.iloc[::-1]

                for _, txn in df_reversed.iterrows():
                    amt_given = txn['amount_given']
                    amt_received = txn['amount_received']
                    run_bal = txn['running_bal']
                    pay_mode = txn['payment_mode'] or 'Transaction'
                    t_date = txn['date']

                    diye_cell = f"<div style='flex:1; text-align:right; font-size:17px; font-weight:900; color:#b91c1c; background:#fef2f2; padding:10px 12px; border-radius:8px;'>₹ {amt_given:,.0f}</div>" if amt_given > 0 else "<div style='flex:1;'></div>"
                    mile_cell = f"<div style='flex:1; text-align:right; font-size:17px; font-weight:900; color:#15803d; background:#f0fdf4; padding:10px 12px; border-radius:8px;'>₹ {amt_received:,.0f}</div>" if amt_received > 0 else "<div style='flex:1;'></div>"

                    st.markdown(f"""
                        <div class="kb-txn-row">
                            <div style="flex:2;">
                                <div style="font-size:13px; color:#64748b; font-weight:700;">{t_date}</div>
                                <div style="margin:4px 0;"><span class="kb-txn-bal">Bal. ₹ {run_bal:,.0f}</span></div>
                                <div style="font-size:14px; font-weight:800; color:#1e293b;">{pay_mode}</div>
                            </div>
                            {diye_cell}
                            {mile_cell}
                        </div>
                    """, unsafe_allow_html=True)

            st.write("")
            # Bottom Dual Action Buttons (Khatabook Style Sticky Bottom)
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🔴 AAPNE DIYE ₹", key="btn_diye_trigger", use_container_width=True):
                    st.session_state['kb_action_mode'] = 'diye'
                    st.rerun()
            with btn_col2:
                if st.button("🟢 AAPKO MILE ₹", key="btn_mile_trigger", use_container_width=True):
                    st.session_state['kb_action_mode'] = 'mile'
                    st.rerun()

        # ======================================================================
        # VIEW B: KHATABOOK CUSTOMER LIST (IMAGE 1)
        # ======================================================================
        else:
            # Khatabook Top Business Header
            st.markdown(f"""
                <div class="kb-topbar">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:22px;">📖</span>
                        <div>
                            <div style="font-size:18px; font-weight:900;">{biz_name.upper()} ▾</div>
                            <div style="font-size:12px; color:#bbdefb;">CUSTOMERS & SUPPLIERS LEDGER</div>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.2); padding:6px 12px; border-radius:20px; font-weight:900; font-size:13px;">
                        🪙 Sandhya SaaS
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Aggregate Customer Balances
            df_cust_agg = pd.read_sql_query(f"""
                SELECT retailer_name, phone,
                       SUM(amount_given) as total_given,
                       SUM(amount_received) as total_received,
                       (SUM(amount_given) - SUM(amount_received)) as net_balance,
                       MAX(date) as last_txn_date
                FROM auto_refill_ledger
                WHERE dist_id={dist_id}
                GROUP BY retailer_name
                ORDER BY last_txn_date DESC
            """, conn)

            # Calculate "Aapko dene hain" vs "Aapko Milenge"
            if not df_cust_agg.empty:
                aapko_milenge = df_cust_agg[df_cust_agg['net_balance'] > 0]['net_balance'].sum()
                aapko_dene_hain = abs(df_cust_agg[df_cust_agg['net_balance'] < 0]['net_balance'].sum())
            else:
                aapko_milenge = 0.0
                aapko_dene_hain = 0.0

            # Khatabook Summary Card (Exact Image 1 Header Card)
            st.markdown(f"""
                <div class="kb-summary-card">
                    <div class="kb-summary-split">
                        <div>
                            <div class="kb-summary-label">Aapko dene hain</div>
                            <div class="kb-summary-dene">₹ {aapko_dene_hain:,.0f}</div>
                        </div>
                        <div style="border-right: 1px solid #f1f5f9;"></div>
                        <div>
                            <div class="kb-summary-label">Aapko Milenge</div>
                            <div class="kb-summary-milenge">₹ {aapko_milenge:,.0f}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Download Report Button
            csv_all_rep = io.StringIO()
            if not df_cust_agg.empty:
                df_cust_agg.to_csv(csv_all_rep, index=False)
            st.download_button(
                label="📄 Reports Dekhein (Download CSV Ledger)",
                data=csv_all_rep.getvalue(),
                file_name=f"Khatabook_Summary_{datetime.now().strftime('%Y%m%d')}.csv",
                use_container_width=True
            )

            # Search bar + Add Customer Row
            s_col1, s_col2 = st.columns([3, 1])
            search_query = s_col1.text_input("🔍 Customer search karein", placeholder="Search by name or phone...", label_visibility="collapsed")
            with s_col2:
                add_new_expander = st.expander("➕ CUSTOMER ADD KAREIN", expanded=False)

            with add_new_expander:
                with st.form("add_new_customer_form", clear_on_submit=True):
                    st.markdown("#### ➕ नया कस्टमर / रिटेलर जोड़ें")
                    nc_name = st.text_input("Customer / Retailer Name*", placeholder="जैसे: RK DIGITAL POINT")
                    nc_phone = st.text_input("Phone / LAPU Number*", placeholder="जैसे: 663144037")
                    nc_opening = st.number_input("Opening Balance (यदि पहले से बकाया हो तो भरें ₹)", min_value=0.0, step=100.0, value=0.0)
                    nc_mode = st.selectbox("Opening Type", ["Aapko Milenge (Due)", "Aapko Dene Hain (Advance)"])
                    
                    submit_nc = st.form_submit_button("💾 Save Customer", type="primary")
                    if submit_nc:
                        if not nc_name.strip():
                            st.error("कृपया कस्टमर का नाम दर्ज करें!")
                        else:
                            clean_p = ''.join(filter(str.isdigit, nc_phone))
                            date_now = datetime.now().strftime('%Y-%m-%d %I:%M %p')
                            g_val = nc_opening if nc_mode == "Aapko Milenge (Due)" else 0.0
                            r_val = nc_opening if nc_mode == "Aapko Dene Hain (Advance)" else 0.0
                            c.execute('''
                                INSERT INTO auto_refill_ledger (dist_id, retailer_name, phone, amount_given, amount_received, payment_mode, remarks, date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (dist_id, nc_name.strip(), clean_p, g_val, r_val, 'Opening Balance', 'Initial setup', date_now))
                            conn.commit()
                            st.success(f"✅ {nc_name} सफलतापूर्वक जुड़ गया!")
                            st.rerun()

            # Filter customer list by search query
            if not df_cust_agg.empty and search_query:
                filtered_customers = df_cust_agg[
                    df_cust_agg['retailer_name'].str.contains(search_query, case=False, na=False) |
                    df_cust_agg['phone'].str.contains(search_query, case=False, na=False)
                ]
            else:
                filtered_customers = df_cust_agg

            # Customer List Render (Exact Image 1 Design)
            if filtered_customers.empty:
                st.info("कोई कस्टमर नहीं मिला। ऊपर दिए गए '+ CUSTOMER ADD KAREIN' से नया रिटेलर जोड़ें।")
            else:
                for idx, row in filtered_customers.iterrows():
                    c_name = row['retailer_name']
                    c_phone = row['phone']
                    c_bal = row['net_balance']
                    c_date = row['last_txn_date'] or "हाल ही में"
                    c_initials = get_initials(c_name)

                    # Reminder link for WhatsApp
                    reminder_msg = (
                        f"नमस्ते {c_name} जी,\n\n"
                        f"यह *{biz_name}* (Jio Distributor) की तरफ से ऑटो-रिफिल बकाया पेमेंट का सूचना संदेश है:\n"
                        f"👉 *वर्तमान बकाया राशि: ₹{c_bal:,.2f}*\n\n"
                        f"कृपया बकाया राशि आज ही कैश या ऑनलाइन जमा कराने की कृपा करें। धन्यवाद!"
                    )
                    wa_url = f"https://api.whatsapp.com/send?phone=91{c_phone}&text={urllib.parse.quote(reminder_msg)}" if c_phone else "#"

                    # Card Row with Columns
                    card_col1, card_col2, card_col3 = st.columns([4, 2, 2])
                    
                    with card_col1:
                        st.markdown(f"""
                            <div style="display:flex; align-items:center;">
                                <div class="kb-avatar">
                                    {c_initials}
                                    {f'<div class="kb-avatar-dot"></div>' if c_bal > 0 else ''}
                                </div>
                                <div>
                                    <div class="kb-customer-name">{c_name.upper()} {c_phone}</div>
                                    <div class="kb-customer-time">{c_date}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                    with card_col2:
                        if c_bal > 0:
                            st.markdown(f"""
                                <div class="kb-amount-due">₹ {c_bal:,.0f}</div>
                                {f'<a href="{wa_url}" target="_blank" class="kb-remind-link">REMIND KARAYEIN &gt;</a>' if c_phone else ''}
                            """, unsafe_allow_html=True)
                        elif c_bal < 0:
                            st.markdown(f"""
                                <div class="kb-amount-advance">₹ {abs(c_bal):,.0f}</div>
                                <div style="font-size:11px; color:#16a34a; font-weight:800; text-align:right;">ADVANCE</div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div class="kb-amount-zero">₹ 0</div>
                                <div style="font-size:11px; color:#64748b; font-weight:700; text-align:right;">SETTLED</div>
                            """, unsafe_allow_html=True)

                    with card_col3:
                        if st.button("📖 खाता खोलें", key=f"open_cust_{idx}", use_container_width=True):
                            st.session_state['kb_selected_retailer'] = c_name
                            st.session_state['kb_action_mode'] = None
                            st.rerun()

                    st.markdown("<hr style='margin: 8px 0; border: none; border-bottom: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

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
                            <h3 style="margin:0; color:#1565c0;">📄 JIO FSE / DAB PAYMENT SLIP</h3>
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
                    <h3 style="margin:0; color:#1565c0;">⚡ JIO AIRFIBER COMMISSION SLIP</h3>
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
                    <h3 style="margin:0; color:#1565c0;">📦 JIO DEVICE RECOVERY SLIP</h3>
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
    with st.sidebar:
        st.markdown(f"**लॉगिन उपयोगकर्ता:** `{st.session_state['username']}`")
        st.markdown(f"**रोल:** `{st.session_state['role'].upper()}`")
        if st.button("🚪 सुरक्षित लॉगआउट (LOGOUT)", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.divider()

    if st.session_state['role'] == 'admin':
        admin_panel()
    else:
        distributor_panel()
