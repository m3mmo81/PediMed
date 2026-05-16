import streamlit as st
from datetime import datetime, timedelta, time

# --- BAZA PODATAKA ---
# "dnevna_mg_kg" predstavlja početnu preporučenu terapijsku dozu (40 mg/kg za paracetamol, 20 mg/kg za ibuprofen)
DRUG_DATABASE = {
    "Paracetamol sirup (120mg/5ml)": {
        "dnevna_mg_kg": 40, "max_dan_fiksno": 4000, "mg_u_5ml": 120, "interval": 6, 
        "tip": "sirup", "napomena": "Razmak min 4h. Max 4 doze u 24h."
    },
    "Neofen / Ibuprofen sirup (100mg/5ml)": {
        "dnevna_mg_kg": 20, "max_dan_fiksno": 1200, "mg_u_5ml": 100, "interval": 6, 
        "tip": "sirup", "napomena": "Razmak min 4h. Dojenčad 3-12 mj: max 3 doze."
    },
    "Paracetamol čepići (80mg)": {"dnevna_mg_kg": 40, "max_dan_fiksno": 800, "mg_u_jedinici": 80, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Paracetamol čepići (120mg)": {
        "dnevna_mg_kg": 40, "max_dan_fiksno": 1000, "mg_u_jedinici": 120, "interval": 6, 
        "tip": "supozitorija", 
        "napomena": "Isključivo cijeli čepići (ne lomiti). Nije prikladno u slučaju proljeva."
    },
    "Paracetamol čepići (150mg)": {"dnevna_mg_kg": 40, "max_dan_fiksno": 1200, "mg_u_jedinici": 150, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Paracetamol čepići (250mg)": {"dnevna_mg_kg": 40, "max_dan_fiksno": 2000, "mg_u_jedinici": 250, "interval": 6, "tip": "supozitorija", "napomena": ""},
    "Ibuprofen čepići (60mg)": {
        "dnevna_mg_kg": 30, "max_dan_fiksno": 600, "mg_u_jedinici": 60, "interval": 8, 
        "tip": "supozitorija", 
        "napomena": "Ne koristiti za djecu <6kg. Razmak min 6-8h. Ne lomiti čepiće."
    },
    "Ibuprofen čepići (125mg)": {"dnevna_mg_kg": 30, "max_dan_fiksno": 1200, "mg_u_jedinici": 125, "interval": 8, "tip": "supozitorija", "napomena": ""}
}

st.set_page_config(page_title="PediMed Safe", page_icon="⚖️", layout="centered")

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

    # --- DIREKTNA KLINIČKA VERIFIKACIJA I FILTRIRANJE ČEPIĆA ---
    if "Paracetamol čepići" in drug_name:
        min_pojedinacna_efikasna = (weight * 30) / 4
        max_pojedinacna_sigurna = (weight * 60) / 4
        odabrana_jacina = data["mg_u_jedinici"]
        
        adekvatni_cepici = []
        if (weight * 60 / 4) >= 80 >= (weight * 30 / 4 - 15): adekvatni_cepici.append("80mg")
        if (weight * 60 / 4) >= 120 >= (weight * 30 / 4 - 20): adekvatni_cepici.append("120mg")
        if (weight * 60 / 4) >= 150 >= (weight * 30 / 4 - 25): adekvatni_cepici.append("150mg")
        if (weight * 60 / 4) >= 250 >= (weight * 30 / 4 - 40): adekvatni_cepici.append("250mg")
        
        preporuka_tekst = " ili ".join(adekvatni_cepici) if adekvatni_cepici else "konsultaciju sa ljekarom"

        if odabrana_jacina < min_pojedinacna_efikasna and abs(odabrana_jacina - min_pojedinacna_efikasna) > 15:
            st.error(f"❌ **Subdoziranje! Odabrani čepić ({odabrana_jacina}mg) je preslab za težinu od {weight} kg.**")
            st.info(f"💡 **Klinički savjet:** Davanje ovog čepića neće efikasno spustiti temperaturu. Za težinu vašeg djeteta, adekvatan izbor su **Paracetamol čepići od {preporuka_tekst}**.")
            st.stop()
            
        if odabrana_jacina > max_pojedinacna_sigurna:
            st.error(f"❌ **Previsoka doza! Odabrani čepić ({odabrana_jacina}mg) je prejak za težinu od {weight} kg.**")
            st.info(f"💡 **Klinički savjet:** Za težinu vašeg djeteta od {weight} kg, adekvatan i siguran izbor su **Paracetamol čepići od {preporuka_tekst}**.")
            st.stop()

    # --- NOVA LOGIKA: DIREKTNA VERIFIKACIJA ZA IBUPROFEN ČEPIĆE ---
    elif "Ibuprofen čepići" in drug_name:
        # Terapijski opseg za ibuprofen na dan je 20 do 30 mg/kg
        min_dnevna_ibu = weight * 20
        max_dnevna_ibu = weight * 30
        odabrana_jacina = data["mg_u_jedinici"]
        broj_davanja = 24 // data["interval"]  # Za ibuprofen sa intervalom 8, ovo je 3 davanja dnevno
        
        # Izračunavamo ukupnu dnevnu dozu koju bi dijete unijelo sa odabranim čepićem (3 čepića dnevno)
        ukupni_dnevni_unos = odabrana_jacina * broj_davanja
        
        # Provjera koji čepići uopšte klinički odgovaraju za ovu težinu u rasponu 20-30 mg/kg/dan
        adekvatni_ibu_cepici = []
        if min_dnevna_ibu <= (60 * 3) <= max_dnevna_ibu:
            adekvatni_ibu_cepici.append("60mg")
        if min_dnevna_ibu <= (125 * 3) <= max_dnevna_ibu:
            adekvatni_ibu_cepici.append("125mg")
            
        preporuka_ibu_tekst = " ili ".join(adekvatni_ibu_cepici) if adekvatni_ibu_cepici else None

        # Ako trenutno odabrani čepić ne upada u siguran opseg od 20-30 mg/kg/dan
        if not (min_dnevna_ibu <= ukupni_dnevni_unos <= max_dnevna_ibu):
            st.error(f"❌ **Neodgovarajuće doziranje čepića!**")
            
            if ukupni_dnevni_unos < min_dnevna_ibu:
                st.write(f"Odabrani čepić od **{odabrana_jacina}mg** daje premalu i neefikasnu dozu za težinu od {weight} kg.")
            elif ukupni_dnevni_unos > max_dnevna_ibu:
                st.write(f"Odabrani čepić od **{odabrana_jacina}mg** prekoračuje maksimalnu dozvoljenu dozu od **{max_dnevna_ibu:.1f} mg/dan** za težinu od {weight} kg.")
            
            if preporuka_ibu_tekst:
                st.info(f"💡 **Klinički savjet:** Za težinu vašeg djeteta, u terapeutski opseg se uklapaju **Ibuprofen čepići od {preporuka_ibu_tekst}**.")
            else:
                st.warning(
                    f"💡 **Klinički savjet:** S obzirom na težinu djeteta od **{weight} kg**, nijedan od dostupnih čepića na tržištu (60mg i 125mg) "
                    f"ne može pokriti potrebe unutar sigurnog opsega (Maksimum: {max_dnevna_ibu:.1f} mg/dan).\n\n"
                    "👉 **Preporučuje se prelazak na Neofen / Ibuprofen sirup** kako bi se doza mogla precizno izmjeriti u mililitrima!"
                )
            st.stop()

    st.divider()
    
    # Terapijski proračun (preporučene doze)
    terapijska_mg_24h = min(weight * data["dnevna_mg_kg"], data["max_dan_fiksno"])
    broj_doza = 24 // data["interval"]
    pojedinacna_mg = terapijska_mg_24h / broj_doza
    
    # --- LOGIKA PRORAČUNA MAKSIMALNIH GRANICA I RASPONA ---
    if "Paracetamol sirup" in drug_name:
        terapijska_ml_24h = round((terapijska_mg_24h * 5) / 120, 1)
        apsolutni_max_24h = min(weight * 60, data["max_dan_fiksno"])
        apsolutni_max_ml_24h = round((apsolutni_max_24h * 5) / 120, 1)
        
        max_pojedinacna_mg = apsolutni_max_24h / broj_doza
        max_pojedinacna_ml = round((max_pojedinacna_mg * 5) / 120, 1)
        preporucena_ml = round((pojedinacna_mg * 5) / 120, 1)
        
        naslov_lijeva = "🔷 RASPON POJEDINAČNE DOZE (40-60 mg/kg):"
        sadrzaj_lijeva = f"**{preporucena_ml} ml** do **{max_pojedinacna_ml} ml**\n\n({round(pojedinacna_mg, 1)} - {round(max_pojedinacna_mg, 1)} mg)"
        plan_ispis = f"{preporucena_ml} ml ({round(pojedinacna_mg, 1)} mg) [Preporučeno]"
        
        naslov_desna = "🟩 UKUPNO KROZ 24 SATA:"
        sadrzaj_desna = f"**Preporučeno:** {round(terapijska_mg_24h, 1)} mg ({terapijska_ml_24h} ml)\n\n**Maksimalno (60 mg/kg):** {round(apsolutni_max_24h, 1)} mg ({apsolutni_max_ml_24h} ml)"
        
    elif "Ibuprofen sirup" in drug_name:
        terapijska_ml_24h = round((terapijska_mg_24h * 5) / 100, 1)
        apsolutni_max_24h = min(weight * 30, data["max_dan_fiksno"])
        apsolutni_max_ml_24h = round((apsolutni_max_24h * 5) / 100, 1)
        
        max_pojedinacna_mg = apsolutni_max_24h / broj_doza
        max_pojedinacna_ml = round((max_pojedinacna_mg * 5) / 100, 1)
        preporucena_ml = round((pojedinacna_mg * 5) / 100, 1)
        
        naslov_lijeva = "🔷 RASPON POJEDINAČNE DOZE (20-30 mg/kg):"
        sadrzaj_lijeva = f"**{preporucena_ml} ml** do **{max_pojedinacna_ml} ml**\n\n({round(pojedinacna_mg, 1)} - {round(max_pojedinacna_mg, 1)} mg)"
        plan_ispis = f"{preporucena_ml} ml ({round(pojedinacna_mg, 1)} mg) [Preporučeno]"
        
        naslov_desna = "🟩 UKUPNO KROZ 24 SATA:"
        sadrzaj_desna = f"**Preporučeno:** {round(terapijska_mg_24h, 1)} mg ({terapijska_ml_24h} ml)\n\n**Maksimalno (30 mg/kg):** {round(apsolutni_max_24h, 1)} mg ({apsolutni_max_ml_24h} ml)"
        
    else:
        # Čepići
        apsolutni_max_24h = min(weight * 60, data["max_dan_fiksno"]) if "Paracetamol" in drug_name else min(weight * 30, data["max_dan_fiksno"])
        
        naslov_lijeva = "🔷 POJEDINAČNA DOZA ČEPIĆA:"
        sadrzaj_lijeva = f"**1 čepić**\n\n({data['mg_u_jedinici']} mg)"
        plan_ispis = f"1 čepić ({data['mg_u_jedinici']} mg)"
        
        naslov_desna = "🟩 UKUPNO KROZ 24 SATA:"
        sadrzaj_desna = f"**Unos odabranog čepića ({broj_doza}x dnevno):** {data['mg_u_jedinici'] * broj_doza} mg\n\n**Apsolutni limit djeteta:** {round(apsolutni_max_24h, 1)} mg"

    # --- 3. PRIKAZ UGRAĐENIH STREAMLIT OKVIRA ---
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.caption(naslov_lijeva)
            st.markdown(sadrzaj_lijeva)
        
    with c2:
        with st.container(border=True):
            st.caption(naslov_desna)
            st.markdown(sadrzaj_desna)

    st.write("") 

    # Satnica
    st.subheader("⏰ Plan davanja (24h) - Na bazi odabranog oblika:")
    current_time = datetime.combine(datetime.today(), start_time)
    for i in range(broj_doza):
        st.success(f"**{i+1}. doza** u **{current_time.strftime('%H:%M')}** — Doza: {plan_ispis}")
        current_time += timedelta(hours=data["interval"])

    st.divider()
    st.error("⚠️ **APSOLUTNI SIGURNOSNI LIMIT (Maksimalna doza):**")
    if "Paracetamol sirup" in drug_name:
        st.write(f"Za težinu od **{weight} kg**, apsolutni dnevni maksimum paracetamola iznosi **{apsolutni_max_ml_24h} ml** (ukupno {round(apsolutni_max_24h, 1)} mg na bazi 60 mg/kg/dan).")
    elif "Ibuprofen sirup" in drug_name:
        st.write(f"Za težinu od **{weight} kg**, maksimalna dopuštena dnevna doza ibuprofena iznosi **{apsolutni_max_ml_24h} ml** (ukupno {round(apsolutni_max_24h, 1)} mg na bazi 30 mg/kg/dan).")
    else:
        limit_tekst = "60 mg/kg/dan" if "Paracetamol" in drug_name else "30 mg/kg/dan"
        st.write(f"Za težinu od **{weight} kg**, apsolutni dnevni maksimum iznosi **{round(apsolutni_max_24h, 1)} mg** ({limit_tekst}).")
    st.write("Nikada ne prelazite ovaj limit u slučaju da kombinujete različite oblike istog lijeka!")

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
    Korištenjem ove aplikacije prihvatate da autor ne snosi odgovornost za eventualne greške u aplikaciji lijeka.
    """)

st.markdown("""
---
📩 **Trebate savjet ili imate pitanje?** Možete me kontaktirati direktno putem kontakt forme na mojoj web stranici:  
[**www.drkarabeg.ba**](https://drkarabeg.ba)
""", unsafe_allow_html=True)

st.markdown(
    "<div style='font-size: 0.8em; color: gray; text-align: center; margin-top: 20px;'>"
    "© " + str(datetime.now().year) + " Created by <a href='https://drkarabeg.ba' target='_blank' style='color: gray; text-decoration: underline;'>Karabeg dr Kemal</a> | PediMed Safe v1.5 |"
    "</div>", 
    unsafe_allow_html=True
)
