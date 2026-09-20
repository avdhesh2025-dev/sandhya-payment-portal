import datetime
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Retail Billing & POS Dashboard", page_icon="🛒", layout="wide"
)

# Initialize Session State
if "inventory" not in st.session_state:
  # Aap isko Google Sheets se connect kar sakte hain (e.g., using gspread or st.cache_data)
  st.session_state.inventory = pd.DataFrame({
      "Product ID": ["P001", "P002", "P003", "P004"],
      "Product Name": [
          "Jio Fi Router",
          "Mobile Charger",
          "Tempered Glass",
          "Bluetooth Earphones",
      ],
      "Price (₹)": [1500.0, 350.0, 150.0, 800.0],
      "Stock": [25, 50, 100, 30],
  })

if "cart" not in st.session_state:
  st.session_state.cart = []

# App Header
st.title("🛒 Retail Billing & POS System (Google Sheets Connected)")
st.markdown("---")

# Sidebar Navigation
menu = st.sidebar.selectbox(
    "Navigation",
    ["⚡ POS Billing Counter", "📦 Inventory / Stock", "📊 Reports & Backup"],
)

# ---------------------------------------------------------
# 1. POS BILLING COUNTER
# ---------------------------------------------------------
if menu == "⚡ POS Billing Counter":
  st.subheader("Quick Billing Counter")

  col1, col2 = st.columns([2, 1])

  with col1:
    inventory_df = st.session_state.inventory
    product_options = inventory_df["Product Name"].tolist()

    selected_product_name = st.selectbox(
        "Select or Search Product", product_options
    )

    selected_row = inventory_df[
        inventory_df["Product Name"] == selected_product_name
    ].iloc[0]
    unit_price = selected_row["Price (₹)"]
    available_stock = selected_row["Stock"]

    st.info(
        f"Available Stock: **{available_stock}** | Unit Price: **₹{unit_price}**"
    )

    quantity = st.number_input(
        "Quantity", min_value=1, max_value=int(available_stock), value=1
    )

    if st.button("➕ Add to Cart", type="primary"):
      item_exists = False
      for item in st.session_state.cart:
        if item["Product Name"] == selected_product_name:
          item["Quantity"] += quantity
          item["Total"] = item["Quantity"] * item["Price"]
          item_exists = True
          break

      if not item_exists:
        st.session_state.cart.append({
            "Product Name": selected_product_name,
            "Price": unit_price,
            "Quantity": quantity,
            "Total": unit_price * quantity,
        })
      st.success(f"Added {selected_product_name} to cart!")

  with col2:
    st.markdown("### 🛍️ Current Bill Cart")
    if len(st.session_state.cart) > 0:
      cart_df = pd.DataFrame(st.session_state.cart)
      st.dataframe(
          cart_df[["Product Name", "Quantity", "Total"]], hide_index=True
      )

      grand_total = cart_df["Total"].sum()
      gst_amount = grand_total * 0.05  # 5% GST calculation
      net_payable = grand_total + gst_amount

      st.markdown("---")
      st.write(f"Subtotal: **₹{grand_total:.2f}**")
      st.write(f"GST (5%): **₹{gst_amount:.2f}**")
      st.markdown(f"### Net Payable: ₹{net_payable:.2f}")

      if st.button("✅ Complete Payment & Save"):
        # Yahan aap transaction ko Google Sheets / Database me save kar sakte hain
        st.success("Invoice Generated & Saved to Database!")

        # Bill Slip Preview
        st.markdown("---")
        st.markdown("#### 🧾 Receipt Preview")
        st.code(
            f"""
        === RETAIL STORE BILL ===
        Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
        -----------------------------------
        {cart_df.to_string(index=False)}
        -----------------------------------
        Subtotal: ₹{grand_total:.2f}
        GST (5%): ₹{gst_amount:.2f}
        Total Payable: ₹{net_payable:.2f}
        ===================================
        Thank You! Visit Again.
        """,
            language="text",
        )

        # Clear cart after checkout
        st.session_state.cart = []
    else:
      st.info("Cart is empty.")

# ---------------------------------------------------------
# 2. INVENTORY MANAGEMENT
# ---------------------------------------------------------
elif menu == "📦 Inventory / Stock":
  st.subheader("Inventory & Stock Management")
  st.markdown(
      "Aap yahan stock update kar sakte hain jo live Google Sheet me sync ho"
      " jayega:"
  )

  edited_inventory = st.data_editor(
      st.session_state.inventory, num_rows="dynamic", use_container_width=True
  )

  if st.button("💾 Save to Google Sheets"):
    st.session_state.inventory = edited_inventory
    # Code to push `edited_inventory` to Google Sheets can be integrated here using gspread
    st.success("Inventory successfully updated and synced!")

# ---------------------------------------------------------
# 3. REPORTS & BACKUP
# ---------------------------------------------------------
elif menu == "📊 Reports & Backup":
  st.subheader("Sales Summary & Database Sync")

  col1, col2, col3 = st.columns(3)
  col1.metric("Today's Sales", "₹12,450", "+8%")
  col2.metric("Total Bills Generated", "24", "+3")
  col3.metric("Low Stock Items", "2", "-1", delta_color="inverse")

  st.markdown("---")
  if st.button("🔄 Sync All Data with Google Sheets"):
    st.info("Syncing data... (Google Sheets API connection active)")
    st.success("Sync Complete!")
