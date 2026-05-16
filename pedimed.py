import streamlit as st
from datetime import datetime, timedelta, time

# --- BAZA PODATAKA ---
# "dnevna_mg_kg" je fiksirana na preporučenu terapijsku dozu (40 mg/kg za paracetamol, 20 mg/kg za ibuprofen)
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
    "Ibuprofen čepići (125mg)": {"dnevna_mg_kg": 30, "max_dan_fiksno": 1200, "mg_u_jedinici": 125, "interval": 8, "tip": "supozitorija", "napomena": ""},
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

    # --- PAMETNA EVALUACIJA ZA PARACETAMOL ČEPIĆE ---
    if "Paracetamol čepići" in drug_name:
        ciljana_pojedinacna = (weight * 40) / 4
        odabrana_jacina = data["mg_u_jedinici"]
        
        if abs(odabrana_jacina - ciljana_pojedinacna) > 20:
            st.error(f"❌ **Neodgovarajuća jačina čepića!**")
            if ciljana_pojedinacna <= 100: preporuka = "80mg"
            elif ciljana_pojedinacna <= 135: preporuka = "120mg"
            elif ciljana_pojedinacna <= 200: preporuka = "150mg"
            else: preporuka = "250mg"
            
            st.write(f"Za težinu od **{weight} kg**, ciljana pojedinačna doza je oko **{round(ciljana_pojedinacna, 1)} mg**.")
            st.info(f"💡 **Savjet:** Trenutno odabrani čepić od {odabrana_jacina}mg ne odgovara djetetu. Preporučuje se primjena **Paracetamol čepića od {preporuka}**.")
            st.stop()

    st.divider()
    
    # Terapijski proračun (preporučene doze)
    terapijska_mg_24h = min(weight * data["dnevna_mg_kg"], data["max_dan_fiksno"])
    broj_doza = 24 // data["interval"]
    pojedinacna_mg = terapijska_mg_24h / broj_doza
    
    # --- LOGIKA MAKSIMALNIH GRANICA I RASPONA (DVOSTRUKA FORMULA) ---
    if "Paracetamol sirup" in drug_name:
        terapijska_ml_24h = round((terapijska_mg_24h * 5) / 120, 1)
        apsolutni_max_24h = min(weight * 60, data["max_dan_fiksno"])
        apsolutni_max_ml_24h = round((apsolutni_max_24h * 5) / 120, 1)
        max_pojedinacna_mg = apsolutni_max_24h / broj_doza
        max_pojedinacna_ml = round((max_pojedinacna_mg * 5) / 120, 1)
    elif "Ibuprofen sirup" in drug_name:
        terapijska_ml_24h = round((terapijska_mg_24h * 5) / 100, 1)
        apsolutni_max_24h = min(weight * 30, data["max_dan_fiksno"])
        apsolutni_max_ml_24h = round((apsolutni_max_24h * 5) / 100, 1)
        max_pojedinacna_mg = apsolutni_max_24h / broj_doza
        max_pojedinacna_ml = round((max_pojedinacna_mg * 5) / 100, 1)
    else:
        # Čepići
        apsolutni_max_24h = min(weight * 60, data["max_dan_fiksno"]) if "Paracetamol" in drug_name else min(weight * 30, data["max_dan_fiksno"])
        terapijska_ml_24h = 0
        apsolutni_max_ml_24h = 0

    # Formatiranje ispisa doza i naslova kartica
    if data["tip"] == "sirup":
        final_ml = round((pojedinacna_mg * 5) / data["mg_u_5ml"], 1)
        
        if "Paracetamol sirup" in drug_name:
            doza_ispis = f"{final_ml} ml do {max_pojedinacna_ml} ml <span style='font-size:0.7em; color:#aaa;'>({round(pojedinacna_mg, 1)}-{round(max_pojedinacna_mg, 1)} mg)</span>"
            plan_ispis = f"{final_ml} ml ({round(pojedinacna_mg, 1)} mg) [Preporučeno]"
            naslov_kartice = "Raspon pojedinačne doze (40-60 mg/kg)"
            desni_naslov = "Ukupno kroz 24h (Terapijski preporučeno)"
            
            desna_kartica_sadrzaj = f"""
            <div style="font-size: 1.4em; font-weight: bold; color: white;">{round(terapijska_mg_24h, 1)} mg <span style="font-size:0.7em; color:#00ff66;">({terapijska_ml_24h} ml)</span></div>
            <div style="font-size: 0.8em; color: #ff4b4b; font-weight: bold; margin-top: 8px; border-top: 1px solid #333; padding-top: 5px;">
                ⚠️ Maksimalno (60 mg/kg): {round(apsolutni_max_24h, 1)} mg ({apsolutni_max_ml_24h} ml)
            </div>
            """
        elif "Ibuprofen sirup" in drug_name:
            doza_ispis = f"{final_ml} ml do {max_pojedinacna_ml} ml <span style='font-size:0.7em; color:#aaa;'>({round(pojedinacna_mg, 1)}-{round(max_pojedinacna_mg, 1)} mg)</span>"
            plan_ispis = f"{final_ml} ml ({round(pojedinacna_mg, 1)} mg) [Preporučeno]"
            naslov_kartice = "Raspon pojedinačne doze (20-30 mg/kg)"
            desni_naslov = "Ukupno kroz 24h (Terapijski preporučeno)"
            
            desna_kartica_sadrzaj = f"""
            <div style="font-size: 1.4em; font-weight: bold; color: white;">{round(terapijska_mg_24h, 1)} mg <span style="font-size:0.7em; color:#00ff66;">({terapijska_ml_24h} ml)</span></div>
            <div style="font-size: 0.8em; color: #ff4b4b; font-weight: bold; margin-top: 8px; border-top: 1px solid #333; padding-top: 5px;">
                ⚠️ Maksimalno (30 mg/kg): {round(apsolutni_max_24h, 1)} mg ({apsolutni_max_ml_24h} ml)
            </div>
            """
    else:
        doza_ispis = f"1 čepić <span style='font-size:0.7em; color:#aaa;'>({data['mg_u_jedinici']} mg)</span>"
        plan_ispis = f"1 čepić ({data['mg_u_jedinici']} mg)"
        naslov_kartice = "Pojedinačna doza (Terapijska)"
        desni_naslov = "Ukupno kroz 24h (Terapijska)"
        
        desna_kartica_sadrzaj = f"""
        <div style="font-size: 1.4em; font-weight: bold; color: white;">{round(terapijska_mg_24h, 1)} mg</div>
        <div style="font-size: 0.8em; color: #ff4b4b; font-weight: bold; margin-top: 8px; border-top: 1px solid #333; padding-top: 5px;">
            ⚠️ Maksimalno: {round(apsolutni_max_24h, 1)} mg
        </div>
        """

    # --- BEZBJEDAN PRIKAZ HTML KARTICA ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div style="background-color: #1e212a; padding: 15px; border-radius: 10px; border-left: 5px solid #00fff0; min-height: 115px;">
            <div style="font-size: 0.82em; color: #aaa; font-weight: bold; margin-bottom: 5px;">{naslov_kartice}</div>
            <div style="font-size: 1.35em; font-weight: bold; color: white; line-height: 1.3;">{doza_ispis}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div style="background-color: #1e212a; padding: 15px; border-radius: 10px; border-left: 5px solid #00ff66; min-height: 115px;">
            <div style="font-size: 0.82em; color: #aaa; font-weight: bold; margin-bottom: 5px;">{desni_naslov}</div>
            {desna_kartica_sadrzaj}
        </div>
        """, unsafe_allow_html=True)

    st.write("") 

    # Satnica
    st.subheader("⏰ Plan davanja (24h) - Na bazi preporučene doze:")
    current_time = datetime.combine(datetime.today(), start_time)
    for i in range(broj_doza):
        st.success(f"**{i+1}. doza** u **{current_time.strftime('%H:%M')}** — Doza: {plan_ispis}")
        current_time += timedelta(hours=data["interval"])

    st.divider()
    st.error(f"⚠️ **APSOLUTNI SIGURNOSNI LIMIT (Maksimalna doza):**")
    if "Paracetamol sirup" in drug_name:
        st.write(f"Za težinu od **{weight} kg**, apsolutni dnevni maksimum paracetamola iznosi **{apsolutni_max_ml_24h} ml** (ukupno {round(apsolutni_max_24h, 1)} mg na bazi 60 mg/kg/dan).")
    elif "Ibuprofen sirup" in drug_name:
        st.write(f"Za težinu od **{weight} kg**, maksimalna dopuštena dnevna doza ibuprofena iznosi **{apsolutni_max_ml_24h} ml** (ukupno {round(apsolutni_max_24h, 1)} mg na bazi 30 mg/kg/dan).")
    else:
        st.write(f"Za težinu od **{weight} kg**, apsolutni dnevni maksimum iznosi **{round(apsolutni_max_24h, 1)} mg**.")
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
    Korištenjem ove aplikacije prihvatate da autor ne snosi odgovornost za eventualne greške u primjeni lijeka.
    """)

st.markdown(f"""
---
📩 **Trebate savjet ili imate pitanje?** Možete me kontaktirati direktno putem kontakt forme na mojoj web stranici:  
[**www.drkarabeg.ba**](https://drkarabeg.ba)
""", unsafe_allow_html=True)

st.markdown(
    f"<div style='font-size: 0.8em; color: gray; text-align: center; margin-top: 20px;'>"
    f"© {datetime.now().year} Created by <a href='https://drkarabeg.ba' target='_blank' style='color: gray; text-decoration: underline;'>Karabeg dr Kemal</a> | PediMed Safe v1.5 |"
    f"</div>", 
    unsafe_allow_html=True
)
