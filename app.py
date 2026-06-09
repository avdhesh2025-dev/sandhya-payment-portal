import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Premium Flipkart Theme & Professional UI Injector
st.set_page_config(page_title="Flipkart Super Store Pro", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    /* Flipkart Core Identity Styling */
    .fk-navbar {
        background-color: #2874f0; padding: 15px 30px; color: white;
        border-radius: 0px 0px 12px 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .fk-card {
        background: #ffffff; padding: 20px; border-radius: 12px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;
        text-align: center; margin-bottom: 20px;
    }
    .fk-price { color: #212121; font-size: 24px; font-weight: bold; margin: 5px 0; }
    .fk-badge { background: #388e3c; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .plus-zone { background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color: #ffe500; padding: 10px; border-radius: 8px; font-weight: bold; text-align: center;}
    .spec-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .spec-table td { padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
    .spec-label { color: #878787; font-weight: bold; width: 30%; }
    .3d-box {
        background: #ffffff; padding: 25px; border-radius: 12px;
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.05), 0px 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #cbd5e1; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 CLOUD DATABASE CONFIG (GOOGLE SHEET)
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
ADMIN_PASSWORD = "Jio Distributor" # 👈 आपका सुरक्षित एडमिन पासवर्ड

# 🟢 ENGINE: DATABASE FETCH SYSTEM (PRODUCT CATALOG)
@st.cache_data(ttl=1)
def sync_products_from_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Product_List&cb={int(time.time())}"
    try:
        df = pd.read_csv(url).dropna(how="all").fillna("")
        df.columns = [str(c).replace(" ", "").strip() for c in df.columns]
        
        products_list = []
        for _, row in df.iterrows():
            if str(row.get("ProductName", "")):
                products_list.append({
                    "id": str(row.get("ProductID", "")),
                    "name": str(row.get("ProductName", "")),
                    "price": float(row.get("Price", 0.0)),
                    "cat": str(row.get("Category", "General")),
                    "rating": "4.4★",
                    "offer": str(row.get("OfferLabel", "Special Price")),
                    "desc": str(row.get("Description", "")),
                    "specs": {"Brand": str(row.get("Brand", "Original")), "Warranty": str(row.get("Warranty", "1 Year")), "Review": str(row.get("Review", "Highly Recommended"))}
                })
        return products_list if products_list else get_default_products()
    except:
        return get_default_products()

def get_default_products():
    return [
        {"id": "FK-M01", "name": "JioPhone Bharat 4G Ultra", "price": 1999.0, "cat": "Electronics", "rating": "4.5★", "offer": "20% OFF", "desc": "Affordable 4G phone with JioApps.", "specs": {"Brand": "Jio", "Warranty": "1 Year", "Review": "Best performance in budget"}},
        {"id": "FK-E02", "name": "Premium Bass Wireless Earbuds", "price": 1499.0, "cat": "Electronics", "rating": "4.3★", "offer": "30% OFF", "desc": "True wireless earbuds with touch control.", "specs": {"Brand": "Sandhya Brand", "Warranty": "1 Year", "Review": "Heavy Bass, excellent backup"}}
    ]

# Initialize Application Session States
if "cart" not in st.session_state: st.session_state.cart = {}
if "login_type" not in st.session_state: st.session_state.login_type = None # 'Customer', 'Admin', or None
if "user_profile" not in st.session_state: st.session_state.user_profile = {"name": "", "phone": "", "address": "", "coins": 50}
if "selected_product" not in st.session_state: st.session_state.selected_product = None

# Load Dynamic Catalog Data
st.session_state.products_db = sync_products_from_sheet()

# --- APP FRONTEND NAVBAR ---
st.markdown("""
    <div class="fk-navbar">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 32px; font-weight: 900; letter-spacing: 0.5px;">flipkart</span>
                <span style="font-size: 14px; font-style: italic; color: #ffe500; font-weight: bold;">plus 🌟</span>
            </div>
            <div style="font-size: 16px; font-weight: bold; background: rgba(255,255,255,0.15); padding: 6px 15px; border-radius: 20px;">
                🏪 Sandhya E-Commerce Infrastructure Engine
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SECURITY & AUTHENTICATION CENTER (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🔑 Gateway Authentication")
    
    if st.session_state.login_type is None:
        role = st.radio("Select Interface Mode:", ["👤 Customer Login (OTP)", "🛠️ Admin Control Desk"])
        
        if role == "👤 Customer Login (OTP)":
            login_phone = st.text_input("Enter Mobile Number", max_chars=10, placeholder="9934XXXXXX")
            if st.button("📲 Access Customer Store", use_container_width=True, type="primary"):
                if len(login_phone) == 10 and login_phone.isdigit():
                    st.session_state.login_type = "Customer"
                    st.session_state.user_profile["phone"] = login_phone
                    st.rerun()
                else: st.error("Verification Error: Enter a valid 10-digit number.")
                
        elif role == "🛠️ Admin Control Desk":
            password_input = st.text_input("Enter Secret System Key*", type="password")
            if st.button("🔓 Open Backend Dashboard", use_container_width=True, type="primary"):
                if password_input == ADMIN_PASSWORD:
                    st.session_state.login_type = "Admin"
                    st.success("Access Granted: Welcome Avdhesh Kumar जी!")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("Access Denied: Invalid Security Key.")
    else:
        if st.session_state.login_type == "Admin":
            st.markdown("<div class='plus-zone' style='background:#be123c; color:white;'>🛠️ CONTROL MODE: APP ADMIN</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='plus-zone'>⭐ SANDHYA PLUS MEMBER<br>Rewards: {st.session_state.user_profile['coins']} Coins 🪙</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"👤 **User Session:** +91 {st.session_state.user_profile['phone']}")
            p_name = st.text_input("Your Full Name", value=st.session_state.user_profile["name"])
            p_addr = st.text_area("Delivery Destination Address", value=st.session_state.user_profile["address"])
            if st.button("💾 Lock Profile to Memory", use_container_width=True):
                st.session_state.user_profile["name"] = p_name
                st.session_state.user_profile["address"] = p_addr
                st.toast("Profile environment synchronized!")
                
        if st.button("🚪 Termination Session (Logout)", use_container_width=True):
            st.session_state.login_type = None
            st.session_state.cart = {}
            st.session_state.selected_product = None
            st.rerun()

    # Customer Live Cart Preview Tracker
    if st.session_state.login_type == "Customer" and st.session_state.cart:
        st.markdown("---")
        st.markdown("### 🛒 Basket Preview")
        tot = sum(item['price'] * item['qty'] for item in st.session_state.cart.values())
        for pid, item in st.session_state.cart.items():
            st.caption(f"• {item['name']} (x{item['qty']})")
        st.markdown(f"**Current Total: ₹{tot:,}**")

# Dynamic Tab Allocator based on Login Role
tabs_list = ["⚡ Flipkart Grid Store", "📦 Secure Checkout System"]
if st.session_state.login_type == "Admin":
    tabs_list.append("➕ Add New Product (Admin)")
    
tabs = st.tabs(tabs_list)

# ==========================================
# ⚡ TAB 1: FRONTEND PRODUCT SEARCH & SELECTION
# ==========================================
with tabs[0]:
    if st.session_state.selected_product is not None:
        p = st.session_state.selected_product
        if st.button("⬅️ Back to Browse Grid", type="secondary"):
            st.session_state.selected_product = None
            st.rerun()
            
        st.markdown("---")
        col_view1, col_view2 = st.columns([1, 1.2])
        with col_view1:
            st.markdown(f'<div style="background:#f8fafc; border:2px dashed #cbd5e1; height:280px; display:flex; align-items:center; justify-content:center; border-radius:12px;"><h3>📸 {p.get("name")} High-Res View</h3></div>', unsafe_allow_html=True)
        with col_view2:
            st.markdown(f'<span class="fk-badge">{p.get("rating")}</span> <span style="color:#388e3c; font-weight:bold; margin-left:10px;">{p.get("offer")}</span>', unsafe_allow_html=True)
            st.h2(p.get("name"))
            st.markdown(f'<div class="fk-price" style="font-size:34px; color:#2874f0;">Special Price: ₹{p.get("price", 0.0):,}</div>', unsafe_allow_html=True)
            st.write(f"**Product Log Description:** {p.get('desc')}")
            
            st.markdown(f'<div style="background:#f8fafc; padding:12px; border-radius:8px; border-left:5px solid #2874f0; margin:15px 0;"><strong>💬 Top Customer Review:</strong><br>"{p.get("specs", {}).get("Review", "Verified Purchase Product")}"</div>', unsafe_allow_html=True)
            
            qty = st.number_input("Choose Quantity", min_value=1, max_value=5, value=1, key="det_qty")
            if st.button("🛒 ADD TO CART PIPELINE", type="primary", use_container_width=True):
                if st.session_state.login_type != "Customer": st.error("System Override: Please log in as a Customer to build a shopping basket!")
                else:
                    st.session_state.cart[p['id']] = {"name": p['name'], "price": p['price'], "qty": qty}
                    st.success("Item packed into cart successfully!")
                    time.sleep(0.5)
                    st.rerun()
    else:
        search_query = st.text_input("🔍 Product Search Bar (Search for products, categories or brands)", placeholder="Type keyword here...")
        st.markdown("---")
        
        filtered = [p for p in st.session_state.products_db if search_query.lower() in p["name"].lower() or search_query.lower() in p["cat"].lower()]
        
        if not filtered:
            st.info("No records matched your search query strings.")
        else:
            col_grid = st.columns(2)
            for idx, p in enumerate(filtered):
                with col_grid[idx % 2]:
                    st.markdown(f"""
                        <div class="fk-card">
                            <span class="fk-badge">{p.get('rating')}</span>
                            <span style="color:#388e3c; font-weight:bold; float:right;">{p.get('offer')}</span>
                            <h3 style="color:#212121; margin:10px 0;">{p.get('name')}</h3>
                            <div class="fk-price">₹{p.get('price', 0.0):,}</div>
                            <p style="font-size:12px; color:#878787;">Category: {p.get('cat')} | Free Delivery</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("🔍 Open Product Specification Sheet", key=f"v_{p['id']}", use_container_width=True):
                        st.session_state.selected_product = p
                        st.rerun()

# ==========================================
# 📦 TAB 2: SECURE ORDER CHECKOUT ROUTING
# ==========================================
with tabs[1]:
    if st.session_state.login_type == "Admin":
        st.info("🛠️ System Notification: Admin session is active. Customer order entries bypass checkout and log directly to your Sheet Ledger database.")
    elif st.session_state.login_type != "Customer":
        st.warning("🔒 Transaction Gateway Locked: Please login with your Mobile number via the sidebar to access checkout operations.")
    elif not st.session_state.cart:
        st.info("Transaction Pipeline empty: Shopping basket has no products.")
    else:
        bill_records = []
        order_total = 0.0
        for pid, item in st.session_state.cart.items():
            sub = item['price'] * item['qty']
            order_total += sub
            bill_records.append({"Specifications": item['name'], "Unit Price": f"₹{item['price']:,}", "Qty": item['qty'], "Subtotal": f"₹{sub:,}"})
        st.dataframe(pd.DataFrame(bill_records), use_container_width=True)
        st.markdown(f"<h3 style='color:#388e3c; text-align:right;'>Invoice Total: ₹{order_total:,}</h3>", unsafe_allow_html=True)
        
        with st.form("checkout_form_master"):
            f_name = st.text_input("Customer/Consignee Name*", value=st.session_state.user_profile["name"])
            f_address = st.text_area("Complete Shipping Destination Address*", value=st.session_state.user_profile["address"])
            pay_mode = st.radio("Select Payment Framework*", ["💵 Cash on Delivery (COD)", "💳 Online UPI Advanced Wire Transfer"])
            
            utr_num = ""
            if "Online" in pay_mode:
                st.info(f"Payment Engine Active: Please process ₹{order_total:,} to secure node handle: avdheshkumar@axisbank")
                utr_num = st.text_input("Enter 12-Digit Banking UTR Number*")
                
            if st.form_submit_button("🚀 CONFIRM PIPELINE & PLACE ORDER", use_container_width=True, type="primary"):
                if not f_name or not f_address: st.error("Validation Failure: Name and Destination fields cannot be blank.")
                elif "Online" in pay_mode and len(utr_num) < 12: st.error("Gateway Rejection: Provide a valid 12-digit UTR verification index.")
                else:
                    items_summary = [f"{v['name']} (x{v['qty']})" for v in st.session_state.cart.values()]
                    status_text = "COD - Pending Shipment" if "Cash" in pay_mode else f"Online Paid (UTR: {utr_num})"
                    
                    # Prepare matching row data payload package for Google Sheet Tab: 'Payment_Ledger'
                    payload = {
                        "sheet_name": "Payment_Ledger", "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": f_name.upper(), "Amount": order_total, "Mode": "Store: " + pay_mode,
                        "SenderUPI_Mobile": st.session_state.user_profile["phone"], "Status": status_text,
                        "Reference": f"Items Ordered: {', '.join(items_bought if 'items_bought' in locals() else items_summary)} | Shipped to: {f_address}"
                    }
                    try:
                        requests.post(WEBHOOK_URL, json=payload, timeout=10)
                        st.session_state.user_profile["coins"] += 10 # Credit Plus coins
                        st.balloons()
                        st.success("🎉 Transaction Completed: Order pushed safely to cloud ledger sheet!")
                        st.session_state.cart = {}
                        st.session_state.selected_product = None
                    except Exception as database_err: st.error(f"Sync Failure: {database_err}")

# ==========================================
# ➕ TAB 3: ADMIN INVENTORY MANAGEMENT (PERMANENT STORAGE)
# ==========================================
if st.session_state.login_type == "Admin":
    with tabs[2]:
        st.subheader("🛠️ Product Management Console (Write-to-Database)")
        st.info("यहाँ नया प्रोडक्ट भरें। यह सीधे आपकी Google Sheet के Product_List टैब में हमेशा के लिए जुड़ जाएगा और स्टोर पर दिखने लगेगा।")
        
        with st.form("admin_add_form"):
            new_id = f"FK-{int(time.time())}" # Auto unique ID generation string
            new_name = st.text_input("Product Title Line*")
            new_price = st.number_input("Set Price Parameter (Rs)*", min_value=1.0, value=499.0)
            new_cat = st.selectbox("Assign Category Group", ["Electronics", "Fashion", "Home", "Other"])
            new_offer = st.text_input("Offer Discount Text Label", value="Special Offer Deal")
            new_desc = st.text_area("Product Specifications Summary")
            spec_brand = st.text_input("Brand", value="Original")
            spec_warranty = st.text_input("Warranty Terms", value="1 Year")
            spec_review = st.text_input("Default Top Review", value="Excellent premium build quality product")
            
            if st.form_submit_button("💾 TRANSMIT AND WRITE TO CLOUD SHEET", use_container_width=True):
                if not new_name: st.error("Constraint Violation: Title field is mandatory.")
                else:
                    # Payload matches exact headers of the Product_List spreadsheet tab
                    product_payload = {
                        "sheet_name": "Product_List",
                        "ProductID": new_id,
                        "ProductName": new_name,
                        "Price": float(new_price),
                        "Category": new_cat,
                        "OfferLabel": new_offer,
                        "Description": new_desc,
                        "Brand": spec_brand,
                        "Warranty": spec_warranty,
                        "Review": spec_review
                    }
                    try:
                        requests.post(WEBHOOK_URL, json=product_payload, timeout=10)
                        st.success(f"🎉 Architecture Success: '{new_name}' permanently registered inside cloud Sheet storage!")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    except Exception as cloud_err: st.error(f"Write failure to Spreadsheet database: {cloud_err}")
