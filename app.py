import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import io
import os

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

/* 🌟 QR PAYMENT CARD */
.qr-card {
    background: #ffffff;
    border: 2px solid #0d47a1;
    border-radius: 20px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 14px 36px rgba(13, 71, 161, 0.15);
    max-width: 480px;
    margin: 10px auto;
}

/* ==============================================================================
   🌟 KHATABOOK AUTHENTIC STYLING
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

        # 7. Renewal Payment Requests Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS renewal_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                utr_number TEXT NOT NULL,
                amount REAL DEFAULT 0.0,
                request_date TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
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

# Safe Date Formatter (Indian Clear Format: 27-Nov-2026)
def format_date_indian(date_str):
    if not date_str:
        return "N/A"
    try:
        dt = datetime.strptime(str(date_str).strip(), '%Y-%m-%d')
        return dt.strftime('%d-%b-%Y')
    except Exception:
        return str(date_str)

# Safe Commission Rates Loader
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
    conn.close()
    return rates

def get_initials(name):
    clean = name.strip()
    if not clean:
        return "R"
    parts = clean.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return clean[:2].upper()

# ==============================================================================
# 3. AUTHENTICATION & PAYMENT RENEWAL SCREEN
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
if 'show_renewal_screen' not in st.session_state:
    st.session_state['show_renewal_screen'] = False
if 'renewal_user_info' not in st.session_state:
    st.session_state['renewal_user_info'] = None
if 'kb_selected_retailer' not in st.session_state:
    st.session_state['kb_selected_retailer'] = None
if 'kb_action_mode' not in st.session_state:
    st.session_state['kb_action_mode'] = None

# Screen: Paytm UPI QR Code Renewal Screen
def render_renewal_payment_screen(user_data):
    st.markdown("""
        <div class="hero-banner" style="text-align:center; max-width: 600px; margin: 20px auto;">
            <div style="font-size: 36px;">📱⚡</div>
            <h1 class="hero-title">खाता नवीनीकरण एवं UPI पेमेंट</h1>
            <p class="hero-subtitle">Sandhya Enterprises • Jio SaaS ERP License Renewal</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="qr-card">', unsafe_allow_html=True)
        
        reason = "🚫 आपका खाता सस्पेंड / ब्लॉक कर दिया गया है।" if user_data.get('status') == 'suspended' else f"⌛ आपका 1 महीने का प्लान समाप्त हो चुका है (समाप्त तारीख: {format_date_indian(user_data.get('valid_until'))})।"
        st.error(reason)
        st.markdown("<h4 style='color:#0d47a1; margin:6px 0;'>📲 Paytm / PhonePe / GPay QR Code स्कैन करें</h4>", unsafe_allow_html=True)

        # Show QR image if available on disk or generate dynamic QR
        qr_file_path = "paytm_qr.jpg"
        if os.path.exists(qr_file_path):
            st.image(qr_file_path, caption="Paytm QR Standee • UPI ID: paytm.s3h7o0c@pty", use_container_width=True)
        else:
            qr_api_url = "https://api.qrserver.com/v1/create-qr-code/?size=260x260&data=upi://pay?pa=paytm.s3h7o0c@pty%26pn=Sandhya%20Enterprises%26cu=INR"
            st.image(qr_api_url, caption="Scan to Pay • Sandhya Enterprises", width=260)

        st.markdown("""
            <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:12px; padding:12px; margin:14px 0; text-align:left;">
                <div style="font-size:13px; color:#64748b; font-weight:700;">PAYMENT DETAILS:</div>
                <div style="font-size:16px; color:#0f172a; font-weight:900; margin-top:4px;">UPI ID: <span style="color:#0d47a1;">paytm.s3h7o0c@pty</span></div>
                <div style="font-size:14px; color:#1e293b; font-weight:800;">पेई नाम: Sandhya Enterprises (Avdhesh Sir)</div>
                <div style="font-size:13px; color:#16a34a; font-weight:800; margin-top:4px;">वैधता: +30 दिन (1 महीना रिन्यूअल)</div>
            </div>
        """, unsafe_allow_html=True)

        # Direct UPI App Link and WhatsApp Share
        upi_pay_link = "upi://pay?pa=paytm.s3h7o0c@pty&pn=Sandhya%20Enterprises&cu=INR"
        wa_text = f"नमस्ते अवधेश जी, मैंने Jio SaaS ERP (Username: {user_data['username']}) का 1 महीने का रिन्यूअल पेमेंट कर दिया है। कृपया मेरा खाता एक्टिवेट कर दें।"
        wa_url = f"https://api.whatsapp.com/send?phone=919876543210&text={urllib.parse.quote(wa_text)}"

        btn_c1, btn_c2 = st.columns(2)
        btn_c1.markdown(f'<a href="{upi_pay_link}" style="display:block; text-align:center; background:#0d47a1; color:white; font-weight:900; padding:10px; border-radius:10px; text-decoration:none;">📱 Pay via UPI</a>', unsafe_allow_html=True)
        btn_c2.markdown(f'<a href="{wa_url}" target="_blank" style="display:block; text-align:center; background:#25D366; color:white; font-weight:900; padding:10px; border-radius:10px; text-decoration:none;">💬 WhatsApp स्लिप</a>', unsafe_allow_html=True)

        st.markdown("<hr style='margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("#### ⚡ पेमेंट कर दिया? UTR नंबर दर्ज करें:")
        
        with st.form("utr_submit_form"):
            utr_no = st.text_input("12-Digit UPI UTR / Transaction ID*", placeholder="e.g. 429817263541")
            paid_amount = st.number_input("भुगतान की गई राशि (Amount Paid ₹)", min_value=1.0, value=500.0, step=100.0)
            submit_utr = st.form_submit_button("🚀 एक्टिवेशन रिक्वेस्ट सबमिट करें", type="primary", use_container_width=True)

            if submit_utr:
                if not utr_no.strip():
                    st.error("कृपया बैंक UTR / ट्रांजैक्शन नंबर दर्ज करें!")
                else:
                    conn = get_db()
                    req_date = datetime.now().strftime('%d-%b-%Y %I:%M %p')
                    conn.execute('''
                        INSERT INTO renewal_requests (user_id, username, utr_number, amount, request_date, status)
                        VALUES (?, ?, ?, ?, ?, 'pending')
                    ''', (user_data['id'], user_data['username'], utr_no.strip(), paid_amount, req_date))
                    conn.commit()
                    conn.close()
                    st.success("🎉 आपकी पेमेंट रिक्वेस्ट सफलतापूर्वक सबमिट हो गई! अवधेश जी द्वारा वेरिफाई करते ही खाता तुरंत एक्टिवेट हो जाएगा।")

        if st.button("⬅️ लॉगिन पेज पर वापस जाएं", use_container_width=True):
            st.session_state['show_renewal_screen'] = False
            st.session_state['renewal_user_info'] = None
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

def login_page():
    if st.session_state.get('show_renewal_screen') and st.session_state.get('renewal_user_info'):
        render_renewal_payment_screen(st.session_state['renewal_user_info'])
        return

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
                        else:
                            # User is expired or suspended -> Show QR payment renewal screen!
                            st.session_state['show_renewal_screen'] = True
                            st.session_state['renewal_user_info'] = dict(user)
                            st.rerun()
                    else:
                        st.error("❌ अमान्य यूजरनेम या पासवर्ड!")
            st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 4. SUPER ADMIN CONTROL PANEL (AVDHESH CONTROL & DATA INSPECTOR)
# ==============================================================================
def admin_panel():
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-title">⚙️ SUPER ADMIN CONTROL HUB (AVDHESH)</h1>
            <p class="hero-subtitle">Distributor Account Provisioning, 30-Day Validity, UPI Approvals & Full Multi-Tenant Data Inspector</p>
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

    # Pending renewal count
    c.execute("SELECT COUNT(*) FROM renewal_requests WHERE status='pending'")
    pending_renewals = c.fetchone()[0]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
            <div class="metric-card">
                <h4>👥 कुल डिस्ट्रीब्यूटर्स (Total)</h4>
                <h2>{total_dist}</h2>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
            <div class="metric-card metric-card-success">
                <h4>🟢 एक्टिव (Active & Valid)</h4>
                <h2 style="color:#16a34a;">{active_dist}</h2>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
            <div class="metric-card metric-card-danger">
                <h4>🔴 एक्सपायर्ड / ब्लॉक (Due)</h4>
                <h2 style="color:#dc2626;">{expired_dist}</h2>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
            <div class="metric-card" style="border-bottom: 5px solid #eab308; background:#fefce8;">
                <h4>🔔 पेमेंट रिक्वेस्ट्स (Pending)</h4>
                <h2 style="color:#ca8a04;">{pending_renewals}</h2>
            </div>
        """, unsafe_allow_html=True)

    tab_manage, tab_approvals, tab_inspect, tab_add, tab_settings = st.tabs([
        "📋 Distributor Roster", 
        f"🔔 UPI Approvals ({pending_renewals})", 
        "🕵️ डिस्ट्रीब्यूटर डेटा इंस्पेक्टर (Help Mode)", 
        "➕ Add New Distributor (30 Days)", 
        "🔐 Admin Settings"
    ])

    # --- TAB 1: PENDING UPI APPROVALS ---
    with tab_approvals:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🔔 पेंडिंग पेमेंट एवं 1-क्लिक रिन्यूअल अप्रूवल")
        st.caption("जब कोई डिस्ट्रीब्यूटर आपके Paytm QR (`paytm.s3h7o0c@pty`) पर पैसे भेजकर UTR दर्ज करेगा, यहाँ दिखेगा। 'Approve' दबाते ही खाता 30 दिन के लिए चालू हो जाएगा।")

        df_reqs = pd.read_sql_query("SELECT * FROM renewal_requests WHERE status='pending' ORDER BY id DESC", conn)
        if df_reqs.empty:
            st.info("अभी कोई नई पेमेंट रिक्वेस्ट पेंडिंग नहीं है।")
        else:
            for idx, r_row in df_reqs.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div style="background:#fefce8; border:1px solid #fef08a; border-left:6px solid #eab308; border-radius:12px; padding:14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h4 style="margin:0; font-size:17px; color:#854d0e;">👤 डिस्ट्रीब्यूटर: {r_row['username']}</h4>
                                <div style="color:#713f12; font-size:14px; margin-top:4px;">
                                    🧾 <b>UTR / Ref No:</b> <code style="background:#ffffff; padding:2px 8px; border-radius:6px; font-weight:900;">{r_row['utr_number']}</code> | 
                                    💰 <b>राशि:</b> ₹{r_row['amount']} | 
                                    📅 <b>समय:</b> {r_row['request_date']}
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    btn_app1, btn_app2 = st.columns([1, 4])
                    if btn_app1.button(f"🟢 Approve & Activate (+30 Days)", key=f"app_{r_row['id']}", type="primary"):
                        today = datetime.now().date()
                        new_exp = (today + timedelta(days=30)).strftime('%Y-%m-%d')
                        c.execute("UPDATE users SET valid_until=?, status='active' WHERE username=?", (new_exp, r_row['username']))
                        c.execute("UPDATE renewal_requests SET status='approved' WHERE id=?", (r_row['id'],))
                        conn.commit()
                        st.success(f"🎉 {r_row['username']} का खाता 30 दिन के लिए एक्टिवेट कर दिया गया! (Valid Till: {format_date_indian(new_exp)})")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 2: DISTRIBUTOR DATA INSPECTOR & HELP MODE ---
    with tab_inspect:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🕵️ किसी भी डिस्ट्रीब्यूटर का डेटा देखें एवं सहायता करें (Admin Support Mode)")
        st.caption("यहाँ से आप किसी भी डिस्ट्रीब्यूटर का खाताबुक, रिटेलर बकाया, FSE पेमेंट स्लिप देख सकते हैं और ज़रूरत पड़ने पर उनके लिए एंट्री भी कर सकते हैं।")

        df_all_dists = pd.read_sql_query("SELECT id, username, business_name, phone, valid_until, status FROM users WHERE role='distributor'", conn)
        if df_all_dists.empty:
            st.info("कोई डिस्ट्रीब्यूटर मौजूद नहीं है।")
        else:
            dist_options = {f"{r['username']} ({r['business_name'] or 'Agency'} - ID: {r['id']})": r['id'] for _, r in df_all_dists.iterrows()}
            selected_dist_label = st.selectbox("डिस्ट्रीब्यूटर चुनें (Select Distributor to Inspect):", list(dist_options.keys()))
            insp_dist_id = dist_options[selected_dist_label]

            # Inspector Sub-tabs
            ins_tab1, ins_tab2, ins_tab3 = st.tabs(["📒 रिटेलर खाताबुक व लेजर", "👥 FSE / DAB स्टाफ पेमेंट्स", "🌐 AirFiber & रिकवरी"])

            with ins_tab1:
                # Distributor's Khatabook Aggregates
                c.execute("SELECT SUM(amount_given), SUM(amount_received) FROM auto_refill_ledger WHERE dist_id=?", (insp_dist_id,))
                sums = c.fetchone()
                d_given = sums[0] if (sums and sums[0]) else 0.0
                d_recv = sums[1] if (sums and sums[1]) else 0.0
                d_due = d_given - d_recv

                m_c1, m_c2, m_c3 = st.columns(3)
                m_c1.metric("कुल ऑटो-रिफिल दिया", f"₹ {d_given:,.0f}")
                m_c2.metric("कुल कैश मिला", f"₹ {d_recv:,.0f}")
                m_c3.metric("मार्केट में बकाया", f"₹ {d_due:,.0f}")

                df_d_retailers = pd.read_sql_query(f"""
                    SELECT retailer_name, phone, 
                           SUM(amount_given) as total_given, 
                           SUM(amount_received) as total_received,
                           (SUM(amount_given) - SUM(amount_received)) as due_balance,
                           MAX(date) as last_date
                    FROM auto_refill_ledger WHERE dist_id={insp_dist_id}
                    GROUP BY retailer_name ORDER BY due_balance DESC
                """, conn)

                if df_d_retailers.empty:
                    st.info("इस डिस्ट्रीब्यूटर के पास अभी कोई रिटेलर एंट्री नहीं है।")
                else:
                    st.dataframe(df_d_retailers, use_container_width=True, hide_index=True)

                st.markdown("#### ➕ इस डिस्ट्रीब्यूटर के लिए एंट्री दर्ज करें (Admin Support Entry)")
                with st.form("admin_support_entry"):
                    sc1, sc2 = st.columns(2)
                    r_name_inp = sc1.text_input("रिटेलर का नाम*")
                    r_phone_inp = sc2.text_input("फोन नंबर")

                    sc3, sc4 = st.columns(2)
                    give_val = sc3.number_input("ऑटो-रिफिल दिया (₹)", min_value=0.0, step=100.0, value=0.0)
                    recv_val = sc4.number_input("कैश प्राप्त हुआ (₹)", min_value=0.0, step=100.0, value=0.0)

                    sub_support = st.form_submit_button("💾 डिस्ट्रीब्यूटर के खाते में सेव करें", type="primary")
                    if sub_support and r_name_inp:
                        d_now = datetime.now().strftime('%Y-%m-%d %I:%M %p')
                        c.execute('''
                            INSERT INTO auto_refill_ledger (dist_id, retailer_name, phone, amount_given, amount_received, payment_mode, remarks, date)
                            VALUES (?, ?, ?, ?, ?, 'Admin Support', 'Added by Admin', ?)
                        ''', (insp_dist_id, r_name_inp.strip(), r_phone_inp.strip(), give_val, recv_val, d_now))
                        conn.commit()
                        st.success(f"✅ एंट्री सेव हो गई! ({r_name_inp})")
                        st.rerun()

            with ins_tab2:
                df_d_fse = pd.read_sql_query(f"SELECT * FROM fse_entries WHERE dist_id={insp_dist_id} ORDER BY id DESC", conn)
                if df_d_fse.empty:
                    st.info("कोई FSE रिकॉर्ड नहीं है।")
                else:
                    st.dataframe(df_d_fse, use_container_width=True, hide_index=True)

            with ins_tab3:
                c1_a, c2_a = st.columns(2)
                with c1_a:
                    st.markdown("##### 🌐 AirFiber Installs")
                    df_d_af = pd.read_sql_query(f"SELECT * FROM airfiber_entries WHERE dist_id={insp_dist_id} ORDER BY id DESC", conn)
                    st.dataframe(df_d_af, use_container_width=True, hide_index=True)
                with c2_a:
                    st.markdown("##### 📦 Device Recoveries")
                    df_d_rec = pd.read_sql_query(f"SELECT * FROM recovery_entries WHERE dist_id={insp_dist_id} ORDER BY id DESC", conn)
                    st.dataframe(df_d_rec, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 3: ROSTER & VALIDITY MANAGEMENT ---
    with tab_manage:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🏢 डिस्ट्रीब्यूटर लिस्ट एवं 1-क्लिक रिन्यूअल (+30 Days)")
        
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

                formatted_exp = format_date_indian(row['valid_until'])

                with st.expander(f"🏢 {row['business_name'] or row['username']} (ID: {row['id']}) — Valid Till: {formatted_exp} ({status_text})"):
                    ec1, ec2, ec3, ec4 = st.columns(4)
                    ec1.write(f"**Username:** `{row['username']}`")
                    ec2.write(f"**Phone:** `{row['phone'] or 'N/A'}`")
                    ec3.write(f"**Valid Till:** `{formatted_exp}`")
                    ec4.markdown(f"**Account Status:** <span style='color:{status_color}; font-weight:900;'>{status_text}</span>", unsafe_allow_html=True)

                    btn_c1, btn_c2, btn_c3 = st.columns(3)
                    with btn_c1:
                        if st.button(f"⚡ +30 दिन रिन्यू करें (पेमेंट आ गया)", key=f"renew_{row['id']}"):
                            base_date = max(today, valid_date)
                            new_expiry = (base_date + timedelta(days=30)).strftime('%Y-%m-%d')
                            c.execute("UPDATE users SET valid_until=?, status='active' WHERE id=?", (new_expiry, row['id']))
                            conn.commit()
                            st.success(f"✅ {row['username']} का अकाउंट 30 दिन के लिए रिन्यू कर दिया गया! नई तारीख: {format_date_indian(new_expiry)}")
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

    # --- TAB 4: ADD NEW DISTRIBUTOR (CLEAR 30-DAY VALIDITY) ---
    with tab_add:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### ➕ नया डिस्ट्रीब्यूटर ऐप ऑनबोर्ड करें (1-Month License)")
        st.caption("नया खाता डिफ़ॉल्ट रूप से आज से ठीक 30 दिनों (1 महीना) की वैधता पर एक्टिवेट होगा।")

        c1, c2 = st.columns(2)
        new_username = c1.text_input("Username (लॉगिन आईडी)*", placeholder="e.g. dist_patna_rajesh")
        new_password = c2.text_input("Password (पासवर्ड)*", value="jio1234")

        c3, c4 = st.columns(2)
        biz_name_inp = c3.text_input("Agency / Business Name", placeholder="e.g. Rajesh Telecom Agency")
        phone_no = c4.text_input("Distributor Contact Phone", placeholder="e.g. 9876543210")

        # Plan preset picker
        today = datetime.now().date()
        plan_choice = st.selectbox("प्लान वैधता चुनें (Validity Period)", [
            "1 महीना (30 Days)",
            "3 महीने (90 Days)",
            "6 महीने (180 Days)",
            "1 साल (365 Days)"
        ])
        days_map = {"1 महीना (30 Days)": 30, "3 महीने (90 Days)": 90, "6 महीने (180 Days)": 180, "1 साल (365 Days)": 365}
        sel_days = days_map[plan_choice]
        calc_exp_date = today + timedelta(days=sel_days)

        st.info(f"📅 वैधता तारीख रहेगी: **{calc_exp_date.strftime('%d-%b-%Y')}** ({sel_days} दिन)")

        if st.button("💾 डिस्ट्रीब्यूटर ऐप एक्टिवेट करें (Create App)", type="primary"):
            if not new_username or not new_password:
                st.error("यूजरनेम और पासवर्ड जरूरी हैं!")
            else:
                exp_str = calc_exp_date.strftime('%Y-%m-%d')
                try:
                    c.execute('''
                        INSERT INTO users (username, password, role, business_name, phone, valid_until, status, created_at)
                        VALUES (?, ?, 'distributor', ?, ?, ?, 'active', datetime('now'))
                    ''', (new_username.strip(), new_password.strip(), biz_name_inp.strip(), phone_no.strip(), exp_str))
                    new_dist_id = c.lastrowid

                    c.execute('''
                        INSERT OR REPLACE INTO commission_settings 
                        (dist_id, fse_sim_rate, fse_mnp_rate, fse_recharge_pct, fse_daily_da, airfiber_rate, idu_rate, stb_rate, odu_rate)
                        VALUES (?, 15.0, 50.0, 1.0, 100.0, 150.0, 40.0, 30.0, 50.0)
                    ''', (new_dist_id,))
                    conn.commit()
                    st.success(f"🎉 डिस्ट्रीब्यूटर '{new_username}' सफलतापूर्वक बन गया! वैधता: {format_date_indian(exp_str)} तक।")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("❌ इस यूजरनेम का डिस्ट्रीब्यूटर पहले से मौजूद है! दूसरा नाम चुनें।")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 5: ADMIN PROFILE ---
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

    c.execute("SELECT valid_until, status FROM users WHERE id=?", (dist_id,))
    user_row = c.fetchone()
    valid_until_str = user_row['valid_until'] if user_row else "2099-12-31"
    valid_date = datetime.strptime(valid_until_str, '%Y-%m-%d').date()
    days_remaining = (valid_date - datetime.now().date()).days
    formatted_validity = format_date_indian(valid_until_str)

    # Top Hero Header
    st.markdown(f"""
        <div class="hero-banner">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <h1 class="hero-title">🏢 {biz_name.upper()}</h1>
                    <p class="hero-subtitle">Jio Authorized Distribution Enterprise Suite • Logged in as: <b>{username}</b></p>
                </div>
                <div style="background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.3); border-radius:12px; padding:8px 16px; text-align:right;">
                    <div style="font-size:12px; color:#bfdbfe; font-weight:700;">PLAN VALIDITY</div>
                    <div style="font-size:18px; color:#ffffff; font-weight:900;">⚡ {formatted_validity} ({days_remaining} दिन बाकी)</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    st.sidebar.markdown(f"### 📱 {biz_name}")
    st.sidebar.info(f"📅 वैधता: **{formatted_validity}**\n⏳ बाकी दिन: **{days_remaining} दिन**")
    
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
        selected_cust = st.session_state.get('kb_selected_retailer')

        # VIEW A: KHATABOOK CUSTOMER PASSBOOK DETAIL (IMAGE 2)
        if selected_cust:
            if st.button("⬅️ Wapas (Sabhi Retailers List)", type="secondary"):
                st.session_state['kb_selected_retailer'] = None
                st.session_state['kb_action_mode'] = None
                st.rerun()

            df_cust_txns = pd.read_sql_query(f"""
                SELECT id, retailer_name, phone, amount_given, amount_received, payment_mode, remarks, date
                FROM auto_refill_ledger
                WHERE dist_id={dist_id} AND retailer_name=?
                ORDER BY id ASC
            """, conn, params=(selected_cust,))

            if not df_cust_txns.empty:
                df_cust_txns['net'] = df_cust_txns['amount_given'] - df_cust_txns['amount_received']
                df_cust_txns['running_bal'] = df_cust_txns['net'].cumsum()
                current_bal = df_cust_txns['running_bal'].iloc[-1]
                cust_phone = df_cust_txns['phone'].iloc[-1]
            else:
                current_bal = 0.0
                cust_phone = ""

            initials = get_initials(selected_cust)

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
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🔴 AAPNE DIYE ₹", key="btn_diye_trigger", use_container_width=True):
                    st.session_state['kb_action_mode'] = 'diye'
                    st.rerun()
            with btn_col2:
                if st.button("🟢 AAPKO MILE ₹", key="btn_mile_trigger", use_container_width=True):
                    st.session_state['kb_action_mode'] = 'mile'
                    st.rerun()

        # VIEW B: KHATABOOK CUSTOMER LIST (IMAGE 1)
        else:
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

            if not df_cust_agg.empty:
                aapko_milenge = df_cust_agg[df_cust_agg['net_balance'] > 0]['net_balance'].sum()
                aapko_dene_hain = abs(df_cust_agg[df_cust_agg['net_balance'] < 0]['net_balance'].sum())
            else:
                aapko_milenge = 0.0
                aapko_dene_hain = 0.0

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

            csv_all_rep = io.StringIO()
            if not df_cust_agg.empty:
                df_cust_agg.to_csv(csv_all_rep, index=False)
            st.download_button(
                label="📄 Reports Dekhein (Download CSV Ledger)",
                data=csv_all_rep.getvalue(),
                file_name=f"Khatabook_Summary_{datetime.now().strftime('%Y%m%d')}.csv",
                use_container_width=True
            )

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

            if not df_cust_agg.empty and search_query:
                filtered_customers = df_cust_agg[
                    df_cust_agg['retailer_name'].str.contains(search_query, case=False, na=False) |
                    df_cust_agg['phone'].str.contains(search_query, case=False, na=False)
                ]
            else:
                filtered_customers = df_cust_agg

            if filtered_customers.empty:
                st.info("कोई कस्टमर नहीं मिला। ऊपर दिए गए '+ CUSTOMER ADD KAREIN' से नया रिटेलर जोड़ें।")
            else:
                for idx, row in filtered_customers.iterrows():
                    c_name = row['retailer_name']
                    c_phone = row['phone']
                    c_bal = row['net_balance']
                    c_date = row['last_txn_date'] or "हाल ही में"
                    c_initials = get_initials(c_name)

                    reminder_msg = (
                        f"नमस्ते {c_name} जी,\n\n"
                        f"यह *{biz_name}* (Jio Distributor) की तरफ से ऑटो-रिफिल बकाया पेमेंट का सूचना संदेश है:\n"
                        f"👉 *वर्तमान बकाया राशि: ₹{c_bal:,.2f}*\n\n"
                        f"कृपया बकाया राशि आज ही कैश या ऑनलाइन जमा कराने की कृपा करें। धन्यवाद!"
                    )
                    wa_url = f"https://api.whatsapp.com/send?phone=91{c_phone}&text={urllib.parse.quote(reminder_msg)}" if c_phone else "#"

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
                st.dataframe(df_d_fse if 'df_d_fse' in locals() else df_fse, use_container_width=True, hide_index=True)
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
