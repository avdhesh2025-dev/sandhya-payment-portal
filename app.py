import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# 1. Page Configuration & Premium English UI
st.set_page_config(page_title="Online Product Store", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    .main .block-container { 
        background-color: #ffffff; padding: 2rem 3rem; border-radius: 15px; 
        max-width: 1100px; box-shadow: 0px 10px 40px rgba(0,0,0,0.1); margin: auto;
    }
    .product-card {
        background: #ffffff; padding: 20px; border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
        text-align: center; margin-bottom: 20px; transition: 0.3s;
    }
    .product-card:hover { box-shadow: 0px 10px 25px rgba(0,0,0,0.15); }
    .price-tag { color: #16a34a; font-size: 22px; font-weight: bold; margin: 10px 0; }
    .cart-summary { background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #cbd5e1; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 GOOGLE SHEET CONFIG (FOR ORDERS)
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwq8_2sAhirNEqEBNYvIQ7qsUhaXELXblnXNbnIL1mpp71nxCB25NBC5WabA92da1jA9g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"

# 🟢 DUMMY PRODUCT DATABASE (You can later connect this to your Google Sheet)
PRODUCTS = [
    {"id": "P001", "name": "Premium Wireless Earbuds", "price": 1499.0, "category": "Electronics", "stock": "In Stock"},
    {"id": "P002", "name": "Smart Fitness Band Pro", "price": 2499.0, "category": "Electronics", "stock": "In Stock"},
    {"id": "P003", "name": "Fast Charging Power Bank 20k mAh", "price": 1199.0, "category": "Accessories", "stock": "In Stock"},
    {"id": "P004", "name": "Ergonomic Wireless Mouse", "price": 699.0, "category": "Accessories", "stock": "Limited Stock"},
]

if "cart" not in st.session_state:
    st.session_state.cart = {}

# Header UI
st.markdown("<div style='background: linear-gradient(90deg, #0f172a 0%, #2563eb 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; margin-bottom: 30px;'><h1 style='margin:0; font-size: 36px;'>🛍️ DIGITAL PRODUCT STORE</h1><p style='margin:5px 0 0 0; font-size: 18px;'>Explore Products & Order Online Instantly</p></div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🛒 Browse Products", "📦 View Cart & Checkout"])

with tab1:
    st.subheader("Our Product Catalog")
    
    # Grid layout for products
    cols = st.columns(2)
    for idx, p in enumerate(PRODUCTS):
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="product-card">
                    <span style="background: #e2e8f0; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #475569;">{p['category']}</span>
                    <h3 style="margin: 15px 0 5px 0; color: #1e293b;">{p['name']}</h3>
                    <p style="color: #64748b; font-size: 13px; margin: 0;">Product ID: {p['id']} | <span style="color: #2563eb;">{p['stock']}</span></p>
                    <div class="price-tag">₹{p['price']:,}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Add to Cart Button inside Streamlit
            if st.button(f"➕ Add to Cart ({p['name']})", key=p['id']):
                if p['id'] in st.session_state.cart:
                    st.session_state.cart[p['id']]['qty'] += 1
                else:
                    st.session_state.cart[p['id']] = {"name": p['name'], "price": p['price'], "qty": 1}
                st.toast(f"Added {p['name']} to cart!")
                time.sleep(0.5)
                st.rerun()

with tab2:
    st.subheader("Your Shopping Cart")
    
    if not st.session_state.cart:
        st.info("Your cart is empty. Go to 'Browse Products' tab to add items!")
    else:
        cart_data = []
        total_amount = 0.0
        
        for pid, item in list(st.session_state.cart.items()):
            subtotal = item['price'] * item['qty']
            total_amount += subtotal
            cart_data.append({
                "Product ID": pid,
                "Product Name": item['name'],
                "Price": f"₹{item['price']:,}",
                "Quantity": item['qty'],
                "Subtotal": f"₹{subtotal:,}"
            })
            
        # Display Cart Table
        st.dataframe(pd.DataFrame(cart_data), use_container_width=True)
        
        st.markdown(f"""
            <div class="cart-summary" style="text-align: right; margin-bottom: 25px;">
                <span style="font-size: 18px; color: #64748b; font-weight: bold;">Grand Total:</span>
                <span style="font-size: 28px; color: #1e293b; font-weight: bold; margin-left: 10px;">₹{total_amount:,}</span>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Cart", type="secondary"):
            st.session_state.cart = {}
            st.rerun()
            
        # Checkout Form
        st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
        st.subheader("📋 Customer Delivery Details")
        
        with st.form("checkout_form"):
            cust_name = st.text_input("Full Name*")
            cust_phone = st.text_input("Mobile Number*")
            cust_address = st.text_area("Delivery Address*")
            
            if st.form_submit_button("🚀 PLACE ORDER & GENERATE INVOICE", use_container_width=True, type="primary"):
                if not cust_name or not cust_phone or not cust_address:
                    st.error("Please fill all the mandatory delivery fields.")
                else:
                    # Prepare Order Description for Google Sheet
                    order_items = [f"{item['name']} (x{item['qty']})" for item in st.session_state.cart.values()]
                    items_summary = ", ".join(order_items)
                    order_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
                    
                    # Payload to match your Google Sheet structure
                    payload = {
                        "sheet_name": "Payment_Ledger",  # Using existing sheet tab for test or you can create a new tab 'Orders'
                        "Date": order_date,
                        "RetailerName": cust_name.upper(),
                        "Amount": total_amount,
                        "Mode": "Online Store Order",
                        "SenderUPI_Mobile": cust_phone,
                        "Status": "Order Placed",
                        "Reference": f"Address: {cust_address} | Items: {items_summary}"
                    }
                    
                    try:
                        requests.post(WEBHOOK_URL, json=payload, timeout=10)
                        st.balloons()
                        st.success(f"🎉 Thank you {cust_name}! Your order worth ₹{total_amount:,} has been booked successfully!")
                        # Clear Cart after successful order
                        st.session_state.cart = {}
                    except Exception as e:
                        st.error(f"Error booking order to Google Sheet: {e}")
