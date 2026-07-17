import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Pogoda Górska — Tatry & Beskidy",
    page_icon="⛰️",
    layout="wide"
)

# ============================================================
# BAZA SZCZYTÓW: (lat, lon, wysokość m n.p.m., pasmo)
# ============================================================
# Pasma: "Tatry Polskie", "Tatry Słowackie", "Beskid Śląski",
#        "Beskid Żywiecki", "Beskid Wyspowy", "Beskid Sądecki",
#        "Gorce", "Pieniny"

SZCZYTY = {
    # ---------- TATRY POLSKIE ----------
    "Rysy":                               (49.1794, 20.0883, 2499, "Tatry Polskie"),
    "Giewont":                            (49.2503, 19.9350, 1894, "Tatry Polskie"),
    "Kasprowy Wierch":                    (49.2317, 19.9817, 1987, "Tatry Polskie"),
    "Świnica":                            (49.2167, 19.9667, 2301, "Tatry Polskie"),
    "Kościelec":                          (49.2333, 20.0167, 2155, "Tatry Polskie"),
    "Skrajny Granat":                     (49.2283, 20.0333, 2225, "Tatry Polskie"),
    "Pośredni Granat":                    (49.2267, 20.0300, 2234, "Tatry Polskie"),
    "Zadni Granat":                       (49.2300, 20.0367, 2240, "Tatry Polskie"),
    "Zawrat":                             (49.2250, 20.0083, 2159, "Tatry Polskie"),
    "Orla Perć (grań)":                   (49.2200, 20.0200, 2000, "Tatry Polskie"),
    "Czarny Staw pod Rysami":             (49.1900, 20.0783, 1580, "Tatry Polskie"),
    "Morskie Oko":                        (49.2017, 20.0717, 1395, "Tatry Polskie"),
    "Żabi Koń":                           (49.2117, 20.0583, 2291, "Tatry Polskie"),
    "Żabi Szczyt Polski":                 (49.2083, 20.0650, 2259, "Tatry Polskie"),
    "Mięguszowiecki Szczyt Wielki":       (49.1950, 20.0667, 2438, "Tatry Polskie"),
    "Mięguszowiecki Szczyt Czarny":       (49.1933, 20.0633, 2410, "Tatry Polskie"),
    "Mięguszowiecki Szczyt Pośredni":     (49.1942, 20.0650, 2393, "Tatry Polskie"),
    "Cubryna":                            (49.2050, 20.0550, 2376, "Tatry Polskie"),
    "Wołowiec":                           (49.2617, 19.8483, 2064, "Tatry Polskie"),
    "Starorobociański Wierch":            (49.2433, 19.8617, 2176, "Tatry Polskie"),
    "Błyszcz":                            (49.2500, 19.8733, 2158, "Tatry Polskie"),
    "Bystra":                             (49.2467, 19.8950, 2248, "Tatry Polskie"),
    "Kopa Kondracka":                     (49.2450, 19.9350, 2005, "Tatry Polskie"),
    "Małołączniak":                       (49.2483, 19.9217, 2096, "Tatry Polskie"),
    "Ciemniak":                           (49.2533, 19.9083, 2096, "Tatry Polskie"),
    "Tomanowy Wierch Polskie":            (49.2283, 19.9000, 2103, "Tatry Polskie"),
    "Krzesanica":                         (49.2467, 19.9150, 2122, "Tatry Polskie"),
    "Zadnia Kopka":                       (49.2317, 20.0483, 2162, "Tatry Polskie"),
    "Pośrednia Kopka":                    (49.2300, 20.0450, 2133, "Tatry Polskie"),
    "Skrajna Turnia":                     (49.2250, 20.0417, 2096, "Tatry Polskie"),
    "Buczynowe Turnie":                   (49.2317, 20.0583, 2183, "Tatry Polskie"),
    "Waksmundzki Wierch":                 (49.2617, 20.0583, 1617, "Tatry Polskie"),
    "Wierch nad Kotlinami":               (49.2650, 20.0433, 1748, "Tatry Polskie"),
    "Hawrań (Tatry Polskie)":             (49.2683, 20.2883, 1152, "Tatry Polskie"),
    "Nosal":                              (49.2700, 19.9683, 1206, "Tatry Polskie"),
    "Gubałówka":                          (49.2983, 19.9500,  1123, "Tatry Polskie"),

    # ---------- TATRY ZACHODNIE (Rohacze i okolice) ----------
    "Rohacz Ostry (Ostrý Roháč)":        (49.1900, 19.7683, 2088, "Tatry Zachodnie"),
    "Rohacz Płaski (Plochý Roháč)":      (49.1933, 19.7567, 2001, "Tatry Zachodnie"),
    "Wołowiec (Tatry Zach.)":            (49.2000, 19.7933, 2063, "Tatry Zachodnie"),
    "Baraniec (Baranec)":                (49.1867, 19.7400, 2184, "Tatry Zachodnie"),
    "Siwy Wierch (Sivý vrch)":           (49.2367, 19.8033, 1806, "Tatry Zachodnie"),
    "Osobita":                           (49.2583, 19.7583, 1687, "Tatry Zachodnie"),
    "Salatín":                           (49.1783, 19.7217, 2048, "Tatry Zachodnie"),
    "Brestová":                          (49.1933, 19.8033, 1903, "Tatry Zachodnie"),
    "Hruba Kopa":                        (49.2000, 19.8250, 2166, "Tatry Zachodnie"),
    "Tatliakova veža":                   (49.1917, 19.7800, 1879, "Tatry Zachodnie"),
    "Pachola":                           (49.2100, 19.8100, 1874, "Tatry Zachodnie"),
    "Gaborova skala":                    (49.1983, 19.8433, 2075, "Tatry Zachodnie"),
    "Banikovský štít":                   (49.1950, 19.8167, 2178, "Tatry Zachodnie"),
    "Tomanová (przełęcz)":               (49.2200, 19.8750, 1686, "Tatry Zachodnie"),
    "Siodłowy Wierch (Sedlo)":           (49.2150, 19.8417, 1995, "Tatry Zachodnie"),

    # ---------- TATRY SŁOWACKIE ----------
    "Gerlach (Gerlachovský štít)":        (49.1833, 20.1333, 2655, "Tatry Słowackie"),
    "Łomnica (Lomnický štít)":            (49.1953, 20.2133, 2634, "Tatry Słowackie"),
    "Kołowy Szczyt (Kolový štít)":        (49.1800, 20.0617, 2418, "Tatry Słowackie"),
    "Krywań (Kriváň)":                    (49.1767, 19.9933, 2494, "Tatry Słowackie"),
    "Wysoka (Vysoká)":                    (49.1817, 20.1017, 2560, "Tatry Słowackie"),
    "Ganek":                              (49.1850, 20.1150, 2462, "Tatry Słowackie"),
    "Lodowy Szczyt (Ľadový štít)":        (49.1900, 20.1483, 2627, "Tatry Słowackie"),
    "Żabi Szczyt Niżni (Žabí štít)":      (49.1983, 20.0900, 2253, "Tatry Słowackie"),
    "Żabi Szczyt Wyżni":                  (49.1967, 20.0867, 2259, "Tatry Słowackie"),
    "Durny Szczyt (Tupá)":                (49.1767, 20.1317, 2618, "Tatry Słowackie"),
    "Szeroka Jaworzyńska (Jahňací štít)": (49.1900, 20.1700, 2210, "Tatry Słowackie"),
    "Mały Kieżmarski Szczyt":             (49.1950, 20.1900, 2513, "Tatry Słowackie"),
    "Wielki Kieżmarski Szczyt":           (49.1933, 20.2017, 2556, "Tatry Słowackie"),
    "Staroleśny Szczyt (Slavkovský štít)":(49.2017, 20.1833, 2452, "Tatry Słowackie"),
    "Hawrań (Havran)":                    (49.2183, 20.2883, 2152, "Tatry Słowackie"),
    "Murań (Murán)":                      (49.2150, 20.2783, 2068, "Tatry Słowackie"),
    "Jagnięcy Szczyt (Baranec)":          (49.1933, 19.8717, 2185, "Tatry Słowackie"),
    "Wołowiec (Volovec)":                 (49.2083, 20.0383, 2064, "Tatry Słowackie"),
    "Solisko":                            (49.2200, 19.9700, 2093, "Tatry Słowackie"),
    "Szatan":                             (49.1967, 20.0483, 2415, "Tatry Słowackie"),
    "Rysy (słowackie podejście)":         (49.1794, 20.0883, 2499, "Tatry Słowackie"),
    "Téryho chata (okolice)":             (49.2017, 20.1600, 2015, "Tatry Słowackie"),
    "Nefcerka":                           (49.1883, 20.0983, 2335, "Tatry Słowackie"),
    "Mengusovský štít":                   (49.1900, 20.0800, 2438, "Tatry Słowackie"),
    "Popradský štít":                     (49.1817, 20.1583, 2369, "Tatry Słowackie"),
    "Rysia veža":                         (49.1850, 20.0950, 2350, "Tatry Słowackie"),

    # ---------- BESKID ŚLĄSKI ----------
    "Skrzyczne":                          (49.7100, 19.0317, 1257, "Beskid Śląski"),
    "Klimczok":                           (49.7383, 19.0383, 1117, "Beskid Śląski"),
    "Błatnia":                            (49.7050, 19.0983, 1005, "Beskid Śląski"),
    "Równica":                            (49.7300, 18.8683,  884, "Beskid Śląski"),
    "Czantoria Wielka":                   (49.7483, 18.8217,  995, "Beskid Śląski"),
    "Barania Góra":                       (49.6617, 18.9200, 1220, "Beskid Śląski"),
    "Magurka Wiślańska":                  (49.6783, 18.9667, 1073, "Beskid Śląski"),
    "Stożek Wielki":                      (49.6883, 18.8633,  978, "Beskid Śląski"),
    "Wielka Czantoria":                   (49.7483, 18.8217,  995, "Beskid Śląski"),
    "Soszów Wielki":                      (49.6950, 18.8467,  863, "Beskid Śląski"),

    # ---------- BESKID ŻYWIECKI ----------
    "Babia Góra":                         (49.5733, 19.5300, 1725, "Beskid Żywiecki"),
    "Pilsko":                             (49.5467, 19.3683, 1557, "Beskid Żywiecki"),
    "Romanka":                            (49.5583, 19.3033, 1366, "Beskid Żywiecki"),
    "Lipowski Wierch":                    (49.5317, 19.2733, 1324, "Beskid Żywiecki"),
    "Mędralowa":                          (49.5600, 19.4183, 1169, "Beskid Żywiecki"),
    "Wielka Racza":                       (49.4617, 19.1083, 1236, "Beskid Żywiecki"),
    "Prusów":                             (49.5683, 19.2583, 1209, "Beskid Żywiecki"),
    "Rysianka":                           (49.5617, 19.4317, 1322, "Beskid Żywiecki"),
    "Hala Miziowa":                       (49.5700, 19.4833, 1180, "Beskid Żywiecki"),
    "Jałowiec":                           (49.6083, 19.5433, 1111, "Beskid Żywiecki"),

    # ---------- GORCE ----------
    "Turbacz":                            (49.5667, 20.1117, 1310, "Gorce"),
    "Luboń Wielki":                       (49.6583, 19.9283,  968, "Gorce"),
    "Mogielica":                          (49.6667, 20.1667, 1170, "Gorce"),
    "Szczebel":                           (49.6983, 20.0833,  977, "Gorce"),
    "Łopień":                             (49.6850, 20.2000,  952, "Gorce"),
    "Kudłoń":                             (49.5783, 20.1167, 1276, "Gorce"),
    "Jaworzyna Gorczańska":               (49.5583, 20.1317, 1288, "Gorce"),

    # ---------- BESKID WYSPOWY ----------
    "Łysa Góra (Beskid Wyspowy)":         (49.7083, 20.4583,  791, "Beskid Wyspowy"),
    "Cichoń":                             (49.6750, 20.3583,  892, "Beskid Wyspowy"),
    "Śnieżnica":                          (49.7167, 20.3083,  1006, "Beskid Wyspowy"),

    # ---------- BESKID SĄDECKI ----------
    "Jaworzyna Krynicka":                 (49.4067, 20.9683, 1114, "Beskid Sądecki"),
    "Radziejowa":                         (49.4567, 20.6383, 1262, "Beskid Sądecki"),
    "Przehyba":                           (49.4667, 20.5833, 1175, "Beskid Sądecki"),
    "Hala Łabowska":                      (49.4417, 20.8533,  997, "Beskid Sądecki"),
    "Wielki Rogacz":                      (49.4383, 20.7000, 1182, "Beskid Sądecki"),
    "Pusta Wielka":                       (49.4083, 20.8083, 1060, "Beskid Sądecki"),

    # ---------- PIENINY ----------
    "Trzy Korony":                        (49.4083, 20.3983,  982, "Pieniny"),
    "Sokolica":                           (49.4017, 20.4017,  747, "Pieniny"),
    "Wysoka":                             (49.3817, 20.4467, 1050, "Pieniny"),
}

PASMA = sorted(set(v[3] for v in SZCZYTY.values()))

# ============================================================
# ZDJĘCIA SZCZYTÓW (Wikimedia Commons — Creative Commons)
# ============================================================
ZDJECIA = {
    "Rysy":                               "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Rysy_from_Morskie_Oko.jpg/800px-Rysy_from_Morskie_Oko.jpg",
    "Giewont":                            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Giewont_z_Kulbackiego.jpg/800px-Giewont_z_Kulbackiego.jpg",
    "Kasprowy Wierch":                    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Kasprowy_Wierch.jpg/800px-Kasprowy_Wierch.jpg",
    "Świnica":                            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Swinica.jpg/800px-Swinica.jpg",
    "Kościelec":                          "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Ko%C5%9Bcielec_from_the_east.jpg/800px-Ko%C5%9Bcielec_from_the_east.jpg",
    "Morskie Oko":                        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Morskie_Oko_2.jpg/800px-Morskie_Oko_2.jpg",
    "Mięguszowiecki Szczyt Wielki":       "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Mieguszowieckie_szczyty.jpg/800px-Mieguszowieckie_szczyty.jpg",
    "Wołowiec":                           "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Wo%C5%82owiec_2064.jpg/800px-Wo%C5%82owiec_2064.jpg",
    "Starorobociański Wierch":            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Starorobocianski_Wierch.jpg/800px-Starorobocianski_Wierch.jpg",
    "Bystra":                             "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Bystra.jpg/800px-Bystra.jpg",
    "Krzesanica":                         "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Krzesanica.jpg/800px-Krzesanica.jpg",
    "Gerlach (Gerlachovský štít)":        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Gerlach%2C_highest_peak_of_the_Tatras.jpg/800px-Gerlach%2C_highest_peak_of_the_Tatras.jpg",
    "Łomnica (Lomnický štít)":            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Lomnick%C3%BD_%C5%A1t%C3%ADt_from_south.jpg/800px-Lomnick%C3%BD_%C5%A1t%C3%ADt_from_south.jpg",
    "Krywań (Kriváň)":                    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Krivan.jpg/800px-Krivan.jpg",
    "Kołowy Szczyt (Kolový štít)":        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Kolovy_stit.jpg/800px-Kolovy_stit.jpg",
    "Babia Góra":                         "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Babia_G%C3%B3ra_from_Zawoja.jpg/800px-Babia_G%C3%B3ra_from_Zawoja.jpg",
    "Turbacz":                            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Turbacz.jpg/800px-Turbacz.jpg",
    "Skrzyczne":                          "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Skrzyczne.jpg/800px-Skrzyczne.jpg",
    "Pilsko":                             "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Pilsko.jpg/800px-Pilsko.jpg",
    "Rohacz Ostry (Ostrý Roháč)":        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Rohace_panorama.jpg/800px-Rohace_panorama.jpg",
    "Rohacz Płaski (Plochý Roháč)":      "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Rohace_panorama.jpg/800px-Rohace_panorama.jpg",
    "Hawrań (Havran)":                    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Havran_from_the_south.jpg/800px-Havran_from_the_south.jpg",
    "Trzy Korony":                        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Trzy_Korony_-_Pieniny.jpg/800px-Trzy_Korony_-_Pieniny.jpg",
}

# ============================================================
# LINKI ZEWNĘTRZNE DO SERWISÓW POGODOWYCH
# ============================================================
def link_mountain_forecast(nazwa, lat, lon, wys):
    """Mountain-forecast.com — wymaga nazwy szczytu w URL."""
    # Normalizuj nazwę do formatu URL (małe litery, myślniki)
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', nazwa.lower().split('(')[0].strip()
                  .replace('ą','a').replace('ć','c').replace('ę','e')
                  .replace('ł','l').replace('ń','n').replace('ó','o')
                  .replace('ś','s').replace('ź','z').replace('ż','z')
                  .replace('á','a').replace('é','e').replace('í','i')
                  .replace('ú','u').replace('ý','y').replace('č','c')
                  .replace('š','s').replace('ž','z').replace('ř','r')
                  ).strip('-')
    return f"https://www.mountain-forecast.com/peaks/{slug}/forecasts/{wys}"

def link_meteoblue(lat, lon, nazwa):
    """Meteoblue — bezpośredni URL do prognozy dla współrzędnych."""
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', nazwa.lower().split('(')[0].strip()
                  .replace('ą','a').replace('ć','c').replace('ę','e')
                  .replace('ł','l').replace('ń','n').replace('ó','o')
                  .replace('ś','s').replace('ź','z').replace('ż','z')
                  ).strip('-')
    return f"https://www.meteoblue.com/pl/pogoda/tydzien/{slug}_polska_{lat:.4f}N{lon:.4f}E"

def link_yr_web(lat, lon):
    """Yr.no — strona z prognozą dla współrzędnych."""
    return f"https://www.yr.no/en/forecast/daily-table/{lat:.4f}N{lon:.4f}E"

def link_windy(lat, lon):
    """Windy.com — dobra wizualizacja wiatru i burz górskich."""
    return f"https://www.windy.com/{lat:.2f}/{lon:.2f}?{lat:.2f},{lon:.2f},11"

def link_meteoalarm(lat, lon):
    """MeteoAlarm — europejskie ostrzeżenia meteorologiczne."""
    return "https://www.meteoalarm.org/en/live/?fbclid=IwAR0#poland"

# ============================================================
# KODY WMO
# ============================================================
WMO_KODY = {
    0:  ("☀️",  "Bezchmurnie"),
    1:  ("🌤️", "Głównie pogodnie"),
    2:  ("⛅",  "Częściowe zachmurzenie"),
    3:  ("☁️",  "Pochmurno"),
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
    75: ("❄️",  "Śnieg intensywny"),
    77: ("🌨️", "Ziarnisty śnieg"),
    80: ("🌦️", "Przelotny deszcz lekki"),
    81: ("🌧️", "Przelotny deszcz umiarkowany"),
    82: ("⛈️",  "Przelotny deszcz intensywny"),
    85: ("🌨️", "Przelotny śnieg lekki"),
    86: ("❄️",  "Przelotny śnieg intensywny"),
    95: ("⛈️",  "Burza"),
    96: ("⛈️",  "Burza z gradem"),
    99: ("⛈️",  "Burza z silnym gradem"),
}

def get_wmo_info(code):
    return WMO_KODY.get(int(code) if code is not None else 0, ("❓", "Nieznane"))

# ============================================================
# POMOCNICZE
# ============================================================
def kierunek_wiatru(stopnie):
    kierunki = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return kierunki[round(stopnie / 45) % 8]

def ocen_warunki(wiatr, porywy, opady, snieg, kod):
    if wiatr > 20 or porywy > 25 or kod in [95, 96, 99]:
        return "🔴 Niebezpieczne"
    elif wiatr > 12 or porywy > 18 or opady > 5 or snieg > 3:
        return "🟡 Utrudnione"
    elif wiatr > 8 or opady > 1:
        return "🟠 Umiarkowane"
    return "🟢 Dobre"

def nastepny_weekend():
    now = datetime.now()
    dni_do_soboty = (5 - now.weekday()) % 7
    if dni_do_soboty == 0 and now.hour >= 20:
        dni_do_soboty = 7
    sobota = (now + timedelta(days=dni_do_soboty)).date()
    return sobota, sobota + timedelta(days=1)

def geokoduj_szczyt(nazwa):
    url = "https://nominatim.openstreetmap.org/search"
    for query in [f"{nazwa} Tatry", f"{nazwa} Beskidy", f"{nazwa} góra Polska", nazwa]:
        try:
            r = requests.get(url, params={"q": query, "format": "json", "limit": 1},
                             headers={"User-Agent": "MountainWeatherApp/1.0"}, timeout=5)
            data = r.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", nazwa)
        except Exception:
            continue
    return None, None, None

# ============================================================
# ŹRÓDŁA POGODY
# ============================================================

def pobierz_open_meteo(lat, lon):
    """Open-Meteo — model best_match (ICON/ECMWF)."""
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": ["temperature_2m", "apparent_temperature", "precipitation",
                   "snowfall", "weathercode", "windspeed_10m", "windgusts_10m",
                   "winddirection_10m", "cloudcover", "visibility", "freezinglevel_height"],
        "windspeed_unit": "ms",
        "timezone": "Europe/Warsaw",
        "forecast_days": 10,
        "models": "best_match",
    }
    r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10)
    d = r.json()
    godziny = pd.to_datetime(d["hourly"]["time"])
    return pd.DataFrame({
        "czas": godziny,
        "temp": d["hourly"]["temperature_2m"],
        "odczuwalna": d["hourly"]["apparent_temperature"],
        "opady": d["hourly"]["precipitation"],
        "snieg": d["hourly"]["snowfall"],
        "kod": d["hourly"]["weathercode"],
        "wiatr": d["hourly"]["windspeed_10m"],
        "porywy": d["hourly"]["windgusts_10m"],
        "kierunek": d["hourly"]["winddirection_10m"],
        "zachmurzenie": d["hourly"]["cloudcover"],
        "widocznosc": d["hourly"]["visibility"],
        "izot0": d["hourly"]["freezinglevel_height"],
    })

def pobierz_yr(lat, lon):
    """Yr.no (MET Norway) — model NWP."""
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/complete?lat={lat:.4f}&lon={lon:.4f}"
    r = requests.get(url, headers={"User-Agent": "MountainWeatherApp/1.0 github.com/minerek/mountain_weather"}, timeout=10)
    data = r.json()
    rows = []
    for ts in data["properties"]["timeseries"]:
        t = pd.to_datetime(ts["time"])
        inst = ts["data"]["instant"]["details"]
        next1 = ts["data"].get("next_1_hours", {}).get("details", {})
        next6 = ts["data"].get("next_6_hours", {}).get("details", {})
        sym = (ts["data"].get("next_1_hours") or ts["data"].get("next_6_hours") or {}).get("summary", {}).get("symbol_code", "")
        opady = next1.get("precipitation_amount") or next6.get("precipitation_amount") or 0
        rows.append({
            "czas": t,
            "temp": inst.get("air_temperature"),
            "odczuwalna": inst.get("air_temperature"),  # yr nie daje odczuwalnej
            "opady": opady,
            "snieg": 0,
            "kod": yr_symbol_to_wmo(sym),
            "wiatr": inst.get("wind_speed", 0),
            "porywy": inst.get("wind_speed_of_gust", inst.get("wind_speed", 0)),
            "kierunek": inst.get("wind_from_direction", 0),
            "zachmurzenie": inst.get("cloud_area_fraction", 0),
            "widocznosc": inst.get("fog_area_fraction", 0),
            "izot0": 0,
            "symbol_yr": sym,
        })
    df = pd.DataFrame(rows)
    df["czas"] = df["czas"].dt.tz_convert("Europe/Warsaw").dt.tz_localize(None)
    return df

def yr_symbol_to_wmo(symbol):
    """Przybliżone mapowanie symboli Yr.no na kody WMO."""
    s = symbol.lower()
    if "thunder" in s:               return 95
    if "heavysnow" in s:             return 75
    if "snow" in s:                  return 71
    if "sleet" in s:                 return 77
    if "heavyrain" in s:             return 65
    if "rain" in s:                  return 61
    if "lightrain" in s:             return 51
    if "fog" in s:                   return 45
    if "cloudy" in s:                return 3
    if "partlycloudy" in s:          return 2
    if "fair" in s:                  return 1
    if "clearsky" in s:              return 0
    return 2

def pobierz_open_meteo_icon(lat, lon):
    """Open-Meteo z modelem ICON-D2 (Niemcy, 2km — najlepszy dla Karpat)."""
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": ["temperature_2m", "apparent_temperature", "precipitation",
                   "snowfall", "weathercode", "windspeed_10m", "windgusts_10m",
                   "winddirection_10m", "cloudcover", "visibility", "freezinglevel_height"],
        "windspeed_unit": "ms",
        "timezone": "Europe/Warsaw",
        "forecast_days": 7,
        "models": "icon_seamless",
    }
    r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10)
    d = r.json()
    godziny = pd.to_datetime(d["hourly"]["time"])
    return pd.DataFrame({
        "czas": godziny,
        "temp": d["hourly"]["temperature_2m"],
        "odczuwalna": d["hourly"]["apparent_temperature"],
        "opady": d["hourly"]["precipitation"],
        "snieg": d["hourly"]["snowfall"],
        "kod": d["hourly"]["weathercode"],
        "wiatr": d["hourly"]["windspeed_10m"],
        "porywy": d["hourly"]["windgusts_10m"],
        "kierunek": d["hourly"]["winddirection_10m"],
        "zachmurzenie": d["hourly"]["cloudcover"],
        "widocznosc": d["hourly"]["visibility"],
        "izot0": d["hourly"]["freezinglevel_height"],
    })

ZRODLA = {
    "Open-Meteo (best_match)": pobierz_open_meteo,
    "Open-Meteo ICON": pobierz_open_meteo_icon,
    "Yr.no (MET Norway)": pobierz_yr,
}

ZRODLA_INFO = {
    "Open-Meteo (best_match)": "Automatyczny dobór najlepszego modelu (ICON/ECMWF/GFS). Darmowe, bez klucza.",
    "Open-Meteo ICON": "Model ICON Seamless (DWD Niemcy) — najlepszy dla Karpat i Alp, rozdzielczość 2–7 km.",
    "Yr.no (MET Norway)": "Norweski serwis meteorologiczny MET Norway. Doskonały dla gór, używa modelu NWP.",
}

# ============================================================
# BURZE — sprawdzenie przez Open-Meteo + link do Blitzortung
# ============================================================
def sprawdz_burze_weekend(df, sobota, niedziela):
    """Zwraca listę godzin z burzą w weekend na podstawie kodu WMO."""
    df_w = df[df["czas"].dt.date.isin([sobota, niedziela])].copy()
    burze = df_w[df_w["kod"].isin([95, 96, 99])]
    return burze

def link_blitzortung(lat, lon, zoom=8):
    return f"https://www.blitzortung.org/en/live_lightning_maps.php?map=10#map={zoom}/{lat:.3f}/{lon:.3f}"

def link_lightningmaps(lat, lon, zoom=9):
    return f"https://www.lightningmaps.org/?lang=pl#m=oss;t=3;s=0;o=0;b=;ts=0;y={lat:.3f};x={lon:.3f};z={zoom};d=2;dl=2;dc=0;"

# ============================================================
# WYŚWIETLANIE PROGNOZY
# ============================================================
def wyswietl_prognoze(df, nazwa, lat, lon, wys, sobota, niedziela, zrodlo_nazwa):
    df_weekend = df[df["czas"].dt.date.isin([sobota, niedziela])].copy()
    if df_weekend.empty:
        st.warning("Brak danych dla tego weekendu.")
        return

    burze = sprawdz_burze_weekend(df, sobota, niedziela)
    if not burze.empty:
        godziny_burz = burze["czas"].dt.strftime("%d.%m %H:%M").tolist()
        st.error(f"⛈️ **UWAGA — BURZE PROGNOZOWANE:** {', '.join(godziny_burz)}")
        col_b1, col_b2 = st.columns(2)
        col_b1.markdown(f"🔴 [Sprawdź wyładowania na Blitzortung]({link_blitzortung(lat, lon)})")
        col_b2.markdown(f"🔴 [Sprawdź wyładowania na LightningMaps]({link_lightningmaps(lat, lon)})")

    for dzien in [sobota, niedziela]:
        df_dzien = df_weekend[df_weekend["czas"].dt.date == dzien]
        if df_dzien.empty:
            continue

        nazwa_dnia = "🟦 Sobota" if dzien == sobota else "🟪 Niedziela"
        st.markdown(f"### {nazwa_dnia} — {dzien.strftime('%d.%m.%Y')}")

        temp_min = df_dzien["temp"].min()
        temp_max = df_dzien["temp"].max()
        wiatr_max = df_dzien["wiatr"].max()
        porywy_max = df_dzien["porywy"].max()
        opady_suma = df_dzien["opady"].sum()
        snieg_suma = df_dzien["snieg"].sum()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("🌡️ Temperatura", f"{temp_min:.0f} / {temp_max:.0f}°C", help="Min / Max")
        c2.metric("💨 Wiatr max", f"{wiatr_max:.1f} m/s")
        c3.metric("🌬️ Porywy", f"{porywy_max:.1f} m/s")
        c4.metric("🌧️ Opady", f"{opady_suma:.1f} mm")
        c5.metric("❄️ Śnieg", f"{snieg_suma:.1f} cm")

        if "izot0" in df_dzien.columns and df_dzien["izot0"].max() > 0:
            izot0_min = df_dzien["izot0"].min()
            izot0_max = df_dzien["izot0"].max()
            st.caption(f"Izotermia 0°C: {izot0_min:.0f}–{izot0_max:.0f} m n.p.m.")

        # Tabela godzinowa
        tab = df_dzien.copy()
        tab["Godzina"] = tab["czas"].dt.strftime("%H:%M")
        tab["Warunki"] = tab["kod"].apply(lambda k: " ".join(get_wmo_info(k)))
        tab["Ocena"] = tab.apply(lambda r: ocen_warunki(r["wiatr"], r["porywy"], r["opady"], r["snieg"], r["kod"]), axis=1)
        tab["Kier."] = tab["kierunek"].apply(kierunek_wiatru)
        cols_show = ["Godzina", "Warunki", "temp", "odczuwalna", "wiatr", "porywy", "Kier.", "opady", "snieg", "zachmurzenie", "Ocena"]
        tab_display = tab[cols_show].copy()
        tab_display.columns = ["Godzina", "Warunki", "Temp°C", "Odcz.°C", "Wiatr m/s", "Porywy m/s", "Kier.", "Opady mm", "Śnieg cm", "Chmury %", "Ocena"]
        st.dataframe(tab_display, use_container_width=True, hide_index=True)

        # Ostrzeżenia
        ost = []
        if wiatr_max > 20:
            ost.append(f"⚠️ **Bardzo silny wiatr** — porywy do {porywy_max:.0f} m/s! Nie zalecane wyjście na grań.")
        elif wiatr_max > 12:
            ost.append(f"⚠️ **Silny wiatr** — porywy do {porywy_max:.0f} m/s.")
        if df_dzien["kod"].isin([95, 96, 99]).any():
            ost.append("⛈️ **Burza** — ryzyko wyładowań! Zejdź z grzbietu przed burzą.")
        if opady_suma > 10:
            ost.append(f"🌧️ **Intensywne opady** — {opady_suma:.0f} mm łącznie.")
        if snieg_suma > 5:
            ost.append(f"❄️ **Śnieg** — {snieg_suma:.0f} cm. Zabierz raki/czeki.")
        if "izot0" in df_dzien.columns and df_dzien["izot0"].max() > 0 and df_dzien["izot0"].min() < 1500:
            ost.append(f"🧊 **Izotermia 0°C poniżej 1500 m** — oblodzenie możliwe.")

        if ost:
            for o in ost:
                st.warning(o)
        else:
            st.success("✅ Warunki bez szczególnych ostrzeżeń")

        st.divider()

    # Wykres
    st.markdown("### 📈 Wykresy")
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=("Temperatura (°C)", "Wiatr i porywy (m/s)", "Opady (mm)"),
                        vertical_spacing=0.08)
    fig.add_trace(go.Scatter(x=df_weekend["czas"], y=df_weekend["temp"],
                             name="Temp", line=dict(color="#e74c3c", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_weekend["czas"], y=df_weekend["odczuwalna"],
                             name="Odczuwalna", line=dict(color="#e74c3c", width=1, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_weekend["czas"], y=df_weekend["wiatr"],
                             name="Wiatr", line=dict(color="#3498db", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_weekend["czas"], y=df_weekend["porywy"],
                             name="Porywy", line=dict(color="#3498db", width=1, dash="dot")), row=2, col=1)
    fig.add_hrect(y0=12, y1=100, row=2, col=1, fillcolor="orange", opacity=0.1, line_width=0)
    fig.add_hrect(y0=20, y1=100, row=2, col=1, fillcolor="red", opacity=0.1, line_width=0)
    fig.add_trace(go.Bar(x=df_weekend["czas"], y=df_weekend["opady"],
                         name="Opady", marker_color="#2ecc71"), row=3, col=1)
    fig.update_layout(height=580, showlegend=True, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Źródło: {zrodlo_nazwa} | Geokodowanie: OpenStreetMap Nominatim")


def wyswietl_porownanie(dfs_dict, nazwa, lat, lon, wys, sobota, niedziela):
    """Wyświetla porównanie wielu źródeł na jednym wykresie."""
    st.markdown("### 🔀 Porównanie źródeł pogody")

    kolory = {"Open-Meteo (best_match)": "#e74c3c",
              "Open-Meteo ICON": "#e67e22",
              "Yr.no (MET Norway)": "#2980b9"}

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=("Temperatura (°C)", "Wiatr max (m/s)", "Opady (mm)"),
                        vertical_spacing=0.08)

    for zrodlo, df in dfs_dict.items():
        df_w = df[df["czas"].dt.date.isin([sobota, niedziela])].copy()
        if df_w.empty:
            continue
        kolor = kolory.get(zrodlo, "#888")
        fig.add_trace(go.Scatter(x=df_w["czas"], y=df_w["temp"],
                                 name=f"Temp — {zrodlo}", line=dict(color=kolor, width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_w["czas"], y=df_w["wiatr"],
                                 name=f"Wiatr — {zrodlo}", line=dict(color=kolor, width=2, dash="dot")), row=2, col=1)
        fig.add_trace(go.Bar(x=df_w["czas"], y=df_w["opady"],
                             name=f"Opady — {zrodlo}", opacity=0.6), row=3, col=1)

    fig.update_layout(height=650, showlegend=True, template="plotly_white",
                      title=f"Porównanie modeli — {nazwa} ({wys} m n.p.m.)")
    st.plotly_chart(fig, use_container_width=True)

    # Tabela podsumowująca
    st.markdown("#### Podsumowanie weekendu wg źródeł")
    summary_rows = []
    for zrodlo, df in dfs_dict.items():
        df_w = df[df["czas"].dt.date.isin([sobota, niedziela])].copy()
        if df_w.empty:
            continue
        summary_rows.append({
            "Źródło": zrodlo,
            "Temp min°C": f"{df_w['temp'].min():.1f}",
            "Temp max°C": f"{df_w['temp'].max():.1f}",
            "Wiatr max m/s": f"{df_w['wiatr'].max():.1f}",
            "Porywy max m/s": f"{df_w['porywy'].max():.1f}",
            "Opady mm": f"{df_w['opady'].sum():.1f}",
            "Burze": "⛈️ TAK" if df_w["kod"].isin([95, 96, 99]).any() else "—",
        })
    if summary_rows:
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)


# ============================================================
# UI
# ============================================================
st.title("⛰️ Pogoda Górska — Tatry & Beskidy")
sobota, niedziela = nastepny_weekend()
st.caption(f"Prognoza na najbliższy weekend: **{sobota.strftime('%d.%m.%Y')} (sob)** — **{niedziela.strftime('%d.%m.%Y')} (nd)**")
st.divider()

# --- Sekcja 1: Wybór źródła ---
st.markdown("### 1️⃣ Wybierz źródło pogody")
tryb_zrodla = st.radio(
    "Tryb:",
    ["Jedno źródło", "Porównaj wszystkie źródła"],
    horizontal=True,
    help="Tryb porównania pobiera dane ze wszystkich źródeł i zestawia je na jednym wykresie."
)

if tryb_zrodla == "Jedno źródło":
    wybrane_zrodlo = st.selectbox(
        "Źródło danych:",
        list(ZRODLA.keys()),
        help="Wybierz skąd pobierać prognozę pogody."
    )
    st.caption(f"ℹ️ {ZRODLA_INFO[wybrane_zrodlo]}")
else:
    st.info("ℹ️ Zostaną pobrane dane ze wszystkich 3 źródeł: Open-Meteo best_match, Open-Meteo ICON oraz Yr.no (MET Norway)")

st.divider()

# --- Sekcja 2: Filtr pasm + wybór szczytu ---
st.markdown("### 2️⃣ Wybierz pasmo i szczyt")

col_pasma, col_szczyt = st.columns([1, 2])

with col_pasma:
    wybrane_pasma = st.multiselect(
        "Pasma górskie:",
        options=PASMA,
        default=["Tatry Polskie", "Tatry Słowackie"],
        help="Zaznacz jedno lub więcej pasm — lista szczytów zostanie odfiltrowana."
    )

if not wybrane_pasma:
    wybrane_pasma = PASMA  # jeśli nic nie zaznaczono — pokaż wszystkie

szczyty_przefiltrowane = {
    nazwa: dane for nazwa, dane in SZCZYTY.items()
    if dane[3] in wybrane_pasma
}

with col_szczyt:
    tryb = st.radio("Wybór szczytu:", ["Z listy", "Wpisz nazwę ręcznie"], horizontal=True)

    if tryb == "Z listy":
        # Grupuj wg pasma dla czytelności
        opcje = sorted(szczyty_przefiltrowane.keys(),
                       key=lambda n: (SZCZYTY[n][3], n))
        wybrany = st.selectbox(
            "Szczyt:",
            opcje,
            format_func=lambda n: f"{n}  ({SZCZYTY[n][2]} m) — {SZCZYTY[n][3]}"
        )
        lat, lon, wys = SZCZYTY[wybrany][0], SZCZYTY[wybrany][1], SZCZYTY[wybrany][2]
        nazwa_wyswietlana = wybrany
        wspolrzedne_ok = True
    else:
        nazwa_wpisana = st.text_input(
            "Wpisz nazwę szczytu:",
            placeholder="np. Kołowy Szczyt, Babia Góra, Gerlach..."
        )
        wspolrzedne_ok = False
        lat = lon = wys = None
        nazwa_wyswietlana = nazwa_wpisana if nazwa_wpisana else ""

# Geokodowanie ręcznej nazwy
if tryb == "Wpisz nazwę ręcznie" and nazwa_wpisana:
    if nazwa_wpisana in SZCZYTY:
        lat, lon, wys = SZCZYTY[nazwa_wpisana][0], SZCZYTY[nazwa_wpisana][1], SZCZYTY[nazwa_wpisana][2]
        nazwa_wyswietlana = nazwa_wpisana
        wspolrzedne_ok = True
    else:
        with st.spinner("Szukam lokalizacji..."):
            lat, lon, display = geokoduj_szczyt(nazwa_wpisana)
        if lat:
            wys = 0
            wspolrzedne_ok = True
            st.success(f"✅ Znaleziono: {display}")
        else:
            st.error("❌ Nie znaleziono. Spróbuj innej pisowni lub wybierz z listy.")

if wspolrzedne_ok and lat:
    wys_str = f"{wys} m n.p.m." if wys else ""

    # Zdjęcie + info obok siebie
    zdjecie_url = ZDJECIA.get(nazwa_wyswietlana)
    if zdjecie_url:
        col_foto, col_info = st.columns([1, 2])
        with col_foto:
            try:
                st.image(zdjecie_url, caption=nazwa_wyswietlana, use_container_width=True)
            except Exception:
                pass
        with col_info:
            st.markdown(f"### 📍 {nazwa_wyswietlana}")
            st.markdown(f"**Wysokość:** {wys_str}  |  `{lat:.4f}°N, {lon:.4f}°E`")
            _pasmo = SZCZYTY.get(nazwa_wyswietlana, (None, None, None, ""))[3]
            if _pasmo:
                st.markdown(f"**Pasmo:** {_pasmo}")
            st.markdown("**🔗 Prognozy zewnętrzne:**")
            ln_cols = st.columns(4)
            ln_cols[0].markdown(f"[🏔️ Mountain\u2011Forecast]({link_mountain_forecast(nazwa_wyswietlana, lat, lon, wys or 1000)})")
            ln_cols[1].markdown(f"[🌐 Meteoblue]({link_meteoblue(lat, lon, nazwa_wyswietlana)})")
            ln_cols[2].markdown(f"[🇳🇴 Yr.no]({link_yr_web(lat, lon)})")
            ln_cols[3].markdown(f"[💨 Windy]({link_windy(lat, lon)})")
    else:
        st.info(f"📍 **{nazwa_wyswietlana}** {wys_str}  |  `{lat:.4f}°N, {lon:.4f}°E`")
        st.markdown("**🔗 Prognozy zewnętrzne:**")
        ln_cols = st.columns(4)
        ln_cols[0].markdown(f"[🏔️ Mountain\u2011Forecast]({link_mountain_forecast(nazwa_wyswietlana, lat, lon, wys or 1000)})")
        ln_cols[1].markdown(f"[🌐 Meteoblue]({link_meteoblue(lat, lon, nazwa_wyswietlana)})")
        ln_cols[2].markdown(f"[🇳🇴 Yr.no]({link_yr_web(lat, lon)})")
        ln_cols[3].markdown(f"[💨 Windy]({link_windy(lat, lon)})")

st.divider()

# --- Przycisk pobierania ---
if wspolrzedne_ok and st.button("🔍 Sprawdź pogodę na weekend", type="primary"):
    if tryb_zrodla == "Porównaj wszystkie źródła":
        dfs = {}
        errors = []
        for nazwa_z, fn in ZRODLA.items():
            try:
                with st.spinner(f"Pobieram z {nazwa_z}..."):
                    dfs[nazwa_z] = fn(lat, lon)
            except Exception as e:
                errors.append(f"❌ {nazwa_z}: {e}")
        if errors:
            for e in errors:
                st.warning(e)
        if dfs:
            wyswietl_porownanie(dfs, nazwa_wyswietlana, lat, lon, wys or 0, sobota, niedziela)
            # Pokaż też ostrzeżenia burzowe z pierwszego dostępnego źródła
            df_ref = list(dfs.values())[0]
            burze = sprawdz_burze_weekend(df_ref, sobota, niedziela)
            if not burze.empty:
                st.markdown("---")
                st.markdown("#### ⛈️ Monitorowanie wyładowań atmosferycznych w czasie rzeczywistym")
                c1, c2 = st.columns(2)
                c1.markdown(f"🗺️ [Blitzortung.org — mapa wyładowań]({link_blitzortung(lat, lon)})")
                c2.markdown(f"🗺️ [LightningMaps.org — mapa wyładowań]({link_lightningmaps(lat, lon)})")
                st.caption("Powyższe linki otwierają mapę wyśrodkowaną na wybrany szczyt.")
    else:
        fn = ZRODLA[wybrane_zrodlo]
        try:
            with st.spinner(f"Pobieram prognozę z {wybrane_zrodlo}..."):
                df = fn(lat, lon)
        except Exception as e:
            st.error(f"Błąd pobierania danych: {e}")
            st.stop()
        wyswietl_prognoze(df, nazwa_wyswietlana, lat, lon, wys or 0, sobota, niedziela, wybrane_zrodlo)

        # Linki do monitorowania burz zawsze widoczne na dole
        st.markdown("---")
        st.markdown("#### ⛈️ Monitorowanie wyładowań atmosferycznych")
        c1, c2 = st.columns(2)
        c1.markdown(f"🗺️ [Blitzortung.org — mapa live]({link_blitzortung(lat, lon)})")
        c2.markdown(f"🗺️ [LightningMaps.org — mapa live]({link_lightningmaps(lat, lon)})")
        st.caption("Linki otwierają mapy wyśrodkowane na wybrany szczyt. Dane burzowe są aktualizowane w czasie rzeczywistym.")

elif not wspolrzedne_ok:
    if tryb == "Wpisz nazwę ręcznie" and not nazwa_wpisana:
        st.info("👆 Wpisz nazwę szczytu lub wybierz z listy, następnie kliknij przycisk.")
else:
    st.info("👆 Wybierz szczyt i kliknij 'Sprawdź pogodę na weekend'")
