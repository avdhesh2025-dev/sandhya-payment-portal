import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Premium Clean UI Theme Configuration
st.set_page_config(page_title="Sandhya Local Delivery Engine", page_icon="🛵", layout="wide")

st.markdown("""
    <style>
    .main .block-container { 
        background-color: #ffffff; padding: 2rem 3rem; border-radius: 15px; 
        max-width: 900px; box-shadow: 0px 10px 40px rgba(0,0,0,0.1); margin: auto;
    }
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%); padding: 25px; 
        border-radius: 12px; text-align: center; color: white; margin-bottom: 25px;
    }
    .service-card {
        background: #f8fafc; padding: 20px; border-radius: 10px;
        border: 1px solid #e2e8f0; margin-bottom: 15px; transition: 0.3s;
    }
    .service-card:hover { box-shadow: 0px 5px 15px rgba(0,0,0,0.08); }
    .bill-box {
        background-color: #fffde7; padding: 20px; border-radius: 10px;
        border: 1px solid #fef08a; margin-top: 15px; color: #713f12;
    }
    .badge-telecom { background: #dbeafe; color: #1e40af; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    .badge-kirana { background: #fef3c7; color: #92400e; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 GOOGLE SHEET WEBHOOK CONNECTION
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
ADMIN_PASSWORD = "Jio Distributor"

# 🟢 LOCAL PRODUCT CATALOG
SERVICES = [
    {"id": "JIO-01", "name": "MNP (Port to Jio)", "price": 0.0, "type": "Telecom", "desc": "Free doorstep mobile number portability service."},
    {"id": "JIO-02", "name": "New Jio SIM Card", "price": 0.0, "type": "Telecom", "desc": "New SIM activation and home delivery."},
    {"id": "JIO-03", "name": "Jio Phone Bharat V4", "price": 1099.0, "type": "Telecom", "desc": "Latest 4G Jio Bharat Phone with live tracking features."},
    {"id": "KRN-04", "name": "Kirana / Grocery Order Desk", "price": 0.0, "type": "Kirana", "desc": "Order items like 5kg Aata, Rice, etc., from nearby shops."}
]

if "active_tab" not in st.session_state: st.session_state.active_tab = "Store"
if "selected_srv" not in st.session_state: st.session_state.selected_srv = None
if "admin_logged" not in st.session_state: st.session_state.admin_logged = False

# --- APP NAVIGATION NAVBAR ---
st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; font-size: 32px; font-weight: 800;">🛵 SANDHYA HYPERLOCAL NETWORK</h1>
        <p style="margin:5px 0 0 0; font-size: 16px;">Jio Telecom Services & Grocery Delivery strictly within 5KMs</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Login Controls
with st.sidebar:
    st.markdown("### 🔐 System Access Mode")
    access_mode = st.radio("Select Role:", ["👤 Customer Interface", "🛠️ Admin Dashboard"])
    
    if access_mode == "🛠️ Admin Dashboard":
        pwd = st.text_input("Enter Secret Admin Password", type="password")
        if pwd == ADMIN_PASSWORD:
            st.session_state.admin_logged = True
            st.success("Welcome Avdhesh Kumar ji!")
        else:
            st.session_state.admin_logged = False
            if pwd: st.error("Access Denied: Incorrect Key.")
    else:
        st.session_state.admin_logged = False
        st.info("Customer mode active. Anyone within 5km can register an order.")

# --- MAIN CONTROLLER GATEWAY ---
if access_mode == "🛠️ Admin Dashboard" and st.session_state.admin_logged:
    st.subheader("🛠️ Central Admin Control Tower")
    st.info("यहाँ से आप अपने 5KM के दायरे के सारे लाइव ऑर्डर्स देख सकते हैं।")
    
    # Live Link Button to Google Sheet
    st.markdown(f"""
        <div style='background:#f0fdf4; border:1px solid #bbf7d0; padding:20px; border-radius:10px; text-align:center;'>
            <h4>📊 Your Database Ledger is Active</h4>
            <p>Every single order, delivery charge, and commission log is instantly dispatched to your Google Sheet.</p>
            <a href='https://docs.google.com/spreadsheets/d/{st.sidebar.text_input("Verify Sheet ID for safety", value="17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM")}/edit' target='_blank'>
                <button style='background-color:#16a34a; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; cursor:pointer;'>Open Live Google Sheet Ledger</button>
            </a>
        </div>
    """, unsafe_allow_html=True)

else:
    # CUSTOMER ENVIRONMENT VIEW
    st.markdown("### 🛒 Welcome to Your Neighborhood Delivery Store")
    
    # Step 1: Customer Info Gathering
    c_name = st.text_input("Enter Your Name*", placeholder="e.g. Ramesh Kumar")
    c_phone = st.text_input("Enter 10-Digit Mobile Number*", max_chars=10)
    c_addr = st.text_area("Delivery Address (Meghpatti Area)*")
    
    # Feature: Radius Gate Lock (Strict 5KM Boundary validation)
    st.markdown("#### 📍 Select Your Distance from Meghpatti Center Office")
    c_dist = st.slider("Distance (KMs)", min_value=0.5, max_value=10.0, value=1.0, step=0.5)
    
    if c_dist > 5.0:
        st.markdown("""
            <div style='background-color:#fef2f2; border:1px solid #fecaca; color:#dc2626; padding:15px; border-radius:8px; font-weight:bold; text-align:center;'>
                🚨 SERVICE UNAVAILABLE: Sandhya Network strictly opertes within a 5KM operational limit to guarantee high speed delivery boy routing.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("---")
        st.markdown("#### 📦 Available Hyperlocal Products & Requests")
        
        # Grid layout for selection
        cols = st.columns(2)
        for i, s in enumerate(SERVICES):
            with cols[i % 2]:
                badge = f'<span class="badge-telecom">Telecom</span>' if s["type"]=="Telecom" else f'<span class="badge-kirana">Kirana</span>'
                st.markdown(f"""
                    <div class="service-card">
                        {badge}
                        <h3 style="margin:10px 0 5px 0; color:#1e3a8a;">{s['name']}</h3>
                        <p style="color:#64748b; font-size:13px; margin:0;">{s['desc']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Choose {s['name']}", key=s['id'], use_container_width=True):
                    st.session_state.selected_srv = s
                    st.toast(f"Selected: {s['name']}")

        # Show Checkout Configuration Box if a product is selected
        if st.session_state.selected_srv is not None:
            srv = st.session_state.selected_srv
            st.markdown("---")
            st.subheader("📋 Order Execution Summary")
            
            # Additional input if Kirana desk item
            kirana_details = ""
            est_item_price = 0.0
            if srv["type"] == "Kirana":
                kirana_details = st.text_input("Enter item details explicitly (e.g., 5kg Aashirvaad Aata)*")
                est_item_price = st.number_input("Estimated cost of item from shop (Rs)*", min_value=10.0, value=250.0, step=10.0)
            
            # Commission and split calculations engine logic
            item_cost = est_item_price if srv["type"] == "Kirana" else srv.get("price", 0.0)
            delivery_boy_fee = 15.0
            shopkeeper_commission = round(item_cost * 0.05, 2) if item_cost > 0 else 0.0
            customer_convenience = round(item_cost * 0.02, 2) if item_cost > 0 else 0.0
            
            final_billing_total = item_cost + delivery_boy_fee + customer_convenience
            
            if item_cost > 0:
                st.markdown(f"""
                    <div class="bill-box">
                        <strong>📊 Split Commission Bill Invoice (Cash on Delivery):</strong><br>
                        • Base Product Cost: ₹{item_cost:,}<br>
                        • Local Delivery Rider Fee: ₹{delivery_boy_fee:,}<br>
                        • Platform Convenience Charge: ₹{customer_convenience:,}<br>
                        <strong>👉 Total Payable to Rider: ₹{final_billing_total:,}</strong><br>
                        <span style='font-size:12px; color:#857f07;'>[Admin Record: Your profit margin shared with partner vendor: ₹{shopkeeper_commission + customer_convenience}]</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info(" JIO Telecom updates: SIM Activation & MNP are free. Standard operator recharge rates apply directly at delivery doorstep verification.")
                final_billing_total = 0.0
                
            if st.button("🚀 SUBMIT REQUEST ON DELIVERY NETWORK", type="primary", use_container_width=True):
                if not c_name or not c_phone or not c_addr:
                    st.error("Please fill all mandatory fields (Name, Phone, Address).")
                elif srv["type"] == "Kirana" and not kirana_details:
                    st.error("Please specify the item details (like 5kg Aata) you need.")
                else:
                    item_desc = kirana_details if srv["type"] == "Kirana" else srv["desc"]
                    log_ref = f"Service: {srv['name']} | Details: {item_desc} | Location Limit: {c_dist}KM | NetProfit: ₹{shopkeeper_commission + customer_convenience}"
                    
                    payload = {
                        "sheet_name": "Payment_Ledger",
                        "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "RetailerName": c_name.upper(),
                        "Amount": final_billing_total,
                        "Mode": f"Hyperlocal ({srv['type']})",
                        "SenderUPI_Mobile": c_phone,
                        "Status": "Rider Assigning",
                        "Reference": log_ref
                    }
                    try:
                        requests.post(WEBHOOK_URL, json=payload, timeout=10)
                        st.balloons()
                        st.success("🎉 Success! Order successfully dispatched onto Sandhya Delivery Network node.")
                        st.session_state.selected_srv = None
                    except Exception as e:
                        st.error(f"Error connecting to cloud Sheet: {e}")
