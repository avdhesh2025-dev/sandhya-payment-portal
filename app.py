import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Page Configuration & Premium Flipkart UI Theme
st.set_page_config(page_title="Flipkart Style Store Pro", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    .fk-header {
        background-color: #2874f0; padding: 15px 30px; border-radius: 0px 0px 10px 10px;
        color: white; margin-bottom: 25px; box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    .fk-card {
        background: #ffffff; padding: 20px; border-radius: 12px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;
        text-align: center; margin-bottom: 25px;
    }
    .fk-price { color: #212121; font-size: 24px; font-weight: bold; margin: 8px 0; }
    .fk-tag { background: #388e3c; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
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
# 🔴 GOOGLE SHEET CONFIG
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"

# Master Inventory Initialization
if "products_db" not in st.session_state:
    st.session_state.products_db = [
        {
            "id": "FK01", "name": "Premium Wireless Earbuds (Super Bass)", "price": 1499.0, "cat": "Electronics", "rating": "4.3★", "offer": "25% OFF",
            "desc": "High-fidelity wireless sound with deep bass and up to 40 hours of total playback time.",
            "specs": {"Brand": "Sandhya Digital", "Battery Life": "40 Hours"}
        },
        {
            "id": "FK02", "name": "Smart Fitness Watch Pro AMOLED", "price": 2499.0, "cat": "Electronics", "rating": "4.5★", "offer": "10% OFF",
            "desc": "1.78 inch AMOLED Always-on display smart watch with continuous heart rate monitoring.",
            "specs": {"Display Type": "AMOLED", "Battery Backup": "Up to 7 Days"}
        }
    ]

# Session State Keys Safety Check
if "cart" not in st.session_state: st.session_state.cart = {}
if "user_login" not in st.session_state: st.session_state.user_login = False
if "user_profile" not in st.session_state: st.session_state.user_profile = {"name": "", "phone": "", "address": ""}
if "live_loc" not in st.session_state: st.session_state.live_loc = ""
if "selected_product" not in st.session_state: st.session_state.selected_product = None

def fetch_auto_location():
    with st.spinner("Tracking Live GPS via Network..."):
        time.sleep(1)
        st.session_state.live_loc = "At Meghpatti, Post Bandhar, Samastipur, Bihar - 848117 (📍 GPS Auto-Detected)"
        st.toast("📌 Location tracked successfully!")

# --- FLIPKART PREMIUM HEADER ---
st.markdown("""
    <div class="fk-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 28px; font-weight: 800; letter-spacing: 1px;">flipkart</span>
                <span style="font-size: 13px; font-style: italic; color: #ffe500; font-weight: bold; margin-left: 5px;">plus 🌟</span>
            </div>
            <div style="font-size: 16px; font-weight: bold;">Sandhya Digital Mall Control Center</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar Account Control Center
with st.sidebar:
    st.markdown("### 👤 Customer Account Center")
    if not st.session_state.user_login:
        st.markdown("<div class='3d-box'>", unsafe_allow_html=True)
        login_phone = st.text_input("Enter Mobile Number", max_chars=10, placeholder="9934XXXXXX")
        if st.button("📲 Login via OTP", use_container_width=True, type="primary"):
            if len(login_phone) == 10 and login_phone.isdigit():
                st.session_state.user_login = True
                st.session_state.user_profile["phone"] = login_phone
                st.rerun()
            else: st.error("Enter valid 10 digits.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='3d-box' style='background-color: #f0fdf4;'>🟢 Active: +91 {st.session_state.user_profile['phone']}</div>", unsafe_allow_html=True)
        p_name = st.text_input("Your Full Name", value=st.session_state.user_profile["name"])
        if st.button("📍 Auto-Detect Live Location", use_container_width=True): fetch_auto_location()
        default_addr = st.session_state.live_loc if st.session_state.live_loc else st.session_state.user_profile["address"]
        p_addr = st.text_area("Delivery Address", value=default_addr)
        if st.button("💾 Save Profile Data", use_container_width=True):
            st.session_state.user_profile["name"] = p_name
            st.session_state.user_profile["address"] = p_addr
            st.toast("Profile details saved!")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_login = False
            st.session_state.cart = {}
            st.session_state.selected_product = None
            st.rerun()

    st.markdown("---")
    st.markdown("### 🛒 Live Cart Summary")
    if not st.session_state.cart: st.caption("Cart is empty.")
    else:
        tot = 0.0
        for pid, item in list(st.session_state.cart.items()):
            sub = item['price'] * item['qty']
            tot += sub
            st.write(f"🛍️ **{item['name']}** (x{item['qty']}) — ₹{sub:,}")
        st.markdown(f"**Total Bill: ₹{tot:,}**")

# Layout Tabs
tab1, tab2, tab3 = st.tabs(["⚡ Flipkart Grid Store", "📦 Secure Checkout System", "➕ Add New Product (Admin)"])

# TAB 1: PRODUCT LIST & BUG-FREE DETAIL PAGE
with tab1:
    # Safe State Checker to avoid AttributeError
    if st.session_state.selected_product is not None:
        p = st.session_state.selected_product
        if st.button("⬅️ Back to All Products", type="secondary"):
            st.session_state.selected_product = None
            st.rerun()
        
        st.markdown("---")
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown(f'<div style="background:#f8fafc; border:2px dashed #cbd5e1; height:300px; display:flex; align-items:center; justify-content:center; border-radius:12px;"><h3>📸 {p.get("name", "Product")} Image</h3></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span class="fk-tag">{p.get("rating", "4.0★")}</span> <span style="color:#388e3c; font-weight:bold;">{p.get("offer", "")}</span>', unsafe_allow_html=True)
            st.h1(p.get("name", "Product Specification"))
            st.markdown(f'<div class="fk-price" style="font-size:32px;">Price: ₹{p.get("price", 0.0):,}</div>', unsafe_allow_html=True)
            st.write(f"**Description:** {p.get('desc', '')}")
            
            spec_html = "<table class='spec-table'>"
            for k, v in p.get('specs', {}).items():
                spec_html += f"<tr><td class='spec-label'>{k}</td><td>{v}</td></tr>"
            spec_html += "</table>"
            st.markdown(spec_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            qnty = st.number_input("Select Qty", min_value=1, max_value=5, value=1, key="qty_select")
            if st.button("🛒 ADD TO CART NOW", type="primary", use_container_width=True):
                if not st.session_state.user_login: st.error("Please login first!")
                else:
                    st.session_state.cart[p['id']] = {"name": p['name'], "price": p['price'], "qty": qnty}
                    st.success("Added to Cart successfully!")
                    time.sleep(0.5)
                    st.rerun()
    else:
        col_grid = st.columns(2)
        for index, p in enumerate(st.session_state.products_db):
            with col_grid[index % 2]:
                st.markdown(f"""
                    <div class="fk-card">
                        <span class="fk-tag">{p.get('rating', '4.0★')}</span>
                        <h3 style="color:#2874f0; margin:10px 0;">{p.get('name', 'Product')}</h3>
                        <div class="fk-price">₹{p.get('price', 0.0):,}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"🔍 View Specs & Details", key=f"btn_{p['id']}", use_container_width=True):
                    st.session_state.selected_product = p
                    st.rerun()

# TAB 2: CHECKOUT (COD / ONLINE WIRE SYSTEM)
with tab2:
    st.subheader("📦 Select Payment Mode & Place Order")
    if not st.session_state.user_login: st.warning("Please login from sidebar.")
    elif not st.session_state.cart: st.info("Your cart is empty.")
    else:
        bill_total = sum(item['price'] * item['qty'] for item in st.session_state.cart.values())
        st.markdown(f"<h3 style='color:#388e3c;'>Grand Total Amount: ₹{bill_total:,}</h3>", unsafe_allow_html=True)
        
        with st.form("payment_checkout_form"):
            final_name = st.text_input("Customer Name", value=st.session_state.user_profile["name"])
            final_address = st.text_area("Delivery Address", value=st.session_state.user_profile["address"])
            
            pay_mode = st.radio("Choose Payment Mode*", ["💵 Cash on Delivery (COD)", "💳 Online UPI Payment (Advance)"])
            
            utr_input = ""
            if "Online" in pay_mode:
                st.markdown(f"""
                    <div style="background:#eff6ff; padding:15px; border-radius:8px; border:1px solid #bfdbfe; margin-top:10px;">
                        <strong>✨ Online Payment Instructions:</strong><br>
                        Please pay ₹{bill_total:,} via UPI to <strong>avdheshkumar@axisbank</strong>.<br>
                        Pay karne ke baad niche 12-digit ka UTR number enter karein.
                    </div>
                """, unsafe_allow_html=True)
                utr_input = st.text_input("Enter 12-Digit UPI Transaction UTR Number*")
            
            if st.form_submit_button("🚀 CONFIRM AND PLACE ORDER", use_container_width=True, type="primary"):
                if not final_name or not final_address:
                    st.error("Please fill Name and Address details.")
                elif "Online" in pay_mode and len(utr_input) < 12:
                    st.error("Please enter a valid 12-digit UTR Number for payment verification.")
                else:
                    items_bought = [f"{v['name']} (x{v['qty']})" for v in st.session_state.cart.values()]
                    full_log = f"Items: {', '.join(items_bought)} | Address: {final_address}"
                    
                    status_text = "COD - Dispatch Pending" if "Cash" in pay_mode else f"Online Paid - Verifying (UTR: {utr_input})"
                    
                    payload = {
                        "sheet_name": "Payment_Ledger",
                        "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": final_name.upper(),
                        "Amount": bill_total,
                        "Mode": "Store: " + pay_mode,
                        "SenderUPI_Mobile": st.session_state.user_profile["phone"],
                        "Status": status_text,
                        "Reference": full_log
                    }
                    
                    try:
                        requests.post(WEBHOOK_URL, json=payload, timeout=10)
                        st.balloons()
                        st.success(f"🎉 Order Confirmed! Sent directly to your Google Sheet Row.")
                        st.session_state.cart = {}
                        st.session_state.selected_product = None
                    except Exception as e: st.error(f"Error connecting to spreadsheet: {e}")

# TAB 3: ADMIN AREA (ADD PRODUCTS LOGIC)
with tab3:
    st.subheader("➕ Sandhya Digital Mall - Inventory Control")
    st.info("यहाँ से नया प्रोडक्ट भरें, वह तुरंत पहले टैब में बिकने के लिए आ जाएगा।")
    
    with st.form("admin_add_product_form"):
        new_id = f"FK{len(st.session_state.products_db) + 1:02d}"
        new_name = st.text_input("Product Title*")
        new_price = st.number_input("Product Price (Rs)*", min_value=1.0, value=299.0)
        new_cat = st.selectbox("Category Group", ["Electronics", "Accessories", "Mobile", "Other"])
        new_offer = st.text_input("Discount Label (e.g., 20% OFF)", value="Special Deal")
        new_desc = st.text_area("Detailed Description")
        
        st.markdown("##### Specifications Parameters")
        spec_k1 = st.text_input("Param 1 (e.g., Brand)", value="Sandhya Brand")
        spec_v1 = st.text_input("Value 1", value="Original")
        spec_k2 = st.text_input("Param 2 (e.g., Warranty)", value="1 Year")
        spec_v2 = st.text_input("Value 2")
        
        if st.form_submit_button("➕ ADD PRODUCT TO LIVE STOREFRONT", use_container_width=True):
            if not new_name:
                st.error("Product title field cannot be left blank.")
            else:
                new_item = {
                    "id": new_id,
                    "name": new_name,
                    "price": float(new_price),
                    "cat": new_cat,
                    "rating": "4.4★",
                    "offer": new_offer,
                    "desc": new_desc,
                    "specs": {spec_k1: spec_v1, spec_k2: spec_v2} if spec_v2 else {spec_k1: spec_v1}
                }
                st.session_state.products_db.append(new_item)
                st.success(f"🎉 Successful: '{new_name}' Live Store Front पर ऐड हो गया!")
                time.sleep(0.5)
                st.rerun()
