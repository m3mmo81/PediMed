import streamlit as st
from datetime import datetime, timedelta

# --- BAZA PODATAKA ---
DRUG_DATABASE = {
    "Neofen / Ibuprofen (100mg/5ml)": {
        "dnevna_mg_kg": 25, 
        "max_pojedinacna_mg": 300,
        "mg_u_5ml": 100,
        "interval": 6, 
        "tip": "sirup",
        "napomena": "Razmak ne smije biti manji od 4h. Dojenčad 3-12 mj: max 3 puta dnevno."
    },
    "Paracetamol sirup (120mg/5ml)": {"dnevna_mg_kg": 60, "max_pojedinacna_mg": 1000, "mg_u_5ml": 120, "interval": 6, "tip": "sirup", "napomena": ""},
    "Paracetamol čepići (120mg)": {"dnevna_mg_kg": 60, "max_pojedinacna_mg": 120, "mg_u_jedinici": 120, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Paracetamol čepići (250mg)": {"dnevna_mg_kg": 60, "max_pojedinacna_mg": 250, "mg_u_jedinici": 250, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Ibuprofen čepići (60mg)": {"dnevna_mg_kg": 30, "max_pojedinacna_mg": 60, "mg_u_jedinici": 60, "interval": 8, "tip": "supozitorija", "napomena": ""},
    "Ibuprofen čepići (125mg)": {"dnevna_mg_kg": 30, "max_pojedinacna_mg": 125, "mg_u_jedinici": 125, "interval": 8, "tip": "supozitorija", "napomena": ""},
    "Diklofenak čepići (12.5mg)": {"dnevna_mg_kg": 3, "max_pojedinacna_mg": 12.5, "mg_u_jedinici": 12.5, "interval": 12, "tip": "supozitorija", "napomena": ""},
    "Ospen / Penicilin V (250mg/5ml)": {"dnevna_mg_kg": 50, "max_pojedinacna_mg": 2000, "mg_u_5ml": 250, "interval": 8, "tip": "antibiotik", "napomena": "Uzeti 1h prije ili 2h poslije jela."},
    "Amoksicilin (250mg/5ml)": {"dnevna_mg_kg": 50, "max_pojedinacna_mg": 1500, "mg_u_5ml": 250, "interval": 8, "tip": "antibiotik", "napomena": ""},
    "Amoksicilin+Klavulonska kis. (400mg/5ml)": {"dnevna_mg_kg": 45, "max_pojedinacna_mg": 1000, "mg_u_5ml": 400, "interval": 12, "tip": "antibiotik", "napomena": ""},
    "Cefaleksin (250mg/5ml)": {"dnevna_mg_kg": 50, "max_pojedinacna_mg": 2000, "mg_u_5ml": 250, "interval": 8, "tip": "antibiotik", "napomena": ""},
    "Cefuroksim (125mg/5ml)": {"dnevna_mg_kg": 30, "max_pojedinacna_mg": 1000, "mg_u_5ml": 125, "interval": 12, "tip": "antibiotik", "napomena": ""},
    "Cefiksim (100mg/5ml)": {"dnevna_mg_kg": 8, "max_pojedinacna_mg": 400, "mg_u_5ml": 100, "interval": 24, "tip": "antibiotik", "napomena": ""},
    "Azitromicin (200mg/5ml)": {"dnevna_mg_kg": 10, "max_pojedinacna_mg": 500, "mg_u_5ml": 200, "interval": 24, "tip": "antibiotik", "napomena": ""},
}

st.set_page_config(page_title="PediMed Pro", page_icon="💊")
st.title("💊 PediMed: Dozator sa dvostrukom provjerom")

# 1. UNOS PODATAKA
col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("Težina pacijenta (kg):", min_value=2.0, max_value=120.0, value=12.0)
    drug_name = st.selectbox("Odaberite lijek:", list(DRUG_DATABASE.keys()))
with col2:
    start_time = st.time_input("Vrijeme prve doze:", value=datetime.now().time())

# Dohvatanje podataka
data = DRUG_DATABASE[drug_name]

if st.button("IZRAČUNAJ"):
    # Matematika
    broj_doza = 24 // data["interval"]
    ukupna_mg_dan = min(weight * data["dnevna_mg_kg"], data.get("max_dnevna_mg", 4000))
    pojedinacna_mg = min(ukupna_mg_dan / broj_doza, data["max_pojedinacna_mg"])
    
    st.divider()

    # 2. PRIKAZ REZULTATA
    r1, r2 = st.columns(2)
    
    if data["tip"] in ["sirup", "antibiotik"]:
        final_ml = round((pojedinacna_mg * 5) / data["mg_u_5ml"], 1)
        # Prikaz ml i mg zajedno
        r1.metric("Pojedinačna doza (ml + mg)", f"{final_ml} ml", f"{round(pojedinacna_mg, 1)} mg")
        doza_ispis = f"{final_ml} ml ({round(pojedinacna_mg, 1)} mg)"
    else:
        r1.metric("Pojedinačna doza", "1 čepić", f"{data['mg_u_jedinici']} mg")
        doza_ispis = f"1 čepić ({data['mg_u_jedinici']} mg)"
        
    r2.metric("Razmak davanja", f"Svakih {data['interval']} h")

    # 3. SATNICA
    st.subheader("⏰ Plan davanja i doze:")
    current_time = datetime.combine(datetime.today(), start_time)
    for i in range(broj_doza):
        st.success(f"**Doza {i+1}** u **{current_time.strftime('%H:%M')}** — Doza: **{doza_ispis}**")
        current_time += timedelta(hours=data["interval"])

    # 4. NAPOMENE
    st.divider()
    with st.expander("ℹ️ Detaljne upute"):
        if data["tip"] == "supozitorija":
            st.error("Primjena: REKTALNO (u anus).")
        else:
            st.write(f"- Za težinu od **{weight}kg**, jedna doza sadrži **{round(pojedinacna_mg, 1)} mg** aktivne tvari.")
            st.write("- Ako dijete povrati sirup unutar 20 min, konsultujte ljekara.")
        
        if data["napomena"]:
            st.info(data["napomena"])

st.caption("Uvijek provjerite dozu sa ljekarom. Aplikacija služi za informativni izračun.")

