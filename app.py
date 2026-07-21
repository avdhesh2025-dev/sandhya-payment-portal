import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta
import time
import re
import json
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIG & MOBILE STYLES (FULL SCREEN & ZOOM LOCK)
# ==========================================
st.set_page_config(page_title="Sandhya Enterprises Mega ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# 🟢 TAGRA ZOOM LOCK & ADVANCED KEYBOARD CONTROLS
components.html(
    """
    <script>
        var parentDoc = window.parent.document;
        var meta = parentDoc.querySelector('meta[name="viewport"]');
        var viewportContent = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=0, viewport-fit=cover';
        if (meta) { meta.content = viewportContent; } 
        else {
            var newMeta = parentDoc.createElement('meta');
            newMeta.name = 'viewport'; newMeta.content = viewportContent;
            parentDoc.head.appendChild(newMeta);
        }
        
        parentDoc.addEventListener('touchmove', function(event) {
            if (event.scale !== 1 && event.scale !== undefined) { event.preventDefault(); }
        }, { passive: false });

        var lastTouchEnd = 0;
        parentDoc.addEventListener('touchend', function(event) {
            var now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) { event.preventDefault(); }
            lastTouchEnd = now;
        }, { passive: false });

        function fixMobileInputs() {
            var allInputs = parentDoc.querySelectorAll('input, textarea, select');
            allInputs.forEach(function(inp) { inp.style.setProperty('font-size', '16px', 'important'); });

            var dateInputs = parentDoc.querySelectorAll('.stDateInput input');
            dateInputs.forEach(function(input) { input.setAttribute('readonly', 'readonly'); input.setAttribute('inputmode', 'none'); });

            var selectInputs = parentDoc.querySelectorAll('div[data-baseweb="select"] input');
            selectInputs.forEach(function(input) { input.setAttribute('readonly', 'readonly'); input.setAttribute('inputmode', 'none'); });

            var numberInputs = parentDoc.querySelectorAll('input[type="number"], .stNumberInput input');
            numberInputs.forEach(function(input) { input.setAttribute('inputmode', 'decimal'); input.setAttribute('pattern', '[0-9]*'); });

            var pwdInputs = parentDoc.querySelectorAll('input[type="password"]');
            pwdInputs.forEach(function(input) { input.setAttribute('inputmode', 'numeric'); input.setAttribute('pattern', '[0-9]*'); });
        }
        setInterval(fixMobileInputs, 400);
    </script>
    """, height=0, width=0
)

st.markdown("""
    <style>
    html, body, .stApp, .main { 
        touch-action: manipulation !important; 
        -webkit-text-size-adjust: 100% !important; 
        background-color: #f4f7fb !important; 
    }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    
    .block-container {
        background-color: #ffffff !important;
        max-width: 98% !important;
        padding: 25px 20px !important;
        margin: 15px auto !important;
        border-radius: 12px !important;
        box-shadow: 0px 5px 20px rgba(0, 0, 0, 0.05) !important;
    }
    
    @media screen and (max-width: 768px) {
        .block-container { margin: 5px auto !important; padding: 10px !important; }
    }
    
    input:focus, textarea:focus, div[data-baseweb="select"]:focus-within {
        background-color: #dcfce7 !important;
        border: 2px solid #16a34a !important;
        color: #000 !important; font-weight: bold !important;
        box-shadow: 0 0 10px rgba(22, 163, 74, 0.5) !important;
    }

    .kpi-card {
        background: #ffffff; border-radius: 12px; padding: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
        text-align: center; margin-bottom: 15px; border-top: 4px solid #004a99;
    }
    .kpi-title { font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 22px; color: #0f172a; font-weight: 800; margin: 4px 0; }
    .kpi-sub { font-size: 11px; font-weight: bold; }
    
    .audit-box {
        background: #0f172a; color: #38bdf8; padding: 15px;
        border-radius: 8px; font-family: monospace; font-size: 12px;
        max-height: 220px; overflow-y: auto; line-height: 1.6;
    }
    
    .login-box {
        background: linear-gradient(145deg, #ffffff, #e6f2ff); padding: 40px;
        border-radius: 20px; box-shadow: 0 10px 25px rgba(0, 74, 153, 0.1);
        text-align: center; border-top: 5px solid #004a99; max-width: 450px; margin: 0 auto;
    }
    .header-box { background: linear-gradient(135deg, #004a99, #0066cc); padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #f8fafc; padding: 8px; border-radius: 10px; flex-wrap: wrap;}
    .stTabs [data-baseweb="tab"] { color: #0f2027; border-radius: 8px; padding: 8px 12px; font-weight: bold; font-size: 13px;}
    .stTabs [aria-selected="true"] { background: linear-gradient(90deg, #004a99, #0066cc) !important; color: white !important;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 🔒 SECURITY & ENVIROMENT SECRETS MANAGEMENT
# ==========================================
products_url = st.secrets.get("PRODUCTS_URL", "https://docs.google.com/spreadsheets/d/1K3ZeUuZbpB3FmUQlt2ryri_3su4EkLOqzS7uxUQYd1Y/gviz/tq?tqx=out:csv&sheet=Products")
base_read_url = st.secrets.get("BASE_READ_URL", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSXrwSrOi_A8LxQShziA5LkyX1_WRdp7jiSLoJadXbMmrDmMPiX0TtmK_2VNcfy80p-chdq_jPo7kmb/pub?output=csv")
write_url = st.secrets.get("WRITE_URL", "https://script.google.com/macros/s/AKfycby3zqCi1GUxH4a-AqFuCgfzLSoUdBbxXQ_F0LHDqS36nYhj2iebYgGIAAO9g3MIV92j/exec")
OWNER_PHONE = st.secrets.get("OWNER_PHONE", "7479584179")

fse_list = ["All Employees", "0690788829 - Ravindra Sharma", "0690903215 - Ravi Kumar", "0690881333 - Gopal Kumar Sahni","0691116975 - Shashank Shekhar Kumar","0691116972 - Nitish Kumar", 
            "0690373395 - Vikash Kumar", "0690499449 - Lal Babu Das", "0690452472 - Md Samim","0691116945 - Ankit Kumar","0691116911 - Nitish Kumar Soni", 
            "0690859418 - Sachin Kumar", "0690749611 - Premjeet Kumar","0691111278 - Ratnesh Kumar", 
            "0690093932 - Uttam Kumar Paswan", "068996776 - Sunil Kumar", "0690899815 - Munna Kumar","0690930677 - Mukesh Kumar","0691003801 - Md Prvez Alam"]

ADMIN_PWD = st.secrets.get("ADMIN_PASSWORD", "9557")
USER_CREDS = {"admin": {"pwd": ADMIN_PWD, "role": "admin", "fse": "All Employees"}}
for emp in fse_list:
    if "-" in emp: 
        emp_id = emp.split(" - ")[0].strip()
        USER_CREDS[emp_id] = {"pwd": st.secrets.get(f"PWD_{emp_id}", emp_id[-4:]), "role": "staff", "fse": emp}

# ==========================================
# 3. STATE MANAGEMENT & AUDIT LOGS
# ==========================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'cart' not in st.session_state: st.session_state['cart'] = []
if 'pdf_viewer' not in st.session_state: st.session_state['pdf_viewer'] = ""
if 'rep_viewer' not in st.session_state: st.session_state['rep_viewer'] = ""
if 'sales_pdf' not in st.session_state: st.session_state['sales_pdf'] = ""
if 'pos_ledger' not in st.session_state: st.session_state['pos_ledger'] = [] 
if 'last_pos_shop' not in st.session_state: st.session_state['last_pos_shop'] = "-- Select Shop --"
if 'staff_last_date' not in st.session_state: st.session_state['staff_last_date'] = date.today()
if 'pos_last_date' not in st.session_state: st.session_state['pos_last_date'] = date.today()

if 'audit_logs' not in st.session_state: st.session_state['audit_logs'] = []
def add_audit_log(user, action):
    t_stamp = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    st.session_state['audit_logs'].insert(0, f"[{t_stamp}] {user}: {action}")

if 'mnp_schemes' not in st.session_state: 
    st.session_state['mnp_schemes'] = [{"target": 1, "reward": "₹40"}, {"target": 2, "reward": "₹100"}, {"target": 3, "reward": "₹180"}, {"target": 5, "reward": "₹350"}]
if 'scheme_start' not in st.session_state: st.session_state['scheme_start'] = date.today()
if 'scheme_end' not in st.session_state: st.session_state['scheme_end'] = date.today()

if 'show_popup' not in st.session_state: st.session_state['show_popup'] = False
if 'popup_msg' not in st.session_state: st.session_state['popup_msg'] = ""
if 'show_staff_popup' not in st.session_state: st.session_state['show_staff_popup'] = False 
if 'staff_popup_msg' not in st.session_state: st.session_state['staff_popup_msg'] = ""        
if 'show_bill_popup' not in st.session_state: st.session_state['show_bill_popup'] = False 
if 'bill_popup_msg' not in st.session_state: st.session_state['bill_popup_msg'] = ""        
if 'show_inv_popup' not in st.session_state: st.session_state['show_inv_popup'] = False 
if 'inv_popup_msg' not in st.session_state: st.session_state['inv_popup_msg'] = ""        

# ==========================================
# 4. UTILITY FUNCTIONS
# ==========================================
def num_to_words(num):
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    def convert(n):
        if n < 20: return units[n]
        if n < 100: return tens[n // 10] + (" " + units[n % 10] if (n % 10) != 0 else "")
        if n < 1000: return units[n // 100] + " Hundred" + (" " + convert(n % 100) if (n % 100) != 0 else "")
        if n < 100000: return convert(n // 1000) + " Thousand" + (" " + convert(n % 1000) if (n % 1000) != 0 else "")
        if n < 10000000: return convert(n // 100000) + " Lakh" + (" " + convert(n % 100000) if (n % 100000) != 0 else "")
        return convert(n // 10000000) + " Crore" + (" " + convert(n % 10000000) if (n % 10000000) != 0 else "")
    val = int(round(float(num)))
    if val == 0: return "Zero Rupees Only"
    return convert(val).strip() + " Rupees Only"

@st.cache_data(ttl=60)
def load_db():
    try:
        df = pd.read_csv(f"{base_read_url}&cb={int(time.time())}", dtype=str).dropna(how='all')
        if df.empty: raise ValueError("Empty Data")
        while len(df.columns) < 15: df[f"Col_{len(df.columns)}"] = "0"
        df['dt_fixed'] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, format="mixed", errors='coerce')
        for c in [7, 10, 11]: df[df.columns[c]] = pd.to_numeric(df[df.columns[c]], errors='coerce').fillna(0)
        return df
    except:
        df = pd.DataFrame(columns=[f"Col_{i}" for i in range(15)])
        df['dt_fixed'] = pd.NaT
        return df

@st.cache_data(ttl=60)
def load_products():
    try: return pd.read_csv(f"{products_url}&cb={int(time.time())}", dtype=str).dropna(how='all')
    except: return pd.DataFrame()

def get_safe_qty(df, act_kw, rem_kw=None):
    if df.empty: return 0
    temp = df[df.iloc[:, 2].astype(str).str.contains(act_kw, na=False, case=False)]
    if rem_kw: temp = temp[temp.iloc[:, 3].astype(str).str.contains(rem_kw, na=False, case=False)]
    if temp.empty: return 0
    return int(temp.iloc[:, 3].apply(lambda x: int(re.search(r'Qty\s*:?\s*(\d+)', str(x), re.IGNORECASE).group(1)) if re.search(r'Qty\s*:?\s*(\d+)', str(x), re.IGNORECASE) else 1).sum())

def parse_tech(tech_str, fallback_total=0.0):
    d = {"Inv": "OLD", "Item": str(tech_str), "Rate": 0.0, "Qty": 1, "Disc": 0.0, "Cost": 0.0, "Total": fallback_total, "Cash":0.0, "Online":0.0, "Card":0.0, "Due":0.0, "Addr": "", "IMEI": "", "Wrnty": ""}
    try:
        has_rate = False
        if "|" in str(tech_str):
            for p in str(tech_str).split("|"):
                p = p.strip()
                if p.startswith("Inv:"): d["Inv"] = p.replace("Inv:", "").strip()
                elif p.startswith("Item:"): d["Item"] = p.replace("Item:", "").strip()
                elif p.startswith("Rate:"): 
                    d["Rate"] = float(re.findall(r"[-+]?\d*\.\d+|\d+", p)[0])
                    has_rate = True
                elif p.startswith("Qty:"): d["Qty"] = float(re.findall(r"[-+]?\d*\.\d+|\d+", p)[0])
                elif p.startswith("Disc:"): d["Disc"] = float(re.findall(r"[-+]?\d*\.\d+|\d+", p)[0])
                elif p.startswith("Cost:"): d["Cost"] = float(re.findall(r"[-+]?\d*\.\d+|\d+", p)[0])
                elif p.startswith("Pay:"): 
                    c_m = re.search(r'C=([-+]?[\d.]+)', p)
                    if c_m: d["Cash"] = float(c_m.group(1))
                    o_m = re.search(r'O=([-+]?[\d.]+)', p)
                    if o_m: d["Online"] = float(o_m.group(1))
                    cr_m = re.search(r'Card=([-+]?[\d.]+)', p)
                    if cr_m: d["Card"] = float(cr_m.group(1))
                    d_m = re.search(r'D=([-+]?[\d.]+)', p)
                    if d_m: d["Due"] = float(d_m.group(1))
                elif p.startswith("Addr:"): d["Addr"] = p.replace("Addr:", "").strip()
                elif p.startswith("IMEI:"): d["IMEI"] = p.replace("IMEI:", "").strip()
                elif p.startswith("Wrnty:"): d["Wrnty"] = p.replace("Wrnty:", "").strip()
        if has_rate:
            d["Total"] = (d["Rate"] * d["Qty"]) - d["Disc"]
    except: pass
    return d

def get_latest_rates(item_name, df_p, df_h):
    cost, sell = 0.0, 0.0
    try:
        p_row = df_p[df_p.iloc[:, 1] == item_name].iloc[0]
        cost = float(p_row.iloc[3])
        sell = float(p_row.iloc[4])
    except: pass
    try:
        stock_df = df_h[(df_h.iloc[:, 2] == "STOCK_IN") & (df_h.iloc[:, 3].astype(str).str.contains(f"Item: {item_name}", regex=False))]
        if not stock_df.empty:
            latest_entry = stock_df.iloc[-1]
            p = parse_tech(latest_entry.iloc[3])
            if p["Cost"] > 0: cost = p["Cost"]
            if p["Rate"] > 0: sell = p["Rate"]
    except: pass
    return cost, sell

# ==========================================
# 5. HTML PDF & VIEW GENERATORS
# ==========================================
def generate_html_viewer(html_content, filename):
    safe_id = re.sub(r'[^A-Za-z0-9]', '_', filename)
    return f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        @media print {{ 
            .no-print {{ display: none !important; }} 
            body {{ margin: 0; padding: 0; background: white; }} 
            * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        }}
        table {{ page-break-inside: auto; width: 100%; }}
        tr, td, th {{ page-break-inside: avoid !important; break-inside: avoid !important; }}
        .unbreak {{ page-break-inside: avoid !important; break-inside: avoid !important; }}
    </style>
    <div style="background:#e2e8f0; padding:20px; border-radius:10px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center;">
        <div id="pdf-content-{safe_id}" style="width:100%; max-width:190mm; background:white; padding:20px; box-sizing:border-box; color:black; font-family:sans-serif; box-shadow:0 10px 30px rgba(0,0,0,0.1); position:relative; overflow: hidden;">
            {html_content}
        </div>
        <div class="no-print" style="width:100%; max-width:190mm; text-align:center; margin-top:20px;">
            <div style="display:flex; justify-content:center; gap:15px; margin-bottom:10px;">
                <button onclick="downloadPDF_{safe_id}()" style="padding:15px 30px; background:#004a99; color:white; border:none; border-radius:8px; font-size:16px; font-weight:bold; cursor:pointer; flex:1;">
                    📥 DOWNLOAD HD PDF
                </button>
                <button onclick="window.print()" style="padding:15px 30px; background:#16a34a; color:white; border:none; border-radius:8px; font-size:16px; font-weight:bold; cursor:pointer; flex:1;">
                    🖨️ PRINT / SAVE
                </button>
            </div>
        </div>
    </div>
    <script>
    function downloadPDF_{safe_id}() {{
        window.scrollTo(0, 0); 
        var element = document.getElementById('pdf-content-{safe_id}');
        var opt = {{ 
            margin: [10, 10, 10, 10], 
            filename: '{filename}.pdf', 
            image: {{ type: 'jpeg', quality: 1.0 }}, 
            html2canvas: {{ scale: 3, useCORS: true, letterRendering: true }}, 
            jsPDF: {{ unit: 'mm', format: 'a4', orientation: 'portrait' }},
            pagebreak: {{ mode: ['css', 'legacy'], avoid: ['tr', 'td', 'th', '.unbreak', 'h1', 'h2', 'h3'] }}
        }};
        html2pdf().set(opt).from(element).save();
    }}
    </script>
    """

def get_invoice_html(cn, cm, ca, inv, dt, rows_html, gt, t_disc, csh, onl, crd, due, amt_words):
    qr_amt = onl if onl > 0 else (due if due > 0 else gt)
    html = f"""
        <div style="font-family: Arial, sans-serif; color: #000; padding: 10px; position: relative; overflow: hidden; min-height: 500px;">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 50px; color: rgba(0, 0, 0, 0.06); font-weight: 900; white-space: nowrap; z-index: 0; pointer-events: none;">
                SANDHYA ENTERPRISES
            </div>
            <div style="position: relative; z-index: 1;">
                <div style="text-align:center; border-bottom:2px solid #000; padding-bottom:10px; margin-bottom:15px;">
                    <h3 style="margin:0; font-size:16px;">TAX INVOICE</h3>
                    <h1 style="margin:5px 0; font-size:32px; font-weight:900;">SANDHYA ENTERPRISES</h1>
                    <p style="margin:2px 0; font-size:12px; font-weight:bold;">Billing Branch : MEGHPATTI</p>
                    <p style="margin:2px 0; font-size:11px;">Ward no 06 Rosera Road Meghpatti, Samastipur, Bihar 848117</p>
                    <p style="margin:2px 0; font-size:11px;">Contact: {OWNER_PHONE} | Email: smp.sandhya02@gmail.com</p>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:15px; border-bottom:2px solid #000; padding-bottom:10px;">
                    <div style="width:60%;">
                        <b>Buyer Name & Address:</b><br>
                        <b>Name :</b> {cn}<br>
                        <b>Mobile :</b> {cm}<br>
                        <b>Address:</b> {ca}
                    </div>
                    <div style="width:35%; border-left:1px solid #000; padding-left:10px;">
                        <b>Invoice No :</b> {inv}<br>
                        <b>Invoice Date :</b> {dt}
                    </div>
                </div>
                <table style="width:100%; border-collapse:collapse; font-size:12px; margin-bottom:10px; border:1px solid #000;">
                    <thead>
                        <tr style="border-bottom:1px solid #000; background-color:#f8f9fa;">
                            <th style="padding:8px; text-align:left; border-right:1px solid #000;">Product Description</th>
                            <th style="padding:8px; text-align:center; border-right:1px solid #000;">Rate</th>
                            <th style="padding:8px; text-align:center; border-right:1px solid #000;">Qty</th>
                            <th style="padding:8px; text-align:right;">Total (Rs)</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
                <div class="unbreak" style="border:1px solid #000; padding:5px 10px; font-size:12px; margin-bottom:15px;">
                    <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #000; padding-bottom:5px; margin-bottom:5px;">
                        <span><b>Discount Saved :</b> Rs. {t_disc:,.2f}</span>
                        <span style="font-size:14px;"><b>TOTAL AMOUNT : Rs. {gt:,.2f}</b></span>
                    </div>
                    <b>Rupees in Words :</b> {amt_words}
                </div>
                <div class="unbreak" style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
                    <div style="width:65%;">
                        <div style="font-size:12px; margin-bottom:15px;">
                            <b>PAYMENT DETAILS</b>
                            <table style="width:100%; border-collapse:collapse; border:1px solid #000; margin-top:5px;">
                                <tr><td style="padding:4px; border-right:1px solid #000;">Cash</td><td style="padding:4px; text-align:right;">{csh:,.2f}</td></tr>
                                <tr><td style="padding:4px; border-right:1px solid #000;">Online</td><td style="padding:4px; text-align:right;">{onl:,.2f}</td></tr>
                                <tr><td style="padding:4px; border-right:1px solid #000;">Card</td><td style="padding:4px; text-align:right;">{crd:,.2f}</td></tr>
                                <tr style="border-top:1px solid #000;"><td style="padding:4px; border-right:1px solid #000;"><b>Due Amount</b></td><td style="padding:4px; text-align:right; color:red;"><b>{due:,.2f}</b></td></tr>
                            </table>
                        </div>
                    </div>
                    <div style="width:30%; text-align:center; padding:10px; border:1px solid #000; border-radius:8px;">
                        <b style="font-size:12px;">SCAN TO PAY</b><br>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=upi://pay?pa={OWNER_PHONE}@ptaxis%26pn=SANDHYA%20ENTERPRISES%26am={qr_amt:.2f}%26cu=INR" style="width:90px; height:90px; margin:5px 0;">
                        <br><b style="font-size:12px;">₹ {qr_amt:,.2f}</b>
                    </div>
                </div>
                <div class="unbreak" style="display:flex; justify-content:space-between; font-size:12px; margin-top:30px;">
                    <div style="text-align:center;">_____________________<br>Customer Signature</div>
                    <div style="text-align:center;">_____________________<br>Authorised Signatory<br><b>SANDHYA ENTERPRISES</b></div>
                </div>
            </div>
        </div>
    """
    return generate_html_viewer(html, f"Bill_{inv}")

# ==========================================
# 6. APPLICATION LOGIN & INTERFACE LOGIC
# ==========================================
if not st.session_state['logged_in']:
    st.markdown('<br><br>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('''
            <div class="login-box">
                <h1 style="margin:0; color:#004a99; font-size: 26px;">🏢 SANDHYA ENTERPRISES</h1>
                <p style="color:#666; font-weight:bold; margin-bottom:15px;">Smart Business ERP Portal</p>
            </div>
        ''', unsafe_allow_html=True)
        
        display_to_fse = {}
        login_list_display = ["-- Select Profile --", "👑 Admin"]
        for e in fse_list:
            if "-" in e:
                name_only = e.split("-")[1].strip()
                login_list_display.append(name_only)
                display_to_fse[name_only] = e

        u_sel_display = st.selectbox("👤 Select Profile", login_list_display)
        u_pwd = st.text_input("🔑 Password", type="password", placeholder="Enter Password...")
        
        if st.button("🚀 SECURE LOGIN", use_container_width=True, type="primary"):
            auth_success = False
            if u_sel_display == "👑 Admin" and u_pwd == ADMIN_PWD:
                st.session_state.update({'logged_in': True, 'role': 'admin', 'fse_name': 'All Employees'})
                add_audit_log("Admin", "Logged in successfully to Master Portal")
                auth_success = True
            elif u_sel_display != "-- Select Profile --":
                full_fse_string = display_to_fse[u_sel_display]
                emp_id = full_fse_string.split(" - ")[0].strip()
                if emp_id in USER_CREDS and USER_CREDS[emp_id]["pwd"] == u_pwd:
                    st.session_state.update({'logged_in': True, 'role': 'staff', 'fse_name': full_fse_string})
                    add_audit_log(full_fse_string, "Logged in to Staff Console")
                    auth_success = True
            
            if auth_success: st.rerun()
            else: st.error("❌ Invalid Password!")

else:
    # 🟢 GLOBAL OVERLAYS & POPUPS
    if st.session_state.get('pdf_viewer') != "":
        components.html(st.session_state['pdf_viewer'], height=1050, scrolling=True)
        if st.button("❌ CLOSE VIEWER", type="primary", use_container_width=True):
            st.session_state['pdf_viewer'] = ""; st.rerun()
        st.stop()

    if st.session_state.get('show_popup'):
        st.markdown(f"""
        <div style="background: white; padding: 25px; border-radius: 15px; text-align: center; border: 3px solid #16a34a; max-width: 450px; margin: 20px auto;">
            <h1 style="color: #16a34a; margin: 0;">✅ SUCCESS!</h1>
            <p style="font-size: 16px; color: #333;">{st.session_state['popup_msg']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("❌ CLOSE", type="primary", use_container_width=True):
            st.session_state['show_popup'] = False; st.rerun()
        st.stop()

    # --- TOP NAVIGATION & BRANDING ---
    nav_c1, nav_c2, nav_c3 = st.columns([2, 1, 1])
    nav_c1.markdown(f"### 🏢 Sandhya ERP | Active: **{st.session_state['fse_name'].split('-')[-1]}**")
    if nav_c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    if nav_c3.button("🚪 Logout", use_container_width=True): st.session_state.clear(); st.rerun()

    df_h = load_db()
    df_p = load_products()

    # TABS ALLOCATION
    if st.session_state['role'] == 'admin':
        tabs = st.tabs(["📊 1. LIVE KPI & PROFIT", "🛒 2. POS BILLING & SCANNER", "👷 3. EMPLOYEE MGT", "📦 4. INVENTORY CONTROL", "📈 5. SALES ANALYTICS", "⚠️ 6. PAYMENT RECOVERY", "🔥 7. MNP SCHEMES", "💰 8. CASH COLLECTION", "🔴 9. RED PROJECT", "🕵️ 10. AUDIT LOGS"])
    else:
        tabs = st.tabs(["👷 MY PERFORMANCE", "🛒 QUICK BILLING", "⚠️ RECOVERY ENTRY"])

    # ==========================================
    # 📊 TAB 1: LIVE KPI & PROFIT DASHBOARD (Priority 1)
    # ==========================================
    if st.session_state['role'] == 'admin':
        with tabs[0]:
            st.subheader("📈 Real-Time Business Performance Dashboard")
            
            today_date_str = date.today().strftime("%d-%m-%Y")
            today_df = df_h[df_h['dt_fixed'].dt.date == date.today()] if not df_h.empty else pd.DataFrame()
            
            today_sale = 0.0
            today_cost = 0.0
            today_profit = 0.0
            
            for _, r in today_df.iterrows():
                tech = parse_tech(r.iloc[3], fallback_total=float(r.iloc[11]) if pd.notna(r.iloc[11]) else 0.0)
                if "Inv: SE-" in tech["Inv"]:
                    s_amt = float(r.iloc[11])
                    c_amt = tech["Cost"] * tech["Qty"]
                    today_sale += s_amt
                    today_cost += c_amt
                    today_profit += (s_amt - c_amt)

            # Monthly Sales & Profit
            curr_month_df = df_h[df_h['dt_fixed'].dt.month == date.today().month] if not df_h.empty else pd.DataFrame()
            month_sale = curr_month_df.iloc[:, 11].sum() if not curr_month_df.empty else 0.0

            # KPI Grid Cards
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.markdown(f'<div class="kpi-card"><div class="kpi-title">Today\'s Sale</div><div class="kpi-value" style="color:#2563eb;">₹{today_sale:,.0f}</div><div class="kpi-sub">Cost: ₹{today_cost:,.0f}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="kpi-card"><div class="kpi-title">Today\'s Profit</div><div class="kpi-value" style="color:#16a34a;">₹{today_profit:,.0f}</div><div class="kpi-sub">Net Profit Margin</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="kpi-card"><div class="kpi-title">Monthly Sales</div><div class="kpi-value" style="color:#0f172a;">₹{month_sale:,.0f}</div><div class="kpi-sub">This Month</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="kpi-card"><div class="kpi-title">Active Staff</div><div class="kpi-value" style="color:#0891b2;">{len(fse_list)-1} Staff</div><div class="kpi-sub">On Roster</div></div>', unsafe_allow_html=True)
            k5.markdown(f'<div class="kpi-card"><div class="kpi-title">Low Stock Alert</div><div class="kpi-value" style="color:#dc2626;">Check Tab 4</div><div class="kpi-sub">Stock Re-order</div></div>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 🤖 Sandhya AI Business Assistant")
            ai_query = st.text_input("Ask AI Assistant (e.g. 'Profit status', 'Today sales'):")
            if ai_query:
                q_lower = ai_query.lower()
                if "profit" in q_lower:
                    st.success(f"🤖 **AI Answer:** आज का कुल नेट प्रॉफिट **₹{today_profit:,.2f}** है।")
                elif "sale" in q_lower:
                    st.success(f"🤖 **AI Answer:** आज की कुल बिक्री **₹{today_sale:,.2f}** है।")
                else:
                    st.info("🤖 **AI Answer:** मैं आपके स्टोर के डेटा का विश्लेषण कर रहा हूँ। अधिक सटीक जानकारी के लिए Profit या Sale टाइप करें।")

    # ==========================================
    # 🛒 TAB 2: SMART BILLING & BARCODE SEARCH (Priority 1 & 2)
    # ==========================================
    pos_tab = tabs[1] if st.session_state['role'] == 'admin' else tabs[1]
    with pos_tab:
        st.subheader("🛒 Fast POS Billing & Barcode Search")
        
        c1, c2, c3 = st.columns(3)
        cn = c1.text_input("Customer Name", value="Walk-in Customer")
        cm = c2.text_input("Customer Mobile No.")
        ca = c3.text_input("Address", value="Samastipur")

        st.markdown("##### 🔍 Scan Barcode / Search Product")
        barcode_search = st.text_input("Type Product Name, Model or Scan Barcode Number", placeholder="Scan Barcode / Model...")
        
        if barcode_search and not df_p.empty:
            match = df_p[df_p.iloc[:, 1].str.contains(barcode_search, case=False, na=False) | df_p.iloc[:, 0].str.contains(barcode_search, case=False, na=False)]
            if not match.empty:
                selected_row = match.iloc[0]
                p_name = selected_row.iloc[1]
                p_cost = float(selected_row.iloc[3]) if pd.notna(selected_row.iloc[3]) else 0.0
                p_rate = float(selected_row.iloc[4]) if pd.notna(selected_row.iloc[4]) else 0.0
                
                st.info(f"🎯 Matched: **{p_name}** | Cost Price: **₹{p_cost}** | Selling Price: **₹{p_rate}**")
                
                q1, q2 = st.columns(2)
                b_qty = q1.number_input("Quantity", min_value=1, value=1)
                b_disc = q2.number_input("Discount (₹)", min_value=0.0, value=0.0)
                
                if st.button("➕ Add Item to Cart", type="primary"):
                    tot = (p_rate * b_qty) - b_disc
                    st.session_state['cart'].append({"Item": p_name, "Rate": p_rate, "Qty": b_qty, "Disc": b_disc, "Cost": p_cost, "IMEI": "N/A", "Wrnty": "1 Year", "Total": tot})
                    add_audit_log(st.session_state['fse_name'], f"Added {p_name} to cart (Qty: {b_qty})")
                    st.success(f"{p_name} added to cart!")

        if st.session_state['cart']:
            st.write("---")
            st.write("### 🛒 Active Cart")
            st.table(pd.DataFrame(st.session_state['cart'])[["Item", "Rate", "Qty", "Total"]])
            grand_t = sum(i['Total'] for i in st.session_state['cart'])
            tot_d = sum(i['Disc'] for i in st.session_state['cart'])
            
            st.markdown(f"### Grand Total: **₹{grand_t:,.2f}**")
            
            p1, p2, p3 = st.columns(3)
            csh = p1.number_input("Cash Received (₹)", value=grand_t)
            onl = p2.number_input("Online Received (₹)", value=0.0)
            due_v = grand_t - (csh + onl)
            p3.markdown(f"**Due (बाकी):** <span style='color:red; font-size:18px;'>₹{due_v:,.2f}</span>", unsafe_allow_html=True)
            
            if st.button("💾 SAVE & GENERATE INVOICE", type="primary", use_container_width=True):
                inv_id = f"SE-{int(time.time())%100000}"
                rows_h = ""
                for i in st.session_state['cart']:
                    tech = f"Inv: {inv_id} | Item: {i['Item']} | Rate: {i['Rate']} | Qty: {i['Qty']} | Disc: {i['Disc']} | Cost: {i['Cost']} | Pay: C={csh},O={onl},D={due_v} | Addr: {ca}"
                    requests.post(write_url, json={"date": date.today().strftime("%d-%m-%Y"), "fse": cn, "activity_boy": cm, "tech": tech, "total": i['Total']})
                    rows_h += f"<tr><td style='padding:5px;'>{i['Item']}</td><td style='padding:5px; text-align:center;'>{i['Rate']}</td><td style='padding:5px; text-align:center;'>{i['Qty']}</td><td style='padding:5px; text-align:right;'>{i['Total']}</td></tr>"
                
                add_audit_log(st.session_state['fse_name'], f"Generated Invoice {inv_id} for ₹{grand_t}")
                st.session_state['pdf_viewer'] = get_invoice_html(cn, cm, ca, inv_id, date.today().strftime("%d/%m/%Y"), rows_h, grand_t, tot_d, csh, onl, 0.0, due_v, num_to_words(grand_t))
                
                # 💬 WhatsApp Share Automation Button Generator (Priority 2)
                wa_msg = f"🏢 *SANDHYA ENTERPRISES TAX INVOICE*\nInvoice No: {inv_id}\nCustomer: {cn}\nTotal Bill: ₹{grand_t}\nThank you for visiting!"
                encoded_wa = requests.utils.quote(wa_msg)
                st.markdown(f'<a href="https://wa.me/91{cm}?text={encoded_wa}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; width:100%; font-weight:bold;">💬 SEND INVOICE ON WHATSAPP</button></a>', unsafe_allow_html=True)
                
                st.session_state['cart'] = []
                st.rerun()

    # ==========================================
    # ⚠️ TAB 6: PAYMENT RECOVERY & REMINDERS (Priority 2)
    # ==========================================
    rec_tab = tabs[5] if st.session_state['role'] == 'admin' else tabs[2]
    with rec_tab:
        st.subheader("⚠️ Payment Recovery & Automatic WhatsApp Reminders")
        st.info("यहाँ उन बकायेदारों की लिस्ट है जिनका पेमेंट बाकी है।")
        
        # Pull due entries from DB
        dues_found = []
        for _, r in df_h.iterrows():
            tech = parse_tech(r.iloc[3])
            if tech.get("Due", 0) > 0:
                dues_found.append({"Customer": r.iloc[1], "Phone": r.iloc[2], "Due": tech["Due"], "Inv": tech["Inv"]})
                
        if dues_found:
            for idx, d in enumerate(dues_found[:10]):
                st.warning(f"👤 **{d['Customer']}** | Inv: {d['Inv']} | Due: **₹{d['Due']}**")
                wa_text = f"प्रिय *{d['Customer']}*,\n\nसंध्या एंटरप्राइजेज का रिमाइंडर: आपका बिल नंबर {d['Inv']} का *₹{d['Due']}* बकाया है। कृपया आज ही भुगतान करें।"
                enc_text = requests.utils.quote(wa_text)
                st.markdown(f'<a href="https://wa.me/91{d["Phone"]}?text={enc_text}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:6px 12px; border-radius:5px; font-weight:bold;">💬 Send WhatsApp Payment Reminder</button></a>', unsafe_allow_html=True)
        else:
            st.success("🎉 All dues cleared! No pending recoveries.")

    # ==========================================
    # 🕵️ TAB 10: AUDIT LOG TRAIL (Priority 1)
    # ==========================================
    if st.session_state['role'] == 'admin':
        with tabs[9]:
            st.subheader("🕵️ System Security & Audit Log History")
            st.info("यह ब्लैक-बॉक्स ट्रैकर दिखाता है कि किस कर्मचारी ने किस समय क्या एक्शन लिया है।")
            if st.session_state['audit_logs']:
                st.markdown(f'<div class="audit-box">{"<br>".join(st.session_state["audit_logs"])}</div>', unsafe_allow_html=True)
            else:
                st.caption("No system activity logged in this session yet.")
