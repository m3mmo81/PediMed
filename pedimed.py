import streamlit as st
from datetime import datetime, timedelta, time

# --- BAZA PODATAKA SA LIMITIMA ---
DRUG_DATABASE = {
    "Paracetamol sirup (120mg/5ml)": {
        "dnevna_mg_kg": 60, "max_dan_fiksno": 4000, "mg_u_5ml": 120, "interval": 6, 
        "tip": "sirup", "napomena": "Razmak min 4h. Max 4 doze u 24h."
    },
    "Neofen / Ibuprofen sirup (100mg/5ml)": {
        "dnevna_mg_kg": 30, "max_dan_fiksno": 1200, "mg_u_5ml": 100, "interval": 6, 
        "tip": "sirup", "napomena": "Razmak min 4h. Dojenčad 3-12 mj: max 3 doze."
    },
    "Paracetamol čepići (80mg)": {"dnevna_mg_kg": 60, "max_dan_fiksno": 800, "mg_u_jedinici": 80, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Paracetamol čepići (120mg)": {
        "dnevna_mg_kg": 60, "max_dan_fiksno": 1000, "mg_u_jedinici": 120, "interval": 6, 
        "tip": "supozitorija", 
        "napomena": "Isključivo cijeli čepići (ne lomiti). Nije prikladno u slučaju proljeva."
    },
    "Paracetamol čepići (150mg)": {"dnevna_mg_kg": 60, "max_dan_fiksno": 1200, "mg_u_jedinici": 150, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Paracetamol čepići (250mg)": {"dnevna_mg_kg": 60, "max_dan_fiksno": 2000, "mg_u_jedinici": 250, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Ibuprofen čepići (60mg)": {
        "dnevna_mg_kg": 30, "max_dan_fiksno": 600, "mg_u_jedinici": 60, "interval": 8, 
        "tip": "supozitorija", 
        "napomena": "Ne koristiti za djecu <6kg. Razmak min 6-8h. Ne lomiti čepiće."
    },
    "Ibuprofen čepići (125mg)": {"dnevna_mg_kg": 30, "max_dan_fiksno": 1200, "mg_u_jedinici": 125, "interval": 8, "tip": "supozitorija", "napomena": ""},
}

st.set_page_config(page_title="PediMed Safe", page_icon="⚖️", layout="centered")

# --- POZDRAVNA PORUKA ---
st.info("👋 **Dobrodošli na PediMed.** Ovaj kalkulator je kreiran da vam olakša precizno doziranje lijekova za vaše najmlađe.")

st.title("⚖️ PediMed: Pedijatrijski Kalkulator Lijekova")

# 1. UNOS PODATAKA
col1, col2 = st.columns(2)

with col1:
    weight = st.number_input("Težina djeteta (kg):", min_value=1.0, max_value=120.0, value=12.0)
    drug_name = st.selectbox("Odaberite lijek:", list(DRUG_DATABASE.keys()))

with col2:
    st.markdown("**Starost djeteta (godine i mjeseci):**")
    age_col1, age_col2 = st.columns(2)
    with age_col1:
        years = st.number_input("Godine", min_value=0, max_value=18, value=2, label_visibility="collapsed")
    with age_col2:
        extra_months = st.number_input("Mjeseci", min_value=0, max_value=11, value=0, label_visibility="collapsed")
    
    total_months = (years * 12) + extra_months
    
    st.markdown("**Vrijeme prve doze (sati : minuti):**")
    trenutno = datetime.now()
    time_col1, time_col2 = st.columns(2)
    with time_col1:
        vrijeme_sati = st.number_input("Sati", min_value=0, max_value=23, value=trenutno.hour, label_visibility="collapsed")
    with time_col2:
        vrijeme_minuti = st.number_input("Minuti", min_value=0, max_value=59, value=trenutno.minute, label_visibility="collapsed")
    
    start_time = time(vrijeme_sati, vrijeme_minuti)

data = DRUG_DATABASE[drug_name]

if st.button("IZRAČUNAJ"):
    # --- VALIDACIJA ZA IBUPROFEN ČEPIĆE 60MG ---
    if drug_name == "Ibuprofen čepići (60mg)":
        if weight < 6.0:
            st.error("❌ Lijek se ne smije primjenjivati u djece tjelesne mase manje od 6,0 kg.")
            st.stop()
        if total_months < 3:
            st.warning("⚠️ Ne smije se koristiti u djece mlađe od 3 mjeseca bez savjeta liječnika.")

    st.divider()
    
    max_mg_24h = min(weight * data["dnevna_mg_kg"], data["max_dan_fiksno"])
    broj_doza = 24 // data["interval"]
    
    # Specifična logika za LUPOCET BABY / Paracetamol 120mg
    if drug_name == "Paracetamol čepići (120mg)":
        if 8 <= weight < 10:
            pojedinacna_mg = 120
            doza_ispis = "1 čepić (120 mg)"
        elif 10 <= weight <= 20:
            if (240 * broj_doza) <= max_mg_24h:
                pojedinacna_mg = 240
                doza_ispis = "1 do 2 čepića (120-240 mg)"
            else:
                pojedinacna_mg = 120
                doza_ispis = "1 čepić (120 mg)"
        else:
            pojedinacna_mg = (weight * 15)
            doza_ispis = f"{round(pojedinacna_mg, 1)} mg"
    else:
        # Standardna logika
        if "Paracetamol" in drug_name and 2 <= total_months <= 3:
            broj_doza = 2
            max_mg_24h = (weight * 15) * 2 
        pojedinacna_mg = max_mg_24h / broj_doza
        
        if data["tip"] == "sirup":
            final_ml = round((pojedinacna_mg * 5) / data["mg_u_5ml"], 1)
            doza_ispis = f"{final_ml} ml ({round(pojedinacna_mg, 1)} mg)"
        else:
            doza_ispis = f"1 čepić ({data['mg_u_jedinici']} mg)"

    # Prikaz rezultata
    c1, c2 = st.columns(2)
    c1.metric("Pojedinačna doza", doza_ispis)
    c2.metric("Maksimalno u 24h", f"{round(max_mg_24h, 1)} mg")

    st.subheader("⏰ Plan davanja (24h):")
    current_time = datetime.combine(datetime.today(), start_time)
    for i in range(broj_doza):
        st.success(f"**{i+1}. doza** u **{current_time.strftime('%H:%M')}** — Doza: {doza_ispis}")
        current_time += timedelta(hours=data["interval"])

    st.divider()
    st.error(f"⚠️ **SIGURNOSNI LIMIT (24 sata):**")
    st.write(f"Za težinu od **{weight}kg**, apsolutni dnevni maksimum je **{round(max_mg_24h, 1)} mg**.")

    with st.expander("ℹ️ Važne napomene za odabrani lijek"):
        if data["napomena"]: st.info(data["napomena"])
        if drug_name == "Ibuprofen čepići (60mg)":
            if 3 <= total_months <= 5:
                st.warning("Ako se simptomi ne povuku unutar 24 sata, obavezno potražiti savjet liječnika.")
            if total_months >= 6:
                st.warning("Ako je lijek potrebno uzimati duže od 3 dana, zatražiti savjet liječnika.")
        st.write("- **Opća napomena:** Ne miješati s drugim lijekovima iste aktivne tvari.")
        st.write("- U slučaju pogoršanja simptoma, odmah kontaktirati ljekara.")

# --- DUGI DISCLAIMER I KONTAKT SEKCIJA ---
st.divider()

with st.container():
    st.warning("⚠️ **VAŽNA NAPOMENA (DISCLAIMER):**")
    st.write("""
    Ova aplikacija je isključivo informativnog karaktera i služi kao pomoć pri izračunu doza prema uputama proizvođača. 
    **PediMed ne predstavlja zamjenu za ljekarski savjet, dijagnozu ili liječenje.** Uvijek se konsultujte sa ljekarom ili farmaceutom prije davanja bilo kojeg lijeka djetetu. 
    Korištenjem ove aplikacije prihvatate da autor ne snosi odgovornost za eventualne greške u primjeni lijeka.
    """)

st.markdown(f"""
---
📩 **Trebate savjet ili imate pitanje?** Možete me kontaktirati direktno putem kontakt forme na mojoj web stranici:  
[**www.drkarabeg.ba**](https://drkarabeg.ba)
""", unsafe_allow_html=True)

# KOREKCIJA: HTML formatiranje unutar st.markdown omogućava da tekst u st.caption (kroz HTML stil) sadrži funkcionalan link
st.markdown(
    f"<div style='font-size: 0.8em; color: gray; text-align: center; margin-top: 20px;'>"
    f"© {datetime.now().year} Created by <a href='https://drkarabeg.ba' target='_blank' style='color: gray; text-decoration: underline;'>Karabeg dr Kemal</a> | PediMed Safe v1.5 |"
    f"</div>", 
    unsafe_allow_html=True
)
