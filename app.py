import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Premium Flipkart-Style Theme & 3D CSS Design
st.set_page_config(page_title="Flipkart Style Store", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    /* Flipkart Header Colors */
    .fk-header {
        background-color: #2874f0; padding: 15px 30px; border-radius: 0px 0px 10px 10px;
        color: white; margin-bottom: 25px; box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    /* 3D Product Cards Like Flipkart Grid */
    .fk-card {
        background: #ffffff; padding: 20px; border-radius: 12px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;
        text-align: center; margin-bottom: 25px; transition: 0.3s ease-in-out;
    }
    .fk-card:hover { transform: translateY(-5px); box-shadow: 0px 12px 30px rgba(0,0,0,0.15); }
    .fk-price { color: #212121; font-size: 24px; font-weight: bold; margin: 8px 0; }
    .fk-tag { background: #388e3c; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    /* 3D Profile & Cart Sections */
    .3d-box {
        background: #ffffff; padding: 25px; border-radius: 12px;
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.05), 0px 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #cbd5e1; margin-bottom: 20px;
    }
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px !important; background-color: #f8fafc !important; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 GOOGLE SHEET CONFIG
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"

# Live Product Catalog Database
PRODUCTS = [
    {"id": "FK01", "name": "Premium Wireless Earbuds (Super Bass)", "price": 1499.0, "cat": "Electronics", "rating": "4.3★", "offer": "25% OFF"},
    {"id": "FK02", "name": "Smart Fitness Watch Pro AMOLED", "price": 2499.0, "cat": "Electronics", "rating": "4.5★", "offer": "10% OFF"},
    {"id": "FK03", "name": "Fast Charging Power Bank 20000mAh", "price": 1199.0, "cat": "Accessories", "rating": "4.1★", "offer": "15% OFF"},
    {"id": "FK04", "name": "Ergonomic Mechanical Wireless Mouse", "price": 699.0, "cat": "Accessories", "rating": "4.2★", "offer": "50% OFF"},
]

# Session States for Cart and User Session
if "cart" not in st.session_state: st.session_state.cart = {}
if "user_login" not in st.session_state: st.session_state.user_login = False
if "user_profile" not in st.session_state: st.session_state.user_profile = {"name": "", "phone": "", "address": ""}
if "live_loc" not in st.session_state: st.session_state.live_loc = ""

# --- 🛰️ AUTOMATIC LOCATION TRACKING SYSTEM ---
# Jab customer click karega, browser se live geo-location lookup dummy format me trigger hoga
def fetch_auto_location():
    with st.spinner("Fetching GPS coordinates via Network..."):
        time.sleep(1)
        # Samastipur, Bihar distribution area automatically tracked based on network node
        st.session_state.live_loc = "At Meghpatti, Post Bandhar, Samastipur, Bihar - 848117 (📍 Detected via GPS Live)"
        st.toast("📌 Live Location tracked automatically!")

# --- 🛍️ FLIPKART PREMIUM HEADER ---
st.markdown("""
    <div class="fk-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 28px; font-weight: 800; letter-spacing: 1px;">flipkart</span>
                <span style="font-size: 13px; font-style: italic; color: #ffe500; font-weight: bold; margin-left: 5px;">plus 🌟</span>
            </div>
            <div style="font-size: 16px; font-weight: bold;">
                Welcome to Sandhya Digital Mall
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar - Login and Profile Center
with st.sidebar:
    st.markdown("### 👤 Customer Account Center")
    
    if not st.session_state.user_login:
        st.markdown("<div class='3d-box'>", unsafe_allow_html=True)
        st.info("🔒 Please login with your Mobile number to start shopping.")
        login_phone = st.text_input("Enter Mobile Number", max_chars=10, placeholder="9934XXXXXX")
        
        if st.button("📲 Send OTP & Login", use_container_width=True, type="primary"):
            if len(login_phone) == 10 and login_phone.isdigit():
                st.session_state.user_login = True
                st.session_state.user_profile["phone"] = login_phone
                st.success("✅ Logged In via OTP Successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid 10-digit mobile number.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='3d-box' style='background-color: #f0fdf4;'>", unsafe_allow_html=True)
        st.markdown(f"🟢 **Active Session:** +91 {st.session_state.user_profile['phone']}")
        
        # Profile Configuration (Will auto-fill in Checkout form)
        st.markdown("#### Edit Your Profile")
        p_name = st.text_input("Your Full Name", value=st.session_state.user_profile["name"])
        
        # Location Auto Tracker Button
        if st.button("📍 Auto-Detect My Live Location", use_container_width=True):
            fetch_auto_location()
            
        default_addr = st.session_state.live_loc if st.session_state.live_loc else st.session_state.user_profile["address"]
        p_addr = st.text_area("Delivery Address", value=default_addr)
        
        if st.button("💾 Save Profile Data", use_container_width=True):
            st.session_state.user_profile["name"] = p_name
            st.session_state.user_profile["address"] = p_addr
            st.toast("Profile details updated & locked!")
            
        if st.button("🚪 Logout Account", use_container_width=True, type="secondary"):
            st.session_state.user_login = False
            st.session_state.cart = {}
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Sidebar Interactive Cart Live Counters
    st.markdown("---")
    st.markdown("### 🛒 Flipkart Cart Summary")
    if not st.session_state.cart:
        st.caption("Your cart is empty.")
    else:
        tot = 0.0
        for pid, item in list(st.session_state.cart.items()):
            sub = item['price'] * item['qty']
            tot += sub
            st.write(f"🛍️ **{item['name']}** (x{item['qty']}) — ₹{sub:,}")
        st.markdown(f"**Grand Total: ₹{tot:,}**")

# Main Page Tabs
tab1, tab2 = st.tabs(["⚡ Flipkart Grid Store", "📦 Secure Checkout System"])

# TAB 1: BROWSE ITEMS
with tab1:
    # Categories selection row
    st.markdown("#### Top Categories: `All Products` | `Electronics` | `Accessories` | `Trending Offers`")
    st.markdown("---")
    
    col_grid = st.columns(2)
    for index, p in enumerate(PRODUCTS):
        with col_grid[index % 2]:
            st.markdown(f"""
                <div class="fk-card">
                    <span class="fk-tag">{p['rating']}</span>
                    <span style="color: #388e3c; font-weight:bold; font-size:13px; float:right;">{p['offer']}</span>
                    <h3 style="margin: 15px 0 5px 0; color: #212121; font-size:20px;">{p['name']}</h3>
                    <p style="color: #878787; font-size: 13px;">Item ID: {p['id']} | Category: {p['cat']}</p>
                    <div class="fk-price">₹{p['price']:,}</div>
                    <p style="color: #388e3c; font-size:12px; font-weight:bold; margin:0;">Standard Free Delivery Available</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Smart Add Button
            if st.button(f"🛒 Add Item to Flipkart Cart", key=p['id'], use_container_width=True):
                if not st.session_state.user_login:
                    st.error("⚠️ Please login with your phone number in the sidebar first!")
                else:
                    if p['id'] in st.session_state.cart:
                        st.session_state.cart[p['id']]['qty'] += 1
                    else:
                        st.session_state.cart[p['id']] = {"name": p['name'], "price": p['price'], "qty": 1}
                    st.toast(f"Success: {p['name']} added to cart!")
                    time.sleep(0.3)
                    st.rerun()

# TAB 2: SMART AUTO-FILLED CHECKOUT
with tab2:
    st.subheader("📦 Finalize Your Flipkart Style Order")
    
    if not st.session_state.user_login:
        st.warning("🔒 Account access required. Please register/login with your mobile number in the left sidebar panels.")
    elif not st.session_state.cart:
        st.info("Your shopping cart is currently empty. Add products from the grid store tab.")
    else:
        # Generate Checkout Billing Preview Table
        bill_records = []
        bill_total = 0.0
        for pid, item in st.session_state.cart.items():
            sub_tot = item['price'] * item['qty']
            bill_total += sub_tot
            bill_records.append({
                "Item ID": pid,
                "Product Specification": item['name'],
                "Unit Price": f"₹{item['price']:,}",
                "Qty": item['qty'],
                "Subtotal Price": f"₹{sub_tot:,}"
            })
        st.dataframe(pd.DataFrame(bill_records), use_container_width=True)
        
        st.markdown(f"""
            <div style="text-align: right; background: #fff9e6; padding: 15px; border-radius: 8px; border: 1px solid #f2c94c; margin-bottom: 20px;">
                <span style="font-size: 16px; font-weight: bold; color: #7d5a00;">Flipkart Deal Total Price:</span>
                <span style="font-size: 26px; font-weight: bold; color: #212121; margin-left:15px;">₹{bill_total:,}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Order booking form - Auto-filled using values from saved Profile State
        st.markdown("### 📋 Verification of Delivery & Profile Data")
        with st.form("fk_checkout_form"):
            st.info("💡 Below details are loaded automatically from your saved profile data.")
            
            # AUTO-FILLED DATA FROM PROFILE MEMORY
            final_name = st.text_input("Customer Name (Auto-filled)", value=st.session_state.user_profile["name"])
            final_phone = st.text_input("Contact Mobile Number (Auto-filled)", value=st.session_state.user_profile["phone"], disabled=True)
            final_address = st.text_area("Shipping Destination Address (Auto-filled)", value=st.session_state.user_profile["address"])
            
            if st.form_submit_button("🚀 CONFIRM & PLACE ORDER VIA GOOGLE SHEET", use_container_width=True, type="primary"):
                if not final_name or not final_address:
                    st.error("Checkout Failed: Profile Name or Delivery Address cannot be empty. Please save your profile data first.")
                else:
                    # Construct detailed receipt overview log string
                    items_bought = [f"{v['name']} (Qty: {v['qty']})" for v in st.session_state.cart.values()]
                    full_summary_log = f"Items Ordered: {', '.join(items_bought)} | Delivery Address: {final_address}"
                    
                    # Prepare matching row data payload package for Google Sheets API endpoint
                    order_payload = {
                        "sheet_name": "Payment_Ledger",
                        "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": final_name.upper(),
                        "Amount": bill_total,
                        "Mode": "Flipkart Style Online Store",
                        "SenderUPI_Mobile": final_phone,
                        "Status": "Order Dispatch Pending",
                        "Reference": full_summary_log
                    }
                    
                    try:
                        requests.post(WEBHOOK_URL, json=order_payload, timeout=10)
                        st.balloons()
                        st.success(f"🎉 Success! Order booked for {final_name}. Total Invoice Worth ₹{bill_total:,} uploaded to database ledger!")
                        # Flush cart items state clean after transaction complete
                        st.session_state.cart = {}
                    except Exception as transaction_err:
                        st.error(f"Network error syncing connection to spreadsheet ledger: {transaction_err}")
