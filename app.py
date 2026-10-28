import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# ---------------- 1. Database Setup (Multi-Tenant) ----------------
conn = sqlite3.connect('jio_distributors.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # Users/Distributors Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, valid_until DATE)''')
    # Retailer Ledger (Auto-refill)
    c.execute('''CREATE TABLE IF NOT EXISTS ledger 
                 (id INTEGER PRIMARY KEY, dist_id INTEGER, retailer_name TEXT, phone TEXT, given REAL, received REAL, date TEXT)''')
    # Staff Commission Settings
    c.execute('''CREATE TABLE IF NOT EXISTS commission_settings 
                 (dist_id INTEGER PRIMARY KEY, airfiber REAL, idu REAL, stb REAL, odu REAL)''')
    
    # Create Default Admin if not exists
    c.execute("SELECT * FROM users WHERE role='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role, valid_until) VALUES ('avdhesh_admin', 'admin123', 'admin', '2099-12-31')")
    conn.commit()

init_db()

# ---------------- 2. Authentication System ----------------
def login():
    st.sidebar.title("SaaS Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        c.execute("SELECT id, role, valid_until FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user:
            valid_until = datetime.strptime(user[2], '%Y-%m-%d').date()
            if valid_until >= datetime.now().date() or user[1] == 'admin':
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user[0]
                st.session_state['role'] = user[1]
                st.sidebar.success("Login Successful!")
                st.rerun()
            else:
                st.sidebar.error("Your subscription has expired! Please contact Avdhesh Admin.")
        else:
            st.sidebar.error("Invalid Credentials")

# ---------------- 3. Admin Panel (Your Control) ----------------
def admin_panel():
    st.title("⚙️ Super Admin Dashboard (Avdhesh)")
    st.write("Manage Samastipur Distributors & Subscriptions")
    
    # Add or Renew Distributor
    with st.expander("➕ Add / Renew Distributor App"):
        d_name = st.text_input("Distributor Username")
        d_pass = st.text_input("Password")
        days = st.number_input("Validity (Days)", min_value=1, value=30)
        
        if st.button("Activate / Create App"):
            valid_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            # Check if exists
            c.execute("SELECT id FROM users WHERE username=?", (d_name,))
            if c.fetchone():
                c.execute("UPDATE users SET valid_until=?, password=? WHERE username=?", (valid_date, d_pass, d_name))
                st.success(f"Renewed {d_name} till {valid_date}")
            else:
                c.execute("INSERT INTO users (username, password, role, valid_until) VALUES (?, ?, 'distributor', ?)", (d_name, d_pass, valid_date))
                st.success(f"Created new app for {d_name}, valid till {valid_date}")
            conn.commit()

    # View All Distributors
    st.subheader("Active Distributors")
    df_users = pd.read_sql_query("SELECT id, username, valid_until FROM users WHERE role='distributor'", conn)
    st.dataframe(df_users, use_container_width=True)

# ---------------- 4. Distributor Panel (Client App) ----------------
def distributor_panel():
    st.sidebar.title("Menu")
    menu = st.sidebar.radio("Go To", ["Auto-refill Ledger", "FSE/DAB Payment", "AirFiber & Recovery"])
    dist_id = st.session_state['user_id']
    
    st.title("📱 Distributor Dashboard")

    # --- Module 1: Auto-refill Ledger ---
    if menu == "Auto-refill Ledger":
        st.header("1. Auto-refill & Retailer Ledger")
        col1, col2 = st.columns(2)
        with col1:
            r_name = st.text_input("Retailer Name (e.g., Rajesh Mobile)")
            r_phone = st.text_input("WhatsApp Number (+91)")
        with col2:
            given = st.number_input("Auto-refill Given (Rs)", min_value=0)
            received = st.number_input("Cash/Account Received (Rs)", min_value=0)
        
        if st.button("Save Entry"):
            date_now = datetime.now().strftime('%Y-%m-%d %H:%M')
            c.execute("INSERT INTO ledger (dist_id, retailer_name, phone, given, received, date) VALUES (?, ?, ?, ?, ?, ?)", 
                      (dist_id, r_name, r_phone, given, received, date_now))
            conn.commit()
            st.success("Entry Saved!")

        st.subheader("Retailer Reports")
        df_ledger = pd.read_sql_query(f"SELECT retailer_name, phone, given, received, (given - received) as due_balance, date FROM ledger WHERE dist_id={dist_id}", conn)
        st.dataframe(df_ledger)
        
        # WhatsApp Reminder Logic
        if not df_ledger.empty:
            st.write("**Send Payment Reminders:**")
            for index, row in df_ledger.iterrows():
                if row['due_balance'] > 0:
                    msg = f"Hello {row['retailer_name']}, your pending balance for Auto-refill is Rs {row['due_balance']}. Please clear it today."
                    wa_link = f"https://wa.me/{row['phone']}?text={msg}"
                    st.markdown(f"[Send Reminder to {row['retailer_name']}]({wa_link})")

    # --- Module 2: AirFiber & Recovery Commission ---
    elif menu == "AirFiber & Recovery":
        st.header("AirFiber & Recovery (IDU/STB/ODU) Tracker")
        
        # Commission Settings
        st.write("⚙️ **Set Commission Rates** (One-time setup)")
        c.execute(f"SELECT airfiber, idu, stb, odu FROM commission_settings WHERE dist_id={dist_id}")
        rates = c.fetchone() or (0.0, 0.0, 0.0, 0.0)
        
        c1, c2, c3, c4 = st.columns(4)
        af_rate = c1.number_input("AirFiber Comm/pc", value=rates[0])
        idu_rate = c2.number_input("IDU Comm/pc", value=rates[1])
        stb_rate = c3.number_input("STB Comm/pc", value=rates[2])
        odu_rate = c4.number_input("ODU Comm/pc", value=rates[3])
        
        if st.button("Update Rates"):
            c.execute("REPLACE INTO commission_settings (dist_id, airfiber, idu, stb, odu) VALUES (?, ?, ?, ?, ?)", 
                      (dist_id, af_rate, idu_rate, stb_rate, odu_rate))
            conn.commit()
            st.success("Commission Rates Updated!")

        st.divider()
        
        # Daily Entry & Payment Slip
        st.write("📝 **Daily Entry & Payout Calculation**")
        staff_name = st.text_input("FSE / DAB Boy Name")
        af_count = st.number_input("AirFiber Activations", min_value=0, step=1)
        idu_count = st.number_input("IDU Recovered", min_value=0, step=1)
        stb_count = st.number_input("STB Recovered", min_value=0, step=1)
        odu_count = st.number_input("ODU Recovered", min_value=0, step=1)
        
        if st.button("Generate Payment Slip"):
            total_payout = (af_count * af_rate) + (idu_count * idu_rate) + (stb_count * stb_rate) + (odu_count * odu_rate)
            st.info(f"### Payment Slip: {staff_name}")
            st.write(f"- AirFiber Payout: {af_count} x ₹{af_rate} = ₹{af_count * af_rate}")
            st.write(f"- Recovery Payout (IDU, STB, ODU): ₹{(idu_count*idu_rate) + (stb_count*stb_rate) + (odu_count*odu_rate)}")
            st.success(f"**Total Payout Calculated: ₹{total_payout}**")

    # --- Module 3: FSE/DAB Payment Logic ---
    elif menu == "FSE/DAB Payment":
        st.header("FSE / DAB Salary & Entry Logic")
        st.write("यहाँ डिस्ट्रीब्यूटर अपने FSE का बेस सैलरी, अटेंडेंस और टारगेट इन्सेंटिव सेट कर सकते हैं। (यह सेक्शन कस्टम लॉजिक के लिए खाली रखा गया है, जिसे डिस्ट्रीब्यूटर के नियम अनुसार डायनामिक बनाया जा सकता है।)")

# ---------------- Main App Routing ----------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
    if st.session_state['role'] == 'admin':
        admin_panel()
    else:
        distributor_panel()
