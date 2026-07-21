import streamlit as st
import pandas as pd
import datetime
from utils import generate_member_id, send_data_to_sheet, generate_qr, get_whatsapp_link, export_to_excel

def render_dashboard():
    st.header("📊 प्रोफेशनल डैशबोर्ड & एनालिटिक्स")
    
    total_members = len(st.session_state.members_db)
    active_members = sum(1 for m in st.session_state.members_db if m.get('status') == '✅ Active')
    
    txns = st.session_state.ledger_transactions
    total_collection = sum(t['credit'] for t in txns if t['credit'] > 0)
    total_loan_out = sum(t['loan'] for t in txns if t['loan'] > 0)
    total_fine = sum(t['fine'] for t in txns if t['fine'] > 0)
    running_balance = total_collection + total_fine - total_loan_out
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("कुल सदस्य", f"{total_members} ({active_members} Active)")
    m2.metric("कुल कलेक्शन (जमा)", f"₹ {total_collection:,.2f}")
    m3.metric("रनिंग लोन (मार्केट में)", f"₹ {total_loan_out:,.2f}")
    m4.metric("करंट रनिंग बैलेंस", f"₹ {running_balance:,.2f}")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 कलेक्शन ट्रेंड (Charts)")
        if len(txns) > 0:
            df_chart = pd.DataFrame(txns)
            df_chart['date'] = pd.to_datetime(df_chart['date'])
            daily_coll = df_chart.groupby('date')['credit'].sum().reset_index()
            st.line_chart(daily_coll.set_index('date'))
        else:
            st.info("चार्ट दिखाने के लिए पर्याप्त डेटा नहीं है।")
            
    with c2:
        st.subheader("🟢 पेंडिंग पेमेंट ट्रैकर")
        if len(st.session_state.payment_status) > 0:
            update_member = st.selectbox("स्टेटस बदलने के लिए मेंबर चुनें:", list(st.session_state.payment_status.keys()))
            new_status = st.radio("नया स्टेटस चुनें:", ["✅ Complete", "❌ Pending"], horizontal=True)
            
            if st.button("स्टेटस अपडेट करें", use_container_width=True):
                st.session_state.payment_status[update_member] = new_status
                st.success(f"✅ {update_member} का स्टेटस अपडेट हो गया है!")
                st.rerun()
                
            status_data = [{"मेंबर": k, "स्टेटस": v} for k, v in st.session_state.payment_status.items()]
            st.dataframe(pd.DataFrame(status_data), use_container_width=True)

def render_add_member():
    st.header("👤 एडवांस्ड मेंबर रजिस्ट्रेशन (Auto ID & Validation)")
    
    with st.form("new_member_form", clear_on_submit=True):
        st.subheader("Personal & Contact Details")
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("पूरा नाम *")
            dob = st.date_input("जन्म तिथि (DOB)", min_value=datetime.date(1950, 1, 1))
            gender = st.selectbox("लिंग (Gender)", ["Male", "Female", "Other"])
        with c2:
            mobile = st.text_input("मोबाइल / WhatsApp नंबर *")
            emergency_contact = st.text_input("इमरजेंसी संपर्क नंबर")
            email = st.text_input("ईमेल (Email)")
        with c3:
            occupation = st.text_input("व्यवसाय (Occupation)")
            nominee = st.text_input("नॉमिनी का नाम (Nominee)")
            reference = st.selectbox("रेफरेंस / गारंटर *", ["-- चुनें --", "Admin", "Self"])

        st.subheader("Identity & Banking (Validation Enabled)")
        c4, c5 = st.columns(2)
        with c4:
            identity_num = st.text_input("Aadhaar Number * (12 Digits)")
            pan = st.text_input("PAN Card Number *")
            address = st.text_area("पूरा पता (Meghpatti, Samastipur, etc.) *")
        with c5:
            bank_ac = st.text_input("Bank Account Number")
            ifsc = st.text_input("Bank IFSC Code")
            upi_id = st.text_input("UPI ID *")

        photo = st.file_uploader("मेंबर की फोटो अपलोड करें *", type=["jpg", "png", "jpeg"])
        
        submit = st.form_submit_button("डेटा सेव करें", use_container_width=True)
        
        if submit:
            existing_mobiles = [m['mobile'] for m in st.session_state.members_db]
            existing_pans = [m['pan'] for m in st.session_state.members_db]
            
            if not name or not mobile or not identity_num or not pan or not address or not upi_id:
                st.error("⚠️ कृपया सभी अनिवार्य (*) फील्ड भरें!")
            elif len(identity_num) != 12 or not identity_num.isdigit():
                st.error("❌ त्रुटि: आधार नंबर ठीक 12 अंकों का होना चाहिए!")
            elif len(pan) != 10:
                st.error("❌ त्रुटि: PAN कार्ड नंबर ठीक 10 अक्षरों का होना चाहिए!")
            elif mobile in existing_mobiles:
                st.error("❌ त्रुटि: यह मोबाइल नंबर पहले से रजिस्टर्ड है!")
            elif pan in existing_pans:
                st.error("❌ त्रुटि: यह PAN नंबर पहले से मौजूद है!")
            else:
                member_id = generate_member_id(len(st.session_state.members_db))
                
                # Payload for Google Sheet (Strict ID Masking)
                payload = {
                    "action": "insert",
                    "member_id": member_id,
                    "name": name,
                    "mobile": mobile,
                    "identity": "[Aadhaar Redacted]", 
                    "pan": pan,
                    "upi": upi_id,
                    "address": address,
                    "reference": reference
                }
                
                send_data_to_sheet(payload) # Async non-blocking call in real env
                
                new_member = {
                    "id": member_id, "name": name, "mobile": mobile, "dob": str(dob), "gender": gender,
                    "email": email, "emergency_contact": emergency_contact, "occupation": occupation,
                    "nominee": nominee, "identity_num": "[Aadhaar Redacted]", "pan": pan, "address": address,
                    "bank_ac": bank_ac, "ifsc": ifsc, "upi": upi_id, "reference": reference,
                    "status": "✅ Active", "loan_status": "Clear", "photo": photo
                }
                
                st.session_state.members_db.append(new_member)
                st.session_state.payment_status[name] = "❌ Pending"
                
                # Auto first ledger entry
                st.session_state.ledger_transactions.append({
                    "txn_id": f"TXN{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "name": name,
                    "date": str(datetime.date.today()),
                    "विवरण": "खाता खुला / रजिस्ट्रेशन जमा",
                    "credit": 2000, "debit": 0, "loan": 0, "commission": 0, "fine": 0, "balance": 2000
                })
                
                st.success(f"✅ {name} सफलतापूर्वक रजिस्टर्ड! Member ID: {member_id}")

def render_ledger():
    st.header("📒 स्मार्ट लेज़र, ट्रांज़ैक्शन & कम्युनिकेशन")
    
    if len(st.session_state.members_db) > 0:
        member_names = [f"{m['name']} ({m['id']})" for m in st.session_state.members_db]
        selected_display = st.selectbox("प्रोफाइल/लेज़र देखने के लिए मेंबर चुनें (Search Enabled):", member_names)
        selected_name = selected_display.split(" (")[0]
        
        m_details = next((m for m in st.session_state.members_db if m['name'] == selected_name), None)
        
        if m_details:
            st.markdown(f"### Sandhya Enterprises - {m_details['name']} Profile")
            st.markdown("📍 Head Office: Meghpatti, Samastipur, Bihar | Admin: Avdhesh Kumar")
            st.markdown("---")
            
            p_col1, p_col2, p_col3 = st.columns([1, 2, 2])
            with p_col1:
                if m_details.get('photo') is not None:
                    st.image(m_details['photo'], width=120)
                else:
                    st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=120)
                st.success(m_details['status'])
                
            with p_col2:
                st.write(f"🆔 **Member ID:** {m_details['id']}")
                st.write(f"📱 **मोबाइल:** {m_details['mobile']}")
                st.write(f"📍 **पता:** {m_details['address']}")
                st.write(f"💼 **व्यवसाय:** {m_details.get('occupation', 'N/A')}")
                
            with p_col3:
                st.write(f"🏛️ **ID:** [Redacted]")
                st.write(f"💳 **PAN:** {m_details['pan']}")
                st.write(f"🏦 **UPI:** {m_details['upi']}")
                st.write(f"👥 **नॉमिनी:** {m_details.get('nominee', 'N/A')}")
            
            # Action Buttons
            action_cols = st.columns(4)
            wh_link = get_whatsapp_link(m_details['mobile'], f"Sandhya Enterprises: Hello {m_details['name']}, your current payment is due. Please pay via UPI: {m_details['upi']}")
            action_cols[0].markdown(f'<a href="{wh_link}" target="_blank"><button style="width:100%; padding:10px; background-color:#25D366; color:white; border:none; border-radius:5px;">💬 WhatsApp Reminder</button></a>', unsafe_allow_html=True)
            
            member_txns = [t for t in st.session_state.ledger_transactions if t['name'] == selected_name]
            
            total_credit = sum([t.get('credit',0) for t in member_txns])
            total_debit = sum([t.get('debit',0) for t in member_txns])
            total_loan = sum([t.get('loan',0) for t in member_txns])
            total_comm = sum([t.get('commission',0) for t in member_txns])
            net_balance = total_credit - total_debit
            
            st.markdown("<br>", unsafe_allow_html=True)
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            f_col1.metric("कुल जमा (Credit)", f"₹ {total_credit:,.2f}")
            f_col2.metric("कुल लोन लिया", f"₹ {total_loan:,.2f}")
            f_col3.metric("कमीशन / प्रॉफिट", f"₹ {total_comm:,.2f}")
            f_col4.metric("Net रनिंग बैलेंस", f"₹ {net_balance:,.2f}")
            
            with st.expander("➕ मैनुअल ट्रांज़ैक्शन एंट्री (Voucher / Receipt)"):
                with st.form(f"txn_form_{m_details['id']}"):
                    t_date = st.date_input("तारीख", datetime.date.today())
                    t_desc = st.text_input("विवरण (Note)")
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        c_amount = st.number_input("क्रेडिट / जमा (₹)", min_value=0.0, value=0.0)
                        l_amount = st.number_input("लोन लिया गया (₹)", min_value=0.0, value=0.0)
                        f_amount = st.number_input("फाइन (₹)", min_value=0.0, value=0.0)
                    with tc2:
                        d_amount = st.number_input("डेबिट / भुगतान (₹)", min_value=0.0, value=0.0)
                        comm_amount = st.number_input("कमीशन (₹)", min_value=0.0, value=0.0)
                        
                    if st.form_submit_button("ट्रांज़ैक्शन सेव करें"):
                        txn_id = f"TXN{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                        st.session_state.ledger_transactions.append({
                            "txn_id": txn_id, "name": selected_name, "date": str(t_date),
                            "विवरण": t_desc if t_desc else "मैनुअल एंट्री",
                            "credit": c_amount, "debit": d_amount, "loan": l_amount,
                            "commission": comm_amount, "fine": f_amount,
                            "balance": net_balance + c_amount - d_amount
                        })
                        st.success(f"✅ एंट्री सेव हो गई! TXN ID: {txn_id}")
                        st.rerun()

            st.subheader("💳 विस्तृत ट्रांज़ैक्शन हिस्ट्री")
            if len(member_txns) > 0:
                df_txn = pd.DataFrame(member_txns)
                st.dataframe(df_txn, use_container_width=True)
                
                # Excel Export
                excel_data = export_to_excel(df_txn, "Ledger")
                st.download_button("📥 लेज़र एक्सेल (Excel) में डाउनलोड करें", data=excel_data, file_name=f"Ledger_{m_details['id']}.xlsx", mime="application/vnd.ms-excel")
            else:
                st.info("कोई ट्रांज़ैक्शन नहीं है।")
    else:
        st.warning("⚠️ लेज़र देखने के लिए पहले मेंबर रजिस्टर करें।")

def render_reports():
    st.header("📥 ग्लोबल रिपोर्टिंग & ऑटो बैकअप")
    st.write("यहाँ से आप पूरे सिस्टम का डेटा निकाल सकते हैं।")
    
    if len(st.session_state.members_db) > 0:
        df_members = pd.DataFrame(st.session_state.members_db)
        # Drop photo objects before export
        if 'photo' in df_members.columns:
            df_members = df_members.drop(columns=['photo'])
            
        mem_excel = export_to_excel(df_members, "Members")
        st.download_button("📥 ऑल मेंबर्स डेटा (Excel)", data=mem_excel, file_name=f"Sandhya_Members_{datetime.date.today()}.xlsx")
        
        if len(st.session_state.ledger_transactions) > 0:
            df_txns = pd.DataFrame(st.session_state.ledger_transactions)
            txn_excel = export_to_excel(df_txns, "Transactions")
            st.download_button("📥 ऑल ट्रांज़ैक्शन डेटा (Excel)", data=txn_excel, file_name=f"Sandhya_Transactions_{datetime.date.today()}.xlsx")
    else:
        st.info("अभी कोई डेटा उपलब्ध नहीं है।")
