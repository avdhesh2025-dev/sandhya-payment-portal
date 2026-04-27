import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

# Utilisation de FPDF pour la génération de reçus
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# 1. Configuration de la page et design style A4
st.set_page_config(page_title="Sandhya Repair & Service", page_icon="🔧", layout="centered")

st.markdown("""
    <style>
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.1);
        max-width: 800px;
    }
    h1, h2, h3 { color: #1e3a8a; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔴 VOS PARAMÈTRES GOOGLE SHEET
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwOOlp0xpOMUO7g5vBl_2LWg69hhzyueQB6RrfuhWA5Q2aNR3WERRodXg3cFPiqw4878g/exec"
SHEET_ID = "17_TBUWgmXEdkRKUBX6Bg8w7kwfi_Tfol2lcmgonamgM"
# ==========================================

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=ServiceDB"

@st.cache_data(ttl=5)
def load_data():
    try:
        cb = int(time.time())
        df = pd.read_csv(f"{csv_url}&cb={cb}").dropna(how="all").fillna("")
        return df
    except:
        return pd.DataFrame(columns=["JobID", "Date", "CustName", "Mobile", "Address", "Category", "ProductDetail", "Fault", "Resolution", "EstCost", "DeliveryDate", "Status"])

# Initialisation de la base de données
if 'repair_db' not in st.session_state:
    st.session_state.repair_db = load_data()

if 'last_receipt_data' not in st.session_state:
    st.session_state.last_receipt_data = None

# Générateur de reçu PDF
def generate_repair_receipt(data):
    if not HAS_FPDF: return None
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête de l'entreprise
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, "SANDHYA ENTERPRISES", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 6, "Reçu de Réparation & Service", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, "Bureau: Rosera Road, Meghpatti, Samastipur, Bihar", ln=True, align='C')
    pdf.cell(0, 5, "Contact: 7479584179 | Email: smp.sandhya02@gmail.com", ln=True, align='C')
    pdf.line(10, 40, 200, 40)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 10)
    def add_row(label, value):
        pdf.cell(50, 8, label, border=1)
        pdf.set_font("Arial", '', 10)
        clean_val = str(value).encode('latin-1', 'ignore').decode('latin-1')
        pdf.cell(0, 8, f" {clean_val}", border=1, ln=True)
        pdf.set_font("Arial", 'B', 10)

    add_row("ID Job / Facture:", data['JobID'])
    add_row("Date:", data['Date'])
    add_row("Nom Client:", data['CustName'])
    add_row("Mobile:", data['Mobile'])
    add_row("Catégorie:", data['Category'])
    add_row("Produit/Modèle:", data['ProductDetail'])
    add_row("Problème:", data['Fault'])
    add_row("Coût Estimé:", f"Rs. {data['EstCost']}")
    add_row("Date de Livraison:", data['DeliveryDate'])
    
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, "Signature Autorisée - Sandhya Enterprises", align='R')
    return pdf.output(dest='S').encode('latin-1')

# Interface Utilisateur
st.markdown("""
    <div style='background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 20px;'>
        <h1 style='margin:0; font-size: 28px; color: white;'>🔧 PORTAIL DE RÉPARATION & SERVICE</h1>
        <p style='margin:0;'>Sandhya Enterprises - Gestion Universelle</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📝 Nouvelle Entrée", "⏳ En Attente", "✅ Historique"])

# TAB 1: NOUVELLE ENTRÉE
with tab1:
    if st.session_state.last_receipt_data:
        res = st.session_state.last_receipt_data
        st.success(f"✅ Job {res['JobID']} enregistré avec succès !")
        if HAS_FPDF:
            pdf = generate_repair_receipt(res)
            st.download_button("📥 Télécharger le Reçu (PDF)", data=pdf, file_name=f"Recu_{res['JobID']}.pdf", mime="application/pdf")
        if st.button("➕ Nouveau Client"):
            st.session_state.last_receipt_data = None
            st.rerun()
    else:
        with st.form("repair_form"):
            st.subheader("👤 Détails du Client")
            c1, c2 = st.columns(2)
            name = c1.text_input("Nom complet*")
            mobile = c2.text_input("Numéro Mobile*")
            addr = st.text_input("Adresse")
            
            st.subheader("📱 Détails de la Réparation")
            cat = st.selectbox("Catégorie*", ["Mobile", "Ventilateur", "Chargeur", "TV", "Autre"])
            prod = st.text_input("Modèle / Nom de l'article*")
            fault = st.text_area("Problème / Panne*")
            
            st.subheader("💰 Frais et Livraison")
            cost = st.text_input("Coût Estimé (₹)*")
            deliv = st.text_input("Délai de livraison*")
            
            submit = st.form_submit_button("💾 Enregistrer et Générer Facture", type="primary")
            
            if submit:
                if not name or not mobile or not prod:
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
                else:
                    new_id = f"REP-{int(time.time())}"
                    new_data = {
                        "action": "add", "JobID": new_id, "Date": datetime.now().strftime("%d-%m-%Y %H:%M"),
                        "CustName": name.upper(), "Mobile": mobile, "Address": addr,
                        "Category": cat, "ProductDetail": prod, "Fault": fault,
                        "Resolution": "En cours", "EstCost": cost, "DeliveryDate": deliv, "Status": "Pending"
                    }
                    try:
                        requests.post(WEBHOOK_URL, json=new_data, timeout=10)
                        st.session_state.last_receipt_data = new_data
                        st.rerun()
                    except:
                        st.error("❌ Erreur de connexion avec Google Sheet.")

# TAB 2: TRAVAUX EN ATTENTE
with tab2:
    st.session_state.repair_db = load_data()
    pending = st.session_state.repair_db[st.session_state.repair_db["Status"].str.contains("Pending", na=False)]
    if pending.empty:
        st.info("Aucun travail en attente.")
    else:
        for idx, row in pending.iterrows():
            with st.container():
                st.markdown(f"### {row['CustName']} - {row['ProductDetail']}")
                st.write(f"**Problème:** {row['Fault']} | **Coût:** ₹{row['EstCost']}")
                if st.button(f"✅ Marquer comme Livré ({row['JobID']})", key=row['JobID']):
                    requests.post(WEBHOOK_URL, json={"action": "update", "ID": row['JobID'], "Status": "Delivered"})
                    st.cache_data.clear()
                    st.rerun()
                st.markdown("---")

# TAB 3: HISTORIQUE
with tab3:
    st.dataframe(st.session_state.repair_db, use_container_width=True)
