import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Premium Hyperlocal Kirana Theme (Blinkit / Zepto Style Grid)
st.set_page_config(page_title="Sandhya Local Mart", page_icon="🛵", layout="wide")

st.markdown("""
    <style>
    .main .block-container { 
        background-color: #ffffff; padding: 2rem 3rem; border-radius: 15px; 
        max-width: 900px; box-shadow: 0px 10px 40px rgba(0,0,0,0.1); margin: auto;
    }
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%); padding: 20px; 
        border-radius: 12px; text-align: center; color: white; margin-bottom: 25px;
    }
    /* Blinkit Style Rounded Category Icons */
    .category-box {
        background: #f4f4f5; padding: 15px; border-radius: 18px;
        text-align: center; border: 1px solid #e4e4e7; cursor: pointer;
        transition: 0.2s ease-in-out; margin-bottom: 15px;
    }
    .category-box:hover { background: #fef08a; border-color: #facc15; transform: scale(1.03); }
    .category-icon { font-size: 40px; margin-bottom: 5px; }
    .category-title { font-size: 14px; font-weight: bold; color: #1f2937; }
    
    .section-title { font-size: 20px; font-weight: 800; color: #111827; margin: 20px 0 10px 0; border-left: 5px solid #2563eb; padding-left: 10px; }
    .bill-box { background-color: #fffde7; padding: 20px; border-radius: 10px; border: 1px solid #fef08a; color: #713f12; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 UPDATED GOOGLE SHEET WEBHOOK CONNECTION
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyHCrzqnjgiwCZvcZy4evkZRToRtaziZJGch9F-ODVQXzVcTdAqJhJRvXxH48PKTfhrug/exec"
ADMIN_PASSWORD = "Jio Distributor"

if "selected_category" not in st.session_state: st.session_state.selected_category = "Telecom"
if "admin_logged" not in st.session_state: st.session_state.admin_logged = False

# App Bar Header
st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; font-size: 28px; font-weight: 800;">🛵 SANDHYA LOCAL MART</h1>
        <p style="margin:5px 0 0 0; font-size: 15px;">Jio Services & Kirana Delivery Within 5KMs (Meghpatti Hub)</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Auth Mode
with st.sidebar:
    st.markdown("### 🔐 System Access Mode")
    access_mode = st.radio("Select Role:", ["👤 Customer Interface", "🛠️ Admin Dashboard"])
    if access_mode == "🛠️ Admin Dashboard":
        pwd = st.text_input("Enter Secret Admin Password", type="password")
        if pwd == ADMIN_PASSWORD: st.session_state.admin_logged = True
        else: st.session_state.admin_logged = False

if access_mode == "🛠️ Admin Dashboard" and st.session_state.admin_logged:
    st.subheader("🛠️ Central Admin Control Tower")
    st.markdown(f"""
        <div style='background:#f0fdf4; border:1px solid #bbf7d0; padding:20px; border-radius:10px; text-align:center;'>
            <h4>📊 Your Connected Google Sheet Ledger is Live</h4>
            <a href='https://docs.google.com/spreadsheets/d/17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM/edit' target='_blank'>
                <button style='background-color:#16a34a; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; cursor:pointer;'>Open Live Google Sheet Ledger</button>
            </a>
        </div>
    """, unsafe_allow_html=True)

else:
    # 👤 CUSTOMER INTERFACE
    st.markdown("### 📋 Customer & Delivery Information")
    c_name = st.text_input("Customer Name*", placeholder="e.g. Avdhesh Kumar")
    c_phone = st.text_input("Mobile Number*", max_chars=10)
    c_addr = st.text_area("Delivery Address (Meghpatti Area)*")
    
    st.markdown("#### 📍 Operational Distance Lock")
    c_dist = st.slider("Distance from Head Office (KM)", min_value=0.5, max_value=10.0, value=1.0, step=0.5)
    
    if c_dist > 5.0:
        st.error("🚨 BOUNDARY LOCK: We strictly deliver within 5KMs range to keep food fresh and deliveries on time.")
    else:
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # --- 🛍️ BLINKIT STYLE GRID CATEGORIES ---
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
        
        # --- 📦 DYNAMIC ITEMS DISPATCH BASED ON SELECTED GRID CATEGORY ---
        current_cat = st.session_state.selected_category
        st.markdown(f"<div class='section-title'>Items inside: {current_cat} Department</div>", unsafe_allow_html=True)
        
        selected_item_name = ""
        base_item_price = 0.0
        details_required = False
        
        if current_cat == "Telecom":
            telecom_option = st.selectbox("Select Jio Service:", ["MNP (Port to Jio) - Free", "New Jio SIM Activation - Free", "Jio Phone Bharat V4 - ₹1099"])
            if "MNP" in telecom_option:
                selected_item_name = "Jio MNP Request"
                base_item_price = 0.0
            elif "New SIM" in telecom_option:
                selected_item_name = "New SIM Activation"
                base_item_price = 0.0
            else:
                selected_item_name = "Jio Phone Bharat V4"
                base_item_price = 1099.0
                
        elif current_cat == "Atta":
            atta_option = st.selectbox("Select Flour Brand:", ["Ashirvaad Shudh Chakki Aata 5Kg", "Fortune Chakki Fresh Aata 5Kg", "Local Mill Fresh Aata 5Kg"])
            selected_item_name = atta_option
            base_item_price = st.number_input("Confirm Store Price (Rs)*", min_value=10.0, value=260.0)
            details_required = True
            
        elif current_cat == "Rice":
            rice_option = st.selectbox("Select Rice/Dal Type:", ["Premium Basmati Rice 1Kg", "Arhar / Toor Dal 1Kg", "Masoor Dal 1Kg"])
            selected_item_name = rice_option
            base_item_price = st.number_input("Confirm Store Price (Rs)*", min_value=10.0, value=140.0)
            details_required = True
            
        elif current_cat == "Oils":
            oil_option = st.selectbox("Select Ghee/Oils:", ["Fortune Mustard Oil 1L", "Dhara Refined Sunflower Oil 1L", "Amul Pure Ghee 1L"])
            selected_item_name = oil_option
            base_item_price = st.number_input("Confirm Store Price (Rs)*", min_value=10.0, value=175.0)
            details_required = True

        # --- 💰 AUTOMATED COMMISSION MATRIX CALCULATION ---
        delivery_rider_fee = 15.0  # Riders dispatch allowance
        merchant_commission = round(base_item_price * 0.05, 2) if base_item_price > 0 else 0.0
        customer_convenience = round(base_item_price * 0.02, 2) if base_item_price > 0 else 0.0
        final_payable_amt = base_item_price + delivery_rider_fee + customer_convenience
        
        if base_item_price > 0:
            st.markdown(f"""
                <div class="bill-box">
                    <strong>📊 Live Hyperlocal Settlement Bill (Cash on Delivery):</strong><br>
                    • Store Product Cost: ₹{base_item_price:,}<br>
                    • Fixed Local Rider Delivery Charge: ₹{delivery_rider_fee:,}<br>
                    • Platform Convenience Fee: ₹{customer_convenience:,}<br>
                    <strong>👉 Net Payable to Rider: ₹{final_payable_amt:,}</strong><br>
                    <span style='font-size:12px; color:#857f07;'>[Admin Margin: Shopkeeper Comm (5%): ₹{merchant_commission} | Net System Profit: ₹{merchant_commission + customer_convenience}]</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("Jio Telecom Support: SIM Services are completely free at doorstep activation. Operator FRC plan rates apply.")
            final_payable_amt = 0.0

        if st.button("🚀 TRANSMIT ORDER TO DELIVERY NETWORK", type="primary", use_container_width=True):
            if not c_name or not c_phone or not c_addr:
                st.error("Please fill Name, Mobile and complete Address lines.")
            else:
                log_ref = f"Cat: {current_cat} | Item: {selected_item_name} | Distance: {c_dist}KM | PlatformProfit: ₹{merchant_commission + customer_convenience}"
                
                payload = {
                    "sheet_name": "Payment_Ledger",
                    "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                    "RetailerName": c_name.upper(),
                    "Amount": final_payable_amt,
                    "Mode": f"Blinkit Mode ({current_cat})",
                    "SenderUPI_Mobile": c_phone,
                    "Status": "Rider Dispatched",
                    "Reference": log_ref
                }
                try:
                    requests.post(WEBHOOK_URL, json=payload, timeout=10)
                    st.balloons()
                    st.success(f"🎉 Success! Order locked. Delivery boy dispatched to nearest partner store for {selected_item_name}.")
                except Exception as e:
                    st.error(f"Spreadsheet connection failure: {e}")
