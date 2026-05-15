import streamlit as st
from datetime import datetime, timedelta

# --- AŽURIRANA BAZA PODATAKA ---
DRUG_DATABASE = {
    "Paracetamol JGL sirup (120mg/5ml)": {
        "dnevna_mg_kg": 60,
        "max_dnevna_mg": 4000,
        "mg_u_5ml": 120,
        "interval": 6, 
        "tip": "sirup",
        "napomena": "Razmak min 4h. Max 4 doze u 24h. Ne davati duže od 3 dana bez ljekara."
    },
    "Neofen / Ibuprofen (100mg/5ml)": {
        "dnevna_mg_kg": 25, 
        "max_pojedinacna_mg": 300,
        "mg_u_5ml": 100,
        "interval": 6, 
        "tip": "sirup",
        "napomena": "Razmak min 4h. Dojenčad 3-12 mj: max 3 puta dnevno."
    },
    "Paracetamol čepići (120mg)": {"dnevna_mg_kg": 60, "max_pojedinacna_mg": 120, "mg_u_jedinici": 120, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Paracetamol čepići (250mg)": {"dnevna_mg_kg": 60, "max_pojedinacna_mg": 250, "mg_u_jedinici": 250, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Ibuprofen čepići (60mg)": {"dnevna_mg_kg": 30, "max_pojedinacna_mg": 60, "mg_u_jedinici": 60, "interval": 8, "tip": "supozitorija", "napomena": ""},
    "Ibuprofen čepići (125mg)": {"dnevna_mg_kg": 30, "max_pojedinacna_mg": 125, "mg_u_jedinici": 125, "interval": 8, "tip": "supozitorija", "napomena": ""},
    "Ospen / Penicilin V (250mg/5ml)": {"dnevna_mg_kg": 50, "max_pojedinacna_mg": 2000, "mg_u_5ml": 250, "interval": 8, "tip": "antibiotik", "napomena": "Uzeti 1h prije ili 2h poslije jela."},
    "Cefaleksin (250mg/5ml)": {"dnevna_mg_kg": 50, "max_pojedinacna_mg": 2000, "mg_u_5ml": 250, "interval": 8, "tip": "antibiotik", "napomena": ""},
}

st.set_page_config(page_title="PediMed Pro", page_icon="💊")
st.title("💊 PediMed: Dozator")

# 1. UNOS PODATAKA
col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("Težina djeteta (kg):", min_value=1.0, max_value=120.0, value=10.0)
    drug_name = st.selectbox("Odaberite lijek:", list(DRUG_DATABASE.keys()))
with col2:
    age_months = st.number_input("Starost djeteta (mjeseci):", min_value=0, max_value=156, value=12)
    start_time = st.time_input("Vrijeme prve doze:", value=datetime.now().time())

data = DRUG_DATABASE[drug_name]

if st.button("IZRAČUNAJ"):
    st.divider()
    
    # Sigurnosne provjere za Paracetamol prema uputstvu
    if "Paracetamol" in drug_name and age_months < 2:
        st.error("❌ OPREZ: Paracetamol se ne smije davati dojenčadi ispod 2 mjeseca bez preporuke ljekara.")
    else:
        # Određivanje broja doza
        broj_doza = 24 // data["interval"]
        if "Paracetamol" in drug_name and 2 <= age_months <= 3:
            broj_doza = 2  # Max 2 doze za 2-3 mjeseca
            st.warning("⚠️ Za dojenčad 2-3 mj. dozvoljene su maksimalno 2 doze u 24h.")

        # Izračun
        ukupna_mg_dan = weight * data["dnevna_mg_kg"]
        pojedinacna_mg = min(ukupna_mg_dan / (24 // data["interval"]), data.get("max_pojedinacna_mg", 1000))
        
        # Prikaz rezultata
        r1, r2 = st.columns(2)
        if data["tip"] in ["sirup", "antibiotik"]:
            final_ml = round((pojedinacna_mg * 5) / data["mg_u_5ml"], 1)
            r1.metric("Pojedinačna doza", f"{final_ml} ml", f"{round(pojedinacna_mg, 1)} mg")
            doza_ispis = f"{final_ml} ml ({round(pojedinacna_mg, 1)} mg)"
        else:
            r1.metric("Pojedinačna doza", "1 čepić", f"{data['mg_u_jedinici']} mg")
            doza_ispis = f"1 čepić ({data['mg_u_jedinici']} mg)"
        
        r2.metric("Razmak", f"Svakih {data['interval']} h")

        # Satnica
        st.subheader("⏰ Plan davanja (24h):")
        current_time = datetime.combine(datetime.today(), start_time)
        for i in range(broj_doza):
            st.success(f"**{i+1}. doza** u **{current_time.strftime('%H:%M')}** — Doza: {doza_ispis}")
            current_time += timedelta(hours=data["interval"])

        # Napomene
        with st.expander("ℹ️ Važne upute za ovaj lijek"):
            if "Paracetamol" in drug_name:
                st.info("Nemojte prekoračiti 4 doze u 24 sata. Razmak mora biti najmanje 4 sata.")
                if age_months < 3:
                    st.warning("Ako je dijete prijevremeno rođeno i mlađe od 3 mj, obavezan je savjet ljekara.")
            if data["tip"] == "supozitorija":
                st.error("PRIMJENA: REKTALNO (u anus).")
            if data["napomena"]:
                st.write(data["napomena"])

st.caption("Aplikacija je informativnog karaktera. Dozu uvijek potvrdite sa ljekarom.")
