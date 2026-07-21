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
    st.header("📊 Business Income Dashboard")
    st.markdown("Enter your monthly figures below to calculate total gross income.")
    
    st.subheader("Monthly Inputs")
    col1, col2 = st.columns(2)
    
    with col1:
        recharge_sent = st.number_input("Total Recharge Sent (₹)", value=1000000.0, step=50000.0)
        sim_sold = st.number_input("Total SIM Sold (MNP + New)", value=200, step=10)
        
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
    st.success(f"**TOTAL GROSS INCOME:** ₹{gross_income:,.2f}")

# ----------------------------------------
# SECTION 2: ACTIVITY BOYS (Excel Style Table)
# ----------------------------------------
elif menu == "Activity Boys":
    st.header("🏃‍♂️ Activity Boys Daily Tracker")
    st.markdown("Enter the daily work for your 10 activity boys. Payouts and deposits will calculate automatically.")
    
    # Initialize 10 rows for Activity Boys
    if 'boys_df' not in st.session_state:
        st.session_state.boys_df = pd.DataFrame({
            "Boy Name": [f"Boy {i+1}" for i in range(10)],
            "MNP Count": [0] * 10,
            "FRC-349": [0] * 10,
            "FRC-123": [0] * 10
        })

    # Editable Table
    edited_df = st.data_editor(st.session_state.boys_df, num_rows="dynamic", use_container_width=True)
    st.session_state.boys_df = edited_df

    # Automatic Calculations
    result_df = edited_df.copy()
    result_df["MNP Payout (₹50)"] = result_df["MNP Count"] * 50
    result_df["Deposit 349 (₹220)"] = result_df["FRC-349"] * 220
    result_df["Deposit 123 (₹110)"] = result_df["FRC-123"] * 110
    result_df["Net Cash to Collect"] = (result_df["Deposit 349 (₹220)"] + result_df["Deposit 123 (₹110)"]) - result_df["MNP Payout (₹50)"]

    st.subheader("Automated Calculation Result")
    st.dataframe(result_df, use_container_width=True)

# ----------------------------------------
# SECTION 3: AIRFIBER TEAM (Sunil & Manoj)
# ----------------------------------------
elif menu == "Airfiber Team":
    st.header("📡 Airfiber Team Payout (Sunil & Manoj)")
    
    if 'af_df' not in st.session_state:
        st.session_state.af_df = pd.DataFrame({
            "Name": ["Sunil Kumar", "Manoj Kumar"],
            "Installs": [0, 0],
            "SR (Complaints)": [0, 0],
            "ODU Recovered": [0, 0],
            "IDU Recovered": [0, 0]
        })

    # Editable Table
    edited_af = st.data_editor(st.session_state.af_df, use_container_width=True)
    st.session_state.af_df = edited_af

    # Custom Payout Functions based on Targets
    def calc_odu(odu):
        if odu >= 25: return odu * 200
        if odu >= 10: return odu * 150
        if odu >= 1: return odu * 100
        return 0

    def calc_idu(idu):
        if idu >= 25: return idu * 150
        if idu >= 10: return idu * 100
        if idu >= 1: return idu * 50
        return 0

    # Automatic Calculations
    res_af = edited_af.copy()
    res_af["Install Pay"] = res_af["Installs"] * 250
    res_af["SR Pay"] = res_af["SR (Complaints)"] * 50
    res_af["ODU Pay"] = res_af["ODU Recovered"].apply(calc_odu)
    res_af["IDU Pay"] = res_af["IDU Recovered"].apply(calc_idu)
    res_af["Total Weekly Payout"] = res_af["Install Pay"] + res_af["SR Pay"] + res_af["ODU Pay"] + res_af["IDU Pay"]

    st.subheader("Weekly Payout Calculations")
    st.dataframe(res_af, use_container_width=True)

# ----------------------------------------
# SECTION 4: RETAILER MNP DRIVE
# ----------------------------------------
elif menu == "Retailer MNP Drive":
    st.header("🏬 Retailer MNP Drive Scheme")
    st.markdown("Add your retailers and their MNP count. The scheme will apply automatically.")
    
    if 'ret_df' not in st.session_state:
        st.session_state.ret_df = pd.DataFrame({
            "Retailer Name": ["Retailer 1", "Retailer 2"],
            "MNP Done": [0, 0]
        })

    # Editable Table
    edited_ret = st.data_editor(st.session_state.ret_df, num_rows="dynamic", use_container_width=True)
    st.session_state.ret_df = edited_ret

    def get_scheme(mnp):
        if mnp >= 10: return 700
        if mnp >= 5: return 350
        if mnp >= 3: return 165
        if mnp >= 2: return 100
        if mnp >= 1: return 30
        return 0

    res_ret = edited_ret.copy()
    res_ret["Scheme Payout"] = res_ret["MNP Done"].apply(get_scheme)

    st.subheader("Retailer Scheme Calculation")
    st.dataframe(res_ret, use_container_width=True)
