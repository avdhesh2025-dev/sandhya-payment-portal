import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta
import time
import re
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIG & STYLES (PROFESSIONAL & A4 FULL SCREEN)
# ==========================================
st.set_page_config(page_title="Sandhya Enterprises Mega ERP", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# 🟢 TAGRA ZOOM LOCK & ADVANCED KEYBOARD CONTROLS (NUKED ZOOM)
components.html(
    """
    <script>
        var parentDoc = window.parent.document;
        
        // 1. Block Zooming Completely
        var meta = parentDoc.querySelector('meta[name="viewport"]');
        var viewportContent = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=0, viewport-fit=cover';
        if (meta) {
            meta.content = viewportContent;
        } else {
            var newMeta = parentDoc.createElement('meta');
            newMeta.name = 'viewport';
            newMeta.content = viewportContent;
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

        // 2. 🟢 ULTIMATE FIX FOR QTY/AMOUNT/PASSWORD ZOOM & KEYBOARDS
        function fixMobileInputs() {
            var allInputs = parentDoc.querySelectorAll('input, textarea, select');
            allInputs.forEach(function(inp) {
                inp.style.setProperty('font-size', '16px', 'important');
            });

            var dateInputs = parentDoc.querySelectorAll('.stDateInput input');
            dateInputs.forEach(function(input) {
                input.setAttribute('readonly', 'readonly');
                input.setAttribute('inputmode', 'none'); 
            });

            var selectInputs = parentDoc.querySelectorAll('div[data-baseweb="select"] input');
            selectInputs.forEach(function(input) {
                input.setAttribute('readonly', 'readonly');
                input.setAttribute('inputmode', 'none');
            });

            var numberInputs = parentDoc.querySelectorAll('input[type="number"], .stNumberInput input');
            numberInputs.forEach(function(input) {
                input.setAttribute('inputmode', 'decimal');
                input.setAttribute('pattern', '[0-9]*');
            });

            var pwdInputs = parentDoc.querySelectorAll('input[type="password"]');
            pwdInputs.forEach(function(input) {
                input.setAttribute('inputmode', 'numeric');
                input.setAttribute('pattern', '[0-9]*');
            });
        }
        setInterval(fixMobileInputs, 400);
    </script>
    """, height=0, width=0
)

st.markdown("""
    <style>
    /* 🟢 CLEAN APP FEEL (FREEZE SCREEN) */
    html, body, .stApp, .main { 
        touch-action: manipulation !important; 
        -webkit-text-size-adjust: 100% !important; 
        background-color: #f4f7fb !important; 
    }
    
    /* SIDEBAR HIDE COMPLETELY */
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    
    /* 🟢 DESKTOP FULL WIDTH VIEW (FIXED A4 SHRINK ISSUE) */
    .block-container {
        background-color: #ffffff !important;
        max-width: 98% !important;
        padding: 30px 20px !important;
        margin: 20px auto !important;
        border-radius: 12px !important;
        box-shadow: 0px 5px 20px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* FULL SCREEN FIX FOR MOBILE */
    @media screen and (max-width: 768px) {
        .block-container {
            margin: 10px auto !important;
            padding: 15px !important;
            border-radius: 8px !important;
            max-width: 98% !important;
            box-shadow: none !important;
        }
    }
    
    /* 🟢 ONLY ADD FONT-SIZE 16px TO STOP ZOOM, KEEPING ORIGINAL LOOK */
    input, input[type="text"], input[type="number"], input[type="tel"], input[type="date"], select, textarea,
    [data-testid="stNumberInput"] input,
    div[data-baseweb="input"] input, 
    div[data-baseweb="select"] div, 
    div[data-baseweb="select"] span, 
    .stDateInput input, 
    .stTextArea textarea {
        font-size: 16px !important;
        touch-action: manipulation !important;
    }
    
    /* 🟢 NEW HIGHLIGHT FEATURE: ACTIVE BOX GREEN COLOR CHANGE */
    input:focus, textarea:focus, div[data-baseweb="select"]:focus-within {
        background-color: #dcfce7 !important;
        border: 2px solid #16a34a !important;
        color: #000 !important;
        font-weight: bold !important;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 0 10px rgba(22, 163, 74, 0.5) !important;
    }
    [data-testid="stDataEditor"] input {
        background-color: #dcfce7 !important;
        color: #000 !important;
        font-weight: bold !important;
        border: 2px solid #16a34a !important;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.1) !important;
    }

    .login-box {
        background: linear-gradient(145deg, #ffffff, #e6f2ff);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0, 74, 153, 0.1);
        text-align: center;
        border-top: 5px solid #004a99;
        max-width: 450px;
        margin: 0 auto;
    }
    
    .nav-box {
        background: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        text-align: center;
        font-weight: bold;
        color: #004a99;
        font-size: 16px;
    }

    .header-box { background: linear-gradient(135deg, #004a99, #0066cc); padding: 25px 15px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #f8fafc; padding: 10px; border-radius: 10px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); flex-wrap: wrap;}
    .stTabs [data-baseweb="tab"] { color: #0f2027; border-radius: 8px; padding: 10px 15px; font-weight: bold; transition: all 0.3s; font-size: 14px;}
    .stTabs [aria-selected="true"] { background: linear-gradient(90deg, #004a99, #0066cc) !important; color: white !important; box-shadow: 0 4px 10px rgba(0,74,153,0.2) !important;}
    .metric-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; border-top: 4px solid #004a99; }
    div.stRadio > div { background: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CREDENTIALS & URLS (NEW URL ADDED HERE)
# ==========================================
try: products_url = st.secrets["PRODUCTS_URL"]
except: products_url = "https://docs.google.com/spreadsheets/d/1K3ZeUuZbpB3FmUQlt2ryri_3su4EkLOqzS7uxUQYd1Y/gviz/tq?tqx=out:csv&sheet=Products"

try: base_read_url = st.secrets["BASE_READ_URL"]
except: base_read_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSXrwSrOi_A8LxQShziA5LkyX1_WRdp7jiSLoJadXbMmrDmMPiX0TtmK_2VNcfy80p-chdq_jPo7kmb/pub?output=csv"

try: write_url = st.secrets["WRITE_URL"]
except: write_url = "https://script.google.com/macros/s/AKfycbxsuB36whQcXtjkTcBOX1Wyp4k1VPgR-4mOoNKlQHqcsN6ylewca9BALhfG0OKWW4JCOA/exec"


fse_list = ["All Employees", "0690788829 - Ravindra Sharma", "0690903215 - Ravi Kumar", "0690881333 - Gopal Kumar Sahni","0691116975 - Shashank Shekhar Kumar","0691116972 - Nitish Kumar", 
            "0690373395 - Vikash Kumar", "0690499449 - Lal Babu Das", "0690452472 - Md Samim","0691116945 - Ankit Kumar","0691116911 - Nitish Kumar Soni", 
            "0690859418 - Sachin Kumar", "0690749611 - Premjeet Kumar","0691111278 - Ratnesh Kumar", 
            "0690093932 - Uttam Kumar Paswan", "068996776 - Sunil Kumar", "0690899815 - Munna Kumar","0690930677 - Mukesh Kumar","0691003801 - Md Prvez Alam"]

USER_CREDS = {"admin": {"pwd": "9557", "role": "admin", "fse": "All Employees"}}
for emp in fse_list:
    if "-" in emp: 
        emp_id = emp.split(" - ")[0].strip()
        USER_CREDS[emp_id] = {"pwd": emp_id[-4:], "role": "staff", "fse": emp}

# ==========================================
# 3. SESSION STATE
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
# 4. NUMBER TO WORDS LOGIC
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

# ==========================================
# 5. DATA LOADERS & PARSERS
# ==========================================
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
            "Agent": name,
            "Week": week,
            "ODU Count": o_qty,
            "IDU Count": i_qty,
            "ODU Rate": o_rate,
            "IDU Rate": i_rate,
            "Gross Payout": t_gross,
            "TDS (2%)": t_tds,
            "Commission": t_comm,
            "Net Payout": t_net
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
    
    t_odu = weekly_df['ODU Count'].sum()
    t_idu = weekly_df['IDU Count'].sum()
    t_net = weekly_df['Net Payout'].sum()
    
    rows_html = ""
    idx = 1
    for _, r in weekly_df.iterrows():
        bg = "#ffffff" if idx % 2 == 0 else "#f8fafc"
        rows_html += f"""
        <tr style='background:{bg};'>
            <td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'>{idx}</td>
            <td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'><b>{r['Week']}</b></td>
            <td style='padding:10px; border:1px solid #e2e8f0; text-align:center; color:#1d4ed8;'>{r['ODU Count']}</td>
            <td style='padding:10px; border:1px solid #e2e8f0; text-align:center; color:#be185d;'>{r['IDU Count']}</td>
            <td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'>₹{r['ODU Rate']} / ₹{r['IDU Rate']}</td>
            <td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'>₹{r['TDS (2%)']:,.1f}</td>
            <td style='padding:10px; border:1px solid #e2e8f0; text-align:center;'>₹{r['Commission']:,.1f}</td>
            <td style='padding:10px; border:1px solid #e2e8f0; text-align:right; font-weight:bold; color:#0f172a;'>₹{r['Net Payout']:,.1f}</td>
        </tr>
        """
        idx += 1

    html = f"""
        <div style="font-family: Arial, sans-serif; background: #ffffff; padding: 20px; border-radius: 15px;">
            <div class="unbreak" style="text-align:center; border-bottom:4px solid #d97706; padding-bottom:15px; margin-bottom:20px;">
                <h1 style="margin:0; color:#d97706; font-size: 32px; font-weight: 900; letter-spacing: 1px;">SANDHYA ENTERPRISES</h1>
                <p style="margin:5px 0; font-weight:bold; font-size: 16px; color: #333;">Device Recovery Weekly Payout</p>
                <p style="margin:0; font-size:13px; color:#64748b; text-transform: uppercase; letter-spacing: 2px;">Official Settlement Slip</p>
            </div>
            
            <div class="unbreak" style="display:flex; justify-content:space-between; margin-bottom:25px; background: #fffbeb; padding: 15px; border-radius: 10px; border-left: 5px solid #d97706;">
                <div style="font-size: 16px;"><b>Recovery Agent:</b> <span style="color:#b45309;">{agent_name}</span></div>
                <div style="font-size: 16px;"><b>Period:</b> <span style="color:#b45309;">{sd.strftime('%d-%m-%Y')} to {ed.strftime('%d-%m-%Y')}</span></div>
            </div>
            
            <div class="unbreak" style="display:flex; justify-content:space-between; gap:10px; margin-bottom:25px; text-align:center;">
                <div style="background: #e0f2fe; padding:15px; border-radius:12px; flex:1; border:1px solid #93c5fd;">
                    <b style="color:#1e3a8a; font-size:14px;">Total ODU</b><br>
                    <span style="font-size:24px; font-weight:900; color:#1e3a8a;">{t_odu}</span>
                </div>
                <div style="background: #fce7f3; padding:15px; border-radius:12px; flex:1; border:1px solid #f9a8d4;">
                    <b style="color:#be185d; font-size:14px;">Total IDU+STB</b><br>
                    <span style="font-size:24px; font-weight:900; color:#be185d;">{t_idu}</span>
                </div>
                <div style="background: #dcfce7; padding:15px; border-radius:12px; flex:1; border:1px solid #86efac;">
                    <b style="color:#166534; font-size:14px;">Final Net Payout</b><br>
                    <span style="font-size:24px; font-weight:900; color:#166534;">₹{t_net:,.0f}</span>
                </div>
            </div>
            
            <table style="width:100%; border-collapse:collapse; margin-bottom:30px; font-size: 12px;">
                <thead>
                    <tr style="background: #d97706; color:white;">
                        <th style="padding:10px; border:1px solid #b45309;">#</th>
                        <th style="padding:10px; border:1px solid #b45309;">WEEK</th>
                        <th style="padding:10px; border:1px solid #b45309;">ODU</th>
                        <th style="padding:10px; border:1px solid #b45309;">IDU</th>
                        <th style="padding:10px; border:1px solid #b45309;">RATE (O/I)</th>
                        <th style="padding:10px; border:1px solid #b45309;">TDS (-2%)</th>
                        <th style="padding:10px; border:1px solid #b45309;">COMM (-₹20/15)</th>
                        <th style="padding:10px; border:1px solid #b45309;">NET PAYOUT</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            
            <div class="unbreak">
                <div style="margin-top:60px; display:flex; justify-content:space-between; font-size:14px; color:#475569; font-weight: bold;">
                    <div style="border-top:2px dashed #94a3b8; width:200px; text-align:center; padding-top:10px;">Agent Signature</div>
                    <div style="border-top:2px dashed #94a3b8; width:200px; text-align:center; padding-top:10px;">Authorised Signatory</div>
                </div>
            </div>
        </div>
    """
    return generate_html_viewer(html, f"Recovery_Payout_{agent_name.replace(' ','_')}")

def get_red_project_history_slip_html(emp, save_date, odu_tot, idu_tot, o_rate, o_ded, i_rate, i_ded, gross, ded, net):
    html = f"""
        <div style="font-family: Arial, sans-serif; background: #ffffff; padding: 20px; border-radius: 15px;">
            <div class="unbreak" style="text-align:center; border-bottom:4px solid #dc2626; padding-bottom:15px; margin-bottom:20px;">
                <h1 style="margin:0; color:#dc2626; font-size: 32px; font-weight: 900; letter-spacing: 1px;">SANDHYA ENTERPRISES</h1>
                <p style="margin:5px 0; font-weight:bold; font-size: 16px; color: #333;">Red Project Payout Slip (Duplicate/History)</p>
                <p style="margin:0; font-size:13px; color:#64748b; text-transform: uppercase; letter-spacing: 2px;">Official Settlement - Processed on {save_date}</p>
            </div>
            
            <div class="unbreak" style="display:flex; justify-content:space-between; margin-bottom:25px; background: #fef2f2; padding: 15px; border-radius: 10px; border-left: 5px solid #dc2626;">
                <div style="font-size: 16px;"><b>Employee:</b> <span style="color:#b91c1c;">{emp}</span></div>
                <div style="font-size: 16px;"><b>Record Date:</b> <span style="color:#b91c1c;">{save_date}</span></div>
            </div>
            
            <div class="unbreak" style="display:flex; justify-content:space-between; gap:15px; margin-bottom:25px;">
                <div style="background: #e0f2fe; padding:15px 10px; border-radius:12px; flex:1; text-align:center; border:1px solid #93c5fd;"><b>Total ODU</b><br><span style="font-size:24px; font-weight:900; color:#1d4ed8;">{odu_tot}</span><br><small style="color:#64748b;">(Rate: ₹{o_rate} | Ded: ₹{o_ded})</small></div>
                <div style="background: #fce7f3; padding:15px 10px; border-radius:12px; flex:1; text-align:center; border:1px solid #f9a8d4;"><b>Total IDU+STB</b><br><span style="font-size:24px; font-weight:900; color:#be185d;">{idu_tot}</span><br><small style="color:#64748b;">(Rate: ₹{i_rate} | Ded: ₹{i_ded})</small></div>
            </div>
            
            <div class="unbreak">
                <div style="background: #f1f5f9; border: 2px solid #cbd5e1; padding:25px; border-radius:15px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="text-align: left;">
                        <span style="color:#64748b; font-size: 14px; font-weight: bold; text-transform: uppercase;">Gross Payout</span><br>
                        <span style="font-size:22px; font-weight:900; color:#10b981;">₹{gross:,.2f}</span>
                    </div>
                    <div style="text-align:center; position: relative;">
                        <div style="position: absolute; left: -30px; top: 10px; width: 2px; height: 40px; background: #cbd5e1;"></div>
                        <span style="color:#64748b; font-size: 14px; font-weight: bold; text-transform: uppercase;">Company Deduction</span><br>
                        <span style="font-size:22px; font-weight:900; color:#ef4444;">- ₹{ded:,.2f}</span>
                        <div style="position: absolute; right: -30px; top: 10px; width: 2px; height: 40px; background: #cbd5e1;"></div>
                    </div>
                    <div style="text-align:right;">
                        <span style="color:#0f172a; font-size: 16px; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">NET PAYABLE</span><br>
                        <span style="font-size:36px; font-weight:900; color:#dc2626;">₹{net:,.2f}</span>
                    </div>
                </div>
            </div>
            
            <div class="unbreak">
                <div style="margin-top:60px; display:flex; justify-content:space-between; font-size:14px; color:#475569; font-weight: bold;">
                    <div style="border-top:2px dashed #94a3b8; width:200px; text-align:center; padding-top:10px;">Employee Signature</div>
                    <div style="border-top:2px dashed #94a3b8; width:200px; text-align:center; padding-top:10px;">Authorised Signatory</div>
                </div>
            </div>
        </div>
    """
    return generate_html_viewer(html, f"RedProjectHistory_{emp.replace(' ','_')}")

def get_red_project_detailed_slip_html(emp, sd, ed, processed_df, gross, ded, net):
    rows_html = ""
    idx = 1
    
    for _, r in processed_df.iterrows():
        dt_val = r['Date'].strftime('%d-%m-%Y')
        w_odu = r['Weekly_ODU']
        w_idu = r['Weekly_IDU']
        o_rate = r['ODU_Rate']
        i_rate = r['IDU_Rate']
        o_ded = r['ODU_DedRate']
        i_ded = r['IDU_DedRate']
        r_gross = r['Row_Gross']
        r_net = r['Row_Net']
        
        w_count_str = f"<span style='color:#1d4ed8;'>O: {w_odu}</span><br><span style='color:#be185d;'>I: {w_idu}</span>"
        rate_str = f"<span style='color:#1d4ed8;'>₹{o_rate}</span><br><span style='color:#be185d;'>₹{i_rate}</span>"
        ded_str = f"<span style='color:#1d4ed8;'>₹{o_ded}</span><br><span style='color:#be185d;'>₹{i_ded}</span>"
        
        rows_html += f"""
        <tr style='background:#f8fafc; border-bottom:1px solid #e2e8f0;'>
            <td style='padding:8px; text-align:center; font-weight:bold; color:#475569;'>{idx}</td>
            <td style='padding:8px; font-weight:bold;'>{dt_val}</td>
            <td style='padding:8px; text-align:center; color:#1d4ed8; font-size:16px;'><b>{r['ODU']}</b></td>
            <td style='padding:8px; text-align:center; color:#be185d; font-size:16px;'><b>{r['IDU+STB']}</b></td>
            <td style='padding:8px; text-align:center; font-size:12px; font-weight:bold;'>{w_count_str}</td>
            <td style='padding:8px; text-align:center; font-size:12px; font-weight:bold;'>{rate_str}</td>
            <td style='padding:8px; text-align:center; font-size:12px; font-weight:bold;'>{ded_str}</td>
            <td style='padding:8px; text-align:center; color:#10b981; font-weight:900;'>₹{r_gross:,.0f}</td>
            <td style='padding:8px; text-align:center; color:#dc2626; font-weight:900;'>₹{r_net:,.0f}</td>
        </tr>
        """
        idx += 1
        
    html = f"""
        <div style="font-family: Arial, sans-serif; background: #ffffff; padding: 20px; border-radius: 15px;">
            <div class="unbreak" style="text-align:center; border-bottom:4px solid #dc2626; padding-bottom:15px; margin-bottom:20px;">
                <h1 style="margin:0; color:#dc2626; font-size: 32px; font-weight: 900; letter-spacing: 1px;">SANDHYA ENTERPRISES</h1>
                <p style="margin:5px 0; font-weight:bold; font-size: 16px; color: #333;">Red Project Weekly Payout Slip</p>
                <p style="margin:0; font-size:13px; color:#64748b; text-transform: uppercase; letter-spacing: 2px;">Official Settlement</p>
            </div>
            
            <div class="unbreak" style="display:flex; justify-content:space-between; margin-bottom:25px; background: #fef2f2; padding: 15px; border-radius: 10px; border-left: 5px solid #dc2626;">
                <div style="font-size: 16px;"><b>Employee:</b> <span style="color:#b91c1c;">{emp}</span></div>
                <div style="font-size: 16px;"><b>Payout Period:</b> <span style="color:#b91c1c;">{sd.strftime('%d-%m-%Y')} to {ed.strftime('%d-%m-%Y')}</span></div>
            </div>
            
            <table style="width:100%; border-collapse:collapse; margin-bottom:30px; font-size: 12px;">
                <thead>
                    <tr style="background: #dc2626; color:white;">
                        <th style="padding:10px; text-align:center; border:1px solid #b91c1c; width:30px;">#</th>
                        <th style="padding:10px; text-align:left; border:1px solid #b91c1c;">ENTRY DATE</th>
                        <th style="padding:10px; text-align:center; border:1px solid #b91c1c;">ODU<br>COUNT</th>
                        <th style="padding:10px; text-align:center; border:1px solid #b91c1c;">IDU+STB<br>COUNT</th>
                        <th style="padding:10px; text-align:center; border:1px solid #b91c1c;">WEEKLY<br>COUNT</th>
                        <th style="padding:10px; text-align:center; border:1px solid #b91c1c;">RATE/UNIT<br>APPLIED</th>
                        <th style="padding:10px; text-align:center; border:1px solid #b91c1c;">DED/UNIT<br>APPLIED</th>
                        <th style="padding:10px; text-align:center; border:1px solid #b91c1c;">GROSS<br>PAYOUT</th>
                        <th style="padding:10px; text-align:center; border:1px solid #b91c1c;">NET<br>PAYOUT</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            
            <div class="unbreak">
                <div style="background: #f1f5f9; border: 2px solid #cbd5e1; padding:25px; border-radius:15px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="text-align: left;">
                        <span style="color:#64748b; font-size: 14px; font-weight: bold; text-transform: uppercase;">Total Gross Payout</span><br>
                        <span style="font-size:22px; font-weight:900; color:#10b981;">₹{gross:,.2f}</span>
                    </div>
                    <div style="text-align:center; position: relative;">
                        <div style="position: absolute; left: -30px; top: 10px; width: 2px; height: 40px; background: #cbd5e1;"></div>
                        <span style="color:#64748b; font-size: 14px; font-weight: bold; text-transform: uppercase;">Total Deduction</span><br>
                        <span style="font-size:22px; font-weight:900; color:#ef4444;">- ₹{ded:,.2f}</span>
                        <div style="position: absolute; right: -30px; top: 10px; width: 2px; height: 40px; background: #cbd5e1;"></div>
                    </div>
                    <div style="text-align:right;">
                        <span style="color:#0f172a; font-size: 16px; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">TOTAL NET PAYABLE</span><br>
                        <span style="font-size:36px; font-weight:900; color:#dc2626;">₹{net:,.2f}</span>
                    </div>
                </div>
            </div>
            
            <div class="unbreak">
                <div style="margin-top:60px; display:flex; justify-content:space-between; font-size:14px; color:#475569; font-weight: bold;">
                    <div style="border-top:2px dashed #94a3b8; width:200px; text-align:center; padding-top:10px;">Employee Signature</div>
                    <div style="border-top:2px dashed #94a3b8; width:200px; text-align:center; padding-top:10px;">Authorised Signatory</div>
                </div>
            </div>
        </div>
    """
    return generate_html_viewer(html, f"RedProject_{emp.replace(' ','_')}")

def get_payroll_html(emp, sd, ed, stats, df_rows, earn, cash, ded, is_fib, sim_bal):
    net = earn + cash - ded
    
    sim_box = ""
    if not is_fib:
        sim_box = f"""
        <div class="unbreak" style="background: #fef08a; padding:15px; border-radius:12px; margin-bottom:20px; text-align:center; border:1px solid #facc15;">
            <span style="font-size:18px; font-weight:bold; color:#854d0e;">📦 Remaining SIM Stock Balance: <span style="font-size:26px; color:#713f12; background: white; padding: 2px 10px; border-radius: 6px; margin-left:8px;">{sim_bal}</span></span>
        </div>
        """
    
    if is_fib:
        cards = f"""
        <div class="unbreak" style="display:flex; justify-content:center; gap:20px; margin-bottom:25px;">
            <div style="background: #e0f2fe; padding:15px 30px; border-radius:12px; border:1px solid #93c5fd; text-align:center;"><b>INSTALLATIONS</b><br><span style="font-size:26px; font-weight:900; color:#1d4ed8;">{stats['INS']}</span></div>
            <div style="background: #f3e8ff; padding:15px 30px; border-radius:12px; border:1px solid #c4b5fd; text-align:center;"><b>SERVICE (SR)</b><br><span style="font-size:26px; font-weight:900; color:#6d28d9;">{stats['SR']}</span></div>
        </div>"""
    else:
        cards = f"""
        <div class="unbreak" style="display:flex; justify-content:space-between; gap:15px; margin-bottom:25px;">
            <div style="background: #e0f2fe; padding:15px 10px; border-radius:12px; flex:1; text-align:center; border:1px solid #93c5fd;"><b>MNP</b><br><span style="font-size:24px; font-weight:900; color:#1d4ed8;">{stats['MNP']}</span></div>
            <div style="background: #fce7f3; padding:15px 10px; border-radius:12px; flex:1; text-align:center; border:1px solid #f9a8d4;"><b>FR 349</b><br><span style="font-size:24px; font-weight:900; color:#be185d;">{stats['FR349']}</span></div>
            <div style="background: #dcfce7; padding:15px 10px; border-radius:12px; flex:1; text-align:center; border:1px solid #86efac;"><b>FR 123</b><br><span style="font-size:24px; font-weight:900; color:#15803d;">{stats['FR123']}</span></div>
            <div style="background: #ffedd5; padding:15px 10px; border-radius:12px; flex:1; text-align:center; border:1px solid #fdba74;"><b>FR 152</b><br><span style="font-size:24px; font-weight:900; color:#c2410c;">{stats['FR152']}</span></div>
        </div>"""
    
    rows_html = ""
    idx = 0
    for _, r in df_rows.iterrows():
        amt = float(r.iloc[11])
        bg = "#ffffff" if idx % 2 == 0 else "#f8fafc"
        clr = "#166534" if amt > 0 else ("#ef4444" if amt < 0 else "#333333")
        amt_str = f"₹{amt:,.2f}" if amt > 0 else f"-₹{abs(amt):,.2f}"
        rows_html += f"<tr style='background:{bg};'><td style='padding:12px 10px; border:1px solid #e2e8f0; text-align:center; font-weight:bold; color:#475569;'>{idx+1}</td><td style='padding:12px 10px; border:1px solid #e2e8f0; color:#475569;'>{r.iloc[0]}</td><td style='padding:12px 10px; border:1px solid #e2e8f0; color:#0f172a;'><b>{r.iloc[2]}</b></td><td style='padding:12px 10px; border:1px solid #e2e8f0; font-size:12px; color:#64748b;'>{r.iloc[3]}</td><td style='padding:12px 10px; border:1px solid #e2e8f0; text-align:right; font-weight:bold; color:{clr};'>{amt_str}</td></tr>"
        idx += 1

    html = f"""
        <div style="font-family: Arial, sans-serif; background: #ffffff; border-radius: 15px;">
            <div class="unbreak" style="text-align:center; border-bottom:4px solid #004a99; padding-bottom:15px; margin-bottom:20px;">
                <h1 style="margin:0; color:#004a99; font-size: 32px; font-weight: 900; letter-spacing: 1px;">SANDHYA ENTERPRISES</h1>
                <p style="margin:5px 0; font-weight:bold; font-size: 16px; color: #333;">Authorised Jio Distributor | Samastipur, Bihar</p>
                <p style="margin:0; font-size:13px; color:#64748b; text-transform: uppercase; letter-spacing: 2px;">Official Payroll Settlement Slip</p>
            </div>
            
            <div class="unbreak" style="display:flex; justify-content:space-between; margin-bottom:25px; background: #f8fafc; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99;">
                <div style="font-size: 16px;"><b>Employee:</b> <span style="color:#004a99;">{emp}</span></div>
                <div style="font-size: 16px;"><b>Period:</b> <span style="color:#004a99;">{sd} to {ed}</span></div>
            </div>
            
            {sim_box}
            {cards}
            
            <table style="width:100%; border-collapse:collapse; margin-bottom:30px; font-size: 14px;">
                <thead>
                    <tr style="background: #004a99; color:white;">
                        <th style="padding:15px 10px; text-align:center; border:1px solid #005bb5; width:40px;">#</th>
                        <th style="padding:15px 10px; text-align:left; border:1px solid #005bb5;">DATE</th>
                        <th style="padding:15px 10px; text-align:left; border:1px solid #005bb5;">ACTIVITY</th>
                        <th style="padding:15px 10px; text-align:left; border:1px solid #005bb5;">REMARK</th>
                        <th style="padding:15px 10px; text-align:right; border:1px solid #005bb5;">AMOUNT</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            
            <div class="unbreak">
                <div style="background: #f1f5f9; border: 2px solid #cbd5e1; padding:25px; border-radius:15px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="text-align: left;">
                        <span style="color:#64748b; font-size: 14px; font-weight: bold; text-transform: uppercase;">Earnings (+ Cash)</span><br>
                        <span style="font-size:22px; font-weight:900; color:#10b981;">₹{earn + cash:,.2f}</span>
                    </div>
                    <div style="text-align:center; position: relative;">
                        <div style="position: absolute; left: -30px; top: 10px; width: 2px; height: 40px; background: #cbd5e1;"></div>
                        <span style="color:#64748b; font-size: 14px; font-weight: bold; text-transform: uppercase;">Deductions (SIM/Adv)</span><br>
                        <span style="font-size:22px; font-weight:900; color:#ef4444;">- ₹{ded:,.2f}</span>
                        <div style="position: absolute; right: -30px; top: 10px; width: 2px; height: 40px; background: #cbd5e1;"></div>
                    </div>
                    <div style="text-align:right;">
                        <span style="color:#0f172a; font-size: 16px; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">NET PAYABLE</span><br>
                        <span style="font-size:36px; font-weight:900; color:#004a99;">₹{net:,.2f}</span>
                    </div>
                </div>
            </div>
            
            <div class="unbreak">
                <div style="margin-top:60px; display:flex; justify-content:space-between; font-size:14px; color:#475569; font-weight: bold;">
                    <div style="border-top:2px dashed #94a3b8; width:200px; text-align:center; padding-top:10px;">Staff Signature</div>
                    <div style="border-top:2px dashed #94a3b8; width:200px; text-align:center; padding-top:10px;">Authorised Signatory</div>
                </div>
            </div>
        </div>
    """
    return generate_html_viewer(html, f"Payroll_{emp.replace(' ','_')}")

def get_calendar_html(emp, sd, ed, stats, df_rows, earn, cash, ded):
    try:
        date_range = pd.date_range(start=sd, end=ed)
    except:
        return "Invalid Dates"
        
    net = earn + cash - ded
    
    top_boxes = f"""
    <div style="display:flex; justify-content:space-between; gap:10px; margin-bottom:25px; flex-wrap:wrap;">
        <div style="flex:1; min-width:120px; background: linear-gradient(135deg, #3b82f6, #2563eb); padding:15px 10px; border-radius:12px; text-align:center; color:white; box-shadow: 0 6px 10px rgba(37,99,235,0.3), inset 0 -4px 0 rgba(0,0,0,0.2);">
            <div style="font-size:12px; font-weight:bold; text-transform:uppercase; letter-spacing:1px; opacity:0.9;">Total MNP</div>
            <div style="font-size:26px; font-weight:900; margin-top:5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{stats.get('MNP', 0)}</div>
        </div>
        <div style="flex:1; min-width:120px; background: linear-gradient(135deg, #ec4899, #db2777); padding:15px 10px; border-radius:12px; text-align:center; color:white; box-shadow: 0 6px 10px rgba(219,39,119,0.3), inset 0 -4px 0 rgba(0,0,0,0.2);">
            <div style="font-size:12px; font-weight:bold; text-transform:uppercase; letter-spacing:1px; opacity:0.9;">Total New SIM</div>
            <div style="font-size:26px; font-weight:900; margin-top:5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{stats.get('FR349', 0) + stats.get('FR123', 0) + stats.get('FR152', 0)}</div>
        </div>
        <div style="flex:1; min-width:120px; background: linear-gradient(135deg, #10b981, #059669); padding:15px 10px; border-radius:12px; text-align:center; color:white; box-shadow: 0 6px 10px rgba(5,150,105,0.3), inset 0 -4px 0 rgba(0,0,0,0.2);">
            <div style="font-size:12px; font-weight:bold; text-transform:uppercase; letter-spacing:1px; opacity:0.9;">Earnings (+Cash)</div>
            <div style="font-size:24px; font-weight:900; margin-top:5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">₹{earn+cash:,.0f}</div>
        </div>
        <div style="flex:1; min-width:120px; background: linear-gradient(135deg, #ef4444, #dc2626); padding:15px 10px; border-radius:12px; text-align:center; color:white; box-shadow: 0 6px 10px rgba(220,38,38,0.3), inset 0 -4px 0 rgba(0,0,0,0.2);">
            <div style="font-size:12px; font-weight:bold; text-transform:uppercase; letter-spacing:1px; opacity:0.9;">Deductions</div>
            <div style="font-size:24px; font-weight:900; margin-top:5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">₹{ded:,.0f}</div>
        </div>
        <div style="flex:1; min-width:120px; background: linear-gradient(135deg, #f59e0b, #d97706); padding:15px 10px; border-radius:12px; text-align:center; color:white; box-shadow: 0 6px 10px rgba(217,119,6,0.3), inset 0 -4px 0 rgba(0,0,0,0.2);">
            <div style="font-size:12px; font-weight:bold; text-transform:uppercase; letter-spacing:1px; opacity:0.9;">Net Payable</div>
            <div style="font-size:24px; font-weight:900; margin-top:5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">₹{net:,.0f}</div>
        </div>
    </div>
    """
        
    cal_html = "<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; width: 100%;'>"
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in days:
        cal_html += f"<div style='text-align:center; font-weight:bold; background: linear-gradient(90deg, #004a99, #0066cc); color:white; padding:10px; border-radius:8px; font-size:14px; box-shadow:0 2px 4px rgba(0,0,0,0.1);'>{day}</div>"
    
    first_day_idx = date_range[0].weekday()
    for _ in range(first_day_idx):
        cal_html += "<div style='background:#f8fafc; border-radius:8px; min-height:110px; border:1px dashed #cbd5e1;'></div>"
    
    for single_date in date_range:
        day_data = df_rows[df_rows['dt_fixed'].dt.date == single_date.date()]
        
        items_html = ""
        bg_color = "#ffffff"
        border_color = "#cbd5e1"
        
        if not day_data.empty:
            bg_color = "#f0fdf4" 
            border_color = "#86efac"
            
            day_mnp = 0
            day_sim = 0
            day_ins = 0
            day_sr = 0
            day_adv = 0.0
            
            for _, r in day_data.iterrows():
                act = str(r.iloc[2]).upper()
                tech_str = str(r.iloc[3]).upper()
                amt = float(r.iloc[11])
                
                if "ISSUE" in act or "STOCK" in act: continue
                
                qty = 1
                m = re.search(r'QTY\s*:?\s*(\d+)', tech_str)
                if m: qty = int(m.group(1))
                
                if "MNP" in act: day_mnp += qty
                elif "SIM" in act or "FR" in act: day_sim += qty
                elif "INSTALL" in act: day_ins += qty
                elif "SR" in act: day_sr += qty
                elif "PAY" in act or "ADVANCE" in act: day_adv += abs(amt)
            
            if day_mnp > 0: items_html += f"<div style='font-size:11px; color:#1d4ed8; font-weight:bold; margin-bottom:2px;'>🔵 MNP: {day_mnp}</div>"
            if day_sim > 0: items_html += f"<div style='font-size:11px; color:#be185d; font-weight:bold; margin-bottom:2px;'>🔴 SIM: {day_sim}</div>"
            if day_ins > 0: items_html += f"<div style='font-size:11px; color:#047857; font-weight:bold; margin-bottom:2px;'>🟢 INS: {day_ins}</div>"
            if day_sr > 0: items_html += f"<div style='font-size:11px; color:#6d28d9; font-weight:bold; margin-bottom:2px;'>🟣 SR: {day_sr}</div>"
            if day_adv > 0: items_html += f"<div style='font-size:11px; color:#b91c1c; font-weight:bold; margin-bottom:2px;'>💸 Adv: ₹{day_adv:,.0f}</div>"
                
        cal_html += f"""
        <div class="unbreak" style='background:{bg_color}; border:2px solid {border_color}; border-radius:10px; padding:8px; height:110px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); display:flex; flex-direction:column; overflow:hidden;'>
            <div style='font-weight:900; font-size:16px; color:#0f172a; border-bottom:2px solid #e2e8f0; margin-bottom:5px; padding-bottom:3px; text-align:right;'>
                <span style="float:left; font-size:10px; color:#64748b; font-weight:bold; margin-top:4px;">{single_date.strftime('%b')}</span>
                {single_date.day}
            </div>
            <div style='flex:1; overflow-y:auto; line-height:1.2; padding-top:2px;'>{items_html}</div>
        </div>
        """
        
    cal_html += "</div>"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; background: #ffffff; padding: 20px; border-radius: 15px;">
        <div class="unbreak" style="text-align:center; border-bottom:4px solid #004a99; padding-bottom:15px; margin-bottom:20px;">
            <h1 style="margin:0; color:#004a99; font-size: 28px; font-weight: 900; letter-spacing: 1px;">SANDHYA ENTERPRISES</h1>
            <p style="margin:5px 0; font-weight:bold; font-size: 14px; color: #333;">Employee Calendar Work Report</p>
        </div>
        
        <div class="unbreak" style="display:flex; justify-content:space-between; margin-bottom:25px; background: #f8fafc; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99;">
            <div style="font-size: 16px;"><b>Employee:</b> <span style="color:#004a99;">{emp}</span></div>
            <div style="font-size: 16px;"><b>Period:</b> <span style="color:#004a99;">{sd.strftime('%d-%m-%Y')} to {ed.strftime('%d-%m-%Y')}</span></div>
        </div>
        
        {top_boxes}
        
        {cal_html}
        
        <div class="unbreak" style="margin-top:40px; display:flex; justify-content:space-between; font-size:14px; color:#475569; font-weight: bold;">
            <div style="border-top:2px dashed #94a3b8; width:200px; text-align:center; padding-top:10px;">Staff Signature</div>
            <div style="border-top:2px dashed #94a3b8; width:200px; text-align:center; padding-top:10px;">Authorised Signatory</div>
        </div>
    </div>
    """
    return generate_html_viewer(html, f"Calendar_{emp.replace(' ','_')}")

def get_invoice_html(cn, cm, ca, inv, dt, rows_html, gt, t_disc, csh, onl, crd, due, amt_words):
    qr_amt = onl if onl > 0 else (due if due > 0 else gt)
    
    html = f"""
        <div style="font-family: Arial, sans-serif; color: #000; padding: 10px; position: relative; overflow: hidden; min-height: 500px;">
            
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 50px; color: rgba(0, 0, 0, 0.06); font-weight: 900; white-space: nowrap; z-index: 0; pointer-events: none; letter-spacing: 4px;">
                SANDHYA ENTERPRISES
            </div>
            
            <div style="position: relative; z-index: 1;">
                <div style="text-align:center; border-bottom:2px solid #000; padding-bottom:10px; margin-bottom:15px;">
                    <h3 style="margin:0; font-size:16px; letter-spacing:1px;">TAX INVOICE</h3>
                    <h1 style="margin:5px 0; font-size:32px; font-weight:900;">SANDHYA ENTERPRISES</h1>
                    <p style="margin:2px 0; font-size:12px; font-weight:bold;">Billing Branch : MEGHPATTI</p>
                    <p style="margin:2px 0; font-size:11px;">Billing Address : Ward no 06 Rosera Rod meghpatti</p>
                    <p style="margin:2px 0; font-size:11px;">City Samastipur 848117 State Bihar State code 10 country India</p>
                    <p style="margin:2px 0; font-size:11px;">Branch Contact Number : {OWNER_PHONE} | Email : smp.sandhya02@gmail.com</p>
                </div>
                
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:15px; border-bottom:2px solid #000; padding-bottom:10px;">
                    <div style="width:60%;">
                        <b style="text-decoration:underline;">Buyer's Name & Address:</b><br>
                        <b>Name :</b> {cn}<br>
                        <b>Mobile :</b> {cm}<br>
                        <b>Address:</b> {ca}
                    </div>
                    <div style="width:35%; border-left:1px solid #000; padding-left:10px;">
                        <b>Invoice No :</b> {inv}<br>
                        <b>Invoice Date :</b> {dt}
                    </div>
                </div>

                <table style="width:100%; border-collapse:collapse; font-size:12px; margin-bottom:10px; border:1px solid #000; background: rgba(255,255,255,0.8);">
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
                
                <div class="unbreak" style="border:1px solid #000; padding:5px 10px; font-size:12px; margin-bottom:15px; background: rgba(255,255,255,0.8);">
                    <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #000; padding-bottom:5px; margin-bottom:5px;">
                        <span><b>Total Discount Saved :</b> Rs. {t_disc:,.2f}</span>
                        <span style="font-size:14px;"><b>TOTAL AMOUNT : Rs. {gt:,.2f}</b></span>
                    </div>
                    <b>Rupees in Words :</b> {amt_words}
                </div>

                <div class="unbreak" style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:30px;">
                    <div style="width:65%;">
                        <div style="font-size:12px; margin-bottom:15px; background: rgba(255,255,255,0.8);">
                            <b style="text-decoration:underline;">PAYMENT DETAILS</b>
                            <table style="width:100%; border-collapse:collapse; border:1px solid #000; margin-top:5px;">
                                <tr style="border-bottom:1px solid #000; background-color:#f8f9fa;">
                                    <th style="padding:5px; text-align:left; border-right:1px solid #000;">Payment Type</th>
                                    <th style="padding:5px; text-align:right;">Amount (Rs)</th>
                                </tr>
                                <tr><td style="padding:5px; border-right:1px solid #000;">Cash</td><td style="padding:5px; text-align:right;">{csh:,.2f}</td></tr>
                                <tr><td style="padding:5px; border-right:1px solid #000;">Online</td><td style="padding:5px; text-align:right;">{onl:,.2f}</td></tr>
                                <tr><td style="padding:5px; border-right:1px solid #000;">Card</td><td style="padding:5px; text-align:right;">{crd:,.2f}</td></tr>
                                <tr style="border-top:1px solid #000;"><td style="padding:5px; border-right:1px solid #000;"><b>Due Amount (Baki)</b></td><td style="padding:5px; text-align:right; color:red;"><b>{due:,.2f}</b></td></tr>
                            </table>
                        </div>
                        <div style="font-size:10px;">
                            <b>Terms & Conditions:</b><br>
                            * Delivery received after full satisfaction. * All disputes subject to Samastipur Jurisdiction.
                        </div>
                    </div>
                    <div style="width:30%; text-align:center; padding:10px; border:1px solid #000; border-radius:8px; background-color:rgba(248,249,250,0.9);">
                        <b style="font-size:12px;">SCAN TO PAY</b><br>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=upi://pay?pa={OWNER_PHONE}@ptaxis%26pn=SANDHYA%20ENTERPRISES%26am={qr_amt:.2f}%26cu=INR" style="width:100px; height:100px; margin:8px 0;">
                        <br><b style="font-size:12px;">₹ {qr_amt:,.2f}</b>
                    </div>
                </div>

                <div class="unbreak" style="display:flex; justify-content:space-between; font-size:12px; margin-top:40px;">
                    <div style="text-align:center;">_____________________<br><br>Customer Signature</div>
                    <div style="text-align:center;">_____________________<br><br>Authorised Signatory<br><b>SANDHYA ENTERPRISES</b></div>
                </div>

                <div class="unbreak" style="text-align:center; font-size:14px; font-weight:bold; margin-top:20px; border-top:1px dashed #000; padding-top:10px;">
                    " THANK YOU VISIT AGAIN !! "
                </div>
            </div>
        </div>
    """
    return generate_html_viewer(html, f"Bill_{inv}")

def get_sales_report_html(d_str, gt, csh, onl, crd, due, profit, rows):
    html = f"""
        <div style="text-align:center; border-bottom:3px solid #004a99; padding-bottom:15px; margin-bottom:20px;">
            <h1 style="margin:0; color:#004a99;">SANDHYA ENTERPRISES</h1>
            <p>Sales, Profit & Analytics Report | <b>{d_str}</b></p>
        </div>
        <div style="display:flex; justify-content:space-between; gap:10px; margin-bottom:30px;">
            <div style="background:#eff6ff; padding:15px; border-radius:8px; text-align:center; flex:1; border:1px solid #bfdbfe;"><small>TOTAL SALES</small><br><b style="font-size:16px;">₹{gt:,.0f}</b></div>
            <div style="background:#f0fdf4; padding:15px; border-radius:8px; text-align:center; flex:1; border:1px solid #bbf7d0;"><small>CASH RECV</small><br><b style="font-size:16px; color:green;">₹{csh:,.0f}</b></div>
            <div style="background:#f5f3ff; padding:15px; border-radius:8px; text-align:center; flex:1; border:1px solid #ddd6fe;"><small>ONLINE RECV</small><br><b style="font-size:16px; color:blue;">₹{onl:,.0f}</b></div>
            <div style="background:#f3f4f6; padding:15px; border-radius:8px; text-align:center; flex:1; border:1px solid #cbd5e1;"><small>CARD RECV</small><br><b style="font-size:16px; color:#475569;">₹{crd:,.0f}</b></div>
            <div style="background:#fef2f2; padding:15px; border-radius:8px; text-align:center; flex:1; border:1px solid #fecaca;"><small>DUES (BAKI)</small><br><b style="font-size:16px; color:red;">₹{due:,.0f}</b></div>
            <div style="background:#fffbeb; padding:15px; border-radius:8px; text-align:center; flex:1; border:1px solid #fde68a;"><small>PROFIT</small><br><b style="font-size:16px; color:#d97706;">₹{profit:,.0f}</b></div>
        </div>
        <table style="width:100%; border-collapse:collapse; font-size:12px;">
            <thead><tr style="background:#004a99; color:white;"><th style="padding:10px; text-align:left;">Date</th><th style="text-align:left;">Customer</th><th style="text-align:left;">Item Detail</th><th style="text-align:right;">Amount</th><th style="text-align:right;">Pay Mode</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    """
    return generate_html_viewer(html, f"Sales_Report_{d_str.replace(' ','_')}")

# ==========================================
# 7. APP LOGIC & UI 
# ==========================================
if not st.session_state['logged_in']:
    st.markdown('<br><br>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('''
            <div class="login-box">
                <h1 style="margin:0; color:#004a99; font-size: 28px;">🔐 SANDHYA ENTERPRISES</h1>
                <p style="color:#666; font-weight:bold; margin-bottom:20px;">Secure Admin & Staff Portal</p>
            </div>
        ''', unsafe_allow_html=True)
        
        display_to_fse = {}
        login_list_display = ["-- Select Profile --", "👑 Admin"]
        for e in fse_list:
            if "-" in e:
                name_only = e.split("-")[1].strip()
                login_list_display.append(name_only)
                display_to_fse[name_only] = e

        u_sel_display = st.selectbox("👤 Select Your Profile", login_list_display)
        u_pwd = st.text_input("🔑 Password", type="password", placeholder="Enter Password...")
        
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("🚀 SECURE LOGIN", use_container_width=True, type="primary"):
            auth_success = False
            if u_sel_display == "👑 Admin" and u_pwd == USER_CREDS["admin"]["pwd"]:
                st.session_state.update({'logged_in': True, 'role': 'admin', 'fse_name': 'All Employees'})
                add_audit_log("Admin", "Logged in successfully")
                auth_success = True
            elif u_sel_display != "-- Select Profile --":
                full_fse_string = display_to_fse[u_sel_display]
                emp_id = full_fse_string.split(" - ")[0].strip()
                if emp_id in USER_CREDS and USER_CREDS[emp_id]["pwd"] == u_pwd:
                    st.session_state.update({'logged_in': True, 'role': 'staff', 'fse_name': full_fse_string})
                    add_audit_log(full_fse_string, "Logged in to Staff Console")
                    auth_success = True
            
            if auth_success:
                st.rerun()
            else: 
                st.error("❌ Invalid Credentials. Kripya sahi Password daalein.")
else:
    # GLOBAL OVERLAYS
    if st.session_state.get('pdf_viewer') != "":
        if st.session_state.get('show_bill_popup'):
            st.markdown(f"""
            <div style="background: #dcfce7; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #16a34a; margin-bottom: 20px;">
                <h2 style="color: #16a34a; margin: 0;">✅ SUCCESSFUL!</h2>
                <p style="font-size: 16px; color: #166534; font-weight: bold; margin: 5px 0 0 0;">{st.session_state.get('bill_popup_msg', '')}</p>
            </div>
            <audio src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" autoplay></audio>
            """, unsafe_allow_html=True)
            
        components.html(st.session_state['pdf_viewer'], height=1050, scrolling=True)
        
        if st.button("❌ CLOSE VIEWER & RETURN", type="primary", use_container_width=True):
            st.session_state['pdf_viewer'] = ""
            st.session_state['show_bill_popup'] = False
            st.rerun()
        st.stop()

    if st.session_state.get('rep_viewer') != "":
        components.html(st.session_state['rep_viewer'], height=1050, scrolling=True)
        if st.button("❌ CLOSE RE-PRINT VIEWER", type="primary", use_container_width=True):
            st.session_state['rep_viewer'] = ""
            st.rerun()
        st.stop()

    if st.session_state.get('sales_pdf') != "":
        components.html(st.session_state['sales_pdf'], height=1050, scrolling=True)
        if st.button("❌ CLOSE REPORT VIEWER", type="primary", use_container_width=True):
            st.session_state['sales_pdf'] = ""
            st.rerun()
        st.stop()

    if st.session_state.get('show_staff_popup'):
        st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-top: 20px; margin-bottom: 20px;">
            <div style="background: white; padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.2); max-width: 450px; width: 100%; border: 3px solid #16a34a;">
                <div style="font-size: 80px; margin-bottom: 10px;">✅</div>
                <h1 style="color: #16a34a; margin-top: 0; font-size: 32px;">SUCCESSFUL!</h1>
                <p style="font-size: 18px; color: #333; margin-top: 15px; line-height: 1.5;">{st.session_state['staff_popup_msg']}</p>
            </div>
        </div>
        <audio src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" autoplay></audio>
        """, unsafe_allow_html=True)
        c_btn1, c_btn2, c_btn3 = st.columns([1,2,1])
        if c_btn2.button("❌ CLOSE & NEW ENTRY", type="primary", use_container_width=True):
            st.session_state['show_staff_popup'] = False
            st.rerun()
        st.stop()

    if st.session_state.get('show_popup'):
        st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-top: 20px; margin-bottom: 20px;">
            <div style="background: white; padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.2); max-width: 450px; width: 100%; border: 3px solid #16a34a;">
                <div style="font-size: 80px; margin-bottom: 10px;">✅</div>
                <h1 style="color: #16a34a; margin-top: 0; font-size: 32px;">SUCCESSFUL!</h1>
                <p style="font-size: 18px; color: #333; margin-top: 15px; line-height: 1.5;">{st.session_state['popup_msg']}</p>
            </div>
        </div>
        <audio src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" autoplay></audio>
        """, unsafe_allow_html=True)
        c_btn1, c_btn2, c_btn3 = st.columns([1,2,1])
        if c_btn2.button("❌ CLOSE & NEW ENTRY", type="primary", use_container_width=True):
            st.session_state['show_popup'] = False
            st.rerun()
        st.stop()
        
    if st.session_state.get('show_inv_popup'):
        st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; margin-top: 20px; margin-bottom: 20px;">
            <div style="background: white; padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.2); max-width: 450px; width: 100%; border: 3px solid #16a34a;">
                <div style="font-size: 80px; margin-bottom: 10px;">✅</div>
                <h1 style="color: #16a34a; margin-top: 0; font-size: 32px;">SUCCESSFUL!</h1>
                <p style="font-size: 18px; color: #333; margin-top: 15px; line-height: 1.5;">{st.session_state['inv_popup_msg']}</p>
            </div>
        </div>
        <audio src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" autoplay></audio>
        """, unsafe_allow_html=True)
        c_btn1, c_btn2, c_btn3 = st.columns([1,2,1])
        if c_btn2.button("❌ CLOSE & ADD MORE", type="primary", use_container_width=True):
            st.session_state['show_inv_popup'] = False
            st.rerun()
        st.stop()

    # --- TOP NAVIGATION BAR ---
    nav_c1, nav_c2, nav_c3 = st.columns([2, 1, 1])
    nav_c1.markdown(f"<div class='nav-box'>👤 {st.session_state['fse_name'].split('-')[-1]}</div>", unsafe_allow_html=True)
    if nav_c2.button("🔄 Global Refresh", use_container_width=True): st.cache_data.clear(); st.rerun()
    if nav_c3.button("🚪 Logout", use_container_width=True): st.session_state.clear(); st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="header-box"><h1 style="margin:0;">SANDHYA ENTERPRISES</h1><p style="margin:0; font-size:18px;">Authorised Jio Distributor | Business Dashboard</p></div>', unsafe_allow_html=True)
    
    df_h = load_db()
    df_p = load_products()

    if st.session_state['role'] == 'admin':
        tabs = st.tabs(["📊 1. LIVE KPI", "🛒 2. NEW BILLING", "🔍 3. RE-PRINT", "📦 4. INVENTORY", "👷 5. EMPLOYEE MGT", "📋 6. ACTIVITY POS", "🔥 7. MNP & SCHEMES", "💰 8. CASH", "🔴 9. RED PROJECT", "📊 10. BUSINESS P&L", "♻️ 11. RECOVERY", "🕵️ 12. AUDIT LOGS"])
    else:
        tabs = st.tabs(["👷 MY PERFORMANCE & SLIPS", "♻️ RECOVERY ENTRY"])

    # ==========================================
    # 📊 KPI DASHBOARD (Priority 1)
    # ==========================================
    if st.session_state['role'] == 'admin':
        with tabs[0]:
            st.subheader("📈 Real-Time Business Performance Dashboard")
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

            curr_month_df = df_h[df_h['dt_fixed'].dt.month == date.today().month] if not df_h.empty else pd.DataFrame()
            month_sale = curr_month_df.iloc[:, 11].sum() if not curr_month_df.empty else 0.0

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.markdown(f'<div class="metric-card">Today\'s Sale<br><h3 style="color:#2563eb;">₹{today_sale:,.0f}</h3><small>Cost: ₹{today_cost:,.0f}</small></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="metric-card">Today\'s Profit<br><h3 style="color:#16a34a;">₹{today_profit:,.0f}</h3><small>Net Margin</small></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="metric-card">Monthly Sales<br><h3 style="color:#0f172a;">₹{month_sale:,.0f}</h3><small>This Month</small></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="metric-card">Active Staff<br><h3 style="color:#0891b2;">{len(fse_list)-1}</h3><small>On Roster</small></div>', unsafe_allow_html=True)
            k5.markdown(f'<div class="metric-card">Low Stock Alert<br><h3 style="color:#dc2626;">Check Inv.</h3><small>Re-order</small></div>', unsafe_allow_html=True)
            
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
    # 🛒 TAB 2: SMART BILLING & BARCODE (Priority 1)
    # ==========================================
    pos_tab = tabs[1] if st.session_state['role'] == 'admin' else None
    if pos_tab:
        with pos_tab:
            c_t1, c_t2 = st.columns([8, 2])
            c_t1.write("### 🛒 Create New Customer Bill")
            if c_t2.button("🔄 Refresh Billing", key="ref_t2", use_container_width=True): st.cache_data.clear(); st.rerun()

            with st.expander("👤 1. Customer Details", expanded=True):
                c1, c2, c3 = st.columns(3); cn = c1.text_input("Customer Name", value="Walk-in Customer"); cm = c2.text_input("Mobile No."); ca = c3.text_input("Address")

            st.write("### 📦 2. Add Items / Telecom Services")
            b_t1, b_t2 = st.tabs(["🛒 Physical Products (Scanner)", "📱 Telecom (Recharge/SIM)"])
            
            with b_t1:
                if not df_p.empty:
                    st.markdown("##### 🔍 Scan Barcode / Search Product")
                    barcode_search = st.text_input("Type Product Name, Model or Scan Barcode Number", placeholder="Scan Barcode / Model...")
                    
                    p_display_list = [""]
                    p_map = {}
                    for _, r_p in df_p.iterrows():
                        p_name = str(r_p.iloc[1]).strip()
                        try:
                            p_model = str(r_p.iloc[2]).strip()
                            disp_name = f"{p_name} | {p_model}" if p_model and p_model.lower() not in ["nan", "none", ""] else p_name
                        except: disp_name = p_name
                        
                        if disp_name not in p_map:
                            p_display_list.append(disp_name)
                            p_map[disp_name] = p_name

                    filtered_opts = [opt for opt in p_display_list if barcode_search.lower() in opt.lower()] if barcode_search else p_display_list
                    p_disp = st.selectbox("👇 Select Product from List:", filtered_opts)
                    
                    if p_disp and p_disp != "":
                        p_sel = p_map[p_disp]
                        c_rate, s_rate = get_latest_rates(p_sel, df_p, df_h)
                        st.info(f"💡 आपकी खरीद (Cost): **₹{c_rate}** | System Selling Rate: **₹{s_rate}**")
                        r1, r2, r3 = st.columns(3)
                        rate = r1.number_input("Selling Rate (₹)", value=float(s_rate))
                        qty = r2.number_input("Quantity", 1)
                        disc = r3.number_input("Extra Discount (₹)", 0.0)
                        
                        w1, w2 = st.columns(2)
                        wr_opts = ["No Warranty", "3 Months", "6 Months", "1 Year", "18 Months", "2 Years", "3 Years", "5 Years", "Lifetime"]
                        wrnty = w1.selectbox("Warranty Period", wr_opts)
                        w_cov = w2.text_input("Warranty Coverage", "Manufacturing Defect Only")
                        imei = st.text_input("IMEI / Serial Number")
                        
                        if st.button("➕ Add Product to Cart", type="secondary"):
                            tot = (rate*qty)-disc
                            st.session_state['cart'].append({"Type": "Product", "Item": p_sel, "Rate": rate, "Qty": qty, "Disc": disc, "Cost": float(c_rate), "IMEI": imei, "Wrnty": f"{wrnty} ({w_cov})", "Total": tot})
                            add_audit_log(st.session_state['fse_name'], f"Added {p_sel} to cart (Qty: {qty})")
                            st.rerun()
            
            with b_t2:
                st.info("💡 Telecom services added here will count towards **Total Sales** but Cost is mapped to Rate.")
                t_type = st.radio("Service Type", ["Recharge", "New SIM (Shop Sale)", "MNP (Shop Sale)"], horizontal=True)
                t_num = st.text_input("Mobile Number (For Recharge/SIM)")
                t_amt = st.number_input("Amount Collected from Customer (₹)", min_value=0.0)
                if st.button("➕ Add Telecom to Cart", type="secondary"):
                    if t_amt > 0:
                        st.session_state['cart'].append({"Type": "Telecom", "Item": f"{t_type} - {t_num}", "Rate": t_amt, "Qty": 1, "Disc": 0.0, "Cost": t_amt, "IMEI": "N/A", "Wrnty": "No", "Total": t_amt})
                        st.rerun()

            if st.session_state['cart']:
                st.write("---"); st.write("### 🛒 3. Shopping Cart")
                st.table(pd.DataFrame(st.session_state['cart'])[["Item", "Rate", "Qty", "Disc", "Total"]])
                
                grand_t = sum(i['Total'] for i in st.session_state['cart'])
                tot_disc = sum(i['Disc'] for i in st.session_state['cart'])
                st.markdown(f"### 💰 Grand Total: <span style='color:#004a99;'>₹{grand_t:,.2f}</span>", unsafe_allow_html=True)
                
                st.write("**Payment Settlement (पैसे कैसे मिले?)**")
                p1, p2, p3, p4 = st.columns(4)
                csh_paid = p1.number_input("Cash Received (₹)", value=grand_t, min_value=0.0)
                onl_paid = p2.number_input("Online Received (₹)", value=0.0, min_value=0.0)
                crd_paid = p3.number_input("Card Received (₹)", value=0.0, min_value=0.0)
                
                due_amt = grand_t - (csh_paid + onl_paid + crd_paid)
                p4.markdown(f"**Due (बाकी):**<br><span style='color:red; font-size:20px;'>₹{due_amt:,.2f}</span>", unsafe_allow_html=True)

                c_clr, c_sav = st.columns(2)
                if c_clr.button("🗑️ Clear Cart", use_container_width=True): st.session_state['cart'] = []; st.rerun()
                if c_sav.button("💾 SAVE & GENERATE BILL", type="primary", use_container_width=True):
                    inv_id = f"SE-{int(time.time())%100000}"; r_h = ""; amt_w = num_to_words(grand_t)
                    
                    with st.spinner("Saving to database..."):
                        for i in st.session_state['cart']:
                            tech = f"Inv: {inv_id} | Item: {i['Item']} | Rate: {i['Rate']} | Qty: {i['Qty']} | Disc: {i['Disc']} | Cost: {i['Cost']} | IMEI: {i['IMEI']} | Wrnty: {i['Wrnty']} | Pay: C={csh_paid},O={onl_paid},Card={crd_paid},D={due_amt} | Addr: {ca}"
                            requests.post(write_url, json={"date": date.today().strftime("%d-%m-%Y"), "fse": cn if cn else "Walk-in", "activity_boy": cm, "tech": tech, "total": i['Total']})
                            
                            det = ""
                            if i.get('IMEI') and i['IMEI'] != "N/A": det += f" | S/N: {i['IMEI']}"
                            if i.get('Wrnty') and i['Wrnty'] != "No": det += f" | Wrnty: {i['Wrnty']}"
                            r_h += f"<tr style='border-bottom:1px solid #ddd;'><td style='padding:8px; border-right:1px solid #000;'><b>{i['Item']}</b><br><small style='color:#666;'>{det}</small></td><td style='padding:8px; text-align:center; border-right:1px solid #000;'>{i['Rate']}</td><td style='padding:8px; text-align:center; border-right:1px solid #000;'>{i['Qty']}</td><td style='padding:8px; text-align:right;'>{i['Total']}</td></tr>"
                    
                    add_audit_log(st.session_state['fse_name'], f"Generated Invoice {inv_id} for ₹{grand_t}")
                    st.session_state['pdf_viewer'] = get_invoice_html(cn if cn else "Walk-in", cm, ca, inv_id, date.today().strftime("%d/%m/%Y"), r_h, grand_t, tot_disc, csh_paid, onl_paid, crd_paid, due_amt, amt_w)
                    st.session_state['cart'] = []
                    
                    st.session_state['bill_popup_msg'] = f"Invoice No: {inv_id} | Total Amount: ₹{grand_t}"
                    st.session_state['show_bill_popup'] = True
                    
                    # 💬 WhatsApp Priority 2 Generation
                    if cm:
                        wa_msg = f"🏢 *SANDHYA ENTERPRISES TAX INVOICE*\nInvoice No: {inv_id}\nCustomer: {cn}\nTotal Bill: ₹{grand_t}\nThank you for visiting!"
                        encoded_wa = requests.utils.quote(wa_msg)
                        st.markdown(f'<a href="https://wa.me/91{cm}?text={encoded_wa}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; width:100%; font-weight:bold;">💬 SEND INVOICE ON WHATSAPP</button></a>', unsafe_allow_html=True)

                    st.rerun()

    # ==========================================
    # 🔍 TAB 3: RE-PRINT
    # ==========================================
    rep_tab = tabs[2] if st.session_state['role'] == 'admin' else None
    if rep_tab:
        with rep_tab:
            st.write("### 🔍 Search Customer History & Re-Print Bill")
            s_mob = st.text_input("Enter Customer Mobile Number")
            if s_mob:
                res = df_h[df_h.iloc[:, 2].astype(str).str.contains(s_mob, na=False)]
                if not res.empty:
                    bills = {}
                    for _, r in res.iterrows():
                        p = parse_tech(r.iloc[3], fallback_total=float(r.iloc[11]) if pd.notna(r.iloc[11]) else 0.0)
                        if "SE-" in p["Inv"]:
                            if p["Inv"] not in bills: bills[p["Inv"]] = {"Name": r.iloc[1], "Date": r.iloc[0], "Items": [], "Total": 0, "Disc": 0, "C": p.get("Cash",0), "O": p.get("Online",0), "Card": p.get("Card",0), "D": p.get("Due",0), "Addr": p["Addr"]}
                            bills[p["Inv"]]["Items"].append(p)
                            bills[p["Inv"]]["Total"] += p.get("Total", 0)
                            bills[p["Inv"]]["Disc"] += p.get("Disc", 0)
                    
                    if bills:
                        b_opts = [f"{k} | Date: {v['Date']} | ₹{v['Total']}" for k, v in bills.items()]
                        sel_b = st.selectbox("Select Invoice to Re-Print", b_opts)
                        if st.button("📑 Fetch & Print Selected Bill", type="primary"):
                            bid = sel_b.split(" | ")[0]
                            bdata = bills[bid]
                            r_h = ""
                            for itm in bdata["Items"]:
                                det = ""
                                if itm.get('IMEI') and itm['IMEI'] != "N/A": det += f" | S/N: {itm['IMEI']}"
                                if itm.get('Wrnty') and itm['Wrnty'] != "No": det += f" | Wrnty: {itm['Wrnty']}"
                                r_h += f"<tr style='border-bottom:1px solid #ddd;'><td style='padding:8px; border-right:1px solid #000;'><b>{itm['Item']}</b><br><small style='color:#666;'>{det}</small></td><td style='padding:8px; text-align:center; border-right:1px solid #000;'>{itm['Rate']}</td><td style='padding:8px; text-align:center; border-right:1px solid #000;'>{itm['Qty']}</td><td style='padding:8px; text-align:right;'>{itm['Total']}</td></tr>"
                            
                            amt_w = num_to_words(bdata['Total'])
                            st.session_state['rep_viewer'] = get_invoice_html(bdata['Name'], s_mob, bdata['Addr'], bid, bdata['Date'], r_h, bdata['Total'], bdata['Disc'], bdata['C'], bdata['O'], bdata['Card'], bdata['D'], amt_w)
                            st.rerun()
                    else: st.warning("No Shop Invoices found for this number (Only Staff entries).")
                else: st.warning("No records found.")

    # ==========================================
    # 📦 TAB 4: INVENTORY
    # ==========================================
    inv_tab = tabs[3] if st.session_state['role'] == 'admin' else None
    if inv_tab:
        with inv_tab:
            st.write("### 📦 Stock Inventory Management")
            sold = {}; added = {}
            if not df_p.empty:
                for _, row in df_h.iterrows():
                    tech_str = str(row.iloc[3])
                    act_str = str(row.iloc[2])
                    if "Inv: SE-" in tech_str or "Issue SIM" in act_str: 
                        p = parse_tech(tech_str)
                        if p["Item"] and p["Item"] != "OLD":
                            sold[p["Item"]] = sold.get(p["Item"], 0) + p["Qty"]
                    elif act_str == "STOCK_IN":
                        p = parse_tech(tech_str); added[p["Item"]] = added.get(p["Item"], 0) + p["Qty"]
                
                inv_list = []
                for _, p in df_p.iterrows():
                    n = str(p.iloc[1]).strip()
                    base = float(p.iloc[5]) if pd.notna(p.iloc[5]) else 0.0
                    live = base + added.get(n, 0) - sold.get(n, 0)
                    c_rate, s_rate = get_latest_rates(n, df_p, df_h)
                    inv_list.append({"Product": n, "Purchase Rate": c_rate, "Selling Rate": s_rate, "Base (Sheet)": base, "New Stock Added": added.get(n, 0), "Sold (App)": sold.get(n, 0), "LIVE STOCK": live})
                
                inv_t1, inv_t2 = st.tabs(["🟢 Live Stock View", "➕ Add New Stock / Update Rate"])
                
                with inv_t1:
                    st.dataframe(pd.DataFrame(inv_list), use_container_width=True)
                
                with inv_t2:
                    st.info("💡 **स्मार्ट इन्वेंट्री:** यहाँ से आप नया माल जोड़ सकते हैं और रेट अपडेट कर सकते हैं।")
                    p_names = [""] + [item["Product"] for item in inv_list]
                    sel_p = st.selectbox("Select Product to Add Stock", p_names)
                    
                    if sel_p:
                        curr_stock = next(item for item in inv_list if item["Product"] == sel_p)["LIVE STOCK"]
                        c_rate, s_rate = get_latest_rates(sel_p, df_p, df_h)
                        st.success(f"📦 Current Stock: **{curr_stock}** | Old Purchase Rate: **₹{c_rate}** | Old Sell Rate: **₹{s_rate}**")
                        
                        with st.form("add_stock_form", clear_on_submit=True):
                            add_qty = st.number_input("New Stock Quantity", min_value=1, step=1)
                            c1, c2 = st.columns(2)
                            new_cost = c1.number_input("New Purchase Rate (₹)", value=float(c_rate))
                            new_sell = c2.number_input("New Selling Rate (₹)", value=float(s_rate))
                            
                            if st.form_submit_button("💾 Update Stock & Rates"):
                                tech_data = f"Item: {sel_p} | Cost: {new_cost} | Rate: {new_sell} | Qty: {add_qty}"
                                requests.post(write_url, json={"date": date.today().strftime("%d-%m-%Y"), "fse": "INVENTORY", "activity_boy": "STOCK_IN", "tech": tech_data, "total": 0})
                                add_audit_log(st.session_state['fse_name'], f"Added {add_qty} stock to {sel_p} at cost ₹{new_cost}")
                                st.cache_data.clear()
                                st.session_state['inv_popup_msg'] = f"<b>Product:</b> {sel_p}<br><b>Stock Added:</b> +{add_qty} Pcs"
                                st.session_state['show_inv_popup'] = True
                                st.rerun()

    # ==========================================
    # 👷 TAB 5: EMPLOYEE MGT (Admin) OR TAB 0 (Staff)
    # ==========================================
    emp_tab = tabs[4] if st.session_state['role'] == 'admin' else tabs[0]
    with emp_tab:
        c_t1, c_t2 = st.columns([8, 2])
        c_t1.write("### 👥 Staff Performance & Settlement")
        if c_t2.button("🔄 Refresh Staff Data", key="ref_t1", use_container_width=True): st.cache_data.clear(); st.rerun()

        with st.expander("🔍 Filter Controls", expanded=True):
            f1, f2, f3 = st.columns(3)
            sd = f1.date_input("Start Date", date.today().replace(day=1))
            ed = f2.date_input("End Date", date.today())
            if st.session_state['role'] == 'admin': se = f3.selectbox("Select Staff", fse_list)
            else: se = st.session_state['fse_name']; f3.info(se.split(' - ')[-1])

        mask = df_h['dt_fixed'].notna() & (df_h['dt_fixed'].dt.date >= sd) & (df_h['dt_fixed'].dt.date <= ed)
        if se != "All Employees": mask &= (df_h.iloc[:, 1] == se)
        is_cust_bill = df_h.iloc[:, 3].astype(str).str.contains("Inv: SE-", na=False) & ~df_h.iloc[:, 3].astype(str).str.contains("ISSUE", na=False)
        df_staff = df_h[mask & (~is_cust_bill) & (df_h.iloc[:, 1] != "INVENTORY")].copy()
        df_staff.sort_values(by='dt_fixed', ascending=True, inplace=True)

        if st.session_state['role'] == 'admin':
            er_t = st.tabs(["📊 Analytics & Reports", "➕ Add Single Entry", "📝 Bulk Excel Entry", "🧾 Auto-Generated Slip", "📅 Calendar Slip", "📈 All FSE Monthly Report"])
            
            with er_t[0]:
                st.write("#### 📊 Employee Analytics Dashboard")
                if not df_staff.empty:
                    ear = df_staff[df_staff.iloc[:, 2].str.contains("MNP|Install|SR", na=False)].iloc[:, 11].sum()
                    ded = abs(df_staff[df_staff.iloc[:, 2].str.contains("New SIM|Pay", na=False)].iloc[:, 11].sum())
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<div class='metric-card'>Total Earnings<br><h3 style='color:green;'>₹{ear:,.0f}</h3></div>", unsafe_allow_html=True)
                    c2.markdown(f"<div class='metric-card'>Total Deductions<br><h3 style='color:red;'>₹{ded:,.0f}</h3></div>", unsafe_allow_html=True)
                    c3.markdown(f"<div class='metric-card'>Net Settlement<br><h3 style='color:#004a99;'>₹{ear-ded:,.0f}</h3></div>", unsafe_allow_html=True)
                    st.dataframe(df_staff.drop(columns=['dt_fixed']), use_container_width=True)
                else: st.warning("No records found.")

            with er_t[1]:
                if 'entry_emp' not in st.session_state: st.session_state['entry_emp'] = fse_list[1]
                e1, e2 = st.columns(2)
                t_emp = e1.selectbox("🎯 Target Employee", fse_list[1:], key="entry_emp")
                t_dt = e2.date_input("📅 Activity Date", st.session_state['staff_last_date'])
                
                w_act = st.radio("📌 Choose Activity Type:", ["MNP (₹50)", "New SIM (FR)", "AirFiber Install (₹250)", "AirFiber SR (₹50)", "Pay Amount (Advance)", "Received Amount", "Issue SIM (Stock)"], horizontal=True)
                
                with st.form("staff_f", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    is_pay = any(x in w_act for x in ["Pay", "Received"])
                    is_issue = "Issue SIM" in w_act
                    
                    if is_pay:
                        amt_v = c1.number_input("💰 Enter Amount (₹)", 0, key="st_amt")
                        q = 1; plan = ""
                    elif is_issue:
                        q = c1.number_input("🔢 Quantity", 1, step=1, key="st_q")
                        c2.info("📦 Product Auto-Set: Jio SIM"); plan = ""; amt_v = 0
                    else:
                        q = c1.number_input("🔢 Quantity / Count", 1, step=1, key="st_q")
                        plan = c2.selectbox("📶 FR Plan (For SIM)", ["FR 349", "FR 123", "FR 152"], key="st_plan") if "SIM" in w_act else ""
                        amt_v = 0
                    
                    rem = st.text_area("Additional Remarks", key="st_rem")
                    
                    if st.form_submit_button("🚀 SECURELY SAVE ENTRY", use_container_width=True):
                        v = 0; info = w_act; final_tech = f"{info} {rem}"
                        if "MNP" in w_act: v = q*50; info = f"MNP Qty: {q}"; final_tech = f"{info} {rem}"
                        elif "SIM (FR)" in w_act: u = 220 if "349" in plan else (110 if "123" in plan else 152); v = -(q*u); info = f"{plan} | Qty: {q}"; final_tech = f"{info} {rem}"
                        elif "Install" in w_act: v = q*250; info = f"Install Qty: {q}"; final_tech = f"{info} {rem}"
                        elif "SR" in w_act: v = q*50; info = f"SR Qty: {q}"; final_tech = f"{info} {rem}"
                        elif "Pay" in w_act: v = -amt_v; final_tech = f"{info} {rem}"
                        elif "Received" in w_act: v = amt_v; final_tech = f"{info} {rem}"
                        elif "Issue SIM" in w_act:
                            v = 0; p_sel = "Jio SIM"; info = f"Issued SIM: {p_sel} | Qty: {q}"
                            final_tech = f"Item: {p_sel} | Rate: 0 | Qty: {q} | {rem}"

                        requests.post(write_url, json={"date": t_dt.strftime("%d-%m-%Y"), "fse": t_emp, "activity_boy": w_act, "tech": final_tech, "total": v})
                        add_audit_log(st.session_state['fse_name'], f"Added entry for {t_emp} ({info})")
                        
                        st.cache_data.clear()
                        st.session_state['staff_last_date'] = t_dt  
                        emp_name_only = t_emp.split('-')[-1].strip() if '-' in t_emp else t_emp
                        amount_str = f"₹{amt_v}" if is_pay else f"{int(q)} Pcs"
                        st.session_state['staff_popup_msg'] = f"<b>Target:</b> {emp_name_only}<br><b>Action:</b> {info}<br><b>Value:</b> {amount_str}"
                        st.session_state['show_staff_popup'] = True
                        st.rerun()

            with er_t[2]:
                st.write("### 📝 Bulk Staff Excel Entry")
                bulk_date = st.date_input("📅 Select Date for Bulk Entry", st.session_state['staff_last_date'], key="bulk_staff_date")
                staff_names = [e for e in fse_list if e != "All Employees"]
                
                if 'bulk_staff_grid' not in st.session_state or st.session_state.get('bulk_staff_grid_date') != bulk_date:
                    init_data = [{"Employee": emp, "MNP": 0, "FR 349": 0, "FR 123": 0, "FR 152": 0, "Install": 0, "SR": 0, "Pay": 0.0, "Received": 0.0, "Remarks": ""} for emp in staff_names]
                    st.session_state['bulk_staff_grid'] = pd.DataFrame(init_data)
                    st.session_state['bulk_staff_grid_date'] = bulk_date

                edited_bulk_df = st.data_editor(st.session_state['bulk_staff_grid'], use_container_width=True, hide_index=True)

                if st.button("💾 SAVE ALL BULK ENTRIES", type="primary", use_container_width=True):
                    with st.spinner("Saving all entries..."):
                        dt_str = bulk_date.strftime("%d-%m-%Y")
                        save_count = 0
                        for _, row in edited_bulk_df.iterrows():
                            emp_name = row["Employee"]
                            rem = str(row["Remarks"]) if pd.notna(row["Remarks"]) and str(row["Remarks"]) != "" else ""
                            rem_str = f" {rem}" if rem else ""

                            if row["MNP"] > 0:
                                q = int(row["MNP"]); requests.post(write_url, json={"date": dt_str, "fse": emp_name, "activity_boy": "MNP (₹50)", "tech": f"MNP Qty: {q}{rem_str}", "total": q*50}); save_count += 1
                            if row["FR 349"] > 0:
                                q = int(row["FR 349"]); requests.post(write_url, json={"date": dt_str, "fse": emp_name, "activity_boy": "New SIM (FR)", "tech": f"FR 349 | Qty: {q}{rem_str}", "total": -(q*220)}); save_count += 1
                            if row["FR 123"] > 0:
                                q = int(row["FR 123"]); requests.post(write_url, json={"date": dt_str, "fse": emp_name, "activity_boy": "New SIM (FR)", "tech": f"FR 123 | Qty: {q}{rem_str}", "total": -(q*110)}); save_count += 1
                            if row["FR 152"] > 0:
                                q = int(row["FR 152"]); requests.post(write_url, json={"date": dt_str, "fse": emp_name, "activity_boy": "New SIM (FR)", "tech": f"FR 152 | Qty: {q}{rem_str}", "total": -(q*152)}); save_count += 1
                            if row["Install"] > 0:
                                q = int(row["Install"]); requests.post(write_url, json={"date": dt_str, "fse": emp_name, "activity_boy": "AirFiber Install (₹250)", "tech": f"Install Qty: {q}{rem_str}", "total": q*250}); save_count += 1
                            if row["SR"] > 0:
                                q = int(row["SR"]); requests.post(write_url, json={"date": dt_str, "fse": emp_name, "activity_boy": "AirFiber SR (₹50)", "tech": f"SR Qty: {q}{rem_str}", "total": q*50}); save_count += 1
                            if row["Pay"] > 0:
                                amt = float(row["Pay"]); requests.post(write_url, json={"date": dt_str, "fse": emp_name, "activity_boy": "Pay Amount (Advance)", "tech": f"Pay Amount (Advance){rem_str}", "total": -amt}); save_count += 1
                            if row["Received"] > 0:
                                amt = float(row["Received"]); requests.post(write_url, json={"date": dt_str, "fse": emp_name, "activity_boy": "Received Amount", "tech": f"Received Amount{rem_str}", "total": amt}); save_count += 1

                        if save_count > 0:
                            st.session_state['staff_last_date'] = bulk_date
                            add_audit_log(st.session_state['fse_name'], f"Bulk excel entry saved ({save_count} operations)")
                            st.session_state['staff_popup_msg'] = f"<b>Bulk Entry Saved!</b><br>{save_count} total entries saved for {dt_str}."
                            st.session_state['show_staff_popup'] = True
                            st.cache_data.clear()
                            del st.session_state['bulk_staff_grid']
                            st.rerun()
                        else: st.warning("⚠️ No data to save.")

            with er_t[3]:
                if se != "All Employees":
                    st.markdown("### 🖨️ Employee Payroll Slip (Auto-Generated)")
                    is_f = any(x in se for x in ["Munna", "Sunil"])
                    stats = {'MNP': get_safe_qty(df_staff, "MNP"), 'FR349': get_safe_qty(df_staff, "New SIM", "349"), 'FR123': get_safe_qty(df_staff, "New SIM", "123"), 'FR152': get_safe_qty(df_staff, "New SIM", "152"), 'INS': get_safe_qty(df_staff, "Install"), 'SR': get_safe_qty(df_staff, "SR")}
                    ear = df_staff[df_staff.iloc[:, 2].str.contains("MNP|Install|SR", na=False)].iloc[:, 11].sum()
                    cash = df_staff[df_staff.iloc[:, 2].str.contains("Received", na=False)].iloc[:, 11].sum()
                    ded = abs(df_staff[df_staff.iloc[:, 2].str.contains("New SIM|Pay", na=False)].iloc[:, 11].sum())
                    
                    df_life = df_h[df_h.iloc[:, 1] == se]
                    life_issued = 0; life_used = 0
                    for _, r in df_life.iterrows():
                        act_str = str(r.iloc[2]).upper(); tech_str = str(r.iloc[3]).upper()
                        qty = 1
                        m = re.search(r'QTY\s*:?\s*(\d+)', tech_str)
                        if m: qty = int(m.group(1))
                        if "ISSUE" in act_str: life_issued += qty
                        elif "MNP" in act_str or "NEW SIM" in act_str: life_used += qty
                    sim_bal = life_issued - life_used
                    
                    components.html(get_payroll_html(se, sd.strftime("%d-%m-%Y"), ed.strftime("%d-%m-%Y"), stats, df_staff, ear, cash, ded, is_f, sim_bal), height=1150, scrolling=True)

            with er_t[4]:
                if se != "All Employees":
                    stats = {'MNP': get_safe_qty(df_staff, "MNP"), 'FR349': get_safe_qty(df_staff, "New SIM", "349"), 'FR123': get_safe_qty(df_staff, "New SIM", "123"), 'FR152': get_safe_qty(df_staff, "New SIM", "152"), 'INS': get_safe_qty(df_staff, "Install"), 'SR': get_safe_qty(df_staff, "SR")}
                    ear = df_staff[df_staff.iloc[:, 2].str.contains("MNP|Install|SR", na=False)].iloc[:, 11].sum()
                    cash = df_staff[df_staff.iloc[:, 2].str.contains("Received", na=False)].iloc[:, 11].sum()
                    ded = abs(df_staff[df_staff.iloc[:, 2].str.contains("New SIM|Pay", na=False)].iloc[:, 11].sum())
                    components.html(get_calendar_html(se, sd, ed, stats, df_staff, ear, cash, ded), height=1150, scrolling=True)
                else: st.info("Kripya upar list me se kisi ek Employee ka naam chunein.")

            with er_t[5]:
                st.markdown("### 📈 All FSE Monthly Performance Report")
                mask_all = df_h['dt_fixed'].notna() & (df_h['dt_fixed'].dt.date >= sd) & (df_h['dt_fixed'].dt.date <= ed)
                df_all_fse = df_h[mask_all & (~is_cust_bill) & (df_h.iloc[:, 1] != "INVENTORY")].copy()
                
                if not df_all_fse.empty:
                    report_data = []
                    for emp_name in [x for x in fse_list if x != "All Employees"]:
                        emp_df = df_all_fse[df_all_fse.iloc[:, 1] == emp_name]
                        if not emp_df.empty:
                            m_mnp = get_safe_qty(emp_df, "MNP")
                            m_ear = emp_df[emp_df.iloc[:, 2].str.contains("MNP|Install|SR", na=False)].iloc[:, 11].sum()
                            m_cash = emp_df[emp_df.iloc[:, 2].str.contains("Received", na=False)].iloc[:, 11].sum()
                            m_ded = abs(emp_df[emp_df.iloc[:, 2].str.contains("New SIM|Pay", na=False)].iloc[:, 11].sum())
                            report_data.append({
                                "Employee Name": emp_name.split('-')[-1].strip(), "MNP": m_mnp,
                                "Earnings (+Cash)": m_ear + m_cash, "Deductions": m_ded, "Net Payable": m_ear + m_cash - m_ded
                            })
                    
                    if report_data:
                        rep_df = pd.DataFrame(report_data)
                        st.dataframe(rep_df, use_container_width=True)
                        st.bar_chart(rep_df.set_index("Employee Name")["Net Payable"])
                else: st.warning("No staff activity found.")

        else:
            if se != "All Employees":
                s_tabs = st.tabs(["🧾 Auto-Generated Slip", "📅 Calendar Slip"])
                stats = {'MNP': get_safe_qty(df_staff, "MNP"), 'FR349': get_safe_qty(df_staff, "New SIM", "349"), 'FR123': get_safe_qty(df_staff, "New SIM", "123"), 'FR152': get_safe_qty(df_staff, "New SIM", "152"), 'INS': get_safe_qty(df_staff, "Install"), 'SR': get_safe_qty(df_staff, "SR")}
                ear = df_staff[df_staff.iloc[:, 2].str.contains("MNP|Install|SR", na=False)].iloc[:, 11].sum()
                cash = df_staff[df_staff.iloc[:, 2].str.contains("Received", na=False)].iloc[:, 11].sum()
                ded = abs(df_staff[df_staff.iloc[:, 2].str.contains("New SIM|Pay", na=False)].iloc[:, 11].sum())
                
                df_life = df_h[df_h.iloc[:, 1] == se]
                life_issued = 0; life_used = 0
                for _, r in df_life.iterrows():
                    qty = 1; m = re.search(r'QTY\s*:?\s*(\d+)', str(r.iloc[3]).upper())
                    if m: qty = int(m.group(1))
                    if "ISSUE" in str(r.iloc[2]).upper(): life_issued += qty
                    elif "MNP" in str(r.iloc[2]).upper() or "NEW SIM" in str(r.iloc[2]).upper(): life_used += qty
                
                sim_bal = life_issued - life_used
                is_f = any(x in se for x in ["Munna", "Sunil"])
                
                with s_tabs[0]: components.html(get_payroll_html(se, sd.strftime("%d-%m-%Y"), ed.strftime("%d-%m-%Y"), stats, df_staff, ear, cash, ded, is_f, sim_bal), height=1150, scrolling=True)
                with s_tabs[1]: components.html(get_calendar_html(se, sd, ed, stats, df_staff, ear, cash, ded), height=1150, scrolling=True)

    # ==========================================
    # 📋 TAB 6: ACTIVITY POS (Admin only)
    # ==========================================
    pos_act_tab = tabs[5] if st.session_state['role'] == 'admin' else None
    if pos_act_tab:
        with pos_act_tab:
            st.markdown("<h2 style='text-align:center; color:#16a34a; margin-top:0;'>📋 DAILY ACTIVITY POS LEDGER</h2>", unsafe_allow_html=True)
            
            pos_names = ["Sandhya Enterprises", "Sandhya Mobile Park", "Babloo Mobile", "Sandhya Digital Point", "Avdhesh Mobile"]
            shop_idx = 0
            if st.session_state['last_pos_shop'] in pos_names: shop_idx = pos_names.index(st.session_state['last_pos_shop']) + 1
            sel_pos = st.selectbox("🏬 Select POS Shop", ["-- Select Shop --"] + pos_names, index=shop_idx, key="pos_shop_selector")
            
            if sel_pos != "-- Select Shop --":
                st.session_state['last_pos_shop'] = sel_pos
                f_c1, f_c2 = st.columns(2)
                f_sd = f_c1.date_input("Filter Start Date", date.today().replace(day=1), key="pos_sd")
                f_ed = f_c2.date_input("Filter End Date", date.today(), key="pos_ed")
                
                filtered_ledger = []
                for e in st.session_state['pos_ledger']:
                    if e['POS'] == sel_pos:
                        try:
                            e_date = datetime.strptime(e['Date'], "%d-%b-%Y").date()
                            if f_sd <= e_date <= f_ed: filtered_ledger.append(e)
                        except: filtered_ledger.append(e)

                df_pos = pd.DataFrame(filtered_ledger) if filtered_ledger else pd.DataFrame(columns=["Date", "Time", "Type", "Amount", "Done By", "Net Profit (Fayda/Lagat)"])
                
                with st.form("pos_form", clear_on_submit=True):
                    entry_dt = st.date_input("Entry Date", st.session_state['pos_last_date'])
                    e1, e2, e3 = st.columns(3)
                    a_type = e1.selectbox("Activity Type", ["MNP", "New FRC 349", "New FRC 123", "New FRC 152", "Jio Phone V4", "Recharge"])
                    
                    if a_type in ["MNP", "New FRC 349"]: e2.info("Sale Auto Set: ₹349"); a_amt = 349.0
                    elif a_type == "New FRC 123": e2.info("Sale Auto Set: ₹123"); a_amt = 123.0
                    elif a_type == "New FRC 152": e2.info("Sale Auto Set: ₹152"); a_amt = 152.0
                    else: a_amt = e2.number_input("Amount (Sale ₹)", min_value=0.0)
                    
                    if a_type == "MNP":
                        done_by = e3.selectbox("Done By", ["Self", "Agent"])
                        growth_p = st.radio("Growth Achieved", ["0%", "5%", "10%", "15%"], horizontal=True)
                    else:
                        done_by = "Self"; growth_p = "N/A"; e3.write("")
                    
                    if st.form_submit_button("💾 Save POS Activity", type="primary", use_container_width=True):
                        profit = 0; comm_paid = 0
                        if a_type == "MNP":
                            base_p = 16 if growth_p == "0%" else (31 if growth_p == "5%" else (35 if growth_p == "10%" else 40))
                            if done_by == "Self": profit = base_p
                            elif done_by == "Agent": comm_paid = 50; profit = base_p - 50 
                        elif a_type == "New FRC 349": profit = 16
                        elif a_type == "New FRC 123": profit = 5
                        elif a_type == "New FRC 152": profit = 16  
                        elif a_type == "Jio Phone V4": profit = 34
                        elif a_type == "Recharge": profit = 0
                        
                        ist_time = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%I:%M %p")
                        entry = {"Date": entry_dt.strftime("%d-%b-%Y"), "Time": ist_time, "POS": sel_pos, "Type": a_type, "Amount": a_amt, "Done By": done_by, "Growth": growth_p, "Commission": comm_paid, "Net Profit (Fayda/Lagat)": profit}
                        st.session_state['pos_ledger'].append(entry)

                        try: requests.post(write_url, json={"date": entry_dt.strftime("%d-%m-%Y"), "fse": f"POS - {sel_pos}", "activity_boy": a_type, "tech": f"Sale: {a_amt} | Done: {done_by} | Growth: {growth_p} | Time: {ist_time}", "total": profit})
                        except: pass
                        
                        add_audit_log(st.session_state['fse_name'], f"POS Entry at {sel_pos} for {a_type}")
                        st.session_state.update({'pos_last_date': entry_dt, 'popup_msg': f"<b>Shop:</b> {sel_pos}<br><b>Activity:</b> {a_type}<br><b>Amount:</b> ₹{a_amt}", 'show_popup': True}); st.rerun()

                if not df_pos.empty:
                    st.write(f"<br>### 📊 Entries from {f_sd.strftime('%d %b')} to {f_ed.strftime('%d %b')}", unsafe_allow_html=True)
                    st.dataframe(df_pos, use_container_width=True)

    # ==========================================
    # 🔥 TAB 7: MNP SCHEMES
    # ==========================================
    mnp_tab = tabs[6] if st.session_state['role'] == 'admin' else None
    if mnp_tab:
        with mnp_tab:
            st.markdown("<h2 style='text-align:center; color:#1d4ed8; margin-top:0;'>🚀 MNP MAHOTSAV & SCHEME MANAGER</h2>", unsafe_allow_html=True)
            c_sd, c_ed = st.columns(2)
            m_sd = c_sd.date_input("Start Date (MNP Dashboard)", date.today().replace(day=1), key="mnp_sd")
            m_ed = c_ed.date_input("End Date (MNP Dashboard)", date.today(), key="mnp_ed")
            
            mask_m = df_h['dt_fixed'].notna() & (df_h['dt_fixed'].dt.date >= m_sd) & (df_h['dt_fixed'].dt.date <= m_ed)
            df_mnp = df_h[mask_m].copy()
            agent_mnp = df_mnp[df_mnp.iloc[:, 2] == "MNP"].iloc[:, 11].sum()
            ret_mnp = df_mnp[df_mnp.iloc[:, 2] == "RETAILER_MNP"].iloc[:, 11].sum()
            total_mnp = agent_mnp + ret_mnp
            
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; gap:15px; margin-bottom:25px; text-align:center; flex-wrap:wrap;">
                <div style="background: linear-gradient(145deg, #e0f2fe, #bfdbfe); padding:20px; border-radius:12px; flex:1; min-width: 250px; border:1px solid #93c5fd; box-shadow: 3px 3px 10px rgba(0,0,0,0.1);"><b>Agent MNP</b><br><span style="font-size:35px; font-weight:900; color:#1d4ed8;">{int(agent_mnp)}</span></div>
                <div style="background: linear-gradient(145deg, #fce7f3, #fbcfe8); padding:20px; border-radius:12px; flex:1; min-width: 250px; border:1px solid #f9a8d4; box-shadow: 3px 3px 10px rgba(0,0,0,0.1);"><b>Market/Retailer MNP</b><br><span style="font-size:35px; font-weight:900; color:#be185d;">{int(ret_mnp)}</span></div>
                <div style="background: linear-gradient(145deg, #dcfce7, #bbf7d0); padding:20px; border-radius:12px; flex:1; min-width: 250px; border:1px solid #86efac; box-shadow: 3px 3px 10px rgba(0,0,0,0.1);"><b>Total Grand MNP</b><br><span style="font-size:35px; font-weight:900; color:#15803d;">{int(total_mnp)}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            t_mnp1, t_mnp2, t_mnp3 = st.tabs(["📝 Excel-Style Bulk Entry", "🎁 Scheme Creator & Poster", "🏆 Scheme Qualifiers Tracker"])
            
            with t_mnp1:
                master_entry_date = st.date_input("📅 Select Date for all entries below:", date.today(), key="master_mnp_date")
                if 'mnp_grid' not in st.session_state or 'Date' in st.session_state['mnp_grid'].columns:
                    st.session_state['mnp_grid'] = pd.DataFrame([{"Name (Agent/Retailer)": "", "Type": "Retailer MNP", "MNP Count": 0} for _ in range(5)])
                
                edited_df = st.data_editor(st.session_state['mnp_grid'], num_rows="dynamic", use_container_width=True)
                
                if st.button("💾 SAVE ALL MNP DATA TO SHEET", type="primary", use_container_width=True):
                    with st.spinner("Saving MNP Data..."):
                        save_count = 0
                        dt_str = master_entry_date.strftime("%d-%m-%Y")
                        for _, row in edited_df.iterrows():
                            if str(row.get('Name (Agent/Retailer)','')).strip() != "" and int(row.get('MNP Count',0)) > 0:
                                act = "RETAILER_MNP" if row.get('Type') == "Retailer MNP" else "MNP"
                                requests.post(write_url, json={"date": dt_str, "fse": str(row['Name (Agent/Retailer)']).strip(), "activity_boy": act, "tech": "Excel Grid Entry", "total": int(row['MNP Count'])})
                                save_count += 1
                        
                        if save_count > 0:
                            st.success(f"✅ {save_count} Entries Saved Successfully!")
                            st.session_state['mnp_grid'] = pd.DataFrame([{"Name (Agent/Retailer)": "", "Type": "Retailer MNP", "MNP Count": 0} for _ in range(5)])
                            add_audit_log(st.session_state['fse_name'], f"Bulk MNP entry saved ({save_count} records)")
                            st.cache_data.clear(); st.rerun()

            with t_mnp2:
                c_sch_sd, c_sch_ed = st.columns(2)
                st.session_state['scheme_start'] = c_sch_sd.date_input("🟢 Scheme Start Date", st.session_state.get('scheme_start', date.today()))
                st.session_state['scheme_end'] = c_sch_ed.date_input("🔴 Scheme End Date", st.session_state.get('scheme_end', date.today()))
                
                scheme_df = st.data_editor(pd.DataFrame(st.session_state['mnp_schemes']), num_rows="dynamic", use_container_width=True)
                st.session_state['mnp_schemes'] = scheme_df.to_dict('records')
                
                st.write("### 📸 Generate Scheme Poster")
                poster_html = f"""
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                <div id="mnp-poster-area" style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); padding: 40px; border-radius: 20px; color: white; text-align: center; max-width: 600px; margin: 0 auto; border: 8px solid #bfdbfe; font-family: Arial, sans-serif;">
                    <h1 style="font-size: 45px; font-weight: 900; margin: 0;">⚡ MNP MAHOTSAV ⚡</h1>
                    <h3 style="font-size: 24px; color: #fef08a; margin-top: 10px;">By SANDHYA ENTERPRISES</h3>
                    <p style="font-size: 18px; margin-bottom: 25px;">🗓️ Valid: {st.session_state['scheme_start'].strftime('%d %b %Y')} to {st.session_state['scheme_end'].strftime('%d %b %Y')}</p>
                    <div style="display:flex; flex-direction:column; gap:15px;">
                """
                colors = ["#ef4444", "#f59e0b", "#10b981", "#8b5cf6", "#ec4899", "#06b6d4"]
                valid_slabs = sorted([s for s in st.session_state['mnp_schemes'] if s.get('target', 0) > 0], key=lambda x: x.get('target', 0))
                for i, slab in enumerate(valid_slabs):
                    c = colors[i % len(colors)]
                    poster_html += f'<div style="background: white; color: {c}; padding: 15px 25px; border-radius: 50px; font-size: 24px; font-weight: 900; display: flex; justify-content: space-between;"><span>🎯 {slab["target"]} MNP</span><span>🎁 {slab["reward"]}</span></div>'
                
                poster_html += """
                    </div><p style="margin-top: 30px; font-size: 16px; color: #cbd5e1;">* Conditions Apply *</p></div>
                <div style="text-align:center; margin-top:20px;">
                    <button onclick="html2canvas(document.getElementById('mnp-poster-area'),{scale:3}).then(c=>{let l=document.createElement('a');l.download='MNP_Scheme.jpg';l.href=c.toDataURL('image/jpeg',1.0);l.click();});" style="padding:15px 40px; background:#16a34a; color:white; border:none; border-radius:10px; font-size:18px; font-weight:bold; cursor:pointer;">📸 DOWNLOAD POSTER AS JPG</button>
                </div>
                """
                components.html(poster_html, height=800)

            with t_mnp3:
                st.write("### 🏆 Scheme Qualifiers List")
                agent_data = df_mnp[df_mnp.iloc[:, 2] == "MNP"].groupby(df_mnp.columns[1])[df_mnp.columns[11]].sum().reset_index()
                ret_data = df_mnp[df_mnp.iloc[:, 2] == "RETAILER_MNP"].groupby(df_mnp.columns[1])[df_mnp.columns[11]].sum().reset_index()
                
                agent_data.columns = ['Name', 'Total MNP']; agent_data['Type'] = 'Agent'
                ret_data.columns = ['Name', 'Total MNP']; ret_data['Type'] = 'Retailer'
                
                all_mnp_data = pd.concat([agent_data, ret_data], ignore_index=True)
                all_mnp_data = all_mnp_data[all_mnp_data['Total MNP'] > 0].sort_values(by='Total MNP', ascending=False)
                st.dataframe(all_mnp_data, use_container_width=True)

    # ==========================================
    # 💰 TAB 8: CASH COLLECTION
    # ==========================================
    cash_tab = tabs[7] if st.session_state['role'] == 'admin' else None
    if cash_tab:
        with cash_tab:
            st.markdown("<h2 style='text-align:center; color:#16a34a; margin-top:0;'>💰 CASH COLLECTION & DEPOSIT MANAGER</h2>", unsafe_allow_html=True)
            c_sd, c_ed, c_fse = st.columns(3)
            c_sd_date = c_sd.date_input("Start Date", date.today().replace(day=1), key="cash_sd")
            c_ed_date = c_ed.date_input("End Date", date.today(), key="cash_ed")
            c_fse_sel = c_fse.selectbox("Select FSE (Receiver)", ["Babloo Kumar Sing"], key="cash_fse_sel")
            
            df_cash_life = df_h[df_h.iloc[:, 1] == c_fse_sel]
            df_cash_period = df_h[(df_h['dt_fixed'].dt.date >= c_sd_date) & (df_h['dt_fixed'].dt.date <= c_ed_date) & (df_h.iloc[:, 1] == c_fse_sel)]
            
            life_cash_col = 0.0; life_bank_dep = 0.0; period_cash_col = 0.0; period_onl_col = 0.0
            for _, r in df_cash_life.iterrows():
                act = str(r.iloc[2]).upper(); amt = float(r.iloc[11]) if pd.notna(r.iloc[11]) else 0.0; tech = str(r.iloc[3]).upper()
                if act == "CASH_COLLECTION" and "MODE: CASH" in tech: life_cash_col += amt
                elif act == "BANK_DEPOSIT": life_bank_dep += amt
            for _, r in df_cash_period.iterrows():
                act = str(r.iloc[2]).upper(); amt = float(r.iloc[11]) if pd.notna(r.iloc[11]) else 0.0; tech = str(r.iloc[3]).upper()
                if act == "CASH_COLLECTION":
                    if "MODE: CASH" in tech: period_cash_col += amt
                    elif "ONLINE" in tech or "TRANSFER" in tech: period_onl_col += amt
            
            running_balance = life_cash_col - life_bank_dep
            
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; gap:15px; margin-bottom:25px; text-align:center;">
                <div style="background: #dcfce7; padding:20px; border-radius:12px; flex:1; border:1px solid #86efac;"><b>Period Cash Collected</b><br><span style="font-size:30px; color:#15803d;">₹{period_cash_col:,.0f}</span></div>
                <div style="background: #e0f2fe; padding:20px; border-radius:12px; flex:1; border:1px solid #93c5fd;"><b>Period Online Transfer</b><br><span style="font-size:30px; color:#1d4ed8;">₹{period_onl_col:,.0f}</span></div>
                <div style="background: #fef08a; padding:20px; border-radius:12px; flex:1; border:1px solid #facc15;"><b>FSE In-Hand Balance</b><br><span style="font-size:30px; color:#854d0e;">₹{running_balance:,.0f}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            ct1, ct2, ct3 = st.tabs(["📥 Retailer Excel Collection", "🏦 Bank Deposit", "📊 Collection Report"])
            with ct1:
                c_date = st.date_input("📅 Date for Collection", date.today(), key="col_master_date")
                if 'col_grid' not in st.session_state: st.session_state['col_grid'] = pd.DataFrame([{"Retailer Name": "", "Mode": "Cash", "Amount": 0.0, "Remarks": ""} for _ in range(5)])
                edited_col = st.data_editor(st.session_state['col_grid'], num_rows="dynamic", use_container_width=True)
                
                if st.button("💾 SAVE COLLECTIONS", type="primary", use_container_width=True):
                    with st.spinner("Saving Collection Data..."):
                        save_count = 0; total_amt = 0.0; dt_str = c_date.strftime("%d-%m-%Y")
                        for _, row in edited_col.iterrows():
                            if str(row.get('Retailer Name','')).strip() != "" and float(row.get('Amount',0)) > 0:
                                tech_str = f"Mode: {row['Mode']} | Retailer: {str(row['Retailer Name']).strip()} | Rem: {str(row.get('Remarks',''))}"
                                requests.post(write_url, json={"date": dt_str, "fse": c_fse_sel, "activity_boy": "CASH_COLLECTION", "tech": tech_str, "total": float(row['Amount'])})
                                save_count += 1; total_amt += float(row['Amount'])
                        
                        if save_count > 0:
                            add_audit_log(st.session_state['fse_name'], f"Saved {save_count} cash collections")
                            st.session_state['popup_msg'] = f"<b>{save_count} Collections Saved!</b>"
                            st.session_state['show_popup'] = True
                            del st.session_state['col_grid']
                            st.cache_data.clear(); st.rerun()

            with ct2:
                with st.form("bank_dep_form", clear_on_submit=True):
                    d_dt = st.date_input("Deposit Date")
                    d_amt = st.number_input("Amount Deposited in Bank (₹)", min_value=0.0)
                    d_ref = st.text_input("Reference No. / Remarks")
                    if st.form_submit_button("🏦 SAVE BANK DEPOSIT", use_container_width=True):
                        if d_amt > 0:
                            requests.post(write_url, json={"date": d_dt.strftime("%d-%m-%Y"), "fse": c_fse_sel, "activity_boy": "BANK_DEPOSIT", "tech": f"Ref: {d_ref}", "total": d_amt})
                            add_audit_log(st.session_state['fse_name'], f"Saved bank deposit ₹{d_amt}")
                            st.session_state['popup_msg'] = f"<b>Bank Deposit Saved Successfully!</b>"
                            st.session_state['show_popup'] = True
                            st.cache_data.clear(); st.rerun()

            with ct3:
                rep_data = []
                for _, r in df_cash_period.iterrows():
                    if str(r.iloc[2]).upper() == "CASH_COLLECTION":
                        tech = str(r.iloc[3]); ret = ""; m_mode = ""
                        ret_m = re.search(r'Retailer:\s*([^|]*)', tech)
                        if ret_m: ret = ret_m.group(1).strip()
                        mode_m = re.search(r'Mode:\s*([^|]*)', tech)
                        if mode_m: m_mode = mode_m.group(1).strip()
                        rep_data.append({"Date": r.iloc[0], "FSE / Receiver": r.iloc[1], "Retailer Name": ret, "Mode": m_mode, "Amount": float(r.iloc[11])})
                st.dataframe(pd.DataFrame(rep_data), use_container_width=True)

    # ==========================================
    # 🔴 TAB 9: RED PROJECT
    # ==========================================
    rp_tab = tabs[8] if st.session_state['role'] == 'admin' else None
    if rp_tab:
        with rp_tab:
            st.markdown("<h2 style='text-align:center; color:#dc2626; margin-top:0;'>🔴 RED PROJECT COMMISSION</h2>", unsafe_allow_html=True)
            rp_c1, rp_c2, rp_c3 = st.columns(3)
            rp_sd = rp_c1.date_input("Week Start Date", date.today() - timedelta(days=7), key="rp_sd")
            rp_ed = rp_c2.date_input("Week End Date", date.today(), key="rp_ed")
            rp_emp = rp_c3.selectbox("Select Employee", fse_list, key="rp_emp")
            
            rp_tab1, rp_tab2 = st.tabs(["📝 Record Weekly Entries", "🔍 Search & Re-Print Old Slips"])
            with rp_tab1:
                if 'rp_grid_v11' not in st.session_state:
                    st.session_state['rp_grid_v11'] = pd.DataFrame([{"Date": None, "ODU": 0, "IDU+STB": 0, "POE": True, "Remote": True, "Charger": True, "HDMI": True} for _ in range(5)])
                edited_rp = st.data_editor(st.session_state['rp_grid_v11'], num_rows="dynamic", use_container_width=True)
                
                mask_rp_saved = df_h['dt_fixed'].notna() & (df_h['dt_fixed'].dt.date >= rp_sd) & (df_h['dt_fixed'].dt.date <= rp_ed)
                rp_saved_df = df_h[mask_rp_saved & (df_h.iloc[:, 1] == rp_emp) & (df_h.iloc[:, 2] == "Red Project Daily")].copy()
                
                s_odu, s_idu = 0, 0
                saved_daily_list = []
                if not rp_saved_df.empty:
                    for _, r in rp_saved_df.iterrows():
                        t_tech = str(r.iloc[3])
                        o_m = re.search(r'ODU:\s*(\d+)', t_tech); d_o = int(o_m.group(1)) if o_m else 0
                        i_m = re.search(r'IDU:\s*(\d+)', t_tech); d_i = int(i_m.group(1)) if i_m else 0
                        s_odu += d_o; s_idu += d_i
                        saved_daily_list.append({'Date': r['dt_fixed'], 'ODU': d_o, 'IDU+STB': d_i})
                
                saved_daily_df = pd.DataFrame(saved_daily_list)
                total_payout = 0.0; total_deduction = 0.0; net_payable = 0.0
                if not saved_daily_df.empty:
                    saved_daily_df['YearWeek'] = saved_daily_df['Date'].dt.strftime('%Y-%W')
                    saved_daily_df['Weekly_ODU'] = saved_daily_df['YearWeek'].map(saved_daily_df.groupby('YearWeek')['ODU'].sum())
                    saved_daily_df['Weekly_IDU'] = saved_daily_df['YearWeek'].map(saved_daily_df.groupby('YearWeek')['IDU+STB'].sum())
                    saved_daily_df['ODU_Rate'], saved_daily_df['ODU_DedRate'] = zip(*saved_daily_df['Weekly_ODU'].map(get_odu_rate))
                    saved_daily_df['IDU_Rate'], saved_daily_df['IDU_DedRate'] = zip(*saved_daily_df['Weekly_IDU'].map(get_idu_rate))
                    saved_daily_df['Row_Gross'] = (saved_daily_df['ODU'] * saved_daily_df['ODU_Rate']) + (saved_daily_df['IDU+STB'] * saved_daily_df['IDU_Rate'])
                    saved_daily_df['Row_Ded'] = (saved_daily_df['ODU'] * saved_daily_df['ODU_DedRate']) + (saved_daily_df['IDU+STB'] * saved_daily_df['IDU_DedRate'])
                    saved_daily_df['Row_Net'] = saved_daily_df['Row_Gross'] - saved_daily_df['Row_Ded']
                    total_payout = saved_daily_df['Row_Gross'].sum()
                    total_deduction = saved_daily_df['Row_Ded'].sum()
                    net_payable = saved_daily_df['Row_Net'].sum()

                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.button("💾 SAVE DATA (Sheet me bhejein)", type="primary", use_container_width=True):
                    valid_rp = edited_rp[edited_rp['Date'].notna() & ((edited_rp['ODU'] > 0) | (edited_rp['IDU+STB'] > 0))].copy()
                    if not valid_rp.empty:
                        with st.spinner("Saving Red Project data..."):
                            save_count = 0
                            for _, r in valid_rp.iterrows():
                                dt_str = pd.to_datetime(r['Date']).strftime('%d-%m-%Y')
                                tech_str = f"ODU: {int(r['ODU'])} | IDU: {int(r['IDU+STB'])} | POE: Yes | REM: Yes | CHG: Yes | HDMI: Yes"
                                requests.post(write_url, json={"date": dt_str, "fse": rp_emp, "activity_boy": "Red Project Daily", "tech": tech_str, "total": 0})
                                save_count += 1
                            add_audit_log(st.session_state['fse_name'], f"Saved {save_count} Red Project entries for {rp_emp}")
                            st.session_state['popup_msg'] = f"<b>{save_count} Daily Entries Saved!</b>"
                            st.session_state['show_popup'] = True
                            st.session_state['rp_grid_v11'] = pd.DataFrame([{"Date": None, "ODU": 0, "IDU+STB": 0, "POE": True, "Remote": True, "Charger": True, "HDMI": True} for _ in range(5)])
                            st.cache_data.clear(); st.rerun()

                if c_btn2.button("📄 GENERATE PAYMENT SLIP (PDF)", type="secondary", use_container_width=True):
                    if not saved_daily_df.empty:
                        st.session_state['pdf_viewer'] = get_red_project_detailed_slip_html(rp_emp, rp_sd, rp_ed, saved_daily_df, total_payout, total_deduction, net_payable)
                        st.session_state['show_bill_popup'] = False 
                        st.rerun()

            with rp_tab2:
                st.write("Old Slips Re-Print functionality can be searched here based on saved 'Red Project Payout' activities in the sheet.")

    # ==========================================
    # ♻️ TAB 11 (Admin) OR TAB 2 (Staff): RECOVERY
    # ==========================================
    rec_view_tab = tabs[10] if st.session_state['role'] == 'admin' else tabs[2]
    with rec_view_tab:
        st.markdown("<h2 style='text-align:center; color:#d97706; margin-top:0;'>♻️ DEVICE RECOVERY MANAGEMENT</h2>", unsafe_allow_html=True)
        st.info("💡 **Recovery Entry:** Excel grid me ODU aur IDU+STB recovery ki date wise entry karein.")
        if 'rec_grid_staff' not in st.session_state:
            st.session_state['rec_grid_staff'] = pd.DataFrame([{"Date": None, "ODU Qty": 0, "IDU+STB Qty": 0, "Recovered By": "Sunil"} for _ in range(5)])
        
        edited_rec = st.data_editor(st.session_state['rec_grid_staff'], num_rows="dynamic", use_container_width=True)
        
        if st.button("💾 SAVE RECOVERY DATA", type="primary", use_container_width=True):
            valid_rec = edited_rec[edited_rec['Date'].notna() & ((edited_rec['ODU Qty'] > 0) | (edited_rec['IDU+STB Qty'] > 0))]
            if not valid_rec.empty:
                with st.spinner("Saving Recovery data..."):
                    save_count = 0
                    for _, r in valid_rec.iterrows():
                        dt_str = pd.to_datetime(r['Date']).strftime('%d-%m-%Y')
                        tech_str = f"ODU: {int(r['ODU Qty'])} | IDU: {int(r['IDU+STB Qty'])} | By: {r['Recovered By']}"
                        requests.post(write_url, json={"date": dt_str, "fse": "RECOVERY", "activity_boy": "Device Recovery", "tech": tech_str, "total": 0})
                        save_count += 1
                    add_audit_log(st.session_state['fse_name'], f"Saved {save_count} recovery entries")
                    st.session_state['popup_msg'] = f"<b>{save_count} Recovery Entries Saved!</b>"
                    st.session_state['show_popup'] = True
                    st.session_state['rec_grid_staff'] = pd.DataFrame([{"Date": None, "ODU Qty": 0, "IDU+STB Qty": 0, "Recovered By": "Sunil"} for _ in range(5)])
                    st.cache_data.clear(); st.rerun()

        st.write("---")
        st.write("### 📊 Search & Download Recovery Report")
        r_sd_col, r_ed_col = st.columns(2)
        rec_start = r_sd_col.date_input("From Date", date.today() - timedelta(days=7), key="rec_sd_staff")
        rec_end = r_ed_col.date_input("To Date", date.today(), key="rec_ed_staff")

        mask_rec = df_h['dt_fixed'].notna() & (df_h['dt_fixed'].dt.date >= rec_start) & (df_h['dt_fixed'].dt.date <= rec_end)
        rec_df = df_h[mask_rec & (df_h.iloc[:, 2] == "Device Recovery")].copy()

        if not rec_df.empty:
            df_weekly = calculate_recovery_weekly(rec_df)
            st.dataframe(df_weekly, use_container_width=True)
            
            # Select Agent to View/Generate PDF (Staff view)
            pdf_agent = st.selectbox("Select Profile for PDF Slip", ["Manoj", "Sunil"])
            agent_wdf = df_weekly[df_weekly['Agent'] == pdf_agent].copy()
            
            if st.button("📄 GENERATE MY PDF SLIP", type="secondary", use_container_width=True):
                if not agent_wdf.empty:
                    st.session_state['pdf_viewer'] = get_recovery_weekly_html(pdf_agent, rec_start, rec_end, agent_wdf)
                    st.session_state['show_bill_popup'] = False
                    st.rerun()
                else: st.warning(f"No payout data found for {pdf_agent}.")
        else: st.info("No recovery data found.")

    # ==========================================
    # 🕵️ TAB 12: AUDIT LOG TRAIL (Priority 1)
    # ==========================================
    audit_tab = tabs[11] if st.session_state['role'] == 'admin' else None
    if audit_tab:
        with audit_tab:
            st.subheader("🕵️ System Security & Audit Log History")
            st.info("यह ब्लैक-बॉक्स ट्रैकर दिखाता है कि किस कर्मचारी ने किस समय क्या एक्शन लिया है।")
            if st.session_state['audit_logs']:
                st.markdown(f'<div class="audit-box">{"<br>".join(st.session_state["audit_logs"])}</div>', unsafe_allow_html=True)
            else:
                st.caption("No system activity logged in this session yet.")
