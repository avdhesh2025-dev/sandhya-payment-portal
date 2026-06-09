import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Premium Professional 3D Layout Injector
st.set_page_config(page_title="Sandhya Local Delivery Engine", page_icon="🛵", layout="wide")

st.markdown("""
    <style>
    .main .block-container { 
        background-color: #ffffff; padding: 2rem 3.5rem; border-radius: 15px; 
        max-width: 850px; box-shadow: 0px 15px 50px rgba(0,0,0,0.15); margin: auto;
    }
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%); padding: 25px; 
        border-radius: 12px; text-align: center; color: white; margin-bottom: 25px;
    }
    .business-card {
        background: #ffffff; padding: 20px; border-radius: 10px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    .3d-box {
        background: #ffffff; padding: 20px; border-radius: 10px;
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.05), 0px 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #cbd5e1; margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 GLOBAL DATABASE CONFIG (GOOGLE SHEET)
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
ADMIN_PASSWORD = "Jio Distributor"

# Core Local Services Directory
LOCAL_SERVICES = [
    {"id": "SRV-01", "name": "MNP (Mobile Number Portability)", "base_price": 0.0, "type": "Telecom", "desc": "Free door-step MNP service to Jio Network."},
    {"id": "SRV-02", "name": "New Jio SIM Card Activation", "base_price": 0.0, "type": "Telecom", "desc": "Get a brand new Jio SIM card delivered and activated at home."},
    {"id": "SRV-03", "name": "Jio Phone Bharat V4", "price": 1099.0, "type": "Telecom", "desc": "Latest Jio Bharat V4 4G phone with instant booking."},
    {"id": "SRV-04", "name": "Local Store Item Order (Kirana/Aata/Other)", "base_price": 0.0, "type": "Kirana", "desc": "Order grocery items like 5Kg Aata from neighboring shops."}
]

# State Variables Initialization Safely
if "cart_service" not in st.session_state: st.session_state.cart_service = None
if "login_role" not in st.session_state: st.session_state.login_role = None
if "customer_profile" not in st.session_state: st.session_state.customer_profile = {"name": "", "phone": "", "address": "", "distance": 1.0}

# --- MAIN DIGITAL MALL HEADER ---
st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; font-size: 32px; font-weight: 800;">🛵 SANDHYA LOCAL DELIVERY NETWORK</h1>
        <p style="margin:5px 0 0 0; font-size: 16px;">Hyperlocal Jio Services & Kirana Delivery Within 5Kms</p>
    </div>
""", unsafe_allow_html=True)

# --- DOUBLE GATE SECURITY AUTHENTICATION (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🔑 Secure Login Interface")
    
    if st.session_state.login_role is None:
        mode_select = st.radio("Access Category:", ["👤 Local Customer Gateway", "🛠️ Owner/Admin Control Panel"])
        
        if mode_select == "👤 Local Customer Gateway":
            c_phone = st.text_input("Enter Mobile Number", max_chars=10, placeholder="9934XXXXXX")
            if st.button("📲 Open Customer App", use_container_width=True, type="primary"):
                if len(c_phone) == 10 and c_phone.isdigit():
                    st.session_state.login_role = "Customer"
                    st.session_state.customer_profile["phone"] = c_phone
                    st.rerun()
                else: st.error("Authentication Failure: Provide a valid 10-digit number.")
                
        elif mode_select == "🛠️ Owner/Admin Control Panel":
            pass_input = st.text_input("Enter System Secret Key*", type="password")
            if st.button("🔓 Open Admin Dashboard", use_container_width=True, type="primary"):
                if pass_input == ADMIN_PASSWORD:
                    st.session_state.login_role = "Admin"
                    st.rerun()
                else: st.error("Access Denied: Security Key mismatch.")
    else:
        if st.session_state.login_role == "Admin":
            st.markdown("<div class='3d-box' style='background-color:#ffe4e6; color:#991b1b; font-weight:bold; text-align:center;'>🛠️ SYSTEM RUNNING IN ADMIN MODE</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='3d-box' style='background-color:#f0fdf4;'>🟢 CUSTOMER PROFILE SYNCED</div>", unsafe_allow_html=True)
            cust_name = st.text_input("Your Full Name", value=st.session_state.customer_profile["name"])
            cust_addr = st.text_area("Delivery Address (Samastipur Area)", value=st.session_state.customer_profile["address"])
            
            # 📍 5KM RADIUS RANGE LOCK
            st.markdown("##### 📍 Distance from Meghpatti Head Office")
            cust_dist = st.slider("Select Distance (KM)", min_value=0.5, max_value=10.0, value=st.session_state.customer_profile["distance"], step=0.5)
            
            if st.button("💾 Lock Delivery Address", use_container_width=True):
                st.session_state.customer_profile["name"] = cust_name
                st.session_state.customer_profile["address"] = cust_addr
                st.session_state.customer_profile["distance"] = cust_dist
                st.toast("Delivery parameters locked to local network map!")
                
        if st.button("🚪 Terminate Session (Logout)", use_container_width=True):
            st.session_state.login_role = None
            st.session_state.cart_service = None
            st.rerun()

# Dynamic Navigation Panel View
if st.session_state.login_role == "Admin":
    st.subheader("🛠️ Central Business Control Panel (Admin View)")
    st.info("स्वागत है अवधेश जी। नीचे आप अपने 5KM के दायरे में आए सभी ग्राहकों के ऑर्डर्स, कमीशन और डिलीवरी लड़कों का हिसाब सीधे अपनी गूगल शीट पर लाइव ट्रैक कर सकते हैं।")
    
    # CRITICAL FIX: Resolved NameError by wrapping variables safely
    sheet_link = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
    st.markdown(f"""
        <div class='3d-box' style='text-align:center; background-color:#eff6ff;'>
            <h4>📊 Your Cloud Google Sheet is Live Connected</h4>
            <p>All real-time customer data, commission figures, and partner merchant requests are stored directly into your Sheet.</p>
            <a href='{sheet_link}' target='_blank'><button style='background-color:#2563eb; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold;'>Open Live Excel Ledger</button></a>
        </div>
    """, unsafe_allow_html=True)

else:
    # CLIENT INTERFACE FRONTEND
    tab_store, tab_checkout = st.tabs(["⚡ Browse Services & Kirana", "📦 Book Local Request"])
    
    with tab_store:
        st.markdown("### Select a Service or Place a Request")
        
        grid = st.columns(2)
        for idx, srv in enumerate(LOCAL_SERVICES):
            with grid[idx % 2]:
                st.markdown(f"""
                    <div class="business-card">
                        <span style="background:#dbeafe; color:#1e40af; padding:3px 8px; border-radius:15px; font-size:12px; font-weight:bold;">{srv['type']}</span>
                        <h3 style="margin:10px 0 5px 0; color:#1e293b;">{srv['name']}</h3>
                        <p style="color:#64748b; font-size:13px; margin-bottom:10px;">{srv['desc']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"⚡ Select {srv['name']}", key=srv['id'], use_container_width=True):
                    if not st.session_state.login_role:
                        st.error("🔒 Security Block: Please login with your Mobile number in the sidebar panel first!")
                    else:
                        st.session_state.cart_service = srv
                        st.success(f"Selected: {srv['name']}. Now go to 'Book Local Request' tab to complete your booking.")
                        time.sleep(0.3)
                        st.rerun()

    with tab_checkout:
        st.subheader("📋 Finalize Your Local Order Placement")
        
        if not st.session_state.login_role:
            st.warning("🔒 Session Gateway Closed: Login via your active cellular number in the sidebar environment.")
        elif st.session_state.cart_service is None:
            st.info("No service selected. Go back to 'Browse Services & Kirana' tab and select a package.")
        else:
            selected_srv = st.session_state.cart_service
            
            # 🛑 EXECUTE 5KM RANGE GUARD PROTECTION RULE
            current_distance = st.session_state.customer_profile["distance"]
            if current_distance > 5.0:
                st.markdown(f"""
                    <div style='background-color:#fef2f2; border:1px solid #fecaca; color:#991b1b; padding:20px; border-radius:8px; font-weight:bold; text-align:center;'>
                        🚨 SERVICE BOUNDARY RESTRICTION<br>
                        Your locked distance is {current_distance} Kms. Sandhya Network exclusively delivers within 5.0 Kms of Meghpatti Head Office to ensure fresh & fast delivery.
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='3d-box' style='background-color:#f8fafc;'>
                        <h4>Selected: <strong>{selected_srv['name']}</strong></h4>
                        <p style='margin:0; color:#475569;'>Category: {selected_srv['type']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.form("hyperlocal_checkout_form"):
                    c_name = st.text_input("Customer Full Name*", value=st.session_state.customer_profile["name"])
                    c_address = st.text_area("Exact Delivery Destination*", value=st.session_state.customer_profile["address"])
                    
                    item_details_text = ""
                    item_est_price = 0.0
                    if selected_srv["type"] == "Kirana":
                        st.markdown("##### 🛒 Specify Item Details:")
                        item_details_text = st.text_input("Type item description (e.g., 5Kg Ashirvaad Aata)*", placeholder="Write exact brand name and quantity")
                        item_est_price = st.number_input("Estimated Price from shop (Rs)*", min_value=10.0, max_value=5000.0, value=250.0, step=10.0)
                    
                    # Business Split Calculations
                    base_cost = item_est_price if selected_srv["type"] == "Kirana" else selected_srv.get("price", 0.0)
                    delivery_charge = 15.0  # Fixed delivery fee for rider
                    
                    # Your Business Matrix Model (5% commission from shopkeeper + 2% from customer convenience)
                    merchant_commission = round(base_cost * 0.05, 2) if base_cost > 0 else 0.0
                    customer_convenience = round(base_cost * 0.02, 2) if base_cost > 0 else 0.0
                    grand_total = base_cost + delivery_charge + customer_convenience
                    
                    if base_cost > 0:
                        st.markdown(f"""
                            <div style='background-color:#fcfba9; padding:15px; border-radius:8px; border:1px solid #e1db43; font-size:14px; color:#4d4a0a;'>
                                <strong>💰 Hyperlocal Bill Overview Summary (Cash on Delivery):</strong><br>
                                • Item Base Cost: ₹{base_cost:,}<br>
                                • Local Delivery Fee: ₹{delivery_charge:,}<br>
                                • Convenience Charge: ₹{customer_convenience:,}<br>
                                <strong>• Pay to Delivery Boy Amount: ₹{grand_total:,}</strong><br>
                                <span style='font-size:12px; color:#857f07;'>[Internal Admin Logs -> Shopkeeper Comm: ₹{merchant_commission} | Net Income: ₹{merchant_commission + customer_convenience}]</span>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Note: MNP and SIM activation base charges are absolutely Free. Standard operator FRC plans apply during doorstep verification.")
                        grand_total = 0.0
                    
                    if st.form_submit_button("🚀 PLACE DOORSTEP REQUEST NOW", use_container_width=True, type="primary"):
                        if not c_name or not c_address:
                            st.error("Validation Error: Customer Name and Destination fields cannot be empty.")
                        elif selected_srv["type"] == "Kirana" and not item_details_text:
                            st.error("Validation Error: Please specify the item details (like 5kg Aata) you need.")
                        else:
                            final_summary = item_details_text if selected_srv["type"] == "Kirana" else selected_srv["desc"]
                            full_reference_log = f"Service: {selected_srv['name']} | Spec: {final_summary} | Destination: {c_address} | Distance: {current_distance}KM | Total Profit Earned: ₹{merchant_commission + customer_convenience}"
                            
                            payload = {
                                "sheet_name": "Payment_Ledger",
                                "Date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                                "RetailerName": c_name.upper(),
                                "Amount": grand_total,
                                "Mode": f"Hyperlocal ({selected_srv['type']})",
                                "SenderUPI_Mobile": st.session_state.customer_profile["phone"],
                                "Status": "Rider Assignment Pending",
                                "Reference": full_reference_log
                            }
                            
                            try:
                                requests.post(WEBHOOK_URL, json=payload, timeout=10)
                                st.balloons()
                                st.success(f"🎉 Success! Order successfully dispatched onto Sandhya Network node. Delivery boy will arrive at your address within 30 minutes.")
                                st.session_state.cart_service = None
                            except Exception as cloud_err: st.error(f"Cloud ledger sync connection error: {cloud_err}")
