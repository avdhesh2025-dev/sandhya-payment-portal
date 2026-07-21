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
try: products_url = st.secrets["PRODUCTS_URL"]
except: products_url = "https://docs.google.com/spreadsheets/d/1K3ZeUuZbpB3FmUQlt2ryri_3su4EkLOqzS7uxUQYd1Y/gviz/tq?tqx=out:csv&sheet=Products"

try: base_read_url = st.secrets["BASE_READ_URL"]
except: base_read_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSXrwSrOi_A8LxQShziA5LkyX1_WRdp7jiSLoJadXbMmrDmMPiX0TtmK_2VNcfy80p-chdq_jPo7kmb/pub?output=csv"

try: write_url = st.secrets["WRITE_URL"]
except: write_url = "https://script.google.com/macros/s/AKfycbxsuB36whQcXtjkTcBOX1Wyp4k1VPgR-4mOoNKlQHqcsN6ylewca9BALhfG0OKWW4JCOA/exec"

try: OWNER_PHONE = st.secrets["OWNER_PHONE"]
except: OWNER_PHONE = "7479584179"

fse_list = ["All Employees", "0690788829 - Ravindra Sharma", "0690903215 - Ravi Kumar", "0690881333 - Gopal Kumar Sahni","0691116975 - Shashank Shekhar Kumar","0691116972 - Nitish Kumar", 
            "0690373395 - Vikash Kumar", "0690499449 - Lal Babu Das", "0690452472 - Md Samim","0691116945 - Ankit Kumar","0691116911 - Nitish Kumar Soni", 
            "0690859418 - Sachin Kumar", "0690749611 - Premjeet Kumar","0691111278 - Ratnesh Kumar", 
            "0690093932 - Uttam Kumar Paswan", "068996776 - Sunil Kumar", "0690899815 - Munna Kumar","0690930677 - Mukesh Kumar","0691003801 - Md Prvez Alam"]

try: ADMIN_PWD = st.secrets["ADMIN_PASSWORD"]
except: ADMIN_PWD = "9557"

USER_CREDS = {"admin": {"pwd": ADMIN_PWD, "role": "admin", "fse": "All Employees"}}
for emp in fse_list:
    if "-" in emp: 
        emp_id = emp.split(" - ")[0].strip()
        try: emp_pwd = st.secrets[f"PWD_{emp_id}"]
        except: emp_pwd = emp_id[-4:]
        USER_CREDS[emp_id] = {"pwd": emp_pwd, "role": "staff", "fse": emp}

# ==========================================
# 3. SAFE STATE MANAGEMENT & AUDIT LOGS (KEYERROR FIX)
# ==========================================
def init_state(key, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value

init_state('logged_in', False)
init_state('cart', [])
init_state('pdf_viewer', "")
init_state('rep_viewer', "")
init_state('sales_pdf', "")
init_state('pos_ledger', []) 
init_state('last_pos_shop', "-- Select Shop --")
init_state('staff_last_date', date.today())
init_state('pos_last_date', date.today())
init_state('audit_logs', [])
init_state('mnp_schemes', [{"target": 1, "reward": "₹40"}, {"target": 2, "reward": "₹100"}, {"target": 3, "reward": "₹180"}, {"target": 5, "reward": "₹350"}])
init_state('scheme_start', date.today())
init_state('scheme_end', date.today())
init_state('show_popup', False)
init_state('popup_msg', "")
init_state('show_staff_popup', False)
init_state('staff_popup_msg', "")        
init_state('show_bill_popup', False)
init_state('bill_popup_msg', "")        
init_state('show_inv_popup', False)
init_state('inv_popup_msg', "")        

def add_audit_log(user, action):
    if 'audit_logs' not in st.session_state: st.session_state['audit_logs'] = []
    t_stamp = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    st.session_state['audit_logs'].insert(0, f"[{t_stamp}] {user}: {action}")

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

def get_odu_rate(w_odu):
    if w_odu >= 25: return 200, 40
    elif w_odu >= 10: return 150, 18
    elif w_odu >= 1: return 100, 15
    return 0, 0

def get_idu_rate(w_idu):
    if w_idu >= 25: return 150, 20
    elif w_idu >= 10: return 100, 15
    elif w_idu >= 1: return 50, 10
    return 0, 0

# 🟢 RECOVERY LOGIC - WEEKLY
def get_recovery_week(d):
    day = d.day
    if day <= 7: return 1
    elif day <= 14: return 2
    elif day <= 21: return 3
    else: return 4

def calculate_recovery_weekly(df_rec):
    if df_rec.empty: return pd.DataFrame()
    df_rec = df_rec.copy()
    df_rec['YearMonth'] = df_rec['dt_fixed'].dt.strftime('%Y-%m')
    df_rec['WeekNum'] = df_rec['dt_fixed'].apply(get_recovery_week)
    df_rec['WeekGroup'] = df_rec['YearMonth'] + "-W" + df_rec['WeekNum'].astype(str)
    
    results = []
    for (name, week), group in df_rec.groupby(['Recovered By', 'WeekGroup']):
        o_qty = group['ODU Qty'].sum()
        i_qty = group['IDU+STB Qty'].sum()
        o_rate = 100 if o_qty <= 9 else (150 if o_qty <= 24 else 200)
        o_gross = o_qty * o_rate
        o_comm = o_qty * 20
        i_rate = 50 if i_qty <= 9 else (100 if i_qty <= 24 else 150)
        i_gross = i_qty * i_rate
        i_comm = i_qty * 15
        
        t_gross = o_gross + i_gross
        t_tds = t_gross * 0.02
        t_comm = o_comm + i_comm
        t_net = t_gross - t_tds - t_comm
        
        results.append({
            "Agent": name, "Week": week, "ODU Count": o_qty, "IDU Count": i_qty,
            "ODU Rate": o_rate, "IDU Rate": i_rate, "Gross Payout": t_gross,
            "TDS (2%)": t_tds, "Commission": t_comm, "Net Payout": t_net
        })
    return pd.DataFrame(results)

# ==========================================
# 6. HTML PDF GENERATORS
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

def get_recovery_weekly_html(agent_name, sd, ed, weekly_df):
    if weekly_df.empty: return "<h2>No Data</h2>"
    t_odu = weekly_df['ODU Count'].sum(); t_idu = weekly_df['IDU Count'].sum(); t_net = weekly_df['Net Payout'].sum()
    rows_html = ""
    for idx, r in weekly_df.reset_index().iterrows():
        bg = "#ffffff" if idx % 2 == 0 else "#f8fafc"
        rows_html += f"<tr style='background:{bg};'><td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'>{idx+1}</td><td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'><b>{r['Week']}</b></td><td style='padding:10px; border:1px solid #e2e8f0; text-align:center; color:#1d4ed8;'>{r['ODU Count']}</td><td style='padding:10px; border:1px solid #e2e8f0; text-align:center; color:#be185d;'>{r['IDU Count']}</td><td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'>₹{r['ODU Rate']} / ₹{r['IDU Rate']}</td><td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'>₹{r['TDS (2%)']:,.1f}</td><td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'>₹{r['Commission']:,.1f}</td><td style='padding:10px; border:1px solid #e2e8f0; text-align:right; font-weight:bold; color:#0f172a;'>₹{r['Net Payout']:,.1f}</td></tr>"

    html = f"""
        <div style="font-family: Arial, sans-serif; background: #ffffff; padding: 20px; border-radius: 15px;">
            <div class="unbreak" style="text-align:center; border-bottom:4px solid #d97706; padding-bottom:15px; margin-bottom:20px;">
                <h1 style="margin:0; color:#d97706; font-size: 32px; font-weight: 900;">SANDHYA ENTERPRISES</h1>
                <p style="margin:5px 0; font-weight:bold; font-size: 16px; color: #333;">Device Recovery Weekly Payout</p>
            </div>
            <div class="unbreak" style="display:flex; justify-content:space-between; margin-bottom:25px; background: #fffbeb; padding: 15px; border-radius: 10px; border-left: 5px solid #d97706;">
                <div style="font-size: 16px;"><b>Recovery Agent:</b> <span style="color:#b45309;">{agent_name}</span></div>
                <div style="font-size: 16px;"><b>Period:</b> <span style="color:#b45309;">{sd.strftime('%d-%m-%Y')} to {ed.strftime('%d-%m-%Y')}</span></div>
            </div>
            <div class="unbreak" style="display:flex; justify-content:space-between; gap:10px; margin-bottom:25px; text-align:center;">
                <div style="background: #e0f2fe; padding:15px; border-radius:12px; flex:1; border:1px solid #93c5fd;"><b style="color:#1e3a8a;">Total ODU</b><br><span style="font-size:24px; font-weight:900; color:#1e3a8a;">{t_odu}</span></div>
                <div style="background: #fce7f3; padding:15px; border-radius:12px; flex:1; border:1px solid #f9a8d4;"><b style="color:#be185d;">Total IDU+STB</b><br><span style="font-size:24px; font-weight:900; color:#be185d;">{t_idu}</span></div>
                <div style="background: #dcfce7; padding:15px; border-radius:12px; flex:1; border:1px solid #86efac;"><b style="color:#166534;">Net Payout</b><br><span style="font-size:24px; font-weight:900; color:#166534;">₹{t_net:,.0f}</span></div>
            </div>
            <table style="width:100%; border-collapse:collapse; margin-bottom:30px; font-size: 12px;">
                <thead><tr style="background: #d97706; color:white;"><th style="padding:10px; border:1px solid #b45309;">#</th><th style="padding:10px; border:1px solid #b45309;">WEEK</th><th style="padding:10px; border:1px solid #b45309;">ODU</th><th style="padding:10px; border:1px solid #b45309;">IDU</th><th style="padding:10px; border:1px solid #b45309;">RATE</th><th style="padding:10px; border:1px solid #b45309;">TDS</th><th style="padding:10px; border:1px solid #b45309;">COMM</th><th style="padding:10px; border:1px solid #b45309;">NET PAYOUT</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    """
    return generate_html_viewer(html, f"Recovery_{agent_name}")

def get_red_project_detailed_slip_html(emp, sd, ed, processed_df, gross, ded, net):
    rows_html = ""
    for idx, r in processed_df.reset_index().iterrows():
        dt_val = r['Date'].strftime('%d-%m-%Y'); w_odu = r['Weekly_ODU']; w_idu = r['Weekly_IDU']
        w_count_str = f"<span style='color:#1d4ed8;'>O:{w_odu}</span><br><span style='color:#be185d;'>I:{w_idu}</span>"
        rows_html += f"<tr style='background:#f8fafc; border-bottom:1px solid #e2e8f0;'><td style='padding:8px; text-align:center;'>{idx+1}</td><td style='padding:8px;'>{dt_val}</td><td style='padding:8px; text-align:center; color:#1d4ed8;'><b>{r['ODU']}</b></td><td style='padding:8px; text-align:center; color:#be185d;'><b>{r['IDU+STB']}</b></td><td style='padding:8px; text-align:center;'>{w_count_str}</td><td style='padding:8px; text-align:center; color:#10b981;'>₹{r['Row_Gross']:,.0f}</td><td style='padding:8px; text-align:center; color:#dc2626;'>₹{r['Row_Net']:,.0f}</td></tr>"
        
    html = f"""
        <div style="font-family: Arial, sans-serif; background: #ffffff; padding: 20px; border-radius: 15px;">
            <div class="unbreak" style="text-align:center; border-bottom:4px solid #dc2626; padding-bottom:15px; margin-bottom:20px;">
                <h1 style="margin:0; color:#dc2626; font-size: 32px;">SANDHYA ENTERPRISES</h1><p>Red Project Weekly Payout</p>
            </div>
            <table style="width:100%; border-collapse:collapse; margin-bottom:30px; font-size: 12px;">
                <thead><tr style="background: #dc2626; color:white;"><th style="padding:10px;">#</th><th style="padding:10px;">DATE</th><th style="padding:10px;">ODU</th><th style="padding:10px;">IDU</th><th style="padding:10px;">WEEK TOTAL</th><th style="padding:10px;">GROSS</th><th style="padding:10px;">NET</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            <div class="unbreak" style="background: #f1f5f9; border: 2px solid #cbd5e1; padding:20px; border-radius:15px; display:flex; justify-content:space-between; align-items:center;">
                <div><span style="color:#64748b;">Gross Payout</span><br><span style="font-size:22px; font-weight:900; color:#10b981;">₹{gross:,.2f}</span></div>
                <div><span style="color:#64748b;">Deduction</span><br><span style="font-size:22px; font-weight:900; color:#ef4444;">- ₹{ded:,.2f}</span></div>
                <div style="text-align:right;"><span style="color:#0f172a; font-weight: 900;">NET PAYABLE</span><br><span style="font-size:32px; font-weight:900; color:#dc2626;">₹{net:,.2f}</span></div>
            </div>
        </div>
    """
    return generate_html_viewer(html, f"RedProject_{emp.replace(' ','_')}")

def get_payroll_html(emp, sd, ed, stats, df_rows, earn, cash, ded, is_fib, sim_bal):
    net = earn + cash - ded
    sim_box = "" if is_fib else f'<div class="unbreak" style="background: #fef08a; padding:15px; border-radius:12px; margin-bottom:20px; text-align:center; border:1px solid #facc15;"><span style="font-size:18px; font-weight:bold; color:#854d0e;">📦 Remaining SIM Balance: <span style="font-size:26px; background: white; padding: 2px 10px; border-radius: 6px;">{sim_bal}</span></span></div>'
    cards = f'<div class="unbreak" style="display:flex; justify-content:center; gap:20px; margin-bottom:25px;"><div style="background: #e0f2fe; padding:15px; border-radius:12px; border:1px solid #93c5fd; text-align:center;"><b>INSTALLATIONS</b><br><span style="font-size:26px; font-weight:900; color:#1d4ed8;">{stats["INS"]}</span></div><div style="background: #f3e8ff; padding:15px; border-radius:12px; border:1px solid #c4b5fd; text-align:center;"><b>SERVICE (SR)</b><br><span style="font-size:26px; font-weight:900; color:#6d28d9;">{stats["SR"]}</span></div></div>' if is_fib else f'<div class="unbreak" style="display:flex; justify-content:space-between; gap:15px; margin-bottom:25px;"><div style="background: #e0f2fe; padding:15px 10px; border-radius:12px; flex:1; text-align:center; border:1px solid #93c5fd;"><b>MNP</b><br><span style="font-size:24px; font-weight:900; color:#1d4ed8;">{stats["MNP"]}</span></div><div style="background: #fce7f3; padding:15px 10px; border-radius:12px; flex:1; text-align:center; border:1px solid #f9a8d4;"><b>FR 349</b><br><span style="font-size:24px; font-weight:900; color:#be185d;">{stats["FR349"]}</span></div><div style="background: #dcfce7; padding:15px 10px; border-radius:12px; flex:1; text-align:center; border:1px solid #86efac;"><b>FR 123</b><br><span style="font-size:24px; font-weight:900; color:#15803d;">{stats["FR123"]}</span></div></div>'
    
    rows_html = ""
    for idx, r in df_rows.reset_index().iterrows():
        amt = float(r.iloc[11]); clr = "#166534" if amt > 0 else ("#ef4444" if amt < 0 else "#333333")
        rows_html += f"<tr style='background: #ffffff;'><td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'>{idx+1}</td><td style='padding:10px; border:1px solid #e2e8f0;'>{r.iloc[0]}</td><td style='padding:10px; border:1px solid #e2e8f0;'><b>{r.iloc[2]}</b></td><td style='padding:10px; border:1px solid #e2e8f0; font-size:12px; color:#64748b;'>{r.iloc[3]}</td><td style='padding:10px; border:1px solid #e2e8f0; text-align:right; font-weight:bold; color:{clr};'>₹{amt:,.2f}</td></tr>"

    html = f"""
        <div style="font-family: Arial, sans-serif; background: #ffffff; border-radius: 15px;">
            <div class="unbreak" style="text-align:center; border-bottom:4px solid #004a99; padding-bottom:15px; margin-bottom:20px;">
                <h1 style="margin:0; color:#004a99; font-size: 32px;">SANDHYA ENTERPRISES</h1><p>Official Payroll Settlement Slip</p>
            </div>
            <div class="unbreak" style="display:flex; justify-content:space-between; margin-bottom:25px; background: #f8fafc; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99;">
                <div><b>Employee:</b> <span style="color:#004a99;">{emp}</span></div><div><b>Period:</b> <span style="color:#004a99;">{sd} to {ed}</span></div>
            </div>
            {sim_box} {cards}
            <table style="width:100%; border-collapse:collapse; margin-bottom:30px; font-size: 14px;">
                <thead><tr style="background: #004a99; color:white;"><th style="padding:10px;">#</th><th style="padding:10px; text-align:left;">DATE</th><th style="padding:10px; text-align:left;">ACTIVITY</th><th style="padding:10px; text-align:left;">REMARK</th><th style="padding:10px; text-align:right;">AMOUNT</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            <div class="unbreak">
                <div style="background: #f1f5f9; border: 2px solid #cbd5e1; padding:25px; border-radius:15px; display:flex; justify-content:space-between; align-items:center;">
                    <div><span style="color:#64748b;">Earnings (+ Cash)</span><br><span style="font-size:22px; font-weight:900; color:#10b981;">₹{earn + cash:,.2f}</span></div>
                    <div><span style="color:#64748b;">Deductions (SIM/Adv)</span><br><span style="font-size:22px; font-weight:900; color:#ef4444;">- ₹{ded:,.2f}</span></div>
                    <div style="text-align:right;"><span style="color:#0f172a; font-weight: 900;">NET PAYABLE</span><br><span style="font-size:32px; font-weight:900; color:#004a99;">₹{net:,.2f}</span></div>
                </div>
            </div>
        </div>
    """
    return generate_html_viewer(html, f"Payroll_{emp.replace(' ','_')}")

def get_calendar_html(emp, sd, ed, stats, df_rows, earn, cash, ded):
    try: date_range = pd.date_range(start=sd, end=ed)
    except: return "Invalid Dates"
    net = earn + cash - ded
    
    top_boxes = f"""
    <div style="display:flex; justify-content:space-between; gap:10px; margin-bottom:25px; flex-wrap:wrap;">
        <div style="flex:1; background: linear-gradient(135deg, #3b82f6, #2563eb); padding:10px; border-radius:12px; text-align:center; color:white;">
            <div style="font-size:12px;">Total MNP</div><div style="font-size:24px; font-weight:900;">{stats.get('MNP', 0)}</div>
        </div>
        <div style="flex:1; background: linear-gradient(135deg, #ec4899, #db2777); padding:10px; border-radius:12px; text-align:center; color:white;">
            <div style="font-size:12px;">Total SIM</div><div style="font-size:24px; font-weight:900;">{stats.get('FR349', 0) + stats.get('FR123', 0) + stats.get('FR152', 0)}</div>
        </div>
        <div style="flex:1; background: linear-gradient(135deg, #f59e0b, #d97706); padding:10px; border-radius:12px; text-align:center; color:white;">
            <div style="font-size:12px;">Net Payable</div><div style="font-size:24px; font-weight:900;">₹{net:,.0f}</div>
        </div>
    </div>
    """
        
    cal_html = "<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; width: 100%;'>"
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        cal_html += f"<div style='text-align:center; font-weight:bold; background: linear-gradient(90deg, #004a99, #0066cc); color:white; padding:10px; border-radius:8px;'>{day}</div>"
    
    for _ in range(date_range[0].weekday()): cal_html += "<div style='background:#f8fafc; border-radius:8px; min-height:110px; border:1px dashed #cbd5e1;'></div>"
    
    for single_date in date_range:
        day_data = df_rows[df_rows['dt_fixed'].dt.date == single_date.date()]
        items_html = ""; bg_color = "#ffffff"; border_color = "#cbd5e1"
        if not day_data.empty:
            bg_color = "#f0fdf4"; border_color = "#86efac"
            day_mnp, day_sim, day_ins, day_sr, day_adv = 0, 0, 0, 0, 0.0
            for _, r in day_data.iterrows():
                act = str(r.iloc[2]).upper(); tech_str = str(r.iloc[3]).upper(); amt = float(r.iloc[11])
                if "ISSUE" in act or "STOCK" in act: continue
                qty = 1; m = re.search(r'QTY\s*:?\s*(\d+)', tech_str)
                if m: qty = int(m.group(1))
                if "MNP" in act: day_mnp += qty
                elif "SIM" in act or "FR" in act: day_sim += qty
                elif "INSTALL" in act: day_ins += qty
                elif "SR" in act: day_sr += qty
                elif "PAY" in act or "ADVANCE" in act: day_adv += abs(amt)
            
            if day_mnp > 0: items_html += f"<div style='font-size:11px; color:#1d4ed8; font-weight:bold;'>🔵 MNP: {day_mnp}</div>"
            if day_sim > 0: items_html += f"<div style='font-size:11px; color:#be185d; font-weight:bold;'>🔴 SIM: {day_sim}</div>"
            if day_ins > 0: items_html += f"<div style='font-size:11px; color:#047857; font-weight:bold;'>🟢 INS: {day_ins}</div>"
            if day_sr > 0: items_html += f"<div style='font-size:11px; color:#6d28d9; font-weight:bold;'>🟣 SR: {day_sr}</div>"
            if day_adv > 0: items_html += f"<div style='font-size:11px; color:#b91c1c; font-weight:bold;'>💸 Adv: ₹{day_adv:,.0f}</div>"
                
        cal_html += f"<div class='unbreak' style='background:{bg_color}; border:2px solid {border_color}; border-radius:10px; padding:8px; height:110px;'><div style='font-weight:900; text-align:right;'>{single_date.day}</div><div>{items_html}</div></div>"
    cal_html += "</div>"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; background: #ffffff; padding: 20px; border-radius: 15px;">
        <div class="unbreak" style="text-align:center; border-bottom:4px solid #004a99; padding-bottom:15px; margin-bottom:20px;">
            <h1 style="margin:0; color:#004a99; font-size: 28px;">SANDHYA ENTERPRISES</h1><p>Employee Calendar Work Report</p>
        </div>
        <div class="unbreak" style="display:flex; justify-content:space-between; margin-bottom:25px; background: #f8fafc; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99;">
            <div><b>Employee:</b> <span style="color:#004a99;">{emp}</span></div><div><b>Period:</b> <span style="color:#004a99;">{sd.strftime('%d-%m-%Y')} to {ed.strftime('%d-%m-%Y')}</span></div>
        </div>
        {top_boxes} {cal_html}
    </div>
    """
    return generate_html_viewer(html, f"Calendar_{emp.replace(' ','_')}")

# ==========================================
# 6. APPLICATION LOGIN & INTERFACE LOGIC
# ==========================================
logged_in_state = st.session_state.get('logged_in', False)

if not logged_in_state:
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
            if u_sel_display == "👑 Admin" and u_pwd == USER_CREDS["admin"]["pwd"]:
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
    # 🟢 SAFE SESSION RETRIEVALS
    current_role = st.session_state.get('role', 'staff')
    current_fse = st.session_state.get('fse_name', 'Guest')
    
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
            <p style="font-size: 16px; color: #333;">{st.session_state.get('popup_msg', 'Data saved.')}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("❌ CLOSE", type="primary", use_container_width=True):
            st.session_state['show_popup'] = False; st.rerun()
        st.stop()

    # --- TOP NAVIGATION & BRANDING ---
    nav_c1, nav_c2, nav_c3 = st.columns([2, 1, 1])
    nav_c1.markdown(f"### 🏢 Sandhya ERP | Active: **{current_fse.split('-')[-1]}**")
    if nav_c2.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()
    if nav_c3.button("🚪 Logout", use_container_width=True): st.session_state.clear(); st.rerun()

    df_h = load_db()
    df_p = load_products()

    # TABS ALLOCATION
    if current_role == 'admin':
        tabs = st.tabs(["📊 1. LIVE KPI & PROFIT", "🛒 2. POS BILLING & SCANNER", "👷 3. EMPLOYEE MGT", "📦 4. INVENTORY CONTROL", "📈 5. SALES ANALYTICS", "⚠️ 6. PAYMENT RECOVERY", "🔥 7. MNP SCHEMES", "💰 8. CASH COLLECTION", "🔴 9. RED PROJECT", "🕵️ 10. AUDIT LOGS"])
    else:
        tabs = st.tabs(["👷 MY PERFORMANCE", "🛒 QUICK BILLING", "⚠️ RECOVERY ENTRY"])

    # ==========================================
    # 📊 TAB 1: LIVE KPI & PROFIT DASHBOARD (Priority 1)
    # ==========================================
    if current_role == 'admin':
        with tabs[0]:
            st.subheader("📈 Real-Time Business Performance Dashboard")
            
            today_date_str = date.today().strftime("%d-%m-%Y")
            today_df = df_h[df_h['dt_fixed'].dt.date == date.today()] if not df_h.empty else pd.DataFrame()
            
            today_sale = 0.0; today_cost = 0.0; today_profit = 0.0
            
            for _, r in today_df.iterrows():
                tech = parse_tech(r.iloc[3], fallback_total=float(r.iloc[11]) if pd.notna(r.iloc[11]) else 0.0)
                if "Inv: SE-" in tech["Inv"]:
                    s_amt = float(r.iloc[11])
                    c_amt = tech["Cost"] * tech["Qty"]
                    today_sale += s_amt
                    today_cost += c_amt
                    today_profit += (s_amt - c_amt)

            # Monthly Sales
            curr_month_df = df_h[df_h['dt_fixed'].dt.month == date.today().month] if not df_h.empty else pd.DataFrame()
            month_sale = curr_month_df.iloc[:, 11].sum() if not curr_month_df.empty else 0.0

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.markdown(f'<div class="kpi-card"><div class="kpi-title">Today\'s Sale</div><div class="kpi-value" style="color:#2563eb;">₹{today_sale:,.0f}</div><div class="kpi-sub">Cost: ₹{today_cost:,.0f}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="kpi-card"><div class="kpi-title">Today\'s Profit</div><div class="kpi-value" style="color:#16a34a;">₹{today_profit:,.0f}</div><div class="kpi-sub">Net Margin</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="kpi-card"><div class="kpi-title">Monthly Sales</div><div class="kpi-value" style="color:#0f172a;">₹{month_sale:,.0f}</div><div class="kpi-sub">This Month</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="kpi-card"><div class="kpi-title">Active Staff</div><div class="kpi-value" style="color:#0891b2;">{len(fse_list)-1} Staff</div><div class="kpi-sub">On Roster</div></div>', unsafe_allow_html=True)
            k5.markdown(f'<div class="kpi-card"><div class="kpi-title">Low Stock Alert</div><div class="kpi-value" style="color:#dc2626;">Check Tab 4</div><div class="kpi-sub">Stock Re-order</div></div>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 🤖 Sandhya AI Business Assistant")
            ai_query = st.text_input("Ask AI Assistant (e.g. 'Profit status', 'Today sales'):")
            if ai_query:
                q_lower = ai_query.lower()
                if "profit" in q_lower: st.success(f"🤖 **AI Answer:** आज का कुल नेट प्रॉफिट **₹{today_profit:,.2f}** है।")
                elif "sale" in q_lower: st.success(f"🤖 **AI Answer:** आज की कुल बिक्री **₹{today_sale:,.2f}** है।")
                else: st.info("🤖 **AI Answer:** मैं आपके स्टोर के डेटा का विश्लेषण कर रहा हूँ। अधिक सटीक जानकारी के लिए Profit या Sale टाइप करें।")

    # ==========================================
    # 🛒 TAB 2: SMART BILLING & BARCODE SEARCH (Priority 1 & 2)
    # ==========================================
    pos_tab = tabs[1] if current_role == 'admin' else tabs[1]
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
                    cart_data = st.session_state.get('cart', [])
                    cart_data.append({"Item": p_name, "Rate": p_rate, "Qty": b_qty, "Disc": b_disc, "Cost": p_cost, "IMEI": "N/A", "Wrnty": "1 Year", "Total": tot})
                    st.session_state['cart'] = cart_data
                    add_audit_log(current_fse, f"Added {p_name} to cart (Qty: {b_qty})")
                    st.success(f"{p_name} added to cart!")

        cart_list = st.session_state.get('cart', [])
        if cart_list:
            st.write("---")
            st.write("### 🛒 Active Cart")
            st.table(pd.DataFrame(cart_list)[["Item", "Rate", "Qty", "Total"]])
            grand_t = sum(i['Total'] for i in cart_list)
            tot_d = sum(i['Disc'] for i in cart_list)
            
            st.markdown(f"### Grand Total: **₹{grand_t:,.2f}**")
            
            p1, p2, p3 = st.columns(3)
            csh = p1.number_input("Cash Received (₹)", value=grand_t)
            onl = p2.number_input("Online Received (₹)", value=0.0)
            due_v = grand_t - (csh + onl)
            p3.markdown(f"**Due (बाकी):** <span style='color:red; font-size:18px;'>₹{due_v:,.2f}</span>", unsafe_allow_html=True)
            
            if st.button("💾 SAVE & GENERATE INVOICE", type="primary", use_container_width=True):
                inv_id = f"SE-{int(time.time())%100000}"
                rows_h = ""
                for i in cart_list:
                    tech = f"Inv: {inv_id} | Item: {i['Item']} | Rate: {i['Rate']} | Qty: {i['Qty']} | Disc: {i['Disc']} | Cost: {i['Cost']} | Pay: C={csh},O={onl},D={due_v} | Addr: {ca}"
                    requests.post(write_url, json={"date": date.today().strftime("%d-%m-%Y"), "fse": cn, "activity_boy": cm, "tech": tech, "total": i['Total']})
                    rows_h += f"<tr><td style='padding:5px;'>{i['Item']}</td><td style='padding:5px; text-align:center;'>{i['Rate']}</td><td style='padding:5px; text-align:center;'>{i['Qty']}</td><td style='padding:5px; text-align:right;'>{i['Total']}</td></tr>"
                
                add_audit_log(current_fse, f"Generated Invoice {inv_id} for ₹{grand_t}")
                st.session_state['pdf_viewer'] = get_invoice_html(cn, cm, ca, inv_id, date.today().strftime("%d/%m/%Y"), rows_h, grand_t, tot_d, csh, onl, 0.0, due_v, num_to_words(grand_t))
                
                if cm:
                    wa_msg = f"🏢 *SANDHYA ENTERPRISES TAX INVOICE*\nInvoice No: {inv_id}\nCustomer: {cn}\nTotal Bill: ₹{grand_t}\nThank you for visiting!"
                    encoded_wa = requests.utils.quote(wa_msg)
                    st.markdown(f'<a href="https://wa.me/91{cm}?text={encoded_wa}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; width:100%; font-weight:bold;">💬 SEND INVOICE ON WHATSAPP</button></a>', unsafe_allow_html=True)
                
                st.session_state['cart'] = []
                st.rerun()

    # ==========================================
    # ⚠️ TAB 6: PAYMENT RECOVERY & REMINDERS (Priority 2)
    # ==========================================
    if current_role == 'admin':
        with tabs[5]:
            st.subheader("⚠️ Payment Recovery & Automatic WhatsApp Reminders")
            st.info("यहाँ उन बकायेदारों की लिस्ट है जिनका पेमेंट बाकी है।")
            
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
    if current_role == 'admin':
        with tabs[9]:
            st.subheader("🕵️ System Security & Audit Log History")
            st.info("यह ब्लैक-बॉक्स ट्रैकर दिखाता है कि किस कर्मचारी ने किस समय क्या एक्शन लिया है।")
            log_list = st.session_state.get('audit_logs', [])
            if log_list:
                st.markdown(f'<div class="audit-box">{"<br>".join(log_list)}</div>', unsafe_allow_html=True)
            else:
                st.caption("No system activity logged in this session yet.")
