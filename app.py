# ----------------------------------------
# PAGE 4: COLLECTION & TRANSFER
# ----------------------------------------
elif st.session_state.page == "Collection":
    st.header("💰 मंथली कलेक्शन और ट्रांसफर")
    st.info("जिस मेंबर ने बोली लगाकर या अपनी बारी पर पैसा लिया है, उसकी एंट्री यहाँ करें।")
    
    loan_taker = st.selectbox("इस महीने पैसा किसको मिला?", ["Member 1", "Member 2", "Member 3"])
    total_amount = st.number_input("टोटल अमाउंट (₹)", value=20000)
    
    # नया फीचर: पैसा लेने का तरीका (बोली या नॉर्मल)
    transfer_type = st.radio("पैसा लेने का तरीका चुनें:", ["नॉर्मल (प्रतिशत ब्याज)", "बोली / फिक्स डिस्काउंट (रुपए में)"])
    
    if transfer_type == "नॉर्मल (प्रतिशत ब्याज)":
        interest_rate = st.number_input("ब्याज (%)", value=2.0)
        deducted_amount = (total_amount * interest_rate) / 100
    else:
        # अगर मेंबर बोली लगाता है कि "मैं 500 कम लूँगा"
        deducted_amount = st.number_input("बोली का अमाउंट (कितना कम लेंगे - ₹)", value=500.0, step=100.0)
    
    # कैलकुलेशन
    final_amount_to_give = total_amount - deducted_amount
    total_members = 10 # 10 लोगों का ग्रुप है
    per_member_profit = deducted_amount / total_members
    
    st.markdown("---")
    st.write(f"**कुल काटा गया अमाउंट (ब्याज/बोली):** ₹ {deducted_amount}")
    st.write(f"**{loan_taker} के अकाउंट में ट्रांसफर होगा:** ₹ {final_amount_to_give}")
    st.write(f"**हर मेंबर (10 लोगों) को प्रॉफिट बँटेगा:** ₹ {per_member_profit}")
    
    if st.button("कंप्लीट ट्रांसफर दर्ज करें", use_container_width=True):
        st.success(f"✅ {loan_taker} को ₹ {final_amount_to_give} ट्रांसफर की एंट्री हो गई है! सभी 10 मेंबर्स के लेज़र में ₹ {per_member_profit} प्रॉफिट क्रेडिट कर दिया गया।")
