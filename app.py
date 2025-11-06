import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

st.title("📊 Bedrijvenzoeker Amsterdam")
st.write("Zoek automatisch naar Uitzendbureaus, Barbershops en Sportscholen in Amsterdam (met e-mail, telefoon en adres).")

headers = {"User-Agent": "Mozilla/5.0"}

def scrape_bedrijven(zoekterm, categorie):
    resultaten = []
    st.write(f"🔍 Bezig met: **{zoekterm}** ...")
    for pagina in range(0, 3):  # verhoog voor meer diepte
        url = f"url = f"https://duckduckgo.com/html/?q={zoekterm}+Amsterdam"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.select("a"):
            link = item.get("href", "")
            if link.startswith("http") and "google" not in link:
                try:
                    res = requests.get(link, headers=headers, timeout=10)
                    html = res.text
                    emails = list(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html)))
                    tels = list(set(re.findall(r"(?:\+31|0)[1-9][0-9\s\-]{7,}", html)))
                    adressen = list(set(re.findall(r"\b[A-Z][a-z]+\s\d{1,3}[A-Z]?,?\s?10\d{2}\s?[A-Z]{2}\b", html)))

                    if emails:
                        resultaten.append({
                            "Categorie": categorie,
                            "Naam bedrijf": link.split("/")[2],
                            "Adres / Stad": ", ".join(adressen[:1]) if adressen else "Amsterdam",
                            "Email": ", ".join(emails[:2]),
                            "Telefoonnummer": ", ".join(tels[:2]) if tels else "",
                            "Website": link
                        })
                    time.sleep(1)
                except:
                    continue
    return resultaten

if st.button("🚀 Start Zoeken"):
    categorieen = [
        ("uitzendbureau Amsterdam", "Uitzendbureaus"),
        ("barbershop Amsterdam", "Barbershops"),
        ("sportschool Amsterdam -BasicFit -TrainMore", "Sportscholen")
    ]
    alle_resultaten = []
    for zoekterm, cat in categorieen:
        alle_resultaten.extend(scrape_bedrijven(zoekterm, cat))

    if alle_resultaten:
        df = pd.DataFrame(alle_resultaten)
        with pd.ExcelWriter("bedrijven_amsterdam.xlsx", engine="openpyxl") as writer:
            for cat in df["Categorie"].unique():
                df_cat = df[df["Categorie"] == cat].drop(columns=["Categorie"])
                df_cat.to_excel(writer, index=False, sheet_name=cat)

        with open("bedrijven_amsterdam.xlsx", "rb") as f:
            st.download_button("📥 Download Excel-bestand", f, file_name="bedrijven_amsterdam.xlsx")

        st.success("✅ Klaar! Klik hierboven om te downloaden.")
    else:
        st.warning("Geen resultaten gevonden — probeer het opnieuw.")
