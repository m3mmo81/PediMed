import streamlit as st
from datetime import datetime, timedelta

# --- BAZA PODATAKA SA LIMITIMA ---
DRUG_DATABASE = {
    "Paracetamol sirup (120mg/5ml)": {
        "dnevna_mg_kg": 60,
        "max_dan_fiksno": 4000,
        "mg_u_5ml": 120,
        "interval": 6, 
        "tip": "sirup",
        "napomena": "Razmak min 4h. Max 4 doze u 24h. Ne duže od 3 dana."
    },
    "Neofen / Ibuprofen (100mg/5ml)": {
        "dnevna_mg_kg": 30, 
        "max_dan_fiksno": 1200,
        "mg_u_5ml": 100,
        "interval": 6, 
        "tip": "sirup",
        "napomena": "Razmak min 4h. Dojenčad 3-12 mj: max 3 doze."
    },
    "Paracetamol čepići (120mg)": {"dnevna_mg_kg": 60, "max_dan_fiksno": 1000, "mg_u_jedinici": 120, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Paracetamol čepići (250mg)": {"dnevna_mg_kg": 60, "max_dan_fiksno": 2000, "mg_u_jedinici": 250, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Ibuprofen čepići (60mg)": {"dnevna_mg_kg": 30, "max_dan_fiksno": 600, "mg_u_jedinici": 60, "interval": 8, "tip": "supozitorija", "napomena": ""},
    "Ibuprofen čepići (125mg)": {"dnevna_mg_kg": 30, "max_dan_fiksno": 1200, "mg_u_jedinici": 125, "interval": 8, "tip": "supozitorija", "napomena": ""},
    "Ospen / Penicilin V (250mg/5ml)": {"dnevna_mg_kg": 50, "max_dan_fiksno": 3000, "mg_u_5ml": 250, "interval": 8, "tip": "antibiotik", "napomena": "1h prije ili 2h poslije jela."},
    "Cefaleksin (250mg/5ml)": {"dnevna_mg_kg": 50, "max_dan_fiksno": 4000, "mg_u_5ml": 250, "interval": 8, "tip": "antibiotik", "napomena": ""},
}

st.set_page_config(page_title="PediMed Safe", page_icon="⚖️")
st.title("⚖️ PediMed: Kalkulator sa Limitima")

# 1. UNOS PODATAKA
col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("Težina djeteta (kg):", min_value=1.0, max_value=120.0, value=12.0)
    drug_name = st.selectbox("Odaberite lijek:", list(DRUG_DATABASE.keys()))
with col2:
    age_months = st.number_input("Starost (mjeseci):", min_value=0, max_value=156, value=24)
    start_time = st.time_input("Vrijeme prve doze:", value=datetime.now().time())

data = DRUG_DATABASE[drug_name]

if st.button("IZRAČUNAJ"):
    st.divider()
    
    # Izračun limita
    max_mg_24h = min(weight * data["dnevna_mg_kg"], data["max_dan_fiksno"])
    broj_doza = 24 // data["interval"]
    
    # Prilagođavanje za Paracetamol (2-3mj)
    if "Paracetamol" in drug_name and 2 <= age_months <= 3:
        broj_doza = 2
        max_mg_24h = (weight * 15) * 2 
    
    pojedinacna_mg = max_mg_24h / broj_doza

    # Prikaz glavne doze
    c1, c2 = st.columns(2)
    if data["tip"] in ["sirup", "antibiotik"]:
        final_ml = round((pojedinacna_mg * 5) / data["mg_u_5ml"], 1)
        max_ml_24h = round((max_mg_24h * 5) / data["mg_u_5ml"], 1)
        
        c1.metric("Pojedinačna doza", f"{final_ml} ml", f"{round(pojedinacna_mg, 1)} mg")
        c2.metric("Maksimalno u 24h", f"{max_ml_24h} ml", f"{round(max_mg_24h, 1)} mg")
        doza_ispis = f"{final_ml} ml ({round(pojedinacna_mg, 1)} mg)"
    else:
        c1.metric("Pojedinačna doza", "1 čepić", f"{data['mg_u_jedinici']} mg")
        c2.metric("Maksimalno u 24h", f"{broj_doza} kom", f"{round(max_mg_24h, 1)} mg")
        doza_ispis = f"1 čepić ({data['mg_u_jedinici']} mg)"

    # Satnica
    st.subheader("⏰ Plan davanja (24h):")
    current_time = datetime.combine(datetime.today(), start_time)
    for i in range(broj_doza):
        st.success(f"**{i+1}. doza** u **{current_time.strftime('%H:%M')}** — Doza: {doza_ispis}")
        current_time += timedelta(hours=data["interval"])

    # Sigurnosni limit u crvenoj zoni
    st.divider()
    st.error(f"⚠️ **SIGURNOSNI LIMIT (24 sata):**")
    if data["tip"] in ["sirup", "antibiotik"]:
        st.write(f"Za težinu od **{weight}kg**, apsolutni dnevni maksimum je **{max_ml_24h} ml** (ukupno {round(max_mg_24h, 1)} mg).")
    else:
        st.write(f"Za težinu od **{weight}kg**, ne prelaziti **{broj_doza} čepića** (ukupno {round(max_mg_24h, 1)} mg) dnevno.")

    with st.expander("ℹ️ Napomene"):
        if data["napomena"]: st.info(data["napomena"])
        st.write("- Ako temperatura i dalje raste, obavezno kontaktirati ljekara.")
        st.write("- Voditi računa da se djetetu ne daje više lijekova sa istom aktivnom tvari istovremeno.")

st.caption("PediMed Safe v1.0 | Uvijek provjerite doze sa ljekarom.")
