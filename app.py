import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Premium Flipkart Theme & 3D CSS Injector
st.set_page_config(page_title="Flipkart Super Store", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
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
    .track-bar { display: flex; justify-content: space-between; background: #f1f5f9; padding: 15px; border-radius: 30px; margin: 20px 0; border: 1px solid #cbd5e1; }
    .track-step-active { color: #388e3c; font-weight: bold; font-size: 14px; }
    .track-step-pending { color: #94a3b8; font-weight: bold; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 GOOGLE SHEET WEBHOOK CONNECTION
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
ADMIN_PASSWORD = "Jio Distributor" # 👈 आपका सीक्रेट एडमिन पासवर्ड

# 🟢 LIVE PRODUCTS FETCH FROM GOOGLE SHEET
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
                    "specs": {"Brand": str(row.get("Brand", "Original")), "Warranty": str(row.get("Warranty", "1 Year")), "Review": str(row.get("Review", "Good Product"))}
                })
        return products_list if products_list else get_default_products()
    except:
        return get_default_products()

def get_default_products():
    return [
        {"id": "FK-M01", "name": "JioPhone Bharat 4G Ultra", "price": 1999.0, "cat": "Electronics", "rating": "4.5★", "offer": "20% OFF", "desc": "Affordable 4G phone.", "specs": {"Brand": "Jio", "Warranty": "1 Year", "Review": "Best features"}},
        {"id": "FK-E02", "name": "Premium Bass Wireless Earbuds", "price": 1499.0, "cat": "Electronics", "rating": "4.3★", "offer": "30% OFF", "desc": "True wireless earbuds.", "specs": {"Brand": "Sandhya Brand", "Warranty": "1 Year", "Review": "Heavy Bass"}}
    ]

# Session States Initialize
if "cart" not in st.session_state: st.session_state.cart = {}
if "login_type" not in st.session_state: st.session_state.login_type = None # 'Customer', 'Admin' ya None
if "user_profile" not in st.session_state: st.session_state.user_profile = {"name": "", "phone": "", "address": "", "coins": 50}
if "selected_product" not in st.session_state: st.session_state.selected_product = None
if "order_history" not in st.session_state: st.session_state.order_history = []

# Synchronize Products
st.session_state.products_db = sync_products_from_sheet()

# --- NAVBAR ---
st.markdown("""
    <div class="fk-navbar">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 32px; font-weight: 900; letter-spacing: 0.5px;">flipkart</span>
                <span style="font-size: 14px; font-style: italic; color: #ffe500; font-weight: bold;">plus 🌟</span>
            </div>
            <div style="font-size: 18px; font-weight: bold; background: rgba(255,255,255,0.15); padding: 6px 15px; border-radius: 20px;">
                🛒 Sandhya Super App Engine
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar System (Customer vs Admin Authentication)
with st.sidebar:
    st.markdown("### 🔑 App Security Center")
    
    if st.session_state.login_type is None:
        role = st.radio("Choose Login Type:", ["👤 Customer Login", "🛠️ Admin Dashboard"])
        
        if role == "👤 Customer Login":
            login_phone = st.text_input("Enter Mobile Number", max_chars=10, placeholder="9934XXXXXX")
            if st.button("📲 Customer Login", use_container_width=True, type="primary"):
                if len(login_phone) == 10 and login_phone.isdigit():
                    st.session_state.login_type = "Customer"
                    st.session_state.user_profile["phone"] = login_phone
                    st.rerun()
                else: st.error("Please enter valid 10 digits.")
                
        elif role == "🛠️ Admin Dashboard":
            password_input = st.text_input("Enter Secret Admin Password*", type="password")
            if st.button("🔓 Access Admin Panel", use_container_width=True, type="primary"):
                if password_input == ADMIN_PASSWORD:
                    st.session_state.login_type = "Admin"
                    st.success("Welcome Avdhesh Kumar ji!")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("Wrong Password! Access Denied.")
    else:
        if st.session_state.login_type == "Admin":
            st.markdown("<div class='plus-zone' style='background:red; color:white;'>🛠️ LOGGED IN AS ADMIN</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='plus-zone'>⭐ PLUS MEMBER<br>Balance: {st.session_state.user_profile['coins']} Coins 🪙</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"🟢 **Customer:** +91 {st.session_state.user_profile['phone']}")
            p_name = st.text_input("Your Full Name", value=st.session_state.user_profile["name"])
            p_addr = st.text_area("Delivery Address", value=st.session_state.user_profile["address"])
            if st.button("💾 Save Profile Memory", use_container_width=True):
                st.session_state.user_profile["name"] = p_name
                st.session_state.user_profile["address"] = p_addr
                st.toast("Profile saved successfully!")
                
        if st.button("🚪 Logout From App", use_container_width=True):
            st.session_state.login_type = None
            st.session_state.cart = {}
            st.session_state.selected_product = None
            st.rerun()

    # Sidebar Live Cart Preview for Customers
    if st.session_state.login_type == "Customer" and st.session_state.cart:
        st.markdown("---")
        st.markdown("### 🛒 Live Cart")
        tot = sum(item['price'] * item['qty'] for item in st.session_state.cart.values())
        for pid, item in st.session_state.cart.items():
            st.write(f"▪️ {item['name']} (x{item['qty']})")
        st.markdown(f"**Total Bill: ₹{tot:,}**")

# --- APP TABS SYSTEM ---
# Adminログイン होने पर ही तीसरा टैब दिखेगा, वरना सिर्फ 2 टैब दिखेंगे
tabs_list = ["⚡ Flipkart Grid Store", "📦 Secure Checkout System"]
if st.session_state.login_type == "Admin":
    tabs_list.append("➕ Add New Product (Admin)")
    
tabs = st.tabs(tabs_list)

# TAB 1: PRODUCT BROWSE & SEARCH
with tabs[0]:
    if st.session_state.selected_product is not None:
        p = st.session_state.selected_product
        if st.button("⬅️ Back to Shop Floor"):
            st.session_state.selected_product = None
            st.rerun()
            
        st.markdown("---")
        col_view1, col_view2 = st.columns([1, 1.2])
        with col_view1:
            st.markdown(f'<div style="background:#f8fafc; border:2px dashed #cbd5e1; height:280px; display:flex; align-items:center; justify-content:center; border-radius:12px;"><h3>📸 {p.get("name")} Preview</h3></div>', unsafe_allow_html=True)
        with col_view2:
            st.markdown(f'<span class="fk-badge">{p.get("rating")}</span> <span style="color:#388e3c; font-weight:bold; margin-left:10px;">{p.get("offer")}</span>', unsafe_allow_html=True)
            st.h2(p.get("name"))
            st.markdown(f'<div class="fk-price" style="font-size:34px; color:#2874f0;">Price: ₹{p.get("price", 0.0):,}</div>', unsafe_allow_html=True)
            st.write(f"**Details:** {p.get('desc')}")
            
            st.markdown(f'<div style="background:#f8fafc; padding:12px; border-radius:8px; border-left:5px solid #2874f0; margin:15px 0;"><strong>💬 Top Customer Review:</strong><br>"{p.get("specs", {}).get("Review", "Good")}"</div>', unsafe_allow_html=True)
            
            qty = st.number_input("Select Quantity", min_value=1, max_value=5, value=1, key="det_qty")
            if st.button("🛒 ADD TO CART", type="primary", use_container_width=True):
                if st.session_state.login_type != "Customer": st.error("⚠️ Please login as a Customer to add items to cart!")
                else:
                    st.session_state.cart[p['id']] = {"name": p['name'], "price": p['price'], "qty": qty}
                    st.success("Product added to cart!")
                    time.sleep(0.5)
                    st.rerun()
    else:
        search_query = st.text_input("🔍 Search for products, brands and categories...", placeholder="Type here...")
        st.markdown("---")
        
        filtered = [p for p in st.session_state.products_db if search_query.lower() in p["name"].lower() or search_query.lower() in p["cat"].lower()]
        
        col_grid = st.columns(2)
        for idx, p in enumerate(filtered):
            with col_grid[idx % 2]:
                st.markdown(f"""
                    <div class="fk-card">
                        <span class="fk-badge">{p.get('rating')}</span>
                        <h3 style="color:#212121; margin:10px 0;">{p.get('name')}</h3>
                        <div class="fk-price">₹{p.get('price', 0.0):,}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🔍 View Details & Ratings", key=f"v_{p['id']}", use_container_width=True):
                    st.session_state.selected_product = p
                    st.rerun()

# TAB 2: SECURE CHECKOUT & HISTORY
with tabs[1]:
    if st.session_state.login_type == "Admin":
        st.info("🛠️ Admin Mode active. Customer order logs can be tracked directly from your Google Sheet Ledger.")
    elif st.session_state.login_type != "Customer":
        st.warning("🔒 Access Locked. Please login with your Mobile number in the sidebar center to use the checkout desk.")
    elif not st.session_state.cart:
        st.info("Your shopping cart is currently empty.")
    else:
        bill_records = []
        order_total = 0.0
        for pid, item in st.session_state.cart.items():
            sub = item['price'] * item['qty']
            order_total += sub
            bill_records.append({"Item Details": item['name'], "Price": f"₹{item['price']:,}", "Quantity": item['qty'], "Subtotal": f"₹{sub:,}"})
        st.dataframe(pd.DataFrame(bill_records), use_container_width=True)
        st.markdown(f"<h3 style='color:#388e3c; text-align:right;'>Grand Total: ₹{order_total:,}</h3>", unsafe_allow_html=True)
        
        with st.form("checkout_form_master"):
            f_name = st.text_input("Consignee Name*", value=st.session_state.user_profile["name"])
            f_address = st.text_area("Complete Shipping Address*", value=st.session_state.user_profile["address"])
            pay_mode = st.radio("Select Payment Option*", ["💵 Cash on Delivery (COD)", "💳 Advance Online Payment (UPI / QR)"])
            
            utr_num = ""
            if "Online" in pay_mode:
                st.info(f"Please transfer ₹{order_total:,} to UPI: avdheshkumar@axisbank")
                utr_num = st.text_input("Enter 12-Digit UTR Number*")
                
            if st.form_submit_button("🚀 CONFIRM AND PLACE ORDER", use_container_width=True, type="primary"):
                if not f_name or not f_address: st.error("Name and Address are required.")
                elif "Online" in pay_mode and len(utr_num) < 12: st.error("Please provide valid 12-Digit UTR.")
                else:
                    items_summary = [f"{v['name']} (x{v['qty']})" for v in st.session_state.cart.values()]
                    status_text = "COD - Dispatch Pending" if "Cash" in pay_mode else f"Paid (UTR: {utr_num})"
                    
                    payload = {
                        "sheet_name": "Payment_Ledger", "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": f_name.upper(), "Amount": order_total, "Mode": "Store: " + pay_mode,
                        "SenderUPI_Mobile": st.session_state.user_profile["phone"], "Status": status_text,
                        "Reference": f"Items: {', '.join(items_summary)} | Shipping to: {f_address}"
                    }
                    try:
                        requests.post(WEBHOOK_URL, json=payload, timeout=10)
                        st.session_state.user_profile["coins"] += 10
                        st.balloons()
                        st.success("🎉 Order successfully logged to Google Sheet!")
                        st.session_state.cart = {}
                        st.session_state.selected_product = None
                    except Exception as e: st.error(f"Error: {e}")

# TAB 3: ADMIN INVENTORY MANAGER (Only opens for Admin Mode)
if st.session_state.login_type == "Admin":
    with tabs[2]:
        st.subheader("➕ Inventory Control - Add Product to Sheet")
        st.info("यहाँ से नया सामान भरें, वह सीधे आपकी Google Sheet के Product_List टैब में हमेशा के लिए सेव हो जाएगा।")
        
        with st.form("admin_add_form"):
            new_id = f"FK-{int(time.time())}" # Unique Auto ID
            new_name = st.text_input("Product Title*")
            new_price = st.number_input("Product Price (Rs)*", min_value=1.0, value=499.0)
            new_cat = st.selectbox("Category Group", ["Electronics", "Fashion", "Home", "Other"])
            new_offer = st.text_input("Offer Discount Label", value="Special Deal")
            new_desc = st.text_area("Detailed Description")
            spec_brand = st.text_input("Brand", value="Original")
            spec_warranty = st.text_input("Warranty Period", value="1 Year")
            spec_review = st.text_input("Top Review Text", value="Highly recommended product")
            
            if st.form_submit_button("💾 SAVE PRODUCT TO GOOGLE SHEET", use_container_width=True):
                if not new_name: st.error("Product Title is mandatory.")
                else:
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
                        st.success(f"🎉 '{new_name}' आपकी एक्सेल शीट में हमेशा के लिए जुड़ गया!")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e: st.error(f"Sync failed: {e}")
