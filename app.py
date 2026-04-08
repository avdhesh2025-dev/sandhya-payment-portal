# 📜 लेजर (खाता) देखें - PDF और Excel के साथ
elif menu == "📜 लेजर (खाता) देखें":
    st.title("📜 रिटेलर का पूरा खाता")
    search_prm = st.selectbox("रिटेलर का खाता देखने के लिए खोजें:", options=dropdown_options)
    
    if search_prm != "सर्च करने के लिए यहाँ टाइप करें...":
        try:
            ledger_df = pd.read_csv(ledger_csv).dropna(how="all").fillna("")
            r_name = retailers_data[search_prm]["Name"]
            user_ledger = ledger_df[ledger_df['Retailer Name'] == r_name].copy()
            
            if not user_ledger.empty:
                st.markdown(f"### 👤 {r_name} का खाता")
                
                # रनिंग बैलेंस कैलकुलेशन
                user_ledger['Amount Out (Debit)'] = pd.to_numeric(user_ledger['Amount Out (Debit)'], errors='coerce').fillna(0)
                user_ledger['Amount In (Credit)'] = pd.to_numeric(user_ledger['Amount In (Credit)'], errors='coerce').fillna(0)
                user_ledger['Balance'] = (user_ledger['Amount Out (Debit)'] - user_ledger['Amount In (Credit)']).cumsum()
                
                st.dataframe(user_ledger, use_container_width=True, hide_index=True)
                
                total_out = user_ledger['Amount Out (Debit)'].sum()
                total_in = user_ledger['Amount In (Credit)'].sum()
                balance = total_out - total_in
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                # 1. Excel डाउनलोड बटन
                with col1:
                    excel_data = user_ledger.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 Excel में डाउनलोड करें",
                        data=excel_data,
                        file_name=f"{r_name}_Ledger.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                # 2. PDF डाउनलोड (सिंपल टेबल फॉर्मेट)
                with col2:
                    # PDF के लिए हम HTML टेबल का इस्तेमाल करेंगे
                    html_table = user_ledger.to_html(index=False)
                    pdf_html = f"""
                    <html>
                    <head><style>
                        table {{ border-collapse: collapse; width: 100%; font-family: sans-serif; }}
                        th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
                        th {{ background-color: #f2f2f2; }}
                        h2 {{ text-align: center; color: #0047AB; }}
                    </style></head>
                    <body>
                        <h2>संध्या इंटरप्राइजेज - लेजर रिपोर्ट</h2>
                        <p><b>रिटेलर:</b> {r_name}</p>
                        <p><b>तारीख:</b> {datetime.now().strftime("%d-%m-%Y")}</p>
                        {html_table}
                        <br>
                        <p><b>कुल माल (Debit):</b> ₹{total_out}</p>
                        <p><b>कुल जमा (Credit):</b> ₹{total_in}</p>
                        <p><b>कुल बकाया (Dues):</b> ₹{balance}</p>
                    </body>
                    </html>
                    """
                    st.download_button(
                        label="📄 PDF में डाउनलोड करें",
                        data=pdf_html,
                        file_name=f"{r_name}_Ledger.html", # अभी के लिए HTML (जिसे मोबाइल पर PDF की तरह सेव कर सकते हैं)
                        mime="text/html",
                        use_container_width=True
                    )
                
                st.info("नोट: मोबाइल पर 'PDF डाउनलोड' बटन दबाने के बाद फाइल खोलें और उसे 'Save as PDF' कर लें।")
                
            else:
                st.info("इस रिटेलर की अभी कोई एंट्री नहीं है।")
        except Exception as e:
            st.error("डेटा लोड करने में समस्या आ रही है।")
