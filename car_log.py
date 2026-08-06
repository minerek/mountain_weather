import streamlit as st
import streamlit.components.v1 as components
import json, os, base64, requests as _req
from datetime import date

# ── Config ────────────────────────────────────────────────────────────────────
_FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23222'/%3E%3Cellipse cx='10' cy='24' rx='3' ry='3' fill='%23999'/%3E%3Cellipse cx='22' cy='24' rx='3' ry='3' fill='%23999'/%3E%3Crect x='3' y='14' width='26' height='9' rx='2' fill='%23444'/%3E%3Cpolygon points='6,14 9,7 23,7 26,14' fill='%23555'/%3E%3Crect x='10' y='8' width='12' height='5' rx='1' fill='%2388aacc'/%3E%3C/svg%3E"

st.set_page_config(page_title="Audi A3 — Serwis", page_icon=_FAVICON, layout="wide")
components.html("""<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">""", height=0)

st.markdown("""
<style>
[data-testid="stAppViewContainer"],[data-testid="stApp"]{background:#111418!important}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stAppViewBlockContainer"]{padding-top:10px!important}
body,.stMarkdown,p,li,span,div{color:#d0d8e4!important}
h1,h2,h3{color:#e8edf2!important}

/* Czcionka Rajdhani dla nagłówków */
.car-title{font-family:'Rajdhani',sans-serif;font-size:2rem;font-weight:700;color:#e8edf2;letter-spacing:2px;line-height:1.1}
.car-sub{font-size:0.72rem;color:#6a8099;letter-spacing:4px;font-family:'Rajdhani',sans-serif;text-transform:uppercase}
.section-head{font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:600;color:#a0bcd4;
  letter-spacing:2px;text-transform:uppercase;border-bottom:1px solid #1e2d3d;
  padding-bottom:5px;margin-top:1.4rem!important;margin-bottom:0.8rem!important}

/* Karty części */
.part-card{background:#141c26;border:1px solid #1e2d3d;border-radius:8px;padding:12px 15px;margin-bottom:6px}
.part-cat{font-family:'Rajdhani',sans-serif;font-size:1.0rem;font-weight:700;color:#c8dcea;letter-spacing:1px}
.part-spec{font-size:0.8rem;color:#6a8099;margin-top:1px}
.part-nums{display:flex;gap:12px;margin-top:6px;flex-wrap:wrap}
.part-badge{background:#0d1a26;border:1px solid #2a4a68;border-radius:5px;
  padding:3px 10px;font-size:0.78rem;color:#8ab4cc;font-family:'Rajdhani',sans-serif;font-weight:600}
.part-badge span{color:#4a7a9b;margin-right:4px;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px}
.part-note{font-size:0.76rem;color:#5a7a94;margin-top:5px;font-style:italic}

/* Karty serwisu */
.svc-card{background:#0e1820;border-left:3px solid #2a5a8a;border-radius:0 8px 8px 0;padding:12px 15px;margin-bottom:6px}
.svc-card.svc-recent{border-left-color:#2a8a5a}
.svc-date{font-family:'Rajdhani',sans-serif;font-size:0.85rem;color:#4a8ab0;font-weight:600;letter-spacing:1px}
.svc-km{font-size:0.8rem;color:#3a6a8a;margin-left:10px}
.svc-items{margin-top:6px}
.svc-item{display:inline-block;background:#0a1826;border:1px solid #1a3a56;border-radius:4px;
  font-size:0.76rem;color:#8ab4cc;padding:2px 8px;margin:2px 3px 2px 0}
.svc-cost{font-family:'Rajdhani',sans-serif;font-size:0.9rem;color:#4aaa6a;font-weight:600;margin-top:4px}
.svc-notes{font-size:0.76rem;color:#4a6a7a;margin-top:3px;font-style:italic}

/* Inputs */
[data-testid="stSelectbox"]>div>div,
[data-testid="stTextInput"]>div>div>input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"]>div>div>input,
[data-testid="stDateInput"] input{background:#141c26!important;color:#d0d8e4!important;
  border:1px solid #1e2d3d!important;border-radius:6px!important}
[data-testid="stMultiSelect"]>div>div{background:#141c26!important;border-color:#1e2d3d!important}
[data-testid="stMultiSelect"] span[data-baseweb="tag"]{background:#1e3a56!important;color:#8ab4cc!important;border:1px solid #2a5a88!important}

/* Przycisk */
[data-testid="stButton"] button{
  background:linear-gradient(135deg,#1a4a7a,#0e2a4a)!important;
  color:#e0eeff!important;border:1px solid #2a5a8a!important;
  border-radius:8px!important;font-family:'Rajdhani',sans-serif!important;
  font-size:1rem!important;font-weight:600!important;letter-spacing:1px!important}
[data-testid="stButton"] button:hover{background:linear-gradient(135deg,#2a5a9a,#1a3a6a)!important}

/* Metryki */
[data-testid="metric-container"]{background:#141c26!important;border:1px solid #1e2d3d!important;border-radius:10px!important;padding:12px 16px!important}
[data-testid="metric-container"] label{color:#4a7a9b!important;font-size:0.75rem!important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#e0eeff!important;font-family:'Rajdhani',sans-serif!important;font-size:1.4rem!important;font-weight:700!important}

a{color:#4a8ab0!important;text-decoration:none!important}
hr{border-color:#1e2d3d!important}
[data-testid="stCaptionContainer"] p{color:#4a6a7a!important}
</style>
""", unsafe_allow_html=True)

# ── GitHub persistence ─────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "car_data.json")
_GH_REPO  = "minerek/mountain_weather"
_GH_PATH  = "car_data.json"

def load():
    try:
        token = st.secrets["GH_TOKEN"]
        url = f"https://api.github.com/repos/{_GH_REPO}/contents/{_GH_PATH}"
        r = _req.get(url, headers={"Authorization": f"token {token}"}, timeout=8)
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"]).decode("utf-8")
            st.session_state["gh_sha_car"] = r.json()["sha"]
            return json.loads(content)
    except Exception:
        pass
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

def save(data):
    content_str = json.dumps(data, ensure_ascii=False, indent=2)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(content_str)
    try:
        token = st.secrets["GH_TOKEN"]
        sha   = st.session_state.get("gh_sha_car", "")
        url   = f"https://api.github.com/repos/{_GH_REPO}/contents/{_GH_PATH}"
        payload = {
            "message": "car: aktualizacja car_data.json",
            "content": base64.b64encode(content_str.encode("utf-8")).decode("ascii"),
            "sha": sha,
            "branch": "main",
        }
        r = _req.put(url, json=payload, headers={"Authorization": f"token {token}"}, timeout=10)
        if r.status_code in (200, 201):
            st.session_state["gh_sha_car"] = r.json()["content"]["sha"]
        else:
            st.warning(f"⚠️ GitHub sync: {r.status_code}")
    except KeyError:
        pass
    except Exception as e:
        st.warning(f"⚠️ GitHub sync error: {e}")

data = load()
car  = data["car"]
parts = data["parts"]
log  = data["service_log"]

# ── Autoryzacja ───────────────────────────────────────────────────────────────
def check_password():
    if st.session_state.get("auth_car"):
        return True
    try:
        correct = st.secrets["APP_PASSWORD"]
    except Exception:
        correct = "audi"
    with st.sidebar:
        st.markdown("### 🔐 Logowanie")
        pwd = st.text_input("Hasło:", type="password", key="car_pwd")
        if st.button("Zaloguj", key="car_login"):
            if pwd == correct:
                st.session_state["auth_car"] = True
                st.rerun()
            else:
                st.error("❌ Nieprawidłowe hasło.")
    return False

logged_in = check_password()

# ── Banner ────────────────────────────────────────────────────────────────────
components.html("""<!DOCTYPE html>
<html><head>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@300;400;600;700;800&display=swap" rel="stylesheet">
</head>
<body style="margin:0;padding:0;background:transparent;">
<div style="width:100%;border-radius:14px;overflow:hidden;margin-bottom:4px;box-shadow:0 4px 32px #000a;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 155" style="width:100%;display:block;">
  <defs>
    <!-- Tlo: ciemny metaliczny gradient -->
    <linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#1a1e24"/>
      <stop offset="40%"  stop-color="#0e1218"/>
      <stop offset="100%" stop-color="#080c10"/>
    </linearGradient>
    <!-- Metaliczny gradient na karoserie -->
    <linearGradient id="body_grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#3a4450"/>
      <stop offset="30%"  stop-color="#5a6878"/>
      <stop offset="60%"  stop-color="#2e3840"/>
      <stop offset="100%" stop-color="#181e26"/>
    </linearGradient>
    <!-- Metaliczny gradient szyb -->
    <linearGradient id="glass_grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#1a2e44" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#0a1820" stop-opacity="0.7"/>
    </linearGradient>
    <!-- Metaliczny gradient tekstu AUDI A3 -->
    <linearGradient id="txt_grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#ffffff"/>
      <stop offset="35%"  stop-color="#c8d8e8"/>
      <stop offset="65%"  stop-color="#8aaac4"/>
      <stop offset="100%" stop-color="#4a6a84"/>
    </linearGradient>
    <!-- Blask reflektora -->
    <radialGradient id="light_l" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#aaccee" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#aaccee" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="light_r" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#aaccee" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#aaccee" stop-opacity="0"/>
    </radialGradient>
    <!-- Cien auta -->
    <radialGradient id="shadow" cx="50%" cy="30%" r="50%">
      <stop offset="0%"   stop-color="#000000" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="softglow">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Tlo -->
  <rect width="900" height="155" fill="url(#bg)"/>

  <!-- Subtelna linia akcentu na dole -->
  <rect x="0" y="148" width="900" height="1" fill="#2a3a4a" opacity="0.8"/>
  <!-- Linia górna -->
  <rect x="0" y="0" width="900" height="1" fill="#2a3a4a" opacity="0.4"/>

  <!-- ═══ SYLWETKA AUDI A3 8PA SPORTBACK ═══ -->
  <!-- Cień pod autem -->
  <ellipse cx="290" cy="138" rx="230" ry="10" fill="#000" opacity="0.5"/>

  <!-- Karoseria główna — profil A3 Sportback -->
  <!-- Dolna belka (progi + podwozie) -->
  <rect x="82" y="112" width="412" height="10" rx="2" fill="#1a2028"/>

  <!-- Koła — obręcze -->
  <circle cx="148" cy="124" r="22" fill="#0e1218" stroke="#3a4a5a" stroke-width="2.5"/>
  <circle cx="148" cy="124" r="14" fill="#1a2028" stroke="#2a3a4a" stroke-width="1.5"/>
  <circle cx="148" cy="124" r="6"  fill="#2a3a4a"/>
  <!-- Szprychy -->
  <line x1="148" y1="110" x2="148" y2="138" stroke="#3a4a5a" stroke-width="1.2"/>
  <line x1="134" y1="124" x2="162" y2="124" stroke="#3a4a5a" stroke-width="1.2"/>
  <line x1="138" y1="114" x2="158" y2="134" stroke="#3a4a5a" stroke-width="1.2"/>
  <line x1="158" y1="114" x2="138" y2="134" stroke="#3a4a5a" stroke-width="1.2"/>

  <circle cx="422" cy="124" r="22" fill="#0e1218" stroke="#3a4a5a" stroke-width="2.5"/>
  <circle cx="422" cy="124" r="14" fill="#1a2028" stroke="#2a3a4a" stroke-width="1.5"/>
  <circle cx="422" cy="124" r="6"  fill="#2a3a4a"/>
  <line x1="422" y1="110" x2="422" y2="138" stroke="#3a4a5a" stroke-width="1.2"/>
  <line x1="408" y1="124" x2="436" y2="124" stroke="#3a4a5a" stroke-width="1.2"/>
  <line x1="412" y1="114" x2="432" y2="134" stroke="#3a4a5a" stroke-width="1.2"/>
  <line x1="432" y1="114" x2="412" y2="134" stroke="#3a4a5a" stroke-width="1.2"/>

  <!-- Karoseria — główna sylwetka A3 Sportback (widok z boku) -->
  <path d="
    M 82,112
    L 82,100
    Q 84,92 95,88
    L 130,82
    Q 155,46 185,36
    Q 215,28 255,26
    Q 295,24 330,26
    Q 360,28 375,32
    L 410,36
    Q 445,42 462,58
    Q 475,70 478,82
    L 490,88
    Q 498,92 500,100
    L 500,112
    Z
  " fill="url(#body_grad)" stroke="#3a4a5a" stroke-width="1"/>

  <!-- Zderzak przedni -->
  <path d="M 82,100 Q 78,104 76,112 L 82,112 Z" fill="#2a3240"/>
  <!-- Zderzak tylny -->
  <path d="M 500,100 Q 504,106 504,112 L 500,112 Z" fill="#2a3240"/>

  <!-- Atrapa grille (przód) -->
  <path d="M 80,96 Q 82,88 90,85 L 82,112 Z" fill="#0e1420" opacity="0.6"/>
  <!-- Reflektory przednie (charakterystyczne Audi) -->
  <path d="M 88,86 Q 102,80 118,82 L 118,92 Q 104,90 90,95 Z" fill="#1a2a3a" stroke="#2a4a6a" stroke-width="0.8"/>
  <ellipse cx="106" cy="88" rx="10" ry="4" fill="url(#light_l)" opacity="0.8"/>

  <!-- Tylne światła -->
  <path d="M 482,82 Q 496,84 500,90 L 500,100 Q 494,96 482,92 Z" fill="#1a1020" stroke="#4a1a1a" stroke-width="0.8"/>
  <ellipse cx="492" cy="90" rx="6" ry="5" fill="#cc2222" opacity="0.4"/>

  <!-- Szyby — charakterystyczny kształt Sportback -->
  <!-- Szyba przednia -->
  <path d="M 185,36 Q 176,60 172,82 L 220,82 L 220,30 Q 205,28 185,36 Z"
        fill="url(#glass_grad)" stroke="#1a3a5a" stroke-width="0.8" opacity="0.9"/>
  <!-- Szyba boczna główna -->
  <path d="M 220,28 L 330,26 L 355,30 L 360,82 L 220,82 Z"
        fill="url(#glass_grad)" stroke="#1a3a5a" stroke-width="0.8" opacity="0.9"/>
  <!-- Szyba tylna (sportback — lekko opada) -->
  <path d="M 360,82 L 358,30 Q 380,28 405,36 Q 430,46 445,62 L 448,82 Z"
        fill="url(#glass_grad)" stroke="#1a3a5a" stroke-width="0.8" opacity="0.85"/>

  <!-- Linia dachu — metaliczny highlight -->
  <path d="M 185,36 Q 255,20 330,22 Q 375,22 410,36"
        fill="none" stroke="#6a8aa4" stroke-width="1.5" opacity="0.6"/>

  <!-- Słupki szyb -->
  <line x1="220" y1="28" x2="222" y2="82" stroke="#1a2a3a" stroke-width="2"/>
  <line x1="358" y1="30" x2="360" y2="82" stroke="#1a2a3a" stroke-width="2"/>

  <!-- Logo Audi na masce (4 kółka uproszczone) -->
  <g transform="translate(108,104)" opacity="0.7">
    <circle cx="0"  cy="0" r="5" fill="none" stroke="#8aaac4" stroke-width="1.2"/>
    <circle cx="9"  cy="0" r="5" fill="none" stroke="#8aaac4" stroke-width="1.2"/>
    <circle cx="18" cy="0" r="5" fill="none" stroke="#8aaac4" stroke-width="1.2"/>
    <circle cx="27" cy="0" r="5" fill="none" stroke="#8aaac4" stroke-width="1.2"/>
  </g>

  <!-- ═══ TEKST PO PRAWEJ ═══ -->
  <!-- Pionowa linia separatora -->
  <line x1="570" y1="25" x2="570" y2="130" stroke="#2a3a4a" stroke-width="1" opacity="0.6"/>

  <!-- AUDI — metaliczny duży napis -->
  <text x="590" y="72" font-family="'Barlow Condensed',sans-serif"
    font-size="58" font-weight="800" fill="url(#txt_grad)"
    letter-spacing="8" filter="url(#softglow)">AUDI</text>

  <!-- A3 SPORTBACK -->
  <text x="592" y="100" font-family="'Barlow Condensed',sans-serif"
    font-size="26" font-weight="600" fill="#4a7a9b"
    letter-spacing="6">A3 SPORTBACK</text>

  <!-- Spec -->
  <text x="593" y="120" font-family="'Barlow Condensed',sans-serif"
    font-size="13" font-weight="400" fill="#2e4a62"
    letter-spacing="4">8PA  ·  1.6 MPI  ·  BSE  ·  2010  ·  102 KM</text>

  <!-- Cienka linia akcentu pod A3 SPORTBACK -->
  <line x1="592" y1="104" x2="870" y2="104" stroke="#1e3a5a" stroke-width="0.8" opacity="0.7"/>

</svg>
</div>
</body></html>""", height=162, scrolling=False)

# ── Statystyki ─────────────────────────────────────────────────────────────────
last_svc  = sorted(log, key=lambda x: x["date"], reverse=True)[0] if log else None
last_date = last_svc["date"] if last_svc else "—"
last_km   = f"{last_svc['km']:,} km".replace(",", " ") if last_svc else "—"
total_cost = sum(s.get("cost", 0) for s in log)

c1, c2, c3, c4 = st.columns(4)
c1.metric("🔧 Wpisów serwisowych", len(log))
c2.metric("📅 Ostatni serwis", last_date)
c3.metric("🛣️ Przebieg (ostatni)", last_km)
c4.metric("💰 Łączny koszt serwisów", f"{total_cost:,} zł".replace(",", " ") if total_cost else "—")

st.divider()

# ── Zakładki ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔧 Historia serwisów", "🛒 Baza części i filtrów", "➕ Dodaj wpis"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Historia serwisów
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-head">Historia serwisów</div>', unsafe_allow_html=True)

    if not log:
        st.info("Brak wpisów serwisowych. Dodaj pierwszy wpis w zakładce ➕")
    else:
        sorted_log = sorted(log, key=lambda x: x["date"], reverse=True)
        for i, s in enumerate(sorted_log):
            is_recent = i == 0
            card_cls  = "svc-card svc-recent" if is_recent else "svc-card"
            items_html = "".join(f'<span class="svc-item">{it}</span>' for it in s.get("items", []))
            cost_html  = f'<div class="svc-cost">💰 {s["cost"]:,} zł</div>'.replace(",", " ") if s.get("cost") else ""
            notes_html = f'<div class="svc-notes">📝 {s["notes"]}</div>' if s.get("notes") else ""
            km_fmt     = f'{s["km"]:,} km'.replace(",", " ") if s.get("km") else ""
            st.markdown(f"""
            <div class="{card_cls}">
              <div style="display:flex;align-items:baseline;gap:4px;">
                <span class="svc-date">📅 {s["date"]}</span>
                <span class="svc-km">· {km_fmt}</span>
                {'<span style="font-size:0.7rem;color:#2a8a5a;margin-left:8px;font-weight:600;">✦ OSTATNI</span>' if is_recent else ''}
              </div>
              <div class="svc-items">{items_html}</div>
              {cost_html}
              {notes_html}
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Baza części
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-head">Baza części — Audi A3 8PA 1.6 MPI BSE</div>', unsafe_allow_html=True)
    st.caption("Numery katalogowe Knecht i Mann+Hummel dla Twojego silnika")

    for p in parts:
        knecht_html = f'<span class="part-badge"><span>Knecht</span>{p["knecht"]}</span>' if p.get("knecht") and p["knecht"] != "—" else ""
        mann_html   = f'<span class="part-badge"><span>Mann</span>{p["mann"]}</span>'     if p.get("mann")   and p["mann"]   != "—" else ""
        note_html   = f'<div class="part-note">⚠️ {p["notes"]}</div>' if p.get("notes") else ""
        st.markdown(f"""
        <div class="part-card">
          <div class="part-cat">{p["category"]}</div>
          <div class="part-spec">{p["spec"]} · {p["ilosc"]}</div>
          <div class="part-nums">{knecht_html}{mann_html}</div>
          {note_html}
        </div>
        """, unsafe_allow_html=True)

    if logged_in:
        st.divider()
        st.markdown('<div class="section-head">Edytuj część</div>', unsafe_allow_html=True)
        part_names = [p["category"] for p in parts]
        sel_part = st.selectbox("Wybierz część:", part_names, key="edit_part")
        ep = next(p for p in parts if p["category"] == sel_part)

        col1, col2 = st.columns(2)
        with col1:
            new_knecht = st.text_input("Nr Knecht:", value=ep.get("knecht", ""), key="knecht_in")
        with col2:
            new_mann   = st.text_input("Nr Mann:", value=ep.get("mann", ""), key="mann_in")
        new_notes = st.text_input("Uwagi:", value=ep.get("notes", ""), key="part_notes_in")

        if st.button("💾 Zapisz część", key="save_part"):
            for p in data["parts"]:
                if p["category"] == sel_part:
                    p["knecht"] = new_knecht.strip()
                    p["mann"]   = new_mann.strip()
                    p["notes"]  = new_notes.strip()
                    break
            save(data)
            st.success("✅ Zapisano!")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Dodaj wpis
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if not logged_in:
        st.markdown("""
        <div style="background:#141c26;border:1px solid #1e2d3d;border-radius:8px;
             padding:18px;text-align:center;color:#4a7a9b;font-size:0.9rem;margin-top:10px;">
          🔐 Zaloguj się przez panel boczny aby dodawać wpisy serwisowe.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-head">Nowy wpis serwisowy</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            new_date = st.date_input("Data serwisu:", value=date.today(),
                                     min_value=date(2000, 1, 1), max_value=date.today())
        with col2:
            new_km = st.number_input("Przebieg (km):", min_value=0, max_value=999999,
                                     value=0, step=1000)

        # Lista czynności — checkboxy + własne
        st.markdown("**Co zostało zrobione?**")
        TYPOWE = [
            "Olej silnikowy + filtr oleju",
            "Filtr powietrza",
            "Filtr kabinowy",
            "Filtr paliwa",
            "Świece zapłonowe",
            "Pasek rozrządu (zestaw)",
            "Płyn hamulcowy",
            "Klocki przód",
            "Klocki tył",
            "Płyn chłodniczy",
            "Przegląd ogólny",
            "Opony letnie → zimowe",
            "Opony zimowe → letnie",
            "Geometria kół",
        ]
        cols = st.columns(2)
        selected_items = []
        for i, item in enumerate(TYPOWE):
            if cols[i % 2].checkbox(item, key=f"chk_{i}"):
                selected_items.append(item)

        custom_items_raw = st.text_input("Inne czynności (oddziel przecinkiem):", placeholder="np. wymiana żarówki, uszczelka pokrywy zaworów")
        if custom_items_raw.strip():
            selected_items += [x.strip() for x in custom_items_raw.split(",") if x.strip()]

        col3, col4 = st.columns(2)
        with col3:
            new_cost = st.number_input("Koszt (zł):", min_value=0, max_value=99999, value=0, step=50)
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)

        new_notes = st.text_area("Notatki:", placeholder="np. serwis ASO, wymieniono też filtr DPF, następny serwis za 10 000 km", height=80)

        if st.button("💾 Zapisz wpis serwisowy", type="primary", use_container_width=True):
            if not selected_items:
                st.error("Zaznacz przynajmniej jedną czynność.")
            else:
                wpis = {
                    "date":  new_date.isoformat(),
                    "km":    int(new_km),
                    "items": selected_items,
                    "cost":  int(new_cost) if new_cost else 0,
                    "notes": new_notes.strip(),
                }
                data["service_log"].append(wpis)
                save(data)
                st.success("✅ Wpis zapisany!")
                st.rerun()

        # Usuń ostatni wpis
        if log:
            st.divider()
            if st.button("🗑️ Usuń ostatni wpis", use_container_width=True):
                newest = sorted(data["service_log"], key=lambda x: x["date"], reverse=True)[0]
                data["service_log"].remove(newest)
                save(data)
                st.info("Ostatni wpis usunięty.")
                st.rerun()

st.markdown("""
<div style="text-align:center;font-size:0.7rem;color:#1e2d3d;padding:12px 0 4px;border-top:1px solid #1a2030;margin-top:16px;">
  hikewithmic · Audi A3 8PA — Dziennik Serwisowy
</div>
""", unsafe_allow_html=True)
