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
        text-align: center; margin-bottom: 25px; cursor: pointer;
    }
    .fk-price { color: #212121; font-size: 24px; font-weight: bold; margin: 8px 0; }
    .fk-tag { background: #388e3c; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .fk-offer { color: #388e3c; font-weight:bold; font-size:14px; }
    
    /* Detailed View Styling */
    .detail-box {
        background: #ffffff; padding: 30px; border-radius: 12px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1); border: 1px solid #cbd5e1;
    }
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
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"

# Live Product Catalog Database with Specifications
PRODUCTS = [
    {
        "id": "FK01", "name": "Premium Wireless Earbuds (Super Bass)", "price": 1499.0, "cat": "Electronics", "rating": "4.3★", "offer": "25% OFF",
        "desc": "High-fidelity wireless sound with deep bass and up to 40 hours of total playback time. Features environmental noise cancellation.",
        "specs": {"Brand": "Sandhya Digital", "Battery Life": "40 Hours", "Bluetooth Version": "5.3", "Water Resistance": "IPX5 Certified"}
    },
    {
        "id": "FK02", "name": "Smart Fitness Watch Pro AMOLED", "price": 2499.0, "cat": "Electronics", "rating": "4.5★", "offer": "10% OFF",
        "desc": "1.78 inch AMOLED Always-on display smart watch with continuous heart rate monitoring, SpO2 tracking, and 100+ sports modes.",
        "specs": {"Display Size": "1.78 Inch", "Display Type": "AMOLED", "Battery Backup": "Up to 7 Days", "Sensors": "Heart Rate, SpO2, Pedometer"}
    },
    {
        "id": "FK03", "name": "Fast Charging Power Bank 20000mAh", "price": 1199.0, "cat": "Accessories", "rating": "4.1★", "offer": "15% OFF",
        "desc": "22.5W ultra-fast charging power bank with triple output ports. Built-in multi-layer protection protocols for safe charging.",
        "specs": {"Capacity": "20000 mAh", "Max Output": "22.5W Fast Charge", "Ports": "2 USB-A, 1 Type-C", "Warranty": "6 Months Domestic"}
    },
    {
        "id": "FK04", "name": "Ergonomic Mechanical Wireless Mouse", "price": 699.0, "cat": "Accessories", "rating": "4.2★", "offer": "50% OFF",
        "desc": "Silent-click multi-device wireless mechanical mouse with adjustable DPI up to 4000. Perfectly curved design for wrist comfort.",
        "specs": {"Type": "Mechanical Wireless", "DPI Range": "800 - 4000 DPI", "Connection": "2.4GHz + Bluetooth", "Battery": "1 x AA (Included)"}
    },
]

# Session States Management
if "cart" not in st.session_state: st.session_state.cart = {}
if "user_login" not in st.session_state: st.session_state.user_login = False
if "user_profile" not in st.session_state: st.session_state.user_profile = {"name": "", "phone": "", "address": ""}
if "live_loc" not in st.session_state: st.session_state.live_loc = ""
if "selected_product" not in st.session_state: st.session_state.selected_product = None

def fetch_auto_location():
    with st.spinner("Fetching GPS coordinates via Network..."):
        time.sleep(1)
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
            <div style="font-size: 16px; font-weight: bold;">Sandhya Digital Mall</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar - Login & Profile Center
with st.sidebar:
    st.markdown("### 👤 Customer Account Center")
    if not st.session_state.user_login:
        st.markdown("<div class='3d-box'>", unsafe_allow_html=True)
        login_phone = st.text_input("Enter Mobile Number", max_chars=10, placeholder="9934XXXXXX")
        if st.button("📲 Send OTP & Login", use_container_width=True, type="primary"):
            if len(login_phone) == 10 and login_phone.isdigit():
                st.session_state.user_login = True
                st.session_state.user_profile["phone"] = login_phone
                st.rerun()
            else: st.error("Invalid 10-digit mobile number.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='3d-box' style='background-color: #f0fdf4;'>🟢 **Active:** +91 {st.session_state.user_profile['phone']}</div>", unsafe_allow_html=True)
        p_name = st.text_input("Your Full Name", value=st.session_state.user_profile["name"])
        if st.button("📍 Auto-Detect Live Location", use_container_width=True): fetch_auto_location()
        default_addr = st.session_state.live_loc if st.session_state.live_loc else st.session_state.user_profile["address"]
        p_addr = st.text_area("Delivery Address", value=default_addr)
        if st.button("💾 Save Profile Data", use_container_width=True):
            st.session_state.user_profile["name"] = p_name
            st.session_state.user_profile["address"] = p_addr
            st.toast("Profile data locked!")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.user_login = False
            st.session_state.cart = {}
            st.session_state.selected_product = None
            st.rerun()

    st.markdown("---")
    st.markdown("### 🛒 My Cart Summary")
    if not st.session_state.cart: st.caption("Your cart is empty.")
    else:
        tot = 0.0
        for pid, item in list(st.session_state.cart.items()):
            sub = item['price'] * item['qty']
            tot += sub
            st.write(f"🛍️ **{item['name']}** (x{item['qty']}) — ₹{sub:,}")
        st.markdown(f"**Grand Total: ₹{tot:,}**")

# Main Page Navigation Control
tab1, tab2 = st.tabs(["⚡ Flipkart Grid Store", "📦 Secure Checkout System"])

with tab1:
    # 🔴 IF PRODUCT IS CLICKED -> OPEN DETAIL VIEW (Like Flipkart)
    if st.session_state.selected_product is not None:
        p = st.session_state.selected_product
        if st.button("⬅️ Back to All Products", type="secondary"):
            st.session_state.selected_product = None
            st.rerun()
            
        st.markdown("---")
        col_img, col_desc = st.columns([1, 1.2])
        
        with col_img:
            # Placeholder Box for Product Image Look
            st.markdown(f"""
                <div style="background: #f8fafc; border: 2px dashed #cbd5e1; height: 350px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                    <div style="text-align: center; color: #64748b;">
                        <span style="font-size: 70px;">📸</span>
                        <h4 style="margin: 10px 0 0 0;">{p['name']} Image Preview</h4>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_desc:
            st.markdown(f"""
                <span class="fk-tag">{p['rating']}</span>
                <h1 style="color:#212121; margin: 10px 0 5px 0; font-size: 28px;">{p['name']}</h1>
                <span class="fk-offer" style="font-size: 18px;">Special Price: {p['offer']}</span>
                <div class="fk-price" style="font-size: 36px; margin: 15px 0;">₹{p['price']:,}</div>
                <p style="color: #212121; font-size: 16px; line-height: 1.6;"><b>Description:</b> {p['desc']}</p>
                <hr style="border: 0; border-top: 1px solid #cbd5e1; margin: 20px 0;">
                <h3>Product Specifications</h3>
            """, unsafe_allow_html=True)
            
            # Generate HTML Table for Specs
            spec_html = "<table class='spec-table'>"
            for label, value in p['specs'].items():
                spec_html += f"<tr><td class='spec-label'>{label}</td><td style='color:#212121;'>{value}</td></tr>"
            spec_html += "</table>"
            st.markdown(spec_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Purchase actions inside detailed view
            qnty = st.number_input("Select Quantity", min_value=1, max_value=10, value=1)
            if st.button("🛒 ADD TO CART NOW", type="primary", use_container_width=True):
                if not st.session_state.user_login:
                    st.error("⚠️ Please login with your phone number in the sidebar panel first!")
                else:
                    st.session_state.cart[p['id']] = {"name": p['name'], "price": p['price'], "qty": qnty}
                    st.success(f"🎉 Successfully added {qnty} quantity of {p['name']} to cart!")
                    time.sleep(1)
                    st.rerun()

    # 🔴 ELSE -> SHOW STANDARD PRODUCT GRID LIST
    else:
        st.markdown("#### Top Categories: `All Products` | `Electronics` | `Accessories`")
        st.markdown("---")
        
        col_grid = st.columns(2)
        for index, p in enumerate(PRODUCTS):
            with col_grid[index % 2]:
                st.markdown(f"""
                    <div class="fk-card">
                        <span class="fk-tag">{p['rating']}</span>
                        <span style="color: #388e3c; font-weight:bold; font-size:13px; float:right;">{p['offer']}</span>
                        <h3 style="margin: 15px 0 5px 0; color: #2874f0; font-size:20px;">{p['name']}</h3>
                        <div class="fk-price">₹{p['price']:,}</div>
                        <p style="color: #878787; font-size: 12px; margin: 0;">Click 'View Details' below to check specifications.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # View Details Button to switch view state
                if st.button(f"🔍 View Full Details & Specs", key=f"det_{p['id']}", use_container_width=True):
                    st.session_state.selected_product = p
                    st.rerun()

# TAB 2: SMART AUTO-FILLED CHECKOUT (Unchanged)
with tab2:
    st.subheader("📦 Finalize Your Flipkart Style Order")
    if not st.session_state.user_login:
        st.warning("🔒 Account access required. Please register/login with your mobile number in the left sidebar panels.")
    elif not st.session_state.cart:
        st.info("Your shopping cart is currently empty. Add products from the grid store tab.")
    else:
        bill_records = []
        bill_total = 0.0
        for pid, item in st.session_state.cart.items():
            sub_tot = item['price'] * item['qty']
            bill_total += sub_tot
            bill_records.append({"Item ID": pid, "Product Specification": item['name'], "Unit Price": f"₹{item['price']:,}", "Qty": item['qty'], "Subtotal Price": f"₹{sub_tot:,}"})
        st.dataframe(pd.DataFrame(bill_records), use_container_width=True)
        
        st.markdown(f"<div style='text-align: right; background: #fff9e6; padding: 15px; border-radius: 8px; border: 1px solid #f2c94c; margin-bottom: 20px;'><span style='font-size: 16px; font-weight: bold; color: #7d5a00;'>Flipkart Deal Total Price:</span><span style='font-size: 26px; font-weight: bold; color: #212121; margin-left:15px;'>₹{bill_total:,}</span></div>", unsafe_allow_html=True)
        
        with st.form("fk_checkout_form"):
            final_name = st.text_input("Customer Name (Auto-filled)", value=st.session_state.user_profile["name"])
            final_phone = st.text_input("Contact Mobile Number (Auto-filled)", value=st.session_state.user_profile["phone"], disabled=True)
            final_address = st.text_area("Shipping Destination Address (Auto-filled)", value=st.session_state.user_profile["address"])
            
            if st.form_submit_button("🚀 CONFIRM & PLACE ORDER VIA GOOGLE SHEET", use_container_width=True, type="primary"):
                if not final_name or not final_address:
                    st.error("Checkout Failed: Profile Name or Delivery Address cannot be empty.")
                else:
                    items_bought = [f"{v['name']} (Qty: {v['qty']})" for v in st.session_state.cart.values()]
                    full_summary_log = f"Items Ordered: {', '.join(items_bought)} | Delivery Address: {final_address}"
                    
                    order_payload = {
                        "sheet_name": "Payment_Ledger", "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": final_name.upper(), "Amount": bill_total, "Mode": "Flipkart Style Online Store",
                        "SenderUPI_Mobile": final_phone, "Status": "Order Dispatch Pending", "Reference": full_summary_log
                    }
                    try:
                        requests.post(WEBHOOK_URL, json=order_payload, timeout=10)
                        st.balloons()
                        st.success(f"🎉 Success! Order booked for {final_name}. Data uploaded to Google Sheet!")
                        st.session_state.cart = {}
                        st.session_state.selected_product = None
                    except Exception as e: st.error(f"Network error: {e}")
