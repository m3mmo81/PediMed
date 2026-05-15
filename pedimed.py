import streamlit as st
from datetime import datetime, timedelta

# --- BAZA PODATAKA ---
# Format: "Ime": [DNEVNA_doza_mg_kg, max_dnevna_mg, mg_u_jedinici, interval_sati, tip]
DRUG_DATABASE = {
    # ANALGETICI / ANTIPIRETIKI (Sirupi)
    "Paracetamol sirup (120mg/5ml)": [60, 4000, 120, 6, "sirup"],
    "Ibuprofen sirup (100mg/5ml)": [30, 1200, 100, 8, "sirup"],
    
    # ČEPIĆI (Supozitorije)
    "Paracetamol čepići (120mg)": [60, 1000, 120, 6, "supozitorija"],
    "Paracetamol čepići (250mg)": [60, 2000, 250, 6, "supozitorija"],
    "Ibuprofen čepići (60mg)": [30, 600, 60, 8, "supozitorija"],
    "Ibuprofen čepići (125mg)": [30, 1200, 125, 8, "supozitorija"],
    "Diklofenak čepići (12.5mg)": [3, 12.5, 12.5, 12, "supozitorija"],
    
    # ANTIBIOTICI
    "Ospen / Penicilin V (250mg/5ml)": [50, 2000, 250, 8, "antibiotik"],
    "Amoksicilin (250mg/5ml)": [50, 1500, 250, 8, "antibiotik"],
    "Amoksicilin+Klavulonska kis. (400mg/5ml)": [45, 1000, 400, 12, "antibiotik"],
    "Cefaleksin (250mg/5ml)": [50, 2000, 250, 8, "antibiotik"],
    "Cefuroksim (125mg/5ml)": [30, 1000, 125, 12, "antibiotik"],
    "Cefiksim (100mg/5ml)": [8, 400, 100, 24, "antibiotik"],
    "Azitromicin (200mg/5ml)": [10, 500, 200, 24, "antibiotik"],
}

st.set_page_config(page_title="PediMed Dozator", page_icon="💊")
st.title("💊 PediMed: Kalkulator Doziranja")

# 1. UNOS PODATAKA
col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("Težina pacijenta (kg):", min_value=2.0, max_value=120.0, value=12.0)
    drug_name = st.selectbox("Odaberite lijek:", list(DRUG_DATABASE.keys()))
with col2:
    start_time = st.time_input("Vrijeme prve doze:", value=datetime.now().time())

# Dohvatanje podataka iz baze
dnevna_mg_kg, max_dnevna, mg_jedinica, interval, tip = DRUG_DATABASE[drug_name]

if st.button("IZRAČUNAJ DOZU I PLAN"):
    # Matematika doziranja
    broj_doza_u_24h = 24 // interval
    ukupna_mg_dan = min(weight * dnevna_mg_kg, max_dnevna)
    pojedinacna_mg = ukupna_mg_dan / broj_doza_u_24h
    
    st.divider()

    # 2. PRIKAZ REZULTATA
    res1, res2 = st.columns(2)
    
    if tip in ["sirup", "antibiotik"]:
        final_ml = round((pojedinacna_mg * 5) / mg_jedinica, 1)
        res1.metric("Pojedinačna doza", f"{final_ml} ml")
        res2.metric("Učestalost", f"Svakih {interval} h")
    else:
        # Prikaz za čepiće
        res1.metric("Pojedinačna doza", "1 čepić")
        res2.metric("Snaga čepića", f"{mg_jedinica} mg")
        
        # Sigurnosna provjera snage čepića
        razlika = abs(pojedinacna_mg - mg_jedinica) / mg_jedinica
        if razlika > 0.25:
            st.warning(f"⚠️ Napomena: Idealna doza za ovu težinu je oko {round(pojedinacna_mg)}mg. Odabrani čepić ima {mg_jedinica}mg.")

    # 3. SATNICA
    st.subheader("⏰ Raspored davanja:")
    current_time = datetime.combine(datetime.today(), start_time)
    
    for i in range(broj_doza_u_24h):
        st.success(f"**{i+1}. doza** u **{current_time.strftime('%H:%M')}**")
        current_time += timedelta(hours=interval)

    # 4. ISPRAVLJENE NAPOMENE
    st.divider()
    with st.expander("ℹ️ Važne napomene za ovaj oblik lijeka"):
        if tip == "supozitorija":
            st.error("**OBLIK PRIMJENE:** Ovaj lijek je čepić i daje se REKTALNO (u anus). Ne gutati!")
            st.write("- Čepići se ne smiju poloviti ili sjeći.")
            st.write("- Ako dijete ima stolicu unutar 20 minuta od postavljanja čepića, on se vjerovatno nije apsorbovao. Konsultujte ljekara.")
        else:
            st.write("- **POVRAĆANJE:** Ako dijete povrati sirup unutar 20 minuta od uzimanja, konsultujte ljekara o ponavljanju doze.")
            
        if tip == "antibiotik":
            st.warning("- **TERAPIJA:** Antibiotik se mora popiti do kraja po uputi ljekara, čak i ako simptomi nestanu ranije.")
        
        if "Ospen" in drug_name:
            st.write("- **Ospen savjet:** Najbolje uzeti na prazan želudac (1h prije ili 2h poslije jela).")

st.markdown("---")
st.caption("Ovaj alat je informativnog karaktera. Uvijek potvrdite dozu sa službenim receptom ljekara.")

