import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Konfiguracja strony ---
st.set_page_config(
    page_title="Pogoda Górska — Tatry & Beskidy",
    page_icon="⛰️",
    layout="wide"
)

# --- Słownik polskich nazw szczytów ---
SZCZYTY = {
    # TATRY POLSKIE
    "Rysy": (49.1794, 20.0883),
    "Giewont": (49.2503, 19.9350),
    "Kasprowy Wierch": (49.2317, 19.9817),
    "Świnica": (49.2167, 19.9667),
    "Kościelec": (49.2333, 20.0167),
    "Orla Perć": (49.2200, 20.0200),
    "Zawrat": (49.2250, 20.0083),
    "Skrajny Granat": (49.2283, 20.0333),
    "Pośredni Granat": (49.2267, 20.0300),
    "Czarny Staw pod Rysami": (49.1900, 20.0783),
    "Morskie Oko": (49.2017, 20.0717),
    "Żabi Koń": (49.2117, 20.0583),
    "Mięguszowiecki Szczyt Wielki": (49.1950, 20.0667),
    "Mięguszowiecki Szczyt Czarny": (49.1933, 20.0633),
    "Cubryna": (49.2050, 20.0550),
    "Wołowiec": (49.2617, 19.8483),
    "Starorobociański Wierch": (49.2433, 19.8617),
    "Błyszcz": (49.2500, 19.8733),
    "Bystra": (49.2467, 19.8950),
    "Kopa Kondracka": (49.2450, 19.9350),
    "Małołączniak": (49.2483, 19.9217),
    "Ciemniak": (49.2533, 19.9083),
    "Tomanowy Wierch": (49.2283, 19.9000),
    "Czerwone Wierchy": (49.2500, 19.9200),
    "Krzesanica": (49.2467, 19.9150),

    # TATRY SŁOWACKIE
    "Łomnica (Lomnický štít)": (49.1953, 20.2133),
    "Gerlach (Gerlachovský štít)": (49.1833, 20.1333),
    "Krywań (Kriváň)": (49.1767, 19.9933),
    "Kołowy Szczyt (Kolový štít)": (49.1800, 20.0617),
    "Wysoka (Vysoká)": (49.1817, 20.1017),
    "Ganek (Ganek)": (49.1850, 20.1150),
    "Lodowy Szczyt (Ľadový štít)": (49.1900, 20.1483),
    "Żabi Szczyt Niżni (Žabí štít nižný)": (49.1983, 20.0900),
    "Żabi Szczyt Wyżni (Žabí štít vyšný)": (49.1967, 20.0867),
    "Durny Szczyt (Tupá)": (49.1767, 20.1317),
    "Szeroka Jaworzyńska (Jahňací štít)": (49.1900, 20.1700),
    "Mały Kieżmarski Szczyt": (49.1950, 20.1900),
    "Wielki Kieżmarski Szczyt": (49.1933, 20.2017),
    "Staroleśny Szczyt (Slavkovský štít)": (49.2017, 20.1833),
    "Hawrań (Havran)": (49.2183, 20.2883),
    "Murań (Murán)": (49.2150, 20.2783),
    "Jagnięcy Szczyt (Baranec)": (49.1933, 19.8717),
    "Wołoszyn (Volovec)": (49.2083, 20.0383),
    "Solisko (Solisko)": (49.2200, 19.9700),
    "Szatan (Satanovo sedlo)": (49.1967, 20.0483),
    "Pośrednia Grań (Prostredný hrebeň)": (49.2100, 20.0500),
    "Rysy — słowackie podejście": (49.1794, 20.0883),
    "Téryho chata okolice": (49.2017, 20.1600),

    # BESKIDY POLSKIE
    "Babia Góra": (49.5733, 19.5300),
    "Turbacz": (49.5667, 20.1117),
    "Pilsko": (49.5467, 19.3683),
    "Skrzyczne": (49.7100, 19.0317),
    "Klimczok": (49.7383, 19.0383),
    "Błatnia": (49.7050, 19.0983),
    "Równica": (49.7300, 18.8683),
    "Czantoria Wielka": (49.7483, 18.8217),
    "Barania Góra": (49.6617, 18.9200),
    "Magurka Wiślańska": (49.6783, 18.9667),
    "Romanka": (49.5583, 19.3033),
    "Lipowski Wierch": (49.5317, 19.2733),
    "Mędralowa": (49.5600, 19.4183),
    "Kościelisko (dolina)": (49.2833, 19.8667),
    "Luboń Wielki": (49.6583, 19.9283),
    "Mogielica": (49.6667, 20.1667),
    "Szczebel": (49.6983, 20.0833),
    "Łopień": (49.6850, 20.2000),
    "Jaworzyna Krynicka": (49.4067, 20.9683),
    "Radziejowa": (49.4567, 20.6383),
    "Wielka Racza": (49.4617, 19.1083),
    "Przehyba": (49.4667, 20.5833),
    "Hala Łabowska": (49.4417, 20.8533),
}

# --- Kody pogodowe WMO ---
WMO_KODY = {
    0: ("☀️", "Bezchmurnie"),
    1: ("🌤️", "Głównie pogodnie"),
    2: ("⛅", "Częściowe zachmurzenie"),
    3: ("☁️", "Pochmurno"),
    45: ("🌫️", "Mgła"),
    48: ("🌫️", "Szadź"),
    51: ("🌦️", "Mżawka lekka"),
    53: ("🌦️", "Mżawka umiarkowana"),
    55: ("🌧️", "Mżawka intensywna"),
    61: ("🌧️", "Deszcz lekki"),
    63: ("🌧️", "Deszcz umiarkowany"),
    65: ("🌧️", "Deszcz intensywny"),
    71: ("🌨️", "Śnieg lekki"),
    73: ("🌨️", "Śnieg umiarkowany"),
    75: ("❄️", "Śnieg intensywny"),
    77: ("🌨️", "Ziarnisty śnieg"),
    80: ("🌦️", "Przelotny deszcz lekki"),
    81: ("🌧️", "Przelotny deszcz umiarkowany"),
    82: ("⛈️", "Przelotny deszcz intensywny"),
    85: ("🌨️", "Przelotny śnieg lekki"),
    86: ("❄️", "Przelotny śnieg intensywny"),
    95: ("⛈️", "Burza"),
    96: ("⛈️", "Burza z gradem"),
    99: ("⛈️", "Burza z silnym gradem"),
}

def get_wmo_info(code):
    return WMO_KODY.get(code, ("❓", "Nieznane"))

def geokoduj_szczyt(nazwa):
    """Geokodowanie przez Nominatim z priorytetem dla Tatr i Beskidów."""
    url = "https://nominatim.openstreetmap.org/search"
    for query in [f"{nazwa} Tatry", f"{nazwa} Beskidy", f"{nazwa} góra Polska", nazwa]:
        params = {
            "q": query,
            "format": "json",
            "limit": 3,
            "featuretype": "natural",
        }
        headers = {"User-Agent": "MountainWeatherApp/1.0"}
        try:
            r = requests.get(url, params=params, headers=headers, timeout=5)
            data = r.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", nazwa)
        except Exception:
            continue
    return None, None, None

def pobierz_pogode(lat, lon):
    """Pobiera prognozę z Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "temperature_2m",
            "apparent_temperature",
            "precipitation",
            "snowfall",
            "weathercode",
            "windspeed_10m",
            "windgusts_10m",
            "winddirection_10m",
            "cloudcover",
            "visibility",
            "freezinglevel_height",
        ],
        "windspeed_unit": "ms",
        "timezone": "Europe/Warsaw",
        "forecast_days": 10,
        "models": "best_match",
    }
    r = requests.get(url, params=params, timeout=10)
    return r.json()

def nastepny_weekend(data_ref=None):
    """Zwraca daty najbliższego weekendu (sobota, niedziela)."""
    if data_ref is None:
        data_ref = datetime.now()
    dni_do_soboty = (5 - data_ref.weekday()) % 7
    if dni_do_soboty == 0 and data_ref.hour >= 20:
        dni_do_soboty = 7
    sobota = (data_ref + timedelta(days=dni_do_soboty)).date()
    niedziela = sobota + timedelta(days=1)
    return sobota, niedziela

def kierunek_wiatru(stopnie):
    kierunki = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = round(stopnie / 45) % 8
    return kierunki[idx]

def ocen_warunki(row):
    """Ocenia warunki górskie i zwraca kolor + opis."""
    wiatr = row["Wiatr (m/s)"]
    porywy = row["Porywy (m/s)"]
    opady = row["Opady (mm)"]
    snieg = row["Śnieg (cm)"]
    kod = row["_kod"]

    if wiatr > 20 or porywy > 25 or kod in [95, 96, 99]:
        return "🔴", "Niebezpieczne"
    elif wiatr > 12 or porywy > 18 or opady > 5 or snieg > 3:
        return "🟡", "Utrudnione"
    elif wiatr > 8 or opady > 1:
        return "🟠", "Umiarkowane"
    else:
        return "🟢", "Dobre"

# ===================== UI =====================

st.title("⛰️ Pogoda Górska — Tatry & Beskidy")
st.markdown("Prognoza na najbliższy weekend z modelu meteorologicznego Open-Meteo")

# --- Wybór szczytu ---
col1, col2 = st.columns([2, 1])

with col1:
    tryb = st.radio("Wybierz szczyt:", ["Z listy", "Wpisz nazwę ręcznie"], horizontal=True)

    if tryb == "Z listy":
        wybrany = st.selectbox("Szczyt:", sorted(SZCZYTY.keys()))
        lat, lon = SZCZYTY[wybrany]
        nazwa_wyswietlana = wybrany
        wspolrzedne_ok = True
    else:
        nazwa_wpisana = st.text_input("Wpisz nazwę szczytu (po polsku lub słowacku):", placeholder="np. Kołowy Szczyt, Babia Góra, Gerlach...")
        wspolrzedne_ok = False
        lat = lon = None
        nazwa_wyswietlana = nazwa_wpisana

with col2:
    sobota, niedziela = nastepny_weekend()
    st.info(f"📅 Najbliższy weekend:\n**{sobota.strftime('%d.%m.%Y')} (sob)** — **{niedziela.strftime('%d.%m.%Y')} (nd)**")

# Geokodowanie ręcznej nazwy
if tryb == "Wpisz nazwę ręcznie" and nazwa_wpisana:
    if nazwa_wpisana in SZCZYTY:
        lat, lon = SZCZYTY[nazwa_wpisana]
        nazwa_wyswietlana = nazwa_wpisana
        wspolrzedne_ok = True
    else:
        with st.spinner("Szukam lokalizacji..."):
            lat, lon, display = geokoduj_szczyt(nazwa_wpisana)
        if lat:
            wspolrzedne_ok = True
            st.success(f"✅ Znaleziono: {display}")
        else:
            st.error("❌ Nie znaleziono szczytu. Spróbuj innej pisowni lub wybierz z listy.")

# --- Pobieranie i wyświetlanie pogody ---
if wspolrzedne_ok and st.button("🔍 Sprawdź pogodę", type="primary"):
    with st.spinner("Pobieram prognozę..."):
        try:
            dane = pobierz_pogode(lat, lon)
        except Exception as e:
            st.error(f"Błąd pobierania danych: {e}")
            st.stop()

    godziny = pd.to_datetime(dane["hourly"]["time"])
    df = pd.DataFrame({
        "czas": godziny,
        "temp": dane["hourly"]["temperature_2m"],
        "odczuwalna": dane["hourly"]["apparent_temperature"],
        "opady": dane["hourly"]["precipitation"],
        "snieg": dane["hourly"]["snowfall"],
        "_kod": dane["hourly"]["weathercode"],
        "wiatr": dane["hourly"]["windspeed_10m"],
        "porywy": dane["hourly"]["windgusts_10m"],
        "kierunek": dane["hourly"]["winddirection_10m"],
        "zachmurzenie": dane["hourly"]["cloudcover"],
        "widocznosc": dane["hourly"]["visibility"],
        "izot0": dane["hourly"]["freezinglevel_height"],
    })

    # Filtruj weekend
    df_weekend = df[df["czas"].dt.date.isin([sobota, niedziela])].copy()

    if df_weekend.empty:
        st.warning("Brak danych dla wybranego weekendu.")
        st.stop()

    st.markdown(f"## 📍 {nazwa_wyswietlana}")
    st.markdown(f"Współrzędne: `{lat:.4f}°N, {lon:.4f}°E`")

    for dzien in [sobota, niedziela]:
        df_dzien = df_weekend[df_weekend["czas"].dt.date == dzien]
        if df_dzien.empty:
            continue

        nazwa_dnia = "🟦 Sobota" if dzien == sobota else "🟪 Niedziela"
        st.markdown(f"### {nazwa_dnia} — {dzien.strftime('%d.%m.%Y')}")

        # Podsumowanie dnia
        temp_min = df_dzien["temp"].min()
        temp_max = df_dzien["temp"].max()
        wiatr_max = df_dzien["wiatr"].max()
        porywy_max = df_dzien["porywy"].max()
        opady_suma = df_dzien["opady"].sum()
        snieg_suma = df_dzien["snieg"].sum()
        izot0_min = df_dzien["izot0"].min()
        izot0_max = df_dzien["izot0"].max()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("🌡️ Temperatura", f"{temp_min:.0f}°C / {temp_max:.0f}°C", help="Min / Max")
        c2.metric("💨 Wiatr max", f"{wiatr_max:.1f} m/s", help="Maksymalna prędkość wiatru")
        c3.metric("🌬️ Porywy max", f"{porywy_max:.1f} m/s")
        c4.metric("🌧️ Opady", f"{opady_suma:.1f} mm")
        c5.metric("❄️ Śnieg", f"{snieg_suma:.1f} cm")

        st.caption(f"Izotermia 0°C: {izot0_min:.0f}–{izot0_max:.0f} m n.p.m.")

        # Tabela godzinowa
        tabela = df_dzien[["czas", "temp", "odczuwalna", "_kod", "wiatr", "porywy", "kierunek", "opady", "snieg", "zachmurzenie"]].copy()
        tabela.columns = ["Godzina", "Temp (°C)", "Odczuwalna (°C)", "_kod", "Wiatr (m/s)", "Porywy (m/s)", "Kierunek (°)", "Opady (mm)", "Śnieg (cm)", "Zachmurzenie (%)"]
        tabela["Godzina"] = tabela["Godzina"].dt.strftime("%H:%M")
        tabela["💨 Kierunek"] = tabela["Kierunek (°)"].apply(kierunek_wiatru)
        tabela["Warunki"] = tabela.apply(lambda r: get_wmo_info(r["_kod"])[0] + " " + get_wmo_info(r["_kod"])[1], axis=1)
        tabela["Ocena"] = tabela.apply(lambda r: ocen_warunki(r)[0] + " " + ocen_warunki(r)[1], axis=1)

        tabela_display = tabela[["Godzina", "Warunki", "Temp (°C)", "Odczuwalna (°C)", "Wiatr (m/s)", "Porywy (m/s)", "💨 Kierunek", "Opady (mm)", "Śnieg (cm)", "Zachmurzenie (%)", "Ocena"]]
        st.dataframe(tabela_display, use_container_width=True, hide_index=True)

        # Ostrzeżenia
        ostrzezenia = []
        if wiatr_max > 20:
            ostrzezenia.append(f"⚠️ **Bardzo silny wiatr** — porywy do {porywy_max:.0f} m/s! Nie zalecane wyjście na grań.")
        elif wiatr_max > 12:
            ostrzezenia.append(f"⚠️ **Silny wiatr** — porywy do {porywy_max:.0f} m/s. Zachowaj ostrożność na eksponowanych miejscach.")
        if any(k in [95, 96, 99] for k in df_dzien["_kod"]):
            ostrzezenia.append("⛈️ **Burza** — ryzyko wyładowań atmosferycznych! Zejdź z grzbietu przed godziną burzy.")
        if opady_suma > 10:
            ostrzezenia.append(f"🌧️ **Intensywne opady** — łącznie {opady_suma:.0f} mm. Szlaki mogą być mokre i śliskie.")
        if snieg_suma > 5:
            ostrzezenia.append(f"❄️ **Opady śniegu** — {snieg_suma:.0f} cm. Sprawdź warunki śniegowe i zabrać raki/czeki.")
        if izot0_min < 1500:
            ostrzezenia.append(f"🧊 **Izotermia 0°C poniżej 1500 m** ({izot0_min:.0f} m) — oblodzenie możliwe na szlaku.")

        if ostrzezenia:
            st.markdown("**Ostrzeżenia:**")
            for o in ostrzezenia:
                st.markdown(f"> {o}")
        else:
            st.success("✅ Warunki bez szczególnych ostrzeżeń")

        st.divider()

    # --- Wykres ---
    st.markdown("### 📈 Wykresy dla weekendu")
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=("Temperatura (°C)", "Wiatr i porywy (m/s)", "Opady (mm)"),
        vertical_spacing=0.08
    )

    fig.add_trace(go.Scatter(
        x=df_weekend["czas"], y=df_weekend["temp"],
        name="Temperatura", line=dict(color="#e74c3c", width=2)
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df_weekend["czas"], y=df_weekend["odczuwalna"],
        name="Odczuwalna", line=dict(color="#e74c3c", width=1, dash="dot")
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_weekend["czas"], y=df_weekend["wiatr"],
        name="Wiatr", line=dict(color="#3498db", width=2)
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df_weekend["czas"], y=df_weekend["porywy"],
        name="Porywy", line=dict(color="#3498db", width=1, dash="dot")
    ), row=2, col=1)
    fig.add_hrect(y0=12, y1=100, row=2, col=1, fillcolor="orange", opacity=0.1, line_width=0, annotation_text="silny wiatr")
    fig.add_hrect(y0=20, y1=100, row=2, col=1, fillcolor="red", opacity=0.1, line_width=0, annotation_text="niebezpieczny")

    fig.add_trace(go.Bar(
        x=df_weekend["czas"], y=df_weekend["opady"],
        name="Opady", marker_color="#2ecc71"
    ), row=3, col=1)

    fig.update_layout(height=600, showlegend=True, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Dane: Open-Meteo (model best_match) | Geokodowanie: OpenStreetMap Nominatim")

elif not wspolrzedne_ok and tryb == "Wpisz nazwę ręcznie" and not nazwa_wpisana:
    st.info("👆 Wpisz nazwę szczytu lub wybierz z listy, następnie kliknij 'Sprawdź pogodę'")
else:
    st.info("👆 Wybierz szczyt i kliknij 'Sprawdź pogodę'")
