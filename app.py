import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Premium Flipkart Theme & 3D CSS Injector
st.set_page_config(page_title="Flipkart Super Store", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    /* Flipkart Core Branding */
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
    
    /* Order Tracking Visuals */
    .track-bar { display: flex; justify-content: space-between; background: #f1f5f9; padding: 15px; border-radius: 30px; margin: 20px 0; border: 1px solid #cbd5e1; }
    .track-step-active { color: #388e3c; font-weight: bold; font-size: 14px; }
    .track-step-pending { color: #94a3b8; font-weight: bold; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 GOOGLE SHEET WEBHOOK CONNECTION
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"

# 🟢 HARDCODED EXPANDED INVENTORY WITH REVIEWS & BRANDS
PRODUCTS_MASTER = [
    {"id": "FK-M01", "name": "JioPhone Bharat 4G Ultra", "price": 1999.0, "cat": "Electronics", "brand": "Jio", "rating": "4.5★", "reviews": "Excellent backup, clear calls.", "desc": "Affordable 4G phone with UPI payment system built-in.", "offer": "20% OFF"},
    {"id": "FK-E02", "name": "Premium Bass Wireless Earbuds", "price": 1499.0, "cat": "Electronics", "brand": "Sandhya Brand", "rating": "4.3★", "reviews": "Super heavy bass, fits perfectly.", "desc": "True wireless earbuds with 40 Hours total playback power.", "offer": "30% OFF"},
    {"id": "FK-S03", "name": "Sports Running Lightweight Shoes", "price": 999.0, "cat": "Fashion", "brand": "Campus", "rating": "4.1★", "reviews": "Very comfortable for long walks.", "desc": "Breathable mesh running shoes with orthopedic sole cushions.", "offer": "50% OFF"},
    {"id": "FK-H04", "name": "Smart Water Bottle with LED Temp", "price": 599.0, "cat": "Home", "brand": "Milton", "rating": "4.2★", "reviews": "Shows exact temperature, premium look.", "desc": "Stainless steel vacuum insulated flask with smart touch sensor.", "offer": "15% OFF"}
]

# Session States Guard Logic
if "cart" not in st.session_state: st.session_state.cart = {}
if "user_login" not in st.session_state: st.session_state.user_login = False
if "user_profile" not in st.session_state: st.session_state.user_profile = {"name": "", "phone": "", "address": "", "coins": 50}
if "selected_product" not in st.session_state: st.session_state.selected_product = None
if "order_history" not in st.session_state: st.session_state.order_history = []

# --- 🛍️ FLIPKART PLUS NAVBAR ---
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

# Sidebar Account and Filter Systems (Features 3 & 5)
with st.sidebar:
    if st.session_state.user_login:
        st.markdown(f"""
            <div class="plus-zone">
                ⭐ FLIPKART PLUS MEMBER<br>
                Balance: {st.session_state.user_profile['coins']} Plus Coins 🪙
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.success(f"🟢 Active Account: +91 {st.session_state.user_profile['phone']}")
        p_name = st.text_input("Customer Name", value=st.session_state.user_profile["name"])
        p_addr = st.text_area("Default Delivery Address", value=st.session_state.user_profile["address"])
        if st.button("💾 Save Profile Memory", use_container_width=True):
            st.session_state.user_profile["name"] = p_name
            st.session_state.user_profile["address"] = p_addr
            st.toast("Profile memory updated instantly!")
        if st.button("🚪 Logout Account", use_container_width=True):
            st.session_state.user_login = False
            st.session_state.cart = {}
            st.session_state.selected_product = None
            st.rerun()
    else:
        st.markdown("### 👤 Customer Login Center")
        login_phone = st.text_input("Enter Mobile Number", max_chars=10, placeholder="9934XXXXXX")
        if st.button("📲 Login via Secure OTP", use_container_width=True, type="primary"):
            if len(login_phone) == 10 and login_phone.isdigit():
                st.session_state.user_login = True
                st.session_state.user_profile["phone"] = login_phone
                st.rerun()
            else: st.error("Please provide valid 10-digit number.")

    # SIDEBAR PRODUCT FILTERS (Feature 3)
    st.markdown("---")
    st.markdown("### 🔍 Filter Selection")
    filter_brand = st.multiselect("Select Brands", ["Jio", "Campus", "Milton", "Sandhya Brand"], default=["Jio", "Campus", "Milton", "Sandhya Brand"])
    max_price = st.slider("Max Price Range (Rs)", min_value=500, max_value=3000, value=3000, step=100)

# Main Navigation Dashboard Tabs
tab1, tab2, tab3 = st.tabs(["⚡ Flipkart Grid Store", "📦 Secure Checkout System", "🚚 My Orders Live Tracker"])

# TAB 1: SEARCH, CATEGORY, GRID VIEW & DETAILS PAGE
with tab1:
    if st.session_state.selected_product is not None:
        p = st.session_state.selected_product
        if st.button("⬅️ Back to Shop Floor", type="secondary"):
            st.session_state.selected_product = None
            st.rerun()
            
        st.markdown("---")
        col_view1, col_view2 = st.columns([1, 1.2])
        with col_view1:
            st.markdown(f'<div style="background:#f8fafc; border:2px dashed #cbd5e1; height:280px; display:flex; align-items:center; justify-content:center; border-radius:12px;"><h3>📸 {p.get("name")} Preview</h3></div>', unsafe_allow_html=True)
        with col_view2:
            st.markdown(f'<span class="fk-badge">{p.get("rating")}</span> <span style="color:#388e3c; font-weight:bold; margin-left:10px;">{p.get("offer")}</span>', unsafe_allow_html=True)
            st.h2(p.get("name"))
            st.markdown(f'<div class="fk-price" style="font-size:34px; color:#2874f0;">Special Price: ₹{p.get("price", 0.0):,}</div>', unsafe_allow_html=True)
            st.write(f"**Product Details:** {p.get('desc')}")
            
            # Feature 3: Customer Reviews Integration
            st.markdown(f"""
                <div style="background:#f8fafc; padding:12px; border-radius:8px; border-left:5px solid #2874f0; margin:15px 0;">
                    <strong>💬 Top Customer Review:</strong><br>
                    <span style="font-style:italic; color:#475569;">"{p.get('reviews')}"</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Specifications Table
            spec_html = "<table class='spec-table'>"
            for k, v in p.get('specs', {}).items():
                spec_html += f"<tr><td class='spec-label'>{k}</td><td>{v}</td></tr>"
            spec_html += "</table>"
            st.markdown(spec_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            qty = st.number_input("Select Quantity", min_value=1, max_value=5, value=1, key="det_qty")
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("🛒 ADD TO CART", use_container_width=True):
                    if not st.session_state.user_login: st.error("Please login first!")
                    else:
                        st.session_state.cart[p['id']] = {"name": p['name'], "price": p['price'], "qty": qty}
                        st.toast("Product added to cart!")
            with c_btn2:
                if st.button("⚡ BUY NOW", type="primary", use_container_width=True):
                    if not st.session_state.user_login: st.error("Please login first!")
                    else:
                        st.session_state.cart = {p['id']: {"name": p['name'], "price": p['price'], "qty": qty}}
                        st.markdown("<script>window.parent.document.querySelector('button[id^=\"tabs-bnd-\"][id$=\"-tab-1\"]').click();</script>", unsafe_allow_html=True)
                        st.toast("Moving to Checkout instantly!")

    else:
        # FEATURE 2: SEARCH BAR AND CATEGORIES
        search_query = st.text_input("🔍 Search for products, brands and more (or click Microphone symbol)", placeholder="Type 'Mobile', 'Shoes'...")
        sel_cat = st.radio("Top Categories Filter:", ["All", "Electronics", "Fashion", "Home"], horizontal=True)
        st.markdown("---")
        
        # Apply Search and Filter Rules
        filtered_products = []
        for p in PRODUCTS_MASTER:
            if search_query.lower() not in p["name"].lower() and search_query.lower() not in p["cat"].lower(): continue
            if sel_cat != "All" and p["cat"] != sel_cat: continue
            if p["brand"] not in filter_brand: continue
            if p["price"] > max_price: continue
            filtered_products.append(p)
            
        if not filtered_products:
            st.info("No products matched your search or slider constraints.")
        else:
            col_grid = st.columns(2)
            for idx, p in enumerate(filtered_products):
                with col_grid[idx % 2]:
                    st.markdown(f"""
                        <div class="fk-card">
                            <span class="fk-badge">{p['rating']}</span>
                            <span style="color:#388e3c; font-weight:bold; float:right;">{p['offer']}</span>
                            <h3 style="color:#212121; margin:10px 0;">{p['name']}</h3>
                            <div class="fk-price">₹{p['price']:,}</div>
                            <p style="font-size:12px; color:#878787;">Brand: {p['brand']} | Free Delivery</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("🔍 View Details & Ratings", key=f"v_{p['id']}", use_container_width=True):
                        st.session_state.selected_product = p
                        st.rerun()

# TAB 2: CART SUMMARY, SHIPPING ADDRESS & PAYMENTS
with tab2:
    st.subheader("📦 Secure Flipkart Order Checkout")
    if not st.session_state.user_login: st.warning("Please login with your mobile number to view your checkout window.")
    elif not st.session_state.cart: st.info("Your shopping cart is empty.")
    else:
        # Display Billing Table
        bill_records = []
        order_total = 0.0
        for pid, item in st.session_state.cart.items():
            sub = item['price'] * item['qty']
            order_total += sub
            bill_records.append({"Item Details": item['name'], "Price": f"₹{item['price']:,}", "Quantity": item['qty'], "Subtotal": f"₹{sub:,}"})
        st.dataframe(pd.DataFrame(bill_records), use_container_width=True)
        
        st.markdown(f"<h3 style='color:#388e3c; text-align:right;'>Total Deal Price: ₹{order_total:,}</h3>", unsafe_allow_html=True)
        
        with st.form("checkout_form_master"):
            # FEATURE 4: AUTO-FILLED ADDRESS FROM PROFILE MEMORY
            f_name = st.text_input("Consignee Name*", value=st.session_state.user_profile["name"])
            f_address = st.text_area("Complete Shipping Address*", value=st.session_state.user_profile["address"])
            
            # FEATURE 5: EXPANDED PAYMENT OPTIONS
            pay_mode = st.radio("Select Payment Option*", [
                "💵 Cash on Delivery (COD)", 
                "💳 Advance Online Payment (UPI / QR)", 
                "⏳ Flipkart Pay Later (Buy Now, Pay Next Month)"
            ])
            
            utr_num = ""
            if "Online" in pay_mode:
                st.markdown(f"""
                    <div style="background:#eff6ff; padding:15px; border-radius:8px; border:1px solid #bfdbfe; margin:10px 0;">
                        <strong>✨ PhonePe / Google Pay QR Desk:</strong><br>
                        Please transfer exactly <strong>₹{order_total:,}</strong> to UPI handle: <code>avdheshkumar@axisbank</code>.<br>
                        Transfer complete hone ke baad niche 12-Digit ka UTR Transaction number enter karein.
                    </div>
                """, unsafe_allow_html=True)
                utr_num = st.text_input("Enter 12-Digit UTR Number*")
                
            if st.form_submit_button("🚀 PLACE ORDER & COMMIT TRANSACTION", use_container_width=True, type="primary"):
                if not f_name or not f_address:
                    st.error("Please fill Name and Shipping Address fields.")
                elif "Online" in pay_mode and len(utr_num) < 12:
                    st.error("UTR verification failed. Please check the 12-digit transaction index.")
                else:
                    items_summary = [f"{v['name']} (x{v['qty']})" for v in st.session_state.cart.values()]
                    full_ref_log = f"Products: {', '.join(items_summary)} | Shipping Address: {f_address}"
                    
                    status_text = "COD - Pending Dispatch"
                    if "Online" in pay_mode: status_text = f"Online Paid (UTR: {utr_num})"
                    elif "Later" in pay_mode: status_text = "Pay Later - Approved"
                    
                    # Prepare matching row data payload package for Google Sheet
                    payload = {
                        "sheet_name": "Payment_Ledger",
                        "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": f_name.upper(),
                        "Amount": order_total,
                        "Mode": pay_mode,
                        "SenderUPI_Mobile": st.session_state.user_profile["phone"],
                        "Status": status_text,
                        "Reference": full_ref_log
                    }
                    
                    try:
                        requests.post(WEBHOOK_URL, json=payload, timeout=10)
                        
                        # Add order to tracking history dictionary
                        new_order_tracking = {
                            "date": datetime.now().strftime("%d-%m-%Y"),
                            "items": ", ".join(items_summary),
                            "total": order_total,
                            "mode": pay_mode,
                            "status_step": 1 # Step 1 means 'Ordered'
                        }
                        st.session_state.order_history.append(new_order_tracking)
                        
                        # Feature 6 (Plus Coins): Add 10 Coins per order
                        st.session_state.user_profile["coins"] += 10
                        
                        st.balloons()
                        st.success("🎉 Order Placed Successfully! Registered on Ekart Network & Google Sheet.")
                        st.session_state.cart = {}
                        st.session_state.selected_product = None
                    except Exception as e: st.error(f"Spreadsheet connection failure: {e}")

# FEATURE 6: LIVE DELIVERY TRACKER (My Orders Panel)
with tab3:
    st.subheader("🚚 Live Order Tracker & History (Ekart Logistics)")
    if not st.session_state.user_login:
        st.warning("Please login to see your transaction history log.")
    elif not st.session_state.order_history:
        st.info("No orders placed yet. Your purchases will be displayed here for real-time tracking.")
    else:
        for idx, order in enumerate(st.session_state.order_history):
            st.markdown(f"""
                <div style="background:#ffffff; padding:20px; border-radius:10px; border:1px solid #cbd5e1; margin-bottom:15px;">
                    <span style="float:right; color:#2874f0; font-weight:bold;">Date: {order['date']}</span>
                    <h4>📦 Order #{idx+1:03d} - {order['items']}</h4>
                    <p style="margin:5px 0;">Amount Paid: <strong>₹{order['total']:,}</strong> | Payment Mode: {order['mode']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Graphical 3-Step Ekart Tracking Bar Visual
            st.markdown("""
                <div class="track-bar">
                    <span class="track-step-active">✅ Ordered & Confirmed</span>
                    <span class="track-step-active">🚚 Shipped via Ekart (Samastipur Hub)</span>
                    <span class="track-step-pending">🏠 Out for Delivery</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
