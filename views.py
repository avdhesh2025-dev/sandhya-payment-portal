import streamlit as st
import pandas as pd
import datetime
from utils import generate_member_id, send_data_to_sheet, generate_qr, get_whatsapp_link, export_to_excel

def render_dashboard():
    st.header("📊 प्रोफेशनल डैशबोर्ड & एनालिटिक्स")
    
    total_members = len(st.session_state.members_db)
    active_members = sum(1 for m in st.session_state.members_db if m.get('status') == '✅ Active')
    
    txns = st.session_state.ledger_transactions
    total_collection = sum(t['credit'] for t in txns if t.get('credit', 0) > 0)
    total_loan_out = sum(t['loan'] for t in txns if t.get('loan', 0) > 0)
    total_repaid = sum(t['loan_repaid'] for t in txns if t.get('loan_repaid', 0) > 0)
    
    running_balance = total_collection - (total_loan_out - total_repaid)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("कुल सदस्य", f"{total_members} ({active_members} Active)")
    m2.metric("कुल कलेक्शन (जमा)", f"₹ {total_collection:,.2f}")
    m3.metric("मार्केट में रनिंग लोन", f"₹ {(total_loan_out - total_repaid):,.2f}")
    m4.metric("करंट सिस्टम बैलेंस", f"₹ {running_balance:,.2f}")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔴 एक्टिव लोन & बकाया (Outstanding)")
        loan_data = []
        for m in st.session_state.members_db:
            m_txns = [t for t in st.session_state.ledger_transactions if t['name'] == m['name']]
            t_loan = sum([t.get('loan',0) for t in m_txns])
            t_repaid = sum([t.get('loan_repaid',0) for t in m_txns])
            out = t_loan - t_repaid
            if out > 0:
                loan_data.append({"मेंबर": m['name'], "कुल लोन लिया": t_loan, "बकाया (Outstanding)": out})
        
        if loan_data:
            st.dataframe(pd.DataFrame(loan_data), use_container_width=True)
        else:
            st.success("🎉 किसी भी मेंबर पर कोई लोन या बकाया नहीं है!")
            
    with c2:
        st.subheader("🟢 पेंडिंग पेमेंट ट्रैकर")
        if len(st.session_state.payment_status) > 0:
            status_data = [{"मेंबर": k, "स्टेटस": v} for k, v in st.session_state.payment_status.items()]
            st.dataframe(pd.DataFrame(status_data), use_container_width=True)

def render_add_member():
    st.header("👤 मेंबर रजिस्ट्रेशन (Auto ID & Validation)")
    with st.form("new_member_form", clear_on_submit=True):
        st.subheader("Personal & Contact Details")
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("पूरा नाम *")
            dob = st.date_input("जन्म तिथि (DOB)", min_value=datetime.date(1950, 1, 1))
        with c2:
            mobile = st.text_input("मोबाइल / WhatsApp नंबर *")
            email = st.text_input("ईमेल (Email)")
        with c3:
            occupation = st.text_input("व्यवसाय (Occupation)")
            reference = st.selectbox("रेफरेंस / गारंटर *", ["-- चुनें --", "Admin", "Self"])

        st.subheader("Identity & Banking")
        c4, c5 = st.columns(2)
        with c4:
            identity_num = st.text_input("Aadhaar Number * (12 Digits)")
            pan = st.text_input("PAN Card Number *")
            address = st.text_area("पूरा पता *")
        with c5:
            bank_ac = st.text_input("Bank Account Number")
            ifsc = st.text_input("Bank IFSC Code")
            upi_id = st.text_input("UPI ID *")

        submit = st.form_submit_button("डेटा सेव करें", use_container_width=True)
        
        if submit:
            if not name or not mobile or not identity_num or not pan or not address or not upi_id:
                st.error("⚠️ कृपया सभी अनिवार्य (*) फील्ड भरें!")
            else:
                member_id = generate_member_id(len(st.session_state.members_db))
                payload = {
                    "action": "insert", "member_id": member_id, "name": name, "mobile": mobile,
                    "identity": "[ID Redacted]", "pan": pan, "upi": upi_id, "address": address, "reference": reference
                }
                send_data_to_sheet(payload)
                
                new_member = {
                    "id": member_id, "name": name, "mobile": mobile, "dob": str(dob), 
                    "email": email, "occupation": occupation, "identity_num": "[ID Redacted]", 
                    "pan": pan, "address": address, "bank_ac": bank_ac, "ifsc": ifsc, "upi": upi_id, 
                    "reference": reference, "status": "✅ Active"
                }
                
                st.session_state.members_db.append(new_member)
                st.session_state.payment_status[name] = "❌ Pending"
                
                st.session_state.ledger_transactions.append({
                    "txn_id": f"TXN{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "name": name, "date": str(datetime.date.today()),
                    "विवरण": "खाता खुला / रजिस्ट्रेशन जमा",
                    "credit": 2000, "debit": 0, "loan": 0, "loan_repaid": 0, "commission": 0, "fine": 0, "balance": 2000
                })
                st.success(f"✅ {name} सफलतापूर्वक रजिस्टर्ड! Member ID: {member_id}")

def render_ledger():
    st.header("📒 स्मार्ट लेज़र, प्रोफाइल & कार्ड")
    
    if len(st.session_state.members_db) > 0:
        member_names = [m['name'] for m in st.session_state.members_db]
        selected_name = st.selectbox("प्रोफाइल देखने के लिए मेंबर चुनें:", member_names)
        m_details = next((m for m in st.session_state.members_db if m['name'] == selected_name), None)
        
        if m_details:
            st.markdown("---")
            # --- Membership Card Visual ---
            st.subheader("💳 डिजिटल मेंबरशिप कार्ड")
            card_html = f"""
            <div style="width: 350px; background: linear-gradient(135deg, #1f2937, #3b82f6); color: white; border-radius: 15px; padding: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); font-family: sans-serif; margin-bottom: 20px;">
                <h3 style="margin: 0; text-align: center; color: #fbbf24;">Sandhya Enterprises</h3>
                <p style="text-align: center; font-size: 12px; margin-top: 5px; color: #e5e7eb;">Digital Committee Membership</p>
                <hr style="border-color: #4b5563;">
                <div style="margin-top: 15px;">
                    <p style="margin: 5px 0;"><b>Name:</b> {m_details['name']}</p>
                    <p style="margin: 5px 0;"><b>Member ID:</b> {m_details['id']}</p>
                    <p style="margin: 5px 0;"><b>Mobile:</b> {m_details['mobile']}</p>
                    <p style="margin: 5px 0;"><b>UPI:</b> {m_details['upi']}</p>
                    <p style="margin: 5px 0; font-size: 11px; color: #d1d5db;">Address: {m_details['address']}</p>
                </div>
                <div style="margin-top: 15px; text-align: right;">
                    <p style="margin: 0; font-size: 12px; font-weight: bold; color: #10b981;">{m_details['status']}</p>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            st.info("👆 आप इस कार्ड का स्क्रीनशॉट लेकर मेंबर को भेज सकते हैं।")
            
            # Action Buttons
            wh_link = get_whatsapp_link(m_details['mobile'], f"Hello {m_details['name']}, your Sandhya Enterprises membership is active.")
            st.markdown(f'<a href="{wh_link}" target="_blank"><button style="padding:10px; background-color:#25D366; color:white; border:none; border-radius:5px;">💬 WhatsApp Message</button></a>', unsafe_allow_html=True)
            
            member_txns = [t for t in st.session_state.ledger_transactions if t['name'] == selected_name]
            st.subheader("💳 विस्तृत ट्रांज़ैक्शन हिस्ट्री")
            if len(member_txns) > 0:
                df_txn = pd.DataFrame(member_txns)
                st.dataframe(df_txn, use_container_width=True)
            else:
                st.info("कोई ट्रांज़ैक्शन नहीं है।")
    else:
        st.warning("⚠️ लेज़र देखने के लिए पहले मेंबर रजिस्टर करें।")

def render_collection():
    st.header("💰 मंथली कमिटी बिडिंग & लोन ट्रांसफर")
    st.info("यहाँ से आप मंथली कलेक्शन का पैसा (पॉट) किसी एक मेंबर को दे सकते हैं।")
    
    if len(st.session_state.members_db) == 0:
        st.warning("⚠️ पहले मेंबर रजिस्टर करें!")
        return
        
    member_names = [m['name'] for m in st.session_state.members_db]
    loan_taker = st.selectbox("इस महीने कमिटी का पैसा किसको मिलेगा?", member_names)
    m_details = next(m for m in st.session_state.members_db if m['name'] == loan_taker)
    
    total_pot = st.number_input("टोटल कलेक्शन / पॉट अमाउंट (₹)", value=20000)
    bid_amount = st.number_input("बिडिंग डिस्काउंट / कमीशन (₹) (उदा: 500)", value=500.0)
    
    # Calculate outstanding loan
    member_txns = [t for t in st.session_state.ledger_transactions if t['name'] == loan_taker]
    total_loan_taken = sum([t.get('loan', 0) for t in member_txns])
    total_loan_repaid = sum([t.get('loan_repaid', 0) for t in member_txns])
    outstanding = total_loan_taken - total_loan_repaid
    
    has_active_loan = outstanding > 0
    force_close = False
    fine_amount = 0
    previous_deduction = 0
    
    if has_active_loan:
        st.error(f"⚠️ {loan_taker} पर पहले से ₹{outstanding} का लोन/कमिटी बकाया है!")
        st.warning("जब तक पिछला बकाया क्लियर नहीं होता, नया पेमेंट QR जनरेट नहीं होगा।")
        force_close = st.checkbox("⚡ फोर्स क्लोज करें (₹999 फाइन + पुराना बकाया काट कर नया पेमेंट दें)")
        if force_close:
            fine_amount = 999
            previous_deduction = outstanding
        else:
            st.stop() # Stops execution here so QR isn't generated
            
    # Calculations
    total_deduction = bid_amount + previous_deduction + fine_amount
    final_payout = total_pot - total_deduction
    total_profit_pool = bid_amount + fine_amount
    per_member_profit = total_profit_pool / len(member_names)
    
    st.markdown("---")
    st.subheader("📊 कैलकुलेशन समरी")
    c1, c2, c3 = st.columns(3)
    c1.metric("कुल कटौती", f"₹{total_deduction}")
    c2.metric("फाइनल पेमेंट (QR)", f"₹{final_payout}")
    c3.metric("हर मेंबर का प्रॉफिट", f"₹{per_member_profit:.2f}")
    
    if final_payout < 0:
        st.error("❌ कटौती का अमाउंट टोटल पॉट से ज्यादा हो गया है!")
        return
        
    st.markdown("### 📲 सुरक्षित पेमेंट QR कोड")
    qr_buf = generate_qr(m_details['upi'], m_details['name'], final_payout, "Committee Payout")
    st.image(qr_buf, width=250, caption=f"Scan to pay ₹{final_payout} to {loan_taker}")
    
    if st.button("✅ ट्रांज़ैक्शन कन्फर्म करें और लेज़र में सेव करें", use_container_width=True):
        txn_id = f"TXN{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Record payout to receiver
        st.session_state.ledger_transactions.append({
            "txn_id": txn_id, "name": loan_taker, "date": str(datetime.date.today()),
            "विवरण": "कमिटी पॉट प्राप्त (Force Closed)" if force_close else "कमिटी पॉट प्राप्त",
            "credit": 0, "debit": final_payout, "loan": total_pot,
            "loan_repaid": previous_deduction, 
            "commission": 0, "fine": fine_amount, "balance": -total_pot
        })
        
        # Record profit for ALL members
        for m in member_names:
            st.session_state.ledger_transactions.append({
                "txn_id": txn_id+"_P", "name": m, "date": str(datetime.date.today()),
                "विवरण": f"कमिटी प्रॉफिट (Bid+Fine)",
                "credit": per_member_profit, "debit": 0, "loan": 0, "loan_repaid": 0,
                "commission": per_member_profit, "fine": 0, "balance": per_member_profit
            })
            
        st.success(f"✅ {loan_taker} को ₹{final_payout} का पेमेंट दर्ज हो गया और सभी मेंबर्स में ₹{per_member_profit} प्रॉफिट बँट गया!")

def render_penalty():
    st.header("⚠️ लेट फाइन & पेनाल्टी मैनेजर")
    st.info("फोर्स क्लोज का फाइन अब सीधे 'कलेक्शन & बिडिंग' पेज से कट जाता है। अगर कोई अलग से फाइन जमा करता है तो आप उसे 'लेज़र' में मैन्युअली जोड़ सकते हैं।")

def render_reports():
    st.header("📥 ग्लोबल रिपोर्टिंग & ऑटो बैकअप")
    if len(st.session_state.members_db) > 0:
        df_members = pd.DataFrame(st.session_state.members_db)
        mem_excel = export_to_excel(df_members, "Members")
        st.download_button("📥 ऑल मेंबर्स डेटा (Excel)", data=mem_excel, file_name=f"Sandhya_Members.xlsx")
        
        if len(st.session_state.ledger_transactions) > 0:
            df_txns = pd.DataFrame(st.session_state.ledger_transactions)
            txn_excel = export_to_excel(df_txns, "Transactions")
            st.download_button("📥 ऑल ट्रांज़ैक्शन डेटा (Excel)", data=txn_excel, file_name=f"Sandhya_Txns.xlsx")
    else:
        st.info("अभी कोई डेटा उपलब्ध नहीं है।")
