import streamlit as st
from datetime import datetime, timedelta, time, timezone

# --- BAZA PODATAKA ---
DRUG_DATABASE = {
    "Paracetamol sirup (120mg/5ml)": {
        "dnevna_mg_kg": 40, "max_dan_fiksno": 4000, "mg_u_5ml": 120, "interval": 6, 
        "tip": "sirup", "napomena": "Razmak min 4h. Max 4 doze u 24h."
    },
    "Neofen / Ibuprofen sirup (100mg/5ml)": {
        "dnevna_mg_kg": 20, "max_dan_fiksno": 1200, "mg_u_5ml": 100, "interval": 6, 
        "tip": "sirup", "napomena": "Razmak min 4h."
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
    "Ibuprofen čepići (125mg)": {"dnevna_mg_kg": 30, "max_dan_fiksno": 1200, "mg_u_jedinici": 125, "interval": 8, "tip": "supozitorija", "napomena": ""},
    "Voltaren / Diklofenak čepići (12,5mg)": {
        "dnevna_mg_kg": 2, "max_dan_fiksno": 150, "mg_u_jedinici": 12.5, "interval": 12, 
        "tip": "supozitorija", "napomena": "Isključivo cijeli čepići (ne lomiti). Dozira se 2 do 3 puta dnevno. Maksimalna dnevna doza je 3 mg/kg/dan."
    },
    "Voltaren / Diklofenak čepići (25mg)": {
        "dnevna_mg_kg": 2, "max_dan_fiksno": 150, "mg_u_jedinici": 25, "interval": 12, 
        "tip": "supozitorija", "napomena": "Isključivo cijeli čepići (ne lomiti). Dozira se 2 do 3 puta dnevno. Maksimalna dnevna doza je 3 mg/kg/dan."
    }
}

st.set_page_config(page_title="PediMed Safe", page_icon="⚖️", layout="centered")

st.info("👋 **Dobrodošli na PediMed.** Ovaj kalkulator je kreiran da vam olakša precizno doziranje lijekova za vaše najmlađe.")
st.title("⚖️ PediMed: Pedijatrijski Kalkulator Lijekova")

# Ručno postavljamo vremensku zonu za BiH (+2 sata u odnosu na UTC) bez vanjskih biblioteka
bih_zona = timezone(timedelta(hours=2))
trenutno = datetime.now(bih_zona)

# 1. UNOS PODATAKA WITH PERFECT ALIGNMENT (Sada pročišćeno bez uzrasta djeteta)
col1, col2 = st.columns(2)

with col1:
    weight = st.number_input("Težina djeteta (kg):", min_value=1.0, max_value=120.0, value=12.0)
    drug_name = st.selectbox("Odaberite lijek:", list(DRUG_DATABASE.keys()))

with col2:
    time_col1, time_col2 = st.columns(2)
    with time_col1:
        vrijeme_sati = st.number_input("Vrijeme prve doze (sati):", min_value=0, max_value=23, value=trenutno.hour)
    with time_col2:
        vrijeme_minuti = st.number_input("Vrijeme prve doze (minuti):", min_value=0, max_value=59, value=trenutno.minute)
    
    start_time = time(vrijeme_sati, vrijeme_minuti)

data = DRUG_DATABASE[drug_name]

if st.button("IZRAČUNAJ"):
    # --- VALIDACIJA ZA IBUPROFEN ČEPIĆE 6MG ---
    if drug_name == "Ibuprofen čepići (60mg)":
        if weight < 6.0:
            st.error("❌ Lijek se ne smije primjenjivati u djece tjelesne mase manje od 6,0 kg.")
            st.warning("⚠️ Ne smije se koristiti u dojenčadi mlađe od 3 mjeseca bez savjeta liječnika.")
            st.stop()

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

    # --- DINAMIČKA LOGIKA ZA IBUPROFEN ČEPIĆE (3x ILI 4x DNEVNO) ---
    elif "Ibuprofen čepići" in drug_name:
        min_dnevna_ibu = weight * 20
        max_dnevna_ibu = weight * 30
        odabrana_jacina = data["mg_u_jedinici"]
        
        validan_rezim_za_odabrani = None
        
        if min_dnevna_ibu <= (odabrana_jacina * 3) <= max_dnevna_ibu:
            validan_rezim_za_odabrani = {"broj_davanja": 3, "interval": 8, "opis": "3 puta dnevno (na 8 sati)"}
        elif min_dnevna_ibu <= (odabrana_jacina * 4) <= max_dnevna_ibu:
            validan_rezim_za_odabrani = {"broj_davanja": 4, "interval": 6, "opis": "4 puta dnevno (na 6 sati)"}
            
        adekvatne_alternative = []
        if min_dnevna_ibu <= (60 * 3) <= max_dnevna_ibu: adekvatne_alternative.append("60mg (3x dnevno)")
        elif min_dnevna_ibu <= (60 * 4) <= max_dnevna_ibu: adekvatne_alternative.append("60mg (4x dnevno)")
        if min_dnevna_ibu <= (125 * 3) <= max_dnevna_ibu: adekvatne_alternative.append("125mg (3x dnevno)")
        elif min_dnevna_ibu <= (125 * 4) <= max_dnevna_ibu: adekvatne_alternative.append("125mg (4x dnevno)")

        if not validan_rezim_za_odabrani:
            st.error(f"❌ **Neodgovarajuće doziranje čepića!**")
            st.write(f"Trenutno odabrani čepić od **{odabrana_jacina}mg** (bilo da se daje 3x ili 4x dnevno) ne može ispuniti siguran opseg za težinu od {weight} kg.")
            
            if adekvatne_alternative:
                preporuka_ibu_tekst = " ili ".join(adekvatne_alternative)
                st.info(f"💡 **Klinički savjet:** Za težinu vašeg djeteta, u terapeutski opseg se uklapa: **Ibuprofen čepići od {preporuka_ibu_tekst}**.")
            else:
                st.warning(
                    f"💡 **Klinički savjet:** S obzirom na težinu djeteta od **{weight} kg**, fiksne doze čepića (60mg i 125mg) "
                    f"u režimima od 3 ili 4 davanja ne odgovaraju sigurnom opsegu (Maksimum: {max_dnevna_ibu:.1f} mg/dan).\n\n"
                    "👉 **Preporučuje se prelazak na Neofen / Ibuprofen sirup** kako bi se doza mogla precizno izmjeriti u mililitrima!"
                )
            st.stop()
        else:
            data["interval"] = validan_rezim_za_odabrani["interval"]
            rezim_opis = validan_rezim_za_odabrani["opis"]

    # --- DIREKTNA KLINIČKA VERIFIKACIJA ZA VOLTAREN ČEPIĆE (2x ILI 3x DNEVNO) ---
    elif "Voltaren" in drug_name:
        min_dnevna_volt = weight * 2
        max_dnevna_volt = weight * 3
        odabrana_jacina = data["mg_u_jedinici"]
        
        validan_rezim_volt = None
        if min_dnevna_volt <= (odabrana_jacina * 2) <= max_dnevna_volt:
            validan_rezim_volt = {"broj_davanja": 2, "interval": 12, "opis": "2 puta dnevno (na 12 sati)"}
        elif min_dnevna_volt <= (odabrana_jacina * 3) <= max_dnevna_volt:
            validan_rezim_volt = {"broj_davanja": 3, "interval": 8, "opis": "3 puta dnevno (na 8 sati)"}
            
        if not validan_rezim_volt:
            st.error(f"❌ **Neodgovarajuća jačina čepića!**")
            st.write(f"Odabrani Voltaren čepić od **{odabrana_jacina}mg** (bilo u režimu 2x ili 3x dnevno) izlazi iz sigurnog terapeutskog raspona od **2-3 mg/kg/dan** za težinu od **{weight} kg**.")
            st.warning(
                "💡 **Klinički savjet:** Doza ove fiksne supozitorije se ne uklapa u sigurne granice. "
                "Molimo vas da razmotrite druge dostupne **paracetamol/ibuprofen sirupe** ili **čepiće** unutar aplikacije "
                "kako biste dozu prilagodili djetetu bez rizika od nuspojava."
            )
            st.stop()
        else:
            data["interval"] = validan_rezim_volt["interval"]
            rezim_opis = validan_rezim_volt["opis"]

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
        if "Paracetamol" in drug_name:
            apsolutni_max_24h = min(weight * 60, data["max_dan_fiksno"])
        elif "Ibuprofen" in drug_name:
            apsolutni_max_24h = min(weight * 30, data["max_dan_fiksno"])
        else: # Voltaren
            apsolutni_max_24h = min(weight * 3, data["max_dan_fiksno"])
        
        naslov_lijeva = "🔷 POJEDINAČNA DOZA ČEPIĆA:"
        sadrzaj_lijeva = f"**1 čepić**\n\n({data['mg_u_jedinici']} mg)"
        plan_ispis = f"1 čepić ({data['mg_u_jedinici']} mg)"
        
        naslov_desna = "🟩 UKUPNO KROZ 24 SATA:"
        if "Ibuprofen" in drug_name or "Voltaren" in drug_name:
            sadrzaj_desna = f"**Režim doziranja:** {rezim_opis}\n\n**Ukupno u 24h:** {data['mg_u_jedinici'] * broj_doza} mg\n\n**Apsolutni limit djeteta:** {round(apsolutni_max_24h, 1)} mg"
        else:
            sadrzaj_desna = f"**Unos odabranog čepića ({broj_doza}x dnevno):** {data['mg_u_jedinici'] * broj_doza} mg\n\n**Apsolutni limit djeteta:** {round(apsolutni_max_24h, 1)} mg"

    # --- PRIKAZ OKVIRA ---
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
        if "Paracetamol" in drug_name: limit_tekst = "60 mg/kg/dan"
        elif "Ibuprofen" in drug_name: limit_tekst = "30 mg/kg/dan"
        else: limit_tekst = "3 mg/kg/dan"
        st.write(f"Za težinu od **{weight} kg**, apsolutni dnevni maksimum iznosi **{round(apsolutni_max_24h, 1)} mg** ({limit_tekst}).")
    st.write("Nikada ne prelazite ovaj limit u slučaju da kombinujete različite oblike istog lijeka!")

    with st.expander("ℹ️ Važne napomene za odabrani lijek"):
        if data["napomena"]: st.info(data["napomena"])
        st.write("- **Opća napomena:** Ne miješati s drugim lijekovima iste aktivne tvari.")
        st.write("- U slučaju pogoršanja simptoma, odmah kontaktirati ljekara.")

# --- DISCLAIMER I KONTAKT SEKCIJA ---
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

📱 **Koristite Android mobitel?** Preuzmite zvaničnu Android aplikaciju za brži pristup:  
[<img src="https://img.shields.io/badge/Preuzmi-Android%20App-green?style=for-the-badge&logo=android&logoColor=white" alt="Preuzmi Android App">](https://drkarabeg.ba/downloads/pedimed.apk)
""", unsafe_allow_html=True)

st.markdown(
    "<div style='font-size: 0.8em; color: gray; text-align: center; margin-top: 20px;'>"
    "© " + str(datetime.now().year) + " Created by <a href='https://drkarabeg.ba' target='_blank' style='color: gray; text-decoration: underline;'>Karabeg dr Kemal</a> | PediMed Safe v1.5 |"
    "</div>", 
    unsafe_allow_html=True
)
