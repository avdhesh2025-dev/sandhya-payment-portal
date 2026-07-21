import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Telecom Business Dashboard", layout="wide", page_icon="📊")

# Sidebar Navigation
st.sidebar.title("Navigation Menu")
menu = st.sidebar.radio("Select Section:", 
                        ["Main Dashboard", "Activity Boys", "Airfiber Team", "Retailer MNP Drive"])

st.sidebar.markdown("---")
st.sidebar.info("Application Interface operates in English.")

# ----------------------------------------
# SECTION 1: MAIN DASHBOARD
# ----------------------------------------
if menu == "Main Dashboard":
    st.header("📊 Business Income & Profit Dashboard")
    st.markdown("Enter your monthly figures below to calculate total gross income and net profit.")
    
    st.subheader("Monthly Inputs")
    col1, col2 = st.columns(2)
    
    with col1:
        recharge_sent = st.number_input("Total Recharge Sent (₹)", value=1000000.0, step=50000.0)
        sim_sold = st.number_input("Total SIM Sold (MNP + New)", value=200, step=10)
        fse_salary = st.number_input("Fixed FSE Salary (₹)", value=15700.0, step=100.0)
        
    with col2:
        last_mnp = st.number_input("Last Month MNP Total", value=100, step=5)
        this_mnp = st.number_input("This Month MNP Total", value=115, step=5)
        
    st.markdown("---")
    
    # Mathematical Calculations
    recharge_margin = recharge_sent * 0.015
    caf_income = sim_sold * 17
    
    # MNP Growth Logic
    growth_pct = ((this_mnp - last_mnp) / last_mnp) * 100 if last_mnp > 0 else 0
    growth_payout_per_mnp = 0
    
    if growth_pct >= 15:
        growth_payout_per_mnp = 24
    elif growth_pct >= 10:
        growth_payout_per_mnp = 18
    elif growth_pct >= 5:
        growth_payout_per_mnp = 14
        
    total_growth_income = this_mnp * growth_payout_per_mnp
    gross_income = recharge_margin + caf_income + total_growth_income
    
    # Display Income Metrics
    st.subheader("Revenue Breakdown")
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Recharge Margin (1.5%)", value=f"₹{recharge_margin:,.2f}")
    m2.metric(label="CAF Income (₹17/SIM)", value=f"₹{caf_income:,.2f}")
    m3.metric(label=f"MNP Growth ({growth_pct:.1f}%)", value=f"₹{total_growth_income:,.2f}")
    
    st.markdown("---")
    
    # Final Profit Display
    st.subheader("Net Monthly Analysis")
    col_g, col_n = st.columns(2)
    col_g.info(f"**TOTAL GROSS INCOME:** ₹{gross_income:,.2f}")
    
    # For a full profit calculation, you can later subtract other team payouts. 
    # Currently subtracting fixed FSE salary.
    net_profit = gross_income - fse_salary
    col_n.success(f"**NET PROFIT (After FSE Salary):** ₹{net_profit:,.2f}")


# ----------------------------------------
# SECTION 2: ACTIVITY BOYS
# ----------------------------------------
elif menu == "Activity Boys":
    st.header("🏃‍♂️ Activity Boys Daily Calculator")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        mnp = st.number_input("MNP Count", min_value=0, value=0, step=1)
    with col2:
        frc349 = st.number_input("FRC-349 Count (New SIM)", min_value=0, value=0, step=1)
    with col3:
        frc123 = st.number_input("FRC-123 Count (New SIM)", min_value=0, value=0, step=1)
        
    # Calculations
    mnp_payout = mnp * 50
    dep_349 = frc349 * 220
    dep_123 = frc123 * 110
    total_deposit = dep_349 + dep_123
    net_collect = total_deposit - mnp_payout
    
    st.markdown("### Calculation Result")
    st.write(f"- **Boy's MNP Payout:** ₹{mnp_payout}")
    st.write(f"- **SIM Deposit Value (349 & 123):** ₹{total_deposit}")
    
    if net_collect > 0:
        st.error(f"**Net Cash to Collect from Boy:** ₹{net_collect}")
    elif net_collect < 0:
        st.success(f"**Net Cash to Pay to Boy:** ₹{abs(net_collect)}")
    else:
        st.info("**Accounts Settled (₹0 Balance)**")


# ----------------------------------------
# SECTION 3: AIRFIBER TEAM
# ----------------------------------------
elif menu == "Airfiber Team":
    st.header("📡 Airfiber Team Weekly Payout")
    
    col1, col2 = st.columns(2)
    with col1:
        installs = st.number_input("Total Installations", min_value=0, value=0)
        sr = st.number_input("Total SR (Complaints) Resolved", min_value=0, value=0)
    with col2:
        odu = st.number_input("ODU Recovered", min_value=0, value=0)
        idu = st.number_input("IDU Recovered", min_value=0, value=0)
        
    # Calculations
    install_pay = installs * 250
    sr_pay = sr * 50
    
    # ODU Slabs
    odu_rate = 200 if odu >= 25 else (150 if odu >= 10 else (100 if odu >= 1 else 0))
    odu_pay = odu * odu_rate
    
    # IDU Slabs
    idu_rate = 150 if idu >= 25 else (100 if idu >= 10 else (50 if idu >= 1 else 0))
    idu_pay = idu * idu_rate
    
    total = install_pay + sr_pay + odu_pay + idu_pay
    
    st.markdown("### Payout Breakdown")
    st.write(f"- Install Payout: ₹{install_pay}")
    st.write(f"- SR Payout: ₹{sr_pay}")
    st.write(f"- ODU Payout (Rate: ₹{odu_rate}/unit): ₹{odu_pay}")
    st.write(f"- IDU Payout (Rate: ₹{idu_rate}/unit): ₹{idu_pay}")
    
    st.success(f"**Total Weekly Payout:** ₹{total}")


# ----------------------------------------
# SECTION 4: RETAILER MNP DRIVE
# ----------------------------------------
elif menu == "Retailer MNP Drive":
    st.header("🏬 Retailer MNP Drive Scheme")
    
    mnp_done = st.number_input("Enter Total MNP Done by Retailer", min_value=0, value=0, step=1)
    
    payout = 0
    if mnp_done >= 10:
        payout = 700
    elif mnp_done >= 5:
        payout = 350
    elif mnp_done >= 3:
        payout = 165
    elif mnp_done >= 2:
        payout = 100
    elif mnp_done >= 1:
        payout = 30
        
    st.markdown("### Scheme Reward")
    st.success(f"**Eligible Scheme Payout:** ₹{payout}")
    
    st.markdown("---")
    st.markdown("""
    **Current Active Slabs:**
    * 1 MNP = ₹30
    * 2 MNP = ₹100
    * 3 MNP = ₹165
    * 5 MNP = ₹350
    * 10 MNP = ₹700
    """)
