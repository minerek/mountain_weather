import streamlit as st
import streamlit.components.v1 as components
import json, os, base64, requests as _req
from datetime import date
from pathlib import Path

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

# ── Banner — obrazek PNG ──────────────────────────────────────────────────────
_banner_path = Path(__file__).parent / "audi_banner.png"
_banner_b64 = base64.b64encode(_banner_path.read_bytes()).decode()
st.markdown(
    f'<div style="margin-top: -50px !important; margin-bottom: -20px !important; padding: 0 !important; width: 100% !important; display: block !important; overflow: hidden !important;">'
    f'  <img src="data:image/png;base64,{_banner_b64}" style="width: 100% !important; height: 160px !important; object-fit: cover !important; object-position: center 50% !important; border-radius: 12px !important; display: block !important; margin: 0 !important; padding: 0 !important;" />'
    f'</div>',
    unsafe_allow_html=True
)

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
  hikewithmic · Audi A3 8PA — Dziennik Serwisowy v1.2
</div>
""", unsafe_allow_html=True)
