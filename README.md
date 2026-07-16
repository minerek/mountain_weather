# ⛰️ Pogoda Górska — Tatry & Beskidy

Aplikacja webowa pokazująca prognozę pogody na najbliższy weekend dla szczytów górskich w Tatrach i Beskidach.

## Funkcje

- 🏔️ Ponad 65 szczytów w bazie (Tatry Polskie, Tatry Słowackie, Beskidy)
- 🔍 Wyszukiwanie dowolnego szczytu po polskiej nazwie
- 📅 Automatyczna prognoza na najbliższy weekend
- ⚠️ Ostrzeżenia górskie (wiatr, burze, oblodzenie)
- 📈 Wykresy temperatury, wiatru i opadów
- 🌡️ Izotermia 0°C, porywy wiatru, zachmurzenie

## Dane

- Prognoza: [Open-Meteo](https://open-meteo.com/) (darmowe, bez klucza API)
- Geokodowanie: [OpenStreetMap Nominatim](https://nominatim.org/)

## Uruchomienie lokalne

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy na Streamlit Cloud

1. Wrzuć to repozytorium na GitHub
2. Wejdź na [share.streamlit.io](https://share.streamlit.io)
3. Zaloguj się przez GitHub
4. Kliknij **"New app"** → wybierz repo → plik `app.py`
5. Kliknij **"Deploy"**
