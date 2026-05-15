import streamlit as st
from datetime import datetime, timedelta

# Baza podataka: [DNEVNA_doza_mg_kg, max_dnevna_mg, mg_u_jedinici, interval_sati, tip]
DRUG_DATABASE = {
    # ANALGETICI / ANTIPIRETIKI (Sirupi)
    "Paracetamol sirup (120mg/5ml)": [60, 4000, 120, 6, "sirup"],
    "Ibuprofen sirup (100mg/5ml)": [30, 1200, 100, 8, "sirup"],
    
    # ČEPIĆI (Vraćeni i dopunjeni)
    "Paracetamol čepići (120mg)": [60, 1000, 120, 6, "supozitorija"],
    "Paracetamol čepići (250mg)": [60, 2000, 250, 6, "supozitorija"],
    "Ibuprofen čepići (60mg)": [30, 600, 60, 8, "supozitorija"],
    "Ibuprofen čepići (125mg)": [30, 1200, 125, 8, "supozitorija"],
    "Diklofenak čepići (12.5mg)": [3, 12.5, 12.5, 12, "supozitorija"],
    
    # ANTIBIOTICI
    "Ospen / Penicilin V (250mg/5ml)": [50, 2000, 250, 8, "antibiotik"],
    "Amoksicilin (250mg/5ml)": [50, 1500, 250, 8, "antibiotik"],
    "Amoksicilin+Klavulonska kis. (400mg+57mg/5ml)": [45, 1000, 400, 12, "antibiotik"],
    "Cefaleksin (250mg/5ml)": [50, 2000, 250, 8, "antibiotik"],
    "Cefuroksim (125mg/5ml)": [30, 1000, 125, 12, "antibiotik"],
    "Cefiksim (100mg/5ml)": [8, 400, 100, 24, "antibiotik"],
    "Azitromicin (200mg/5ml)": [10, 500, 200, 24, "antibiotik"],
}

st.set_page_config(page_title="MedCalc Pro", page_icon="💊", layout="centered")
st.title("💊 Sveobuhvatni Kalkulator Doza")

# 1. Unos podataka
col_1, col_2 = st.columns(2)
with col_1:
    weight = st.number_input("Težina pacijenta (kg):", min_value=2.0, max_value=120.0, value=15.0)
    drug_name = st.selectbox("Odaberite lijek ili čepić:", list(DRUG_DATABASE.keys()))
with col_2:
    start_time = st.time_input("Vrijeme prve doze:", value=datetime.now().time())

# Dohvatanje podataka
dnevna_mg_kg, max_dnevna, mg_jedinica, interval, tip = DRUG_DATABASE[drug_name]

if st.button("IZRAČUNAJ"):
    # Matematika
    broj_doza = 24 // interval
    ukupna_mg_dan = min(weight * dnevna_mg_kg, max_dnevna)
    pojedinacna_mg = ukupna_mg_dan / broj_doza
    
    st.divider()

    # Prikaz rezultata
    res1, res2 = st.columns(2)
    
    if tip in ["sirup", "antibiotik"]:
        final_ml = round((pojedinacna_mg * 5) / mg_jedinica, 1)
        res1.metric("Pojedinačna doza (ml)", f"{final_ml} ml")
        res2.metric("Interval", f"Svakih {interval} h")
    else:
        # Logika za čepiće - provjera adekvatnosti
        idealna_pojedinacna = pojedinacna_mg
        res1.metric("Pojedinačna doza", "1 čepić")
        res2.metric("Snaga čepića", f"{mg_jedinica} mg")
        
        # Sigurnosna provjera za čepiće
        razlika = abs(idealna_pojedinacna - mg_jedinica) / mg_jedinica
        if razlika > 0.25:
            st.warning(f"⚠️ Pažnja: Ovaj čepić ({mg_jedinica}mg) odstupa od idealne doze za težinu djeteta ({round(idealna_pojedinacna)}mg).")

    # 3. Satnica
    st.subheader("📅 Plan davanja doza:")
    current_time = datetime.combine(datetime.today(), start_time)
    
    for i in range(broj_doza):
        st.success(f"**Doza {i+1}** — u **{current_time.strftime('%H:%M')}**")
        current_time += timedelta(hours=interval)

    # 4. Dodatne napomene
    with st.expander("Važne napomene za ovaj lijek"):
        if tip == "supozitorija":
            st.write("- Čepići se ne smiju sjeći ili poloviti.")
        if "Ospen" in drug_name:
            st.write("- Uzimati na prazan stomak (1h prije ili 2h poslije jela).")
        if "Azitromicin" in drug_name or "Cefiksim" in drug_name:
            st.write("- Uzima se samo jednom dnevno u isto vrijeme.")
        st.write("- U slučaju povraćanja unutar 20 min od uzimanja, konsultovati ljekara o ponavljanju doze.")
