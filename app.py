import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Page Configuration & Professional Styling
st.set_page_config(
    page_title="Sandhya ERP & Local Mart Pro",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI Layout, KPI Cards, and Recovery Boxes
st.markdown("""
    <style>
    .main .block-container { padding: 1.5rem 2rem; max-width: 1000px; }
    
    /* KPI Card Styles */
    .kpi-card {
        background: #ffffff; border-radius: 12px; padding: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
        text-align: center; margin-bottom: 15px;
    }
    .kpi-title { font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 20px; color: #0f172a; font-weight: 800; margin: 5px 0; }
    .kpi-sub { font-size: 11px; font-weight: bold; }
    
    /* Category Grid Box */
    .category-box {
        background: #f4f4f5; padding: 15px; border-radius: 18px;
        text-align: center; border: 1px solid #e4e4e7; cursor: pointer; transition: 0.2s;
    }
    .category-box:hover { background: #fef08a; border-color: #facc15; transform: scale(1.03); }
    .category-icon { font-size: 36px; margin-bottom: 5px; }
    .category-title { font-size: 13px; font-weight: bold; color: #1f2937; }
    
    /* Audit Log Box */
    .audit-box {
        background: #0f172a; color: #38bdf8; padding: 15px;
        border-radius: 8px; font-family: monospace; font-size: 12px;
        max-height: 200px; overflow-y: auto;
    }
    
    .section-title { font-size: 18px; font-weight: 800; color: #111827; margin: 15px 0 10px 0; border-left: 5px solid #2563eb; padding-left: 10px; }
    .bill-box { background-color: #fffde7; padding: 15px; border-radius: 10px; border: 1px solid #fef08a; color: #713f12; }
    .recovery-card { background-color: #fef2f2; border: 1px solid #fee2e2; padding: 12px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔒 SECURE CONFIGURATION & CREDENTIALS
# ==========================================
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", "https://script.google.com/macros/s/AKfycbyHCrzqnjgiwCZvcZy4evkZRToRtaziZJGch9F-ODVQXzVcTdAqJhJRvXxH48PKTfhrug/exec")
SHEET_ID = st.secrets.get("SHEET_ID", "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "Jio Distributor")
OWNER_WHATSAPP_NUMBER = st.secrets.get("OWNER_WHATSAPP", "919934000000")

# ==========================================
# 🧠 STATE MANAGEMENT & AUDIT LOGS
# ==========================================
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []

def add_audit_log(user, action):
    timestamp = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    st.session_state.audit_logs.insert(0, f"[{timestamp}] {user}: {action}")

if "login_role" not in st.session_state: st.session_state.login_role = None
if "current_user" not in st.session_state: st.session_state.current_user = "Guest"
if "selected_category" not in st.session_state: st.session_state.selected_category = "Telecom"
if "order_placed_success" not in st.session_state: st.session_state.order_placed_success = False

# Inventory Database with Barcode & Purchase Costs
if "inventory_db" not in st.session_state:
    st.session_state.inventory_db = [
        {"barcode": "8901001", "name": "Ashirvaad Aata 5Kg", "cat": "Atta", "cost": 210.0, "price": 260.0, "stock": 18, "min_stock": 5},
        {"barcode": "8901002", "name": "Fortune Mustard Oil 1L", "cat": "Oils", "cost": 140.0, "price": 175.0, "stock": 3, "min_stock": 5},
        {"barcode": "8901003", "name": "Jio Phone Bharat V4", "cat": "Telecom", "cost": 950.0, "price": 1099.0, "stock": 12, "min_stock": 3},
        {"barcode": "8901004", "name": "Premium Basmati Rice 1Kg", "cat": "Rice", "cost": 110.0, "price": 140.0, "stock": 25, "min_stock": 8}
    ]

# Sales Database for KPIs
if "sales_db" not in st.session_state:
    st.session_state.sales_db = [
        {"date": datetime.now().strftime("%Y-%m-%d"), "item": "Ashirvaad Aata 5Kg", "qty": 2, "sale": 520.0, "cost": 420.0, "profit": 100.0, "staff": "Ravi Kumar"},
        {"date": datetime.now().strftime("%Y-%m-%d"), "item": "Jio Phone Bharat V4", "qty": 1, "sale": 1099.0, "cost": 950.0, "profit": 149.0, "staff": "Gopal Sharma"}
    ]

# Dues Ledger for Payment Recovery Desk
if "dues_data" not in st.session_state:
    st.session_state.dues_data = [
        {"name": "AMIT KUMAR", "phone": "9934012345", "amount": 1000, "area": "Meghpatti Market"},
        {"name": "RAMESH SINGH", "phone": "9801234567", "amount": 2500, "area": "Samastipur Road"}
    ]

# ==========================================
# 📱 APP NAVBAR & AUTH SIDEBAR
# ==========================================
st.markdown(f"""
    <div style="background: #1e293b; color: white; padding: 15px 20px; border-radius: 10px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; font-size: 20px;">🏢 SANDHYA ENTERPRISES ERP</h3>
                <p style="margin: 0; font-size: 12px; color: #94a3b8;">Hyperlocal Local Mart & Telecom System</p>
            </div>
            <div style="text-align: right;">
                <span style="background: #334155; padding: 5px 12px; border-radius: 20px; font-size: 12px; color: #38bdf8;">
                    👤 Active: {st.session_state.current_user}
                </span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔐 System Access Mode")
    if st.session_state.login_role is None:
        role_type = st.radio("Access Level:", ["👤 Customer / Staff", "🛠️ Owner / Admin"])
        user_name_input = st.text_input("Enter Your Name", value="Avdhesh Kumar")
        
        if role_type == "🛠️ Owner / Admin":
            pwd_input = st.text_input("Enter Admin Password", type="password")
            if st.button("🔓 Admin Login", use_container_width=True, type="primary"):
                if pwd_input == ADMIN_PASSWORD:
                    st.session_state.login_role = "Admin"
                    st.session_state.current_user = f"Admin ({user_name_input})"
                    add_audit_log(st.session_state.current_user, "Logged into Admin Control Tower")
                    st.rerun()
                else:
                    st.error("Invalid Password!")
        else:
            if st.button("📲 Customer / Staff Login", use_container_width=True, type="primary"):
                st.session_state.login_role = "User"
                st.session_state.current_user = user_name_input
                add_audit_log(st.session_state.current_user, "Logged into Portal")
                st.rerun()
    else:
        st.success(f"Mode: **{st.session_state.login_role}**")
        if st.button("🚪 Logout", use_container_width=True):
            add_audit_log(st.session_state.current_user, "Logged out of system")
            st.session_state.login_role = None
            st.session_state.current_user = "Guest"
            st.rerun()

# Navigation Tabs
nav_tabs = st.tabs(["🛍️ Local Mart & Billing", "📊 KPI Dashboard", "⚠️ AI Payment Recovery", "📦 Inventory & Audit"])

# ==========================================
# 🛒 TAB 1: LOCAL MART & BLINKIT STYLE GRID
# ==========================================
with nav_tabs[0]:
    st.markdown("### 📋 Customer & Delivery Information")
    c_name = st.text_input("Customer Name*", value=st.session_state.current_user if st.session_state.current_user != "Guest" else "")
    c_phone = st.text_input("Mobile Number*", max_chars=10)
    c_addr = st.text_area("Delivery Address (Meghpatti Area)*")
    
    st.markdown("#### 📍 Operational Distance Lock")
    c_dist = st.slider("Distance from Head Office (KM)", min_value=0.5, max_value=10.0, value=1.0, step=0.5)
    
    if c_dist > 5.0:
        st.error("🚨 BOUNDARY LOCK: We strictly deliver within 5KMs range to keep food fresh.")
    else:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Cooking Essentials & Jio Services</div>", unsafe_allow_html=True)
        
        grid_cols = st.columns(4)
        with grid_cols[0]:
            st.markdown('<div class="category-box"><div class="category-icon">📱</div><div class="category-title">Jio Telecom</div></div>', unsafe_allow_html=True)
            if st.button("Open Jio Desk", key="cat_telecom", use_container_width=True): st.session_state.selected_category = "Telecom"
        with grid_cols[1]:
            st.markdown('<div class="category-box"><div class="category-icon">🌾</div><div class="category-title">Atta & Flours</div></div>', unsafe_allow_html=True)
            if st.button("Open Atta Desk", key="cat_atta", use_container_width=True): st.session_state.selected_category = "Atta"
        with grid_cols[2]:
            st.markdown('<div class="category-box"><div class="category-icon">🍚</div><div class="category-title">Rice & Dal</div></div>', unsafe_allow_html=True)
            if st.button("Open Rice Desk", key="cat_rice", use_container_width=True): st.session_state.selected_category = "Rice"
        with grid_cols[3]:
            st.markdown('<div class="category-box"><div class="category-icon">🧈</div><div class="category-title">Ghee & Oils</div></div>', unsafe_allow_html=True)
            if st.button("Open Oils Desk", key="cat_oils", use_container_width=True): st.session_state.selected_category = "Oils"

        st.markdown("---")
        current_cat = st.session_state.selected_category
        st.markdown(f"<div class='section-title'>Items inside: {current_cat} Department</div>", unsafe_allow_html=True)
        
        selected_item_name = ""
        base_item_price = 0.0
        
        if current_cat == "Telecom":
            telecom_option = st.selectbox("Select Jio Service:", ["MNP (Port to Jio) - Free", "New Jio SIM Activation - Free", "Jio Phone Bharat V4 - ₹1099"])
            selected_item_name = telecom_option.split(" - ")[0]
            base_item_price = 1099.0 if "Phone" in telecom_option else 0.0
        elif current_cat == "Atta":
            selected_item_name = st.selectbox("Select Flour Brand:", ["Ashirvaad Shudh Chakki Aata 5Kg", "Fortune Chakki Fresh Aata 5Kg"])
            base_item_price = st.number_input("Confirm Store Price (Rs)*", min_value=10.0, value=260.0)
        elif current_cat == "Rice":
            selected_item_name = st.selectbox("Select Rice Type:", ["Premium Basmati Rice 1Kg", "Arhar / Toor Dal 1Kg"])
            base_item_price = st.number_input("Confirm Store Price (Rs)*", min_value=10.0, value=140.0)
        elif current_cat == "Oils":
            selected_item_name = st.selectbox("Select Ghee/Oils:", ["Fortune Mustard Oil 1L", "Amul Pure Ghee 1L"])
            base_item_price = st.number_input("Confirm Store Price (Rs)*", min_value=10.0, value=175.0)

        delivery_rider_fee = 15.0  
        platform_handling_fee = 5.0  
        merchant_commission = round(base_item_price * 0.05, 2) if base_item_price > 0 else 0.0
        final_payable_amt = base_item_price + delivery_rider_fee + platform_handling_fee
        
        if base_item_price > 0:
            st.markdown(f"""
                <div class="bill-box">
                    <strong>📋 संध्या मार्ट - इनवॉइस (COD):</strong><br>
                    • सामान की कीमत: ₹{base_item_price:,}<br>
                    • डिलीवरी चार्ज (Rider Fee): ₹{delivery_rider_fee:,}<br>
                    • प्लेटफॉर्म शुल्क: ₹{platform_handling_fee:,}<br>
                    <hr style='border-top: 1px solid #fef08a; margin: 5px 0;'>
                    <strong>👉 कुल देय राशि: ₹{final_payable_amt:,}</strong>
                </div>
            """, unsafe_allow_html=True)
            
        if st.button("🚀 TRANSMIT ORDER TO DELIVERY NETWORK", type="primary", use_container_width=True):
            if not c_name or not c_phone or not c_addr:
                st.error("Please fill Name, Mobile and Address fields.")
            else:
                try:
                    payload = {
                        "sheet_name": "Payment_Ledger",
                        "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": c_name.upper(),
                        "Amount": final_payable_amt,
                        "Mode": f"Hyperlocal Mart ({current_cat})",
                        "SenderUPI_Mobile": c_phone,
                        "Status": "Rider Dispatched",
                        "Reference": f"Item: {selected_item_name} | Profit: ₹{merchant_commission+platform_handling_fee}"
                    }
                    requests.post(WEBHOOK_URL, json=payload, timeout=10)
                    st.session_state.last_order_details = {"name": c_name, "phone": c_phone, "addr": c_addr, "item": selected_item_name, "bill": final_payable_amt}
                    st.session_state.order_placed_success = True
                    add_audit_log(c_name, f"Placed Order for {selected_item_name} (Amount: ₹{final_payable_amt})")
                    st.balloons()
                except Exception as e:
                    st.error(f"Spreadsheet connection failure: {e}")

        if st.session_state.order_placed_success:
            od = st.session_state.last_order_details
            whatsapp_msg = f"🛵 *संध्या लोकल मार्ट - नया ऑर्डर*\n\n👤 *ग्राहक:* {od['name']}\n📞 *नंबर:* {od['phone']}\n📦 *सामान:* {od['item']}\n💵 *बिल:* ₹{od['bill']}\n🏠 *पता:* {od['addr']}"
            st.markdown(f'<a href="https://wa.me/{OWNER_WHATSAPP_NUMBER}?text={requests.utils.quote(whatsapp_msg)}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 25px; border-radius:8px; font-weight:bold; font-size:16px; cursor:pointer; width:100%;">💬 WHATSAPP पर ऑर्डर भेजें</button></a>', unsafe_allow_html=True)

# ==========================================
# 📊 TAB 2: LIVE KPI & PROFIT DASHBOARD
# ==========================================
with nav_tabs[1]:
    st.subheader("📈 Real-Time Business Performance Dashboard")
    
    df_sales = pd.DataFrame(st.session_state.sales_db)
    df_inv = pd.DataFrame(st.session_state.inventory_db)
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_sales_df = df_sales[df_sales['date'] == today_str] if not df_sales.empty else pd.DataFrame()
    
    today_sale_total = today_sales_df['sale'].sum() if not today_sales_df.empty else 0.0
    today_profit_total = today_sales_df['profit'].sum() if not today_sales_df.empty else 0.0
    low_stock_count = len(df_inv[df_inv['stock'] <= df_inv['min_stock']]) if not df_inv.empty else 0
    total_stock_value = (df_inv['stock'] * df_inv['cost']).sum() if not df_inv.empty else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f'<div class="kpi-card"><div class="kpi-title">Today\'s Sales</div><div class="kpi-value" style="color:#2563eb;">₹{today_sale_total:,.2f}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="kpi-card"><div class="kpi-title">Today\'s Profit</div><div class="kpi-value" style="color:#16a34a;">₹{today_profit_total:,.2f}</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="kpi-card"><div class="kpi-title">Stock Value</div><div class="kpi-value" style="color:#0f172a;">₹{total_stock_value:,.2f}</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="kpi-card"><div class="kpi-title">Low Stock Alert</div><div class="kpi-value" style="color:#dc2626;">{low_stock_count} Items</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    if low_stock_count > 0:
        st.markdown("##### 🔔 Low Stock Items (Re-order Alert)")
        st.dataframe(df_inv[df_inv['stock'] <= df_inv['min_stock']][['name', 'cat', 'stock', 'min_stock']], use_container_width=True)

# ==========================================
# ⚠️ TAB 3: AI PAYMENT RECOVERY DESK
# ==========================================
with nav_tabs[2]:
    st.subheader("⚠️ AI Payment Recovery Tower")
    st.info("यहाँ उन बकायेदारों की लिस्ट है जिनका पेमेंट पेंडिंग है। आप AI Voice Call या WhatsApp नोटिस ट्रिगर कर सकते हैं।")
    
    for idx, row in enumerate(st.session_state.dues_data):
        st.markdown(f"""
            <div class="recovery-card">
                <span style="background:#dc2626; color:white; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:bold;">OVERDUE</span>
                <h4 style="margin:5px 0; color:#991b1b;">👤 {row['name']} (Dues: ₹{row['amount']})</h4>
                <p style="margin:0; font-size:12px; color:#7f1d1d;">📍 Area: {row['area']} | 📞 Phone: +91 {row['phone']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_call, col_wa, col_clear = st.columns([1, 1, 1])
        with col_call:
            if st.button(f"📞 AI Voice Call Trigger", key=f"call_{idx}"):
                add_audit_log(st.session_state.current_user, f"Triggered AI Call Reminder to {row['name']} for ₹{row['amount']}")
                st.success(f"🤖 AI Call Dispatched to +91 {row['phone']}!")
        with col_wa:
            wa_text = f"प्रिय *{row['name']}*,\n\nसंध्या एंटरप्राइजेज का रिमाइंडर। आपका बकाया *₹{row['amount']}* है। कृपया आज ही जमा करें।"
            st.markdown(f'<a href="https://wa.me/91{row["phone"]}?text={requests.utils.quote(wa_text)}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:6px 12px; border-radius:5px; font-weight:bold; cursor:pointer; width:100%;">💬 Send WhatsApp Notice</button></a>', unsafe_allow_html=True)
        with col_clear:
            if st.button("✅ Mark Paid", key=f"clear_{idx}"):
                add_audit_log(st.session_state.current_user, f"Cleared dues for {row['name']}")
                st.session_state.dues_data.pop(idx)
                st.rerun()

# ==========================================
# 📦 TAB 4: INVENTORY & AUDIT LOGS
# ==========================================
with nav_tabs[3]:
    st.subheader("📦 Inventory Stock & Audit Trail")
    
    st.dataframe(pd.DataFrame(st.session_state.inventory_db), use_container_width=True)
    
    st.markdown("---")
    st.markdown("##### 📜 Audit Logs (System Action History)")
    if st.session_state.audit_logs:
        st.markdown(f'<div class="audit-box">{"<br>".join(st.session_state.audit_logs)}</div>', unsafe_allow_html=True)
    else:
        st.caption("No logs recorded yet.")
