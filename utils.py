import hashlib
import qrcode
from io import BytesIO
import pandas as pd
import requests
import datetime
import urllib.parse

# --- Security: Password Hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

ADMIN_HASH = hash_password("9557") 

# --- Database Integration (Google Apps Script) ---
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw1cjdszgSRrSb8PlvupUVQTlea4e7dkvcCdDKJ-o8TssXJLmLRMBTJqBfhGhqcRjU-wg/exec"

def load_data_from_sheet():
    try:
        response = requests.get(APPS_SCRIPT_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def send_data_to_sheet(payload):
    try:
        # Added headers and allow_redirects to fix the Google Sheet Saving Issue
        headers = {'Content-Type': 'application/json'}
        response = requests.post(APPS_SCRIPT_URL, json=payload, headers=headers, allow_redirects=True, timeout=10)
        return response.status_code in [200, 302]
    except:
        return False

# --- Utilities ---
def generate_member_id(current_length):
    return f"SE{current_length + 1:04d}"

def generate_qr(upi_id, name, amount, note="Sandhya Enterprises"):
    upi_url = f"upi://pay?pa={upi_id}&pn={urllib.parse.quote(name)}&am={amount}&cu=INR&tn={urllib.parse.quote(note)}"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf

def get_whatsapp_link(mobile, message):
    encoded_msg = urllib.parse.quote(message)
    if not str(mobile).startswith("91"):
        mobile = f"91{mobile}"
    return f"https://wa.me/{mobile}?text={encoded_msg}"

def export_to_excel(df, filename):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Data", index=False)
    return buffer
