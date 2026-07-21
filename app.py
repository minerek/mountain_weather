import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Favicon jako SVG data-URI — trojkat gorki, te same kolory co banner
_FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%230a2a3a'/%3E%3Cpolygon points='16,4 28,26 4,26' fill='%234a7a9b'/%3E%3Cpolygon points='16,4 21,13 11,13' fill='%23ddeeff' opacity='0.9'/%3E%3Cpolygon points='11,13 13,18 4,26 28,26 21,13 19,18' fill='%23144a5e'/%3E%3C/svg%3E"

st.set_page_config(
    page_title="Mountain Weather — Tatry & Beskidy",
    page_icon=_FAVICON,
    layout="wide"
)

# ============================================================
# CUSTOM CSS — wygląd i czytelność
# ============================================================
# Zaladuj Google Font Cinzel (serif gorski) przez components.html — st.markdown blokuje @import
components.html("""<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap" rel="stylesheet">""", height=0)

st.markdown("""
<style>
/* ---- Czcionka Cinzel dla naglowkow ---- */
.mw-heading {
    font-family: 'Cinzel', Georgia, serif !important;
    color: #90bce0 !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    border-bottom: 1px solid #1e3a58;
    padding-bottom: 5px;
    margin-top: 1.1rem !important;
    margin-bottom: 0.6rem !important;
}
.mw-peak-title {
    font-family: 'Cinzel', Georgia, serif !important;
    color: #c8ddf0 !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    margin-bottom: 4px !important;
}
/* ---- Ciemne tlo granatowe ---- */
[data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0e1e2f !important;
}
[data-testid="stHeader"] {
    background-color: #0a1520 !important;
}
/* Pasek Streamlit ma ok 58px — odsuwamy tresc zeby banner byl widoczny */
[data-testid="stMain"] { padding-top: 0 !important; }
[data-testid="stAppViewBlockContainer"] { padding-top: 75px !important; }
/* Iframe bannera — pelna szerokosc */
iframe[title="streamlit_component.v1.html"] {
    display: block !important;
    width: 100% !important;
    border-radius: 8px !important;
}
/* ---- Tekst ogolny ---- */
body, p, div, span, label {
    color: #c8ddf0 !important;
}
/* ---- Nagłówki ---- */
h1 { font-size: 1.9rem !important; font-weight: 800 !important; color: #e8f4ff !important; }
h2 { color: #c8ddf0 !important; }
h3 { font-family: 'Cinzel', Georgia, serif !important; color: #90bce0 !important; border-bottom: 1px solid #1e3a58; padding-bottom: 4px; margin-top: 1.2rem !important; font-size: 1.1rem !important; letter-spacing: 1px !important; }

/* ---- Karty metryk ---- */
[data-testid="metric-container"] {
    background: #152436;
    border: 1px solid #1e3a58;
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
[data-testid="metric-container"] label { font-size: 0.75rem !important; color: #7aaac8 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.25rem !important; font-weight: 700 !important; color: #e0f0ff !important;
}

/* ---- Selectbox / multiselect ---- */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #152436 !important;
    border-color: #1e3a58 !important;
    color: #c8ddf0 !important;
    border-radius: 8px !important;
}

/* ---- Radio ---- */
[data-testid="stRadio"] > div { gap: 8px; }
[data-testid="stRadio"] label {
    background: #152436 !important;
    border: 1px solid #1e3a58 !important;
    border-radius: 6px;
    padding: 4px 14px;
    font-size: 0.88rem;
    color: #c8ddf0 !important;
}

/* ---- Przycisk primary ---- */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #2c6fad, #1a4a7a) !important;
    color: white !important;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    padding: 0.55rem 1.6rem;
    border: none;
    box-shadow: 0 2px 8px rgba(28,74,122,0.5);
}

/* ---- Tabela danych ---- */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* ---- Alerty ---- */
[data-testid="stAlert"] { border-radius: 8px; }

/* ---- Divider ---- */
hr { border-color: #1e3a58 !important; margin: 0.8rem 0 !important; }

/* ---- Linki bez podkreslenia ---- */
a { text-decoration: none !important; }
a:hover { text-decoration: underline !important; opacity: 0.85; }

/* ---- Caption / subtext ---- */
[data-testid="stCaptionContainer"] p { color: #7aaac8 !important; }

/* ---- Multiselect tagi — ciemnogranatowe ---- */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: #1e3a58 !important;
    color: #c8ddf0 !important;
    border: 1px solid #2e5a88 !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] svg { fill: #7aaac8 !important; }

/* ---- Dataframe tlo ---- */
[data-testid="stDataFrame"] table { background: #0e1e2f !important; }

/* ---- Karty rekomendacji pasm ---- */
.rec-card {
    background: #0e2233;
    border: 1px solid #1e4060;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
}
.rec-card.rec-best {
    background: #0a2a1a;
    border: 1px solid #1e7a40;
}
.rec-card.rec-warn {
    background: #2a1a0a;
    border: 1px solid #7a4010;
}
.rec-badge {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #7aaac8;
}
.rec-name {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #e8f4ff;
}
.rec-stats {
    font-size: 0.82rem;
    color: #8ab4cc;
    margin-top: 2px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# BAZA SZCZYTÓW: (lat, lon, wysokość m n.p.m., pasmo)
# ============================================================
# Pasma: "Tatry Polskie", "Tatry Słowackie", "Beskid Śląski",
#        "Beskid Żywiecki", "Beskid Wyspowy", "Beskid Sądecki",
#        "Gorce", "Pieniny"

# Wielka Korona Tatr (WKT) — 14 szczytów ≥8000 stóp z wybitnością ≥100m
WKT = {
    "Gerlach (Gerlachovský štít) ⭐WKT",
    "Łomnica (Lomnický štít) ⭐WKT",
    "Lodowy Szczyt (Ľadový štít) ⭐WKT",
    "Durny Szczyt (Pyšný štít) ⭐WKT",
    "Wysoka (Vysoká) ⭐WKT",
    "Kieżmarski Szczyt (Kežmarský štít) ⭐WKT",
    "Kończysta (Končistá) ⭐WKT",
    "Baranie Rogi (Baranie rohy) ⭐WKT",
    "Rysy ⭐WKT",
    "Krywań (Kriváň) ⭐WKT",
    "Staroleśny Szczyt (Bradavica) ⭐WKT",
    "Ganek (Gánok) ⭐WKT",
    "Sławkowski Szczyt (Slavkovský štít) ⭐WKT",
    "Pośrednia Grań (Prostredný hrot) ⭐WKT",
}

SZCZYTY = {
    # ---------- TATRY WYSOKIE — WSCHODNIA CZĘŚĆ (Morskie Oko, Rysy, Granaty...) ----------
    "Rysy ⭐WKT":                                    (49.1793, 20.0884, 2501, "Tatry Polskie"),
    "Kozi Wierch":                                   (49.2182, 20.0163, 2291, "Tatry Polskie"),
    "Kozie Czuby":                                   (49.2178, 20.0125, 2263, "Tatry Polskie"),
    "Mały Kozi Wierch":                              (49.2190, 20.0076, 2228, "Tatry Polskie"),
    "Zadni Granat":                                  (49.2248, 20.0294, 2240, "Tatry Polskie"),
    "Pośredni Granat":                               (49.2263, 20.0332, 2234, "Tatry Polskie"),
    "Skrajny Granat":                                (49.2280, 20.0368, 2225, "Tatry Polskie"),
    "Żabi Koń":                                      (49.1772, 20.0805, 2291, "Tatry Polskie"),
    "Jagnięcy Szczyt (Jahňací štít)":                (49.2155, 20.2120, 2229, "Tatry Słowackie"),
    "Żabi Szczyt Polski":                            (49.1925, 20.0869, 2259, "Tatry Polskie"),
    "Mięguszowiecki Szczyt Wielki":                  (49.1875, 20.0591, 2438, "Tatry Polskie"),
    "Mięguszowiecki Szczyt Czarny":                  (49.1893, 20.0653, 2410, "Tatry Polskie"),
    "Mięguszowiecki Szczyt Pośredni":                (49.1882, 20.0619, 2393, "Tatry Polskie"),
    "Cubryna":                                       (49.1895, 20.0536, 2376, "Tatry Polskie"),
    "Szpiglasowy Wierch (Hrubý štít)":               (49.1969, 20.0411, 2172, "Tatry Polskie"),
    "Kazalnica Mięguszowiecka":                      (49.1897, 20.0694, 2159, "Tatry Polskie"),
    "Kościelec":                                     (49.2255, 20.0147, 2155, "Tatry Polskie"),
    "Zawrat":                                        (49.2195, 20.0161, 2159, "Tatry Polskie"),
    "Świnica":                                       (49.2196, 20.0094, 2301, "Tatry Polskie"),
    "Morskie Oko":                                   (49.2014, 20.0708, 1395, "Tatry Polskie"),
    "Czarny Staw pod Rysami":                        (49.1917, 20.0725, 1580, "Tatry Polskie"),
    "Mały Kościelec":                                (49.2291, 20.0142, 1866, "Tatry Polskie"),
    "Nosal":                                         (49.2783, 19.9796, 1206, "Tatry Polskie"),
    "Sarnia Skała":                                  (49.2638, 19.9405, 1377, "Tatry Polskie"),
    "Wielki Kopieniec":                              (49.2778, 19.9922, 1328, "Tatry Polskie"),

    # ---------- TATRY ZACHODNIE (polskie i słowackie) ----------
    "Bystra (Bystrá)":                               (49.1892, 19.8427, 2248, "Tatry Zachodnie"),
    "Starorobociański Wierch (Klin)":                (49.2003, 19.8142, 2176, "Tatry Zachodnie"),
    "Wołowiec (Volovec)":                            (49.2118, 19.7628, 2064, "Tatry Zachodnie"),
    "Baraniec (Baranec)":                            (49.1738, 19.7428, 2185, "Tatry Zachodnie"),
    "Banówka (Baníkov)":                             (49.1983, 19.7103, 2178, "Tatry Zachodnie"),
    "Hruba Kopa (Hrubá kopa)":                       (49.2008, 19.7214, 2166, "Tatry Zachodnie"),
    "Rohacz Ostry (Ostrý Roháč)":                    (49.2016, 19.7454, 2088, "Tatry Zachodnie"),
    "Rohacz Płaczliwy (Plačlivý Roháč)":             (49.1967, 19.7483, 2126, "Tatry Zachodnie"),
    "Smrek":                                         (49.2081, 19.7505, 2072, "Tatry Zachodnie"),
    "Kopa Kondracka (Kondratova kopa)":              (49.2368, 19.9328, 2005, "Tatry Zachodnie"),
    "Kończysty Wierch":                              (49.2346, 19.8202, 2002, "Tatry Zachodnie"),
    "Kasprowy Wierch (Kasprový vrch)":               (49.2323, 19.9817, 1987, "Tatry Zachodnie"),
    "Krzesanica (Kresanica)":                        (49.2338, 19.9142, 2122, "Tatry Zachodnie"),
    "Małołączniak (Malolúčniak)":                    (49.2355, 19.9230, 2096, "Tatry Zachodnie"),
    "Ciemniak (Temniak)":                            (49.2323, 19.9015, 2096, "Tatry Zachodnie"),
    "Tomanowy Wierch":                               (49.2227, 19.8972, 2103, "Tatry Zachodnie"),
    "Skrajne Solisko (Predné Solisko)":              (49.1558, 20.0319, 2117, "Tatry Słowackie"),
    "Twarda Kopa":                                   (49.2217, 19.8494, 2026, "Tatry Zachodnie"),
    "Beskid (Beskyd)":                               (49.2281, 19.8272, 2012, "Tatry Zachodnie"),
    "Smutny Zwornik (Smutný zvornik)":               (49.2233, 19.8531, 2010, "Tatry Zachodnie"),
    "Siwy Zwornik (Sivá veža)":                      (49.2336, 19.8317, 1965, "Tatry Zachodnie"),
    "Giewont":                                       (49.2510, 19.9339, 1894, "Tatry Zachodnie"),
    "Rakoń (Rákoň)":                                 (49.2197, 19.7634, 1879, "Tatry Zachodnie"),
    "Świstowa Kopa":                                 (49.2489, 19.8811, 1875, "Tatry Zachodnie"),
    "Ornak":                                         (49.2389, 19.8402, 1854, "Tatry Zachodnie"),
    "Siwy Wierch (Sivý vrch)":                       (49.2114, 19.6427, 1805, "Tatry Zachodnie"),
    "Trzydniowiański Wierch":                        (49.2396, 19.8091, 1765, "Tatry Zachodnie"),
    "Grześ (Lúčna)":                                 (49.2372, 19.7663, 1653, "Tatry Zachodnie"),
    "Salatín (Salatyński Wierch)":                   (49.2144, 19.6847, 2048, "Tatry Zachodnie"),
    "Mały Salatyn (Malý Salatín)":                   (49.1844, 19.7197, 2046, "Tatry Zachodnie"),
    "Klin (Malý Baranec)":                           (49.1878, 19.7467, 2044, "Tatry Zachodnie"),
    "Brestová (Brestowa)":                           (49.1953, 19.8058, 1934, "Tatry Zachodnie"),
    "Pachoł (Pachoľa)":                              (49.2100, 19.8100, 2167, "Tatry Zachodnie"),
    "Osobita":                                       (49.2572, 19.7542, 1687, "Tatry Zachodnie"),
    "Jarząbczy Wierch (Hrubý vrch)":                 (49.1960, 19.7915, 2137, "Tatry Zachodnie"),
    "Trzy Kopy — Przednia Kopa (Prvá kopa)":         (49.2297, 19.8717, 2136, "Tatry Zachodnie"),
    "Drobna Kopa (Druhá kopa)":                      (49.2308, 19.8703, 2129, "Tatry Zachodnie"),
    "Szeroka Kopa (Tretia kopa)":                    (49.2319, 19.8686, 2128, "Tatry Zachodnie"),
    "Rohacz Płaski (Plochý Roháč)":                  (49.1947, 19.7606, 2001, "Tatry Zachodnie"),
    "Nogawica (Nohavica)":                           (49.2156, 19.7928, 2052, "Tatry Zachodnie"),
    "Pośrednia Magura (Prostredná Magura)":          (49.2097, 19.7825, 2050, "Tatry Zachodnie"),
    "Pośredni Przysłop (Prostredný prislop)":        (49.2233, 19.8625, 2026, "Tatry Zachodnie"),

    # ---------- TATRY SŁOWACKIE ----------
    # WKT — szczyty Wielkiej Korony Tatr (oznaczone ⭐WKT)
    "Gerlach (Gerlachovský štít) ⭐WKT":          (49.1639, 20.1336, 2655, "Tatry Słowackie"),
    "Łomnica (Lomnický štít) ⭐WKT":              (49.1953, 20.2130, 2633, "Tatry Słowackie"),
    "Lodowy Szczyt (Ľadový štít) ⭐WKT":          (49.1895, 20.1504, 2627, "Tatry Słowackie"),
    "Durny Szczyt (Pyšný štít) ⭐WKT":            (49.1942, 20.1982, 2621, "Tatry Słowackie"),
    "Wysoka (Vysoká) ⭐WKT":                      (49.1728, 20.0983, 2558, "Tatry Słowackie"),
    "Kieżmarski Szczyt (Kežmarský štít) ⭐WKT":   (49.1932, 20.2120, 2557, "Tatry Słowackie"),
    "Kończysta (Končistá) ⭐WKT":                 (49.1643, 20.1087, 2538, "Tatry Słowackie"),
    "Baranie Rogi (Baranie rohy) ⭐WKT":          (49.1992, 20.1741, 2526, "Tatry Słowackie"),
    "Krywań (Kriváň) ⭐WKT":                      (49.1625, 20.0000, 2495, "Tatry Słowackie"),
    "Staroleśny Szczyt (Bradavica) ⭐WKT":        (49.1685, 20.1585, 2489, "Tatry Słowackie"),
    "Ganek (Gánok) ⭐WKT":                        (49.1770, 20.1037, 2464, "Tatry Słowackie"),
    "Sławkowski Szczyt (Slavkovský štít) ⭐WKT":  (49.1633, 20.1834, 2452, "Tatry Słowackie"),
    "Pośrednia Grań (Prostredný hrot) ⭐WKT":     (49.1873, 20.1941, 2439, "Tatry Słowackie"),
    # Pozostałe szczyty słowackie
    "Mała Wysoka (Východná Vysoká)":              (49.1738, 20.1411, 2429, "Tatry Słowackie"),
    "Koprowy Wierch (Kôprovský štít)":            (49.1718, 20.0469, 2363, "Tatry Słowackie"),
    "Koprowe Ramię (Kôprovské plece)":            (49.1931, 20.0139, 2312, "Tatry Słowackie"),
    "Kołowy Szczyt (Kolový štít)":                (49.1792, 20.0628, 2418, "Tatry Słowackie"),
    "Żabi Szczyt Niżni (Žabí štít)":              (49.1994, 20.0925, 2253, "Tatry Słowackie"),
    "Żabi Szczyt Wyżni":                          (49.1978, 20.0889, 2259, "Tatry Słowackie"),
    "Szeroka Jaworzyńska (Jahňací štít)":         (49.1908, 20.1714, 2210, "Tatry Słowackie"),
    "Mały Kieżmarski Szczyt":                     (49.1947, 20.1894, 2513, "Tatry Słowackie"),
    "Wielki Kieżmarski Szczyt":                   (49.1931, 20.2006, 2556, "Tatry Słowackie"),
    "Hawrań (Havran)":                            (49.2189, 20.2864, 2152, "Tatry Słowackie"),
    "Murań (Murán)":                              (49.2158, 20.2761, 2068, "Tatry Słowackie"),
    "Jagnięcy Szczyt (Baranec)":                  (49.1931, 19.8722, 2185, "Tatry Słowackie"),
    "Wołowiec (Volovec)":                         (49.2089, 20.0408, 2064, "Tatry Słowackie"),
    "Solisko":                                    (49.2183, 19.9717, 2093, "Tatry Słowackie"),
    "Szatan":                                     (49.1633, 20.0525, 2415, "Tatry Słowackie"),
    "Rysy (słowackie podejście)":                 (49.1794, 20.0883, 2501, "Tatry Słowackie"),
    "Mengusovský štít":                           (49.1908, 20.0803, 2438, "Tatry Słowackie"),
    "Popradský štít":                     (49.1828, 20.1567, 2369, "Tatry Słowackie"),

    # ---------- BESKID ŚLĄSKI ----------
    "Skrzyczne":                          (49.6844, 19.0303, 1257, "Beskid Śląski"),
    "Klimczok":                           (49.7397, 18.9950, 1117, "Beskid Śląski"),
    "Błatnia":                            (49.7347, 18.9669, 1005, "Beskid Śląski"),
    "Równica":                            (49.7153, 18.8475,  884, "Beskid Śląski"),
    "Czantoria Wielka":                   (49.6791, 18.7997,  995, "Beskid Śląski"),
    "Barania Góra":                       (49.6105, 19.0116, 1220, "Beskid Śląski"),
    "Magurka Wiślańska":                  (49.6272, 19.0228, 1073, "Beskid Śląski"),
    "Stożek Wielki":                      (49.6059, 18.8475,  978, "Beskid Śląski"),
    "Wielka Czantoria":                   (49.6791, 18.7997,  995, "Beskid Śląski"),
    "Soszów Wielki":                      (49.6385, 18.8166,  863, "Beskid Śląski"),

    # ---------- BESKID ŻYWIECKI ----------
    "Babia Góra":                         (49.5733, 19.5294, 1725, "Beskid Żywiecki"),
    "Pilsko":                             (49.5283, 19.3175, 1557, "Beskid Żywiecki"),
    "Romanka":                            (49.5661, 19.2319, 1366, "Beskid Żywiecki"),
    "Lipowski Wierch":                    (49.5483, 19.2069, 1324, "Beskid Żywiecki"),
    "Mędralowa":                          (49.6133, 19.4678, 1169, "Beskid Żywiecki"),
    "Wielka Racza":                       (49.4072, 18.9806, 1236, "Beskid Żywiecki"),
    "Prusów":                             (49.5539, 19.1417, 1209, "Beskid Żywiecki"),
    "Rysianka":                           (49.5492, 19.2217, 1322, "Beskid Żywiecki"),
    "Hala Miziowa":                       (49.5700, 19.4833, 1180, "Beskid Żywiecki"),
    "Jałowiec":                           (49.6456, 19.4897, 1111, "Beskid Żywiecki"),

    # ---------- GORCE ----------
    "Turbacz":                            (49.5428, 20.1114, 1310, "Gorce"),
    "Luboń Wielki":                       (49.6385, 19.9897,  968, "Gorce"),
    "Mogielica":                          (49.6552, 20.2764, 1170, "Gorce"),
    "Szczebel":                           (49.6853, 19.9844,  977, "Gorce"),
    "Łopień":                             (49.6978, 20.2644,  952, "Gorce"),
    "Kudłoń":                             (49.5739, 20.1744, 1276, "Gorce"),
    "Jaworzyna Gorczańska":               (49.5583, 20.1317, 1288, "Gorce"),

    # ---------- BESKID WYSPOWY ----------
    "Łysa Góra (Beskid Wyspowy)":         (49.7214, 20.4022,  791, "Beskid Wyspowy"),
    "Cichoń":                             (49.6417, 20.3547,  892, "Beskid Wyspowy"),
    "Śnieżnica":                          (49.7153, 20.1878,  1006, "Beskid Wyspowy"),

    # ---------- BESKID SĄDECKI ----------
    "Jaworzyna Krynicka":                 (49.4217, 20.9100, 1114, "Beskid Sądecki"),
    "Radziejowa":                         (49.4496, 20.6033, 1262, "Beskid Sądecki"),
    "Przehyba":                           (49.4633, 20.5567, 1175, "Beskid Sądecki"),
    "Hala Łabowska":                      (49.4417, 20.8533,  997, "Beskid Sądecki"),
    "Wielki Rogacz":                      (49.4319, 20.6272, 1182, "Beskid Sądecki"),
    "Pusta Wielka":                       (49.4186, 20.8406, 1060, "Beskid Sądecki"),

    # ---------- PIENINY ----------
    "Trzy Korony":                        (49.4147, 20.4144,  982, "Pieniny"),
    "Sokolica":                           (49.4172, 20.4403,  747, "Pieniny"),
    "Wysoka":                             (49.3801, 20.5517, 1050, "Pieniny"),
}

PASMA = sorted(set(v[3] for v in SZCZYTY.values()))

# ============================================================
# ZDJĘCIA SZCZYTÓW (Wikimedia Commons — sprawdzone URL-e)
# ============================================================
# Tylko zweryfikowane pliki które na pewno istnieją na Wikimedia
ZDJECIA = {
    "Rysy":                               "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Rysy_-_widok_z_Morskiego_Oka.jpg/640px-Rysy_-_widok_z_Morskiego_Oka.jpg",
    "Giewont":                            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Giewont_widziany_z_Bystrej.jpg/640px-Giewont_widziany_z_Bystrej.jpg",
    "Kasprowy Wierch":                    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Kasprowy_Wierch_2.jpg/640px-Kasprowy_Wierch_2.jpg",
    "Morskie Oko":                        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Morskie_Oko_2014.JPG/640px-Morskie_Oko_2014.JPG",
    "Gerlach (Gerlachovský štít)":        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Gerlach_from_Rysy.jpg/640px-Gerlach_from_Rysy.jpg",
    "Łomnica (Lomnický štít)":            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Lomnicky_stit_from_the_north.jpg/640px-Lomnicky_stit_from_the_north.jpg",
    "Krywań (Kriváň)":                    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Krivan_Slovakia.jpg/640px-Krivan_Slovakia.jpg",
    "Babia Góra":                         "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Babia_Gora_z_Zawoi.jpg/640px-Babia_Gora_z_Zawoi.jpg",
    "Rohacz Ostry (Ostrý Roháč)":         "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Rohace.jpg/640px-Rohace.jpg",
    "Rohacz Płaski (Plochý Roháč)":       "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Rohace.jpg/640px-Rohace.jpg",
    "Trzy Korony":                        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Trzy_Korony_2006.jpg/640px-Trzy_Korony_2006.jpg",
    "Turbacz":                            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Turbacz_szczyt.jpg/640px-Turbacz_szczyt.jpg",
    "Skrzyczne":                          "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Skrzyczne.jpg/640px-Skrzyczne.jpg",
}

def zdjecie_szczytu(nazwa, lat, lon):
    """Zwraca URL zdjęcia lub None jeśli brak."""
    return ZDJECIA.get(nazwa)

def miniatura_mapa_html(lat, lon, nazwa="", zoom=14):
    """Leaflet.js + OpenTopoMap — precyzyjny marker z podpisem szczytu."""
    # Czyścimy ⭐WKT z nazwy do podpisu na mapie
    label = nazwa.replace(" ⭐WKT", "").replace("'", "\\'").replace('"', "&quot;")
    return f"""
<div id="map_{int(lat*10000)}_{int(lon*10000)}"
     style="width:100%;height:240px;border-radius:8px;border:1px solid #555;">
</div>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
(function(){{
  var divId = 'map_{int(lat*10000)}_{int(lon*10000)}';
  var map = L.map(divId, {{zoomControl:true, attributionControl:false}})
             .setView([{lat}, {lon}], {zoom});
  L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 17,
    attribution: 'OpenTopoMap'
  }}).addTo(map);
  var icon = L.divIcon({{
    html: '<div style="background:#c0392b;width:12px;height:12px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 3px #000;"></div>',
    iconSize:[12,12], iconAnchor:[6,6], className:''
  }});
  L.marker([{lat}, {lon}], {{icon:icon}})
   .addTo(map)
   .bindTooltip('{label}', {{permanent:true, direction:'top', offset:[0,-8],
     className:'peak-label'}});
}})();
</script>
<style>
.peak-label {{
  background:rgba(0,0,0,0.7);color:#fff;border:none;
  padding:2px 6px;border-radius:3px;font-size:11px;font-weight:bold;
  white-space:nowrap;box-shadow:none;
}}
.peak-label::before {{ display:none; }}
</style>
<div style="font-size:11px;color:#888;margin-top:3px;">
  📍 <a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map={zoom}/{lat}/{lon}"
     target="_blank" style="color:#888;">Otwórz w OpenStreetMap</a>
  &nbsp;|&nbsp;
  <a href="https://mapy.cz/turisticka?x={lon}&y={lat}&z={zoom}&source=coor&id={lon}%2C{lat}"
     target="_blank" style="color:#888;">Mapy.cz</a>
</div>
"""

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

HOURLY_FIELDS = "temperature_2m,apparent_temperature,precipitation,snowfall,weathercode,windspeed_10m,windgusts_10m,winddirection_10m,cloudcover,visibility,freezinglevel_height"

def _parse_open_meteo(d):
    """Wspólny parser odpowiedzi Open-Meteo."""
    if "hourly" not in d:
        raise ValueError(d.get("reason", str(d)))
    h = d["hourly"]
    return pd.DataFrame({
        "czas":        pd.to_datetime(h["time"]),
        "temp":        h["temperature_2m"],
        "odczuwalna":  h["apparent_temperature"],
        "opady":       h["precipitation"],
        "snieg":       h["snowfall"],
        "kod":         h["weathercode"],
        "wiatr":       h["windspeed_10m"],
        "porywy":      h["windgusts_10m"],
        "kierunek":    h["winddirection_10m"],
        "zachmurzenie":h["cloudcover"],
        "widocznosc":  h["visibility"],
        "izot0":       h["freezinglevel_height"],
    })

@st.cache_data(ttl=3600, show_spinner=False)
def pobierz_open_meteo(lat, lon):
    """Open-Meteo — bez parametru models (w pełni darmowe). Cache 1h."""
    # UWAGA: models=best_match / icon_seamless mogą być płatne na niektórych IP
    # Używamy domyślnego endpointu bez models= — zawsze darmowy
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly={HOURLY_FIELDS}"
        f"&windspeed_unit=ms&timezone=Europe%2FWarsaw"
        f"&forecast_days=10"
    )
    r = requests.get(url, timeout=15)
    d = r.json()
    if "error" in d or "reason" in d:
        # Fallback: spróbuj przez ECMWF endpoint
        url2 = url.replace("v1/forecast", "v1/ecmwf")
        d = requests.get(url2, timeout=15).json()
    return _parse_open_meteo(d)

@st.cache_data(ttl=3600, show_spinner=False)
def pobierz_yr(lat, lon):
    """Yr.no (MET Norway) — model NWP. Cache 1h."""
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

@st.cache_data(ttl=3600, show_spinner=False)
def pobierz_open_meteo_icon(lat, lon):
    """Open-Meteo — endpoint DWD ICON (zawsze darmowy). Cache 1h."""
    # Używamy dedykowanego endpointu DWD zamiast models=icon_seamless
    url = (
        f"https://api.open-meteo.com/v1/dwd-icon"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly={HOURLY_FIELDS}"
        f"&windspeed_unit=ms&timezone=Europe%2FWarsaw"
        f"&forecast_days=7"
    )
    r = requests.get(url, timeout=15)
    d = r.json()
    if "error" in d or "reason" in d:
        # Fallback na standardowy endpoint
        url2 = url.replace("v1/dwd-icon", "v1/forecast")
        d = requests.get(url2, timeout=15).json()
    return _parse_open_meteo(d)

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
# REKOMENDACJA NAJLEPSZEGO PASMA NA WEEKEND
# ============================================================

# Reprezentatywny szczyt dla każdego pasma — wybieramy popularny, niezbyt wysoki punkt
_REPR_PASMA = {
    "Tatry Polskie":    "Kasprowy Wierch (Kasprový vrch)",
    "Tatry Zachodnie":  "Giewont",
    "Tatry Słowackie":  "Łomnica (Lomnický štít) ⭐WKT",
    "Beskid Śląski":    "Skrzyczne",
    "Beskid Żywiecki":  "Babia Góra",
    "Gorce":            "Turbacz",
    "Beskid Wyspowy":   "Śnieżnica",
    "Beskid Sądecki":   "Radziejowa",
    "Pieniny":          "Trzy Korony",
}

def _ocen_pasmo_weekend(df, sobota, niedziela):
    """
    Ocenia warunki weekendowe na podstawie danych godzinowych.
    Zwraca dict z score (niższy = lepszy), bool burza, opady_suma, wiatr_max, opis.
    """
    df_w = df[df["czas"].dt.date.isin([sobota, niedziela])].copy()
    if df_w.empty:
        return {"score": 999, "burza": False, "opady": 0, "wiatr_max": 0, "opis": "Brak danych"}

    burza = bool(df_w["kod"].isin([95, 96, 99]).any())
    deszcz_h = df_w[df_w["kod"].isin([51,53,55,61,63,65,80,81,82])].shape[0]  # liczba godzin z opadami
    opady_suma = float(df_w["opady"].sum())
    wiatr_max = float(df_w["wiatr"].max())
    porywy_max = float(df_w["porywy"].max())
    pochmurnych_h = df_w[df_w["zachmurzenie"] > 75].shape[0] if "zachmurzenie" in df_w.columns else 0

    # Scoring — niższy = lepszy
    score = 0
    if burza:
        score += 1000
    score += opady_suma * 5          # każdy mm opadów +5 pkt
    score += deszcz_h * 10           # każda godzina z deszczem +10 pkt
    score += max(0, wiatr_max - 10) * 3   # wiatr ponad 10 m/s
    score += pochmurnych_h * 1       # godziny pełnego zachmurzenia

    # Czytelny opis
    if burza:
        opis = "⛈️ Burze prognozowane"
    elif opady_suma > 10 or deszcz_h > 5:
        opis = "🌧️ Intensywne opady"
    elif opady_suma > 3 or deszcz_h > 2:
        opis = "🌦️ Przelotne deszcze"
    elif opady_suma > 0.5:
        opis = "🌂 Lekkie opady"
    elif wiatr_max > 18:
        opis = "💨 Silny wiatr"
    elif pochmurnych_h > 12:
        opis = "☁️ Bardzo pochmurnie"
    else:
        opis = "🌤️ Dobre warunki"

    return {
        "score": score,
        "burza": burza,
        "opady": round(opady_suma, 1),
        "wiatr_max": round(wiatr_max, 1),
        "porywy_max": round(porywy_max, 1),
        "opis": opis,
        "deszcz_h": deszcz_h,
    }

@st.cache_data(ttl=3600, show_spinner=False)
def _pobierz_repr_pasma(lat, lon):
    """Cache'd wrapper — pobiera Open-Meteo best_match dla repr. szczytu."""
    return pobierz_open_meteo(lat, lon)

def znajdz_najlepsze_pasma(sobota, niedziela):
    """
    Pobiera prognozę dla reprezentatywnego szczytu każdego pasma,
    ocenia warunki i zwraca listę pasm posortowaną od najlepszej do najgorszej.
    """
    wyniki = []
    for pasmo, nazwa_szczytu in _REPR_PASMA.items():
        if nazwa_szczytu not in SZCZYTY:
            continue
        lat, lon, wys, _ = SZCZYTY[nazwa_szczytu]
        try:
            df = _pobierz_repr_pasma(lat, lon)
            ocena = _ocen_pasmo_weekend(df, sobota, niedziela)
        except Exception as e:
            ocena = {"score": 999, "burza": False, "opady": 0, "wiatr_max": 0,
                     "porywy_max": 0, "opis": f"❓ Błąd: {e}", "deszcz_h": 0}
        wyniki.append({
            "pasmo": pasmo,
            "szczyt_repr": nazwa_szczytu,
            "wys": wys,
            **ocena,
        })

    wyniki.sort(key=lambda x: x["score"])
    return wyniki

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
# Banner — rozciaga sie na pelna szerokosc (none), bez etykiet, bez sniegu, bez paska tytulowego
BANNER_HTML = """<!DOCTYPE html>
<html><head><style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:100%; height:200px; overflow:hidden; background:#0d1b2e; }
</style></head>
<body>
<svg viewBox="0 0 1200 220" preserveAspectRatio="none"
     xmlns="http://www.w3.org/2000/svg"
     style="width:100%;height:200px;display:block;">
  <defs>
    <!-- Niebo: noc -> świt po prawej -->
    <linearGradient id="bsky" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#0d1b2e"/>
      <stop offset="45%"  stop-color="#0d1b2e"/>
      <stop offset="70%"  stop-color="#1a2f50"/>
      <stop offset="85%"  stop-color="#8b3a2a"/>
      <stop offset="93%"  stop-color="#d4621a"/>
      <stop offset="100%" stop-color="#e8922a"/>
    </linearGradient>
    <!-- Gradient pionowy nieba -->
    <linearGradient id="bsky2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#000000" stop-opacity="0.0"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.35"/>
    </linearGradient>
    <!-- Blask wschodu -->
    <radialGradient id="bglow" cx="88%" cy="55%" r="30%">
      <stop offset="0%"   stop-color="#f5a030" stop-opacity="0.55"/>
      <stop offset="50%"  stop-color="#c0541a" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <!-- Mgła -->
    <linearGradient id="bfog" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#4a8fa8" stop-opacity="0"/>
      <stop offset="100%" stop-color="#4a8fa8" stop-opacity="0.40"/>
    </linearGradient>
    <!-- Śnieg na wierzchołkach -->
    <linearGradient id="bsnow" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#e8f4ff" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#e8f4ff" stop-opacity="0"/>
    </linearGradient>
    <!-- Zieleń drzew -->
    <linearGradient id="btree" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#1a4a28"/>
      <stop offset="100%" stop-color="#0d2a18"/>
    </linearGradient>
    <!--
      Poziome gradienty dla warstw gór 4→1 — taki sam kierunek co niebo (x).
      Lewo: ciemny granat, prawo: ciepły brąz/pomarańcz — każda warstwa
      w ciut innym jasności, żeby zachować głębię.
    -->
    <linearGradient id="gmtn4" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#1e4a6a"/>
      <stop offset="60%"  stop-color="#1e4a6a"/>
      <stop offset="80%"  stop-color="#2a4050"/>
      <stop offset="92%"  stop-color="#5a3828"/>
      <stop offset="100%" stop-color="#7a4828"/>
    </linearGradient>
    <linearGradient id="gmtn3" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#183a52"/>
      <stop offset="55%"  stop-color="#183a52"/>
      <stop offset="75%"  stop-color="#22323e"/>
      <stop offset="88%"  stop-color="#4a2e1e"/>
      <stop offset="100%" stop-color="#6a3a20"/>
    </linearGradient>
    <linearGradient id="gmtn2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#112a3e"/>
      <stop offset="50%"  stop-color="#112a3e"/>
      <stop offset="72%"  stop-color="#1e2830"/>
      <stop offset="85%"  stop-color="#3a2218"/>
      <stop offset="100%" stop-color="#542e18"/>
    </linearGradient>
    <linearGradient id="gmtn1" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#091820"/>
      <stop offset="45%"  stop-color="#091820"/>
      <stop offset="68%"  stop-color="#141a1e"/>
      <stop offset="82%"  stop-color="#2a1a10"/>
      <stop offset="100%" stop-color="#3c2210"/>
    </linearGradient>
    <!-- Gradient obramowania ikony IG (uproszczony: żółty→różowy→fiolet) -->
    <linearGradient id="iggrad" x1="1" y1="1" x2="0" y2="0">
      <stop offset="0%"   stop-color="#f9ce34"/>
      <stop offset="35%"  stop-color="#ee2a7b"/>
      <stop offset="100%" stop-color="#6228d7"/>
    </linearGradient>
  </defs>

  <!-- Niebo -->
  <rect width="1200" height="220" fill="url(#bsky)"/>
  <rect width="1200" height="220" fill="url(#bglow)"/>
  <rect width="1200" height="220" fill="url(#bsky2)"/>

  <!-- Gwiazdy (lewa/środkowa część nieba) -->
  <g fill="#ffffff">
    <circle cx="42"  cy="18" r="1.1" opacity="0.9"/>
    <circle cx="115" cy="28" r="0.9" opacity="0.7"/>
    <circle cx="188" cy="12" r="1.3" opacity="0.85"/>
    <circle cx="254" cy="32" r="0.8" opacity="0.6"/>
    <circle cx="320" cy="8"  r="1.0" opacity="0.8"/>
    <circle cx="390" cy="22" r="0.7" opacity="0.65"/>
    <circle cx="455" cy="14" r="1.2" opacity="0.75"/>
    <circle cx="510" cy="35" r="0.8" opacity="0.55"/>
    <circle cx="565" cy="10" r="1.0" opacity="0.7"/>
    <circle cx="78"  cy="42" r="0.7" opacity="0.5"/>
    <circle cx="145" cy="55" r="0.9" opacity="0.6"/>
    <circle cx="230" cy="44" r="0.8" opacity="0.55"/>
    <circle cx="300" cy="50" r="1.1" opacity="0.65"/>
    <circle cx="420" cy="48" r="0.7" opacity="0.5"/>
  </g>

  <!-- Warstwa 4 — najdalsze góry — gradient poziomy -->
  <polygon fill="url(#gmtn4)" opacity="0.75" points="
    0,220 0,130 60,115 130,103 200,90 270,80 340,72 410,64
    480,58 545,52 600,48 655,52 710,58 770,65 840,72 910,78
    980,84 1050,78 1120,72 1200,68 1200,220
  "/>

  <!-- Warstwa 3 — środkowe góry — gradient poziomy -->
  <polygon fill="url(#gmtn3)" points="
    0,220 0,150 50,140 100,128 155,114 215,100
    265,88 315,76 360,66 395,56 425,48 455,42 485,36
    515,42 545,48 575,54 605,60 640,68 680,78 720,88
    760,98 805,106 855,114 905,120 960,126 1015,120
    1070,114 1125,120 1180,126 1200,128 1200,220
  "/>

  <!-- Śnieg na warswie 3 (wierzchołki środkowe) -->
  <polygon fill="#ddeeff" opacity="0.75" points="
    415,48 425,48 455,42 485,36 515,42 545,48 540,54 515,50 485,44 455,50 425,54
  "/>
  <polygon fill="#ddeeff" opacity="0.55" points="
    260,88 275,80 295,72 315,76 310,84 290,80
  "/>
  <polygon fill="#ddeeff" opacity="0.55" points="
    635,68 645,60 660,52 680,60 670,68
  "/>

  <!-- Mgła między warstwami -->
  <rect x="0" y="112" width="1200" height="50" fill="url(#bfog)"/>

  <!-- Warstwa 2 — gradient poziomy (ciemny granat → ciepły brąz) -->
  <polygon fill="url(#gmtn2)" points="
    0,220 0,168 55,158 110,146 162,132 205,120 242,108
    272,96 298,84 322,74 344,64 364,56 384,50 404,44
    424,38 444,44 460,50 476,58 490,68 507,78 530,88
    558,96 588,104 622,112 665,120 718,128 772,136
    828,142 888,148 950,142 1012,136 1068,142
    1130,148 1200,150 1200,220
  "/>

  <!-- Śnieg na warswie 2 -->
  <polygon fill="#e8f4ff" opacity="0.80" points="
    398,50 404,44 424,38 444,44 455,50 444,54 424,46 404,54
  "/>
  <polygon fill="#e8f4ff" opacity="0.60" points="
    316,74 322,74 344,64 356,68 344,72 322,78
  "/>

  <!-- Warstwa 1 — gradient poziomy (najciemniejszy, niemal czarny → ciemny brąz) -->
  <polygon fill="url(#gmtn1)" points="
    0,220 0,185 40,178 80,170 122,162 162,154 198,144
    228,134 252,124 268,114 278,124 292,134 314,122
    340,110 366,98 386,88 400,96 416,104 432,94
    446,82 460,90 474,102 488,112 504,122
    526,132 552,140 588,148 640,154 700,160
    762,166 826,170 888,174 950,170 1012,166
    1072,170 1132,174 1200,176 1200,220
  "/>

  <!-- Drzewa iglaste po lewej — zielone -->
  <g fill="url(#btree)">
    <polygon points="14,220 26,192 38,220"/>
    <polygon points="20,210 26,190 32,210"/>
    <polygon points="34,220 44,198 54,220"/>
    <polygon points="54,220 65,194 76,220"/>
    <polygon points="61,212 65,192 69,212"/>
    <polygon points="74,220 84,196 94,220"/>
    <polygon points="92,220 101,200 110,220"/>
    <polygon points="108,220 116,204 124,220"/>
  </g>
  <!-- Drzewa iglaste po lewej — ciemniejsza warstwa (głąb lasu) -->
  <g fill="#0a1e10" opacity="0.6">
    <polygon points="24,220 33,198 42,220"/>
    <polygon points="46,220 54,200 62,220"/>
    <polygon points="80,220 88,202 96,220"/>
  </g>

  <!-- Drzewa iglaste po prawej — zielone -->
  <g fill="url(#btree)">
    <polygon points="1092,220 1104,192 1116,220"/>
    <polygon points="1098,210 1104,190 1110,210"/>
    <polygon points="1112,220 1122,196 1132,220"/>
    <polygon points="1130,220 1140,194 1150,220"/>
    <polygon points="1136,212 1140,192 1144,212"/>
    <polygon points="1148,220 1157,198 1166,220"/>
    <polygon points="1164,220 1172,202 1180,220"/>
  </g>
  <!-- Drzewa po prawej — podświetlone blaskiem wschodu -->
  <g fill="#7a3015" opacity="0.30">
    <polygon points="1130,220 1140,194 1150,220"/>
    <polygon points="1148,220 1157,198 1166,220"/>
    <polygon points="1164,220 1172,202 1180,220"/>
  </g>

</svg>
</body></html>"""

# ---- IG badge — nad bannerem, górny prawy róg ----
st.markdown("""
<div style="display:flex;justify-content:flex-end;margin-bottom:-8px;">
  <a href="https://www.instagram.com/hikewithmic" target="_blank" style="text-decoration:none;">
    <div style="display:inline-flex;align-items:center;gap:8px;background:transparent;padding:5px 0;">
      <svg width="22" height="22" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
        <defs>
          <linearGradient id="ig1" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%"   stop-color="#f9ce34"/>
            <stop offset="30%"  stop-color="#ee2a7b"/>
            <stop offset="65%"  stop-color="#9b27af"/>
            <stop offset="100%" stop-color="#4f5bd5"/>
          </linearGradient>
        </defs>
        <rect width="36" height="36" rx="9" fill="url(#ig1)"/>
        <rect x="7" y="7" width="22" height="22" rx="6" fill="none" stroke="white" stroke-width="2.2"/>
        <circle cx="18" cy="18" r="5.5" fill="none" stroke="white" stroke-width="2.2"/>
        <circle cx="25" cy="11" r="1.6" fill="white"/>
      </svg>
      <span style="font-family:'Cinzel',Georgia,serif;font-weight:600;font-size:0.72rem;color:#c8ddf0;letter-spacing:1.5px;">@hikewithmic</span>
    </div>
  </a>
</div>
""", unsafe_allow_html=True)

components.html(BANNER_HTML, height=205, scrolling=False)

sobota, niedziela = nastepny_weekend()

# ---- Tytuł + data weekendu ----
col_tytul, col_weekend = st.columns([3, 1])
with col_tytul:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-top:10px;margin-bottom:4px;">
      <svg width="34" height="34" viewBox="0 0 38 38" xmlns="http://www.w3.org/2000/svg">
        <polygon points="19,4 35,32 3,32" fill="#4a7a9b" stroke="#5a96c0" stroke-width="1"/>
        <polygon points="19,4 27,17 11,17" fill="#ddeeff" opacity="0.9"/>
        <polygon points="11,17 15,24 3,32 35,32 27,17 23,24" fill="#144a5e"/>
      </svg>
      <div>
        <div style="font-family:'Cinzel',Georgia,serif;font-size:1.75rem;font-weight:700;color:#e8f4ff;line-height:1.1;letter-spacing:1px;">Mountain Weather</div>
        <div style="font-size:0.75rem;color:#7aaac8;letter-spacing:3px;">TATRY &amp; BESKIDY</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
with col_weekend:
    st.markdown(f"""
    <div style="background:#243d52;border:1px solid #3a6080;border-radius:10px;padding:10px 16px;text-align:center;margin-top:10px;">
      <div style="font-size:0.68rem;color:#7aaac8;text-transform:uppercase;letter-spacing:2px;margin-bottom:3px;">Prognoza na weekend</div>
      <div style="font-size:1.1rem;font-weight:700;color:#e8f4ff;">{sobota.strftime('%d.%m')} sob – {niedziela.strftime('%d.%m')} nd</div>
    </div>
    """, unsafe_allow_html=True)
st.divider()

# ============================================================
# --- Sekcja 0: Rekomendacja najlepszego pasma na weekend ---
# ============================================================
st.markdown("""<div class="mw-heading">
  <svg style="vertical-align:-3px;margin-right:8px" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5a96c0" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/>
    <line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/>
    <line x1="4.22" y1="4.22" x2="6.34" y2="6.34"/><line x1="17.66" y1="17.66" x2="19.78" y2="19.78"/>
    <line x1="4.22" y1="19.78" x2="6.34" y2="17.66"/><line x1="17.66" y1="6.34" x2="19.78" y2="4.22"/>
  </svg>
  Gdzie pojechać w ten weekend? — Rekomendacja pasma
</div>""", unsafe_allow_html=True)

_col_rec_btn, _col_rec_info = st.columns([1, 3])
with _col_rec_btn:
    _do_rec = st.button("🔎 Szukaj najlepszej pogody", help="Sprawdza prognozę dla każdego pasma i poleca te bez burz i deszczu.")
with _col_rec_info:
    st.caption("Pobiera prognozę dla reprezentatywnego szczytu w każdym paśmie i rankinguje wg warunków (brak burz → mało opadów → słaby wiatr).")

if _do_rec:
    with st.spinner("Sprawdzam pogodę dla wszystkich pasm… (~9 zapytań, kilka sekund)"):
        _wyniki_rec = znajdz_najlepsze_pasma(sobota, niedziela)

    if _wyniki_rec:
        _najlepsze = _wyniki_rec[0]
        # Nagłówek z rekomendacją
        _medal_kolor = "#2e7d4f" if not _najlepsze["burza"] else "#7a3010"
        st.markdown(f"""
        <div style="background:{_medal_kolor};border-radius:12px;padding:14px 20px;margin-bottom:14px;">
          <div style="font-size:0.72rem;color:#c0e8c0;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">🏆 Polecane pasmo na {sobota.strftime('%d.%m')}–{niedziela.strftime('%d.%m')}</div>
          <div style="font-family:'Cinzel',Georgia,serif;font-size:1.5rem;font-weight:700;color:#ffffff;letter-spacing:1px;">{_najlepsze['pasmo']}</div>
          <div style="font-size:0.9rem;color:#d4f0d4;margin-top:4px;">{_najlepsze['opis']} &nbsp;·&nbsp; Opady: {_najlepsze['opady']} mm &nbsp;·&nbsp; Wiatr max: {_najlepsze['wiatr_max']} m/s</div>
          <div style="font-size:0.78rem;color:#a0c8a0;margin-top:3px;">Reprezentatywny szczyt: {_najlepsze['szczyt_repr'].replace(' ⭐WKT','')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Tabela wszystkich pasm
        _ncols = 3
        _rows = [_wyniki_rec[i:i+_ncols] for i in range(0, len(_wyniki_rec), _ncols)]
        for _row in _rows:
            _cols = st.columns(_ncols)
            for _ci, _w in enumerate(_row):
                _is_best = _w == _najlepsze
                _css_extra = "rec-best" if _is_best else ("rec-warn" if _w["burza"] or _w["opady"] > 5 else "")
                _rank = _wyniki_rec.index(_w) + 1
                _medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(_rank, f"#{_rank}")
                _cols[_ci].markdown(f"""
                <div class="rec-card {_css_extra}">
                  <div class="rec-badge">{_medal} Miejsce {_rank}</div>
                  <div class="rec-name">{_w['pasmo']}</div>
                  <div class="rec-stats">{_w['opis']}</div>
                  <div class="rec-stats">💧 {_w['opady']} mm &nbsp; 💨 {_w['wiatr_max']} m/s (porywy {_w['porywy_max']} m/s)</div>
                  <div class="rec-stats" style="color:#617a8a;font-size:0.75rem;">ref: {_w['szczyt_repr'].replace(' ⭐WKT','')}</div>
                </div>
                """, unsafe_allow_html=True)

st.divider()

# --- Sekcja 1: Wybór źródła ---
st.markdown("""<div class="mw-heading">
  <svg style="vertical-align:-3px;margin-right:8px" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5a96c0" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
  Źródło pogody
</div>""", unsafe_allow_html=True)
col_z1, col_z2 = st.columns([2, 3])
with col_z1:
    tryb_zrodla = st.selectbox(
        "Tryb:",
        ["Jedno źródło", "Porównaj wszystkie źródła"],
        help="Tryb porównania pobiera dane ze wszystkich źródeł i zestawia je na jednym wykresie."
    )
with col_z2:
    if tryb_zrodla == "Jedno źródło":
        wybrane_zrodlo = st.selectbox(
            "Źródło danych:",
            list(ZRODLA.keys()),
            help="Wybierz skąd pobierać prognozę pogody."
        )
        st.caption(f"ℹ️ {ZRODLA_INFO[wybrane_zrodlo]}")
    else:
        st.info("ℹ️ Dane ze wszystkich 3 źródeł: Open-Meteo, ICON, Yr.no")

st.divider()

# --- Sekcja 2: Filtr pasm + wybór szczytu ---
st.markdown("""<div class="mw-heading">
  <svg style="vertical-align:-3px;margin-right:8px" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5a96c0" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="3,20 12,4 21,20"/><polyline points="3,20 21,20"/><line x1="9" y1="14" x2="15" y2="14"/></svg>
  Wybierz pasmo i szczyt
</div>""", unsafe_allow_html=True)

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
    _pasmo = SZCZYTY.get(nazwa_wyswietlana, (None, None, None, ""))[3]

    col_foto, col_info = st.columns([1, 2])

    with col_foto:
        zdjecie_url = ZDJECIA.get(nazwa_wyswietlana)
        if zdjecie_url:
            # Pobieramy zdjęcie przez requests jako bytes — omija blokadę hotlinkingu
            try:
                resp = requests.get(
                    zdjecie_url,
                    headers={"User-Agent": "Mozilla/5.0", "Referer": "https://commons.wikimedia.org/"},
                    timeout=6,
                )
                if resp.status_code == 200:
                    st.image(resp.content, caption="© Wikimedia Commons", use_container_width=True)
                else:
                    components.html(miniatura_mapa_html(lat, lon, nazwa_wyswietlana), height=260)
            except Exception:
                components.html(miniatura_mapa_html(lat, lon, nazwa_wyswietlana), height=260)
        else:
            # Brak zdjęcia — mapa OSM przez iframe (nie ma limitów)
            components.html(miniatura_mapa_html(lat, lon, nazwa_wyswietlana), height=260)

    with col_info:
        st.markdown(f"""<div class="mw-peak-title">
          <svg style="vertical-align:-4px;margin-right:6px" width="18" height="18" viewBox="0 0 24 24" fill="#e05050" stroke="#e05050" stroke-width="0.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5" fill="#fff" stroke="none"/></svg>
          {nazwa_wyswietlana}
        </div>""", unsafe_allow_html=True)
        st.markdown(f"**Wysokość:** {wys_str}  |  `{lat:.4f}°N, {lon:.4f}°E`")
        if _pasmo:
            st.markdown(f"**Pasmo:** {_pasmo}")
        st.markdown("**🔗 Prognozy zewnętrzne (kliknij aby otworzyć):**")
        ln_cols = st.columns(4)
        ln_cols[0].markdown(f"[🏔️ Mountain‑Forecast]({link_mountain_forecast(nazwa_wyswietlana, lat, lon, wys or 1000)})")
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
            import traceback
            st.error(f"Błąd pobierania danych: {e}")
            st.code(traceback.format_exc(), language="text")
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
