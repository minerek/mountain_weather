import streamlit as st
import streamlit.components.v1 as components
import json
import os
from datetime import date

_FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%230a2a3a'/%3E%3Cpolygon points='16,4 28,26 4,26' fill='%234a7a9b'/%3E%3Cpolygon points='16,4 21,13 11,13' fill='%23ddeeff' opacity='0.9'/%3E%3Cpolygon points='11,13 13,18 4,26 28,26 21,13 19,18' fill='%23144a5e'/%3E%3C/svg%3E"

st.set_page_config(page_title="Moje Tatry — Dziennik", page_icon=_FAVICON, layout="wide")
components.html("""<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap" rel="stylesheet">""", height=0)

st.markdown("""
<style>
[data-testid="stAppViewContainer"],[data-testid="stApp"]{background:#0e1e2f!important}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stAppViewBlockContainer"]{padding-top:75px!important}
body,.stMarkdown,p,li,span{color:#c8ddf0!important}
.mw-title{font-family:'Cinzel',Georgia,serif;font-size:1.55rem;font-weight:700;color:#e8f4ff;letter-spacing:1px;line-height:1.1}
.mw-sub{font-size:0.72rem;color:#7aaac8;letter-spacing:3px}
.mw-heading{font-family:'Cinzel',Georgia,serif!important;color:#90bce0!important;font-size:1.05rem!important;
  font-weight:600!important;letter-spacing:1.5px!important;border-bottom:1px solid #1e3a58;
  padding-bottom:5px;margin-top:1.2rem!important;margin-bottom:0.7rem!important}
[data-testid="stSelectbox"]>div>div,
[data-testid="stTextInput"]>div>div>input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input{background:#142840!important;color:#e8f4ff!important;
  border:1px solid #2a4a68!important;border-radius:6px!important}
[data-testid="stButton"] button{background:linear-gradient(135deg,#1e5c8a,#0e3a5a)!important;
  color:#e8f4ff!important;border:1px solid #3a7aaa!important;border-radius:8px!important;font-weight:600!important}
[data-testid="stButton"] button:hover{background:linear-gradient(135deg,#2a7ab8,#1a5080)!important}
[data-testid="stMetric"]{background:#0e2235!important;border:1px solid #1e3a58!important;
  border-radius:10px!important;padding:10px 14px!important}
.entry-card{background:#0a2218;border:1px solid #1a5a30;border-radius:10px;padding:11px 15px;margin-bottom:7px}
.entry-rank{font-size:0.72rem;color:#7aaac8;letter-spacing:1px;text-transform:uppercase;margin-bottom:2px}
.entry-name{font-family:'Cinzel',Georgia,serif;font-size:1.0rem;font-weight:700;color:#e8f4ff}
.entry-meta{font-size:0.8rem;color:#7aaac8;margin-top:2px}
.entry-notes{font-size:0.8rem;color:#8ab4cc;margin-top:3px;font-style:italic}
.wkt-badge{display:inline-block;background:#1a3a10;border:1px solid #3a8a20;color:#8ade60;
  border-radius:5px;font-size:0.68rem;padding:1px 6px;margin-left:6px;font-weight:600;vertical-align:middle}
.trasa-badge{display:inline-block;background:#2a2a10;border:1px solid #6a6a20;color:#c8c860;
  border-radius:5px;font-size:0.68rem;padding:1px 6px;margin-left:6px;font-weight:600;vertical-align:middle}
.prog-bar-bg{background:#0e2235;border-radius:8px;height:10px;overflow:hidden;border:1px solid #1e3a58}
.prog-bar-fill{background:linear-gradient(90deg,#2a7a4a,#3aaa6a);height:100%;border-radius:8px}
a{color:#5a9ecf!important;text-decoration:none!important}
a:hover{text-decoration:underline!important}
</style>
""", unsafe_allow_html=True)

# ── Dane + GitHub persistence ─────────────────────────────────────────────────
import base64, requests as _req

DATA_FILE = os.path.join(os.path.dirname(__file__), "summits.json")
_GH_REPO  = "minerek/mountain_weather"
_GH_PATH  = "summits.json"

def load():
    """Ładuje dane — najpierw próbuje GitHuba (zawsze aktualne), fallback lokalny."""
    try:
        token = st.secrets["GH_TOKEN"]
        url = f"https://api.github.com/repos/{_GH_REPO}/contents/{_GH_PATH}"
        r = _req.get(url, headers={"Authorization": f"token {token}"}, timeout=8)
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"]).decode("utf-8")
            # Zapamiętaj SHA do późniejszego commitu
            st.session_state["gh_sha"] = r.json()["sha"]
            return json.loads(content)
    except Exception:
        pass
    # Fallback: plik lokalny (środowisko deweloperskie)
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

def save(data):
    """Zapisuje lokalnie ORAZ pushuje do GitHuba przez API."""
    content_str = json.dumps(data, ensure_ascii=False, indent=2)
    # Zapis lokalny (działa w każdym środowisku)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(content_str)
    # Push do GitHuba
    try:
        token = st.secrets["GH_TOKEN"]
        sha   = st.session_state.get("gh_sha", "")
        url   = f"https://api.github.com/repos/{_GH_REPO}/contents/{_GH_PATH}"
        payload = {
            "message": "dziennik: aktualizacja summits.json",
            "content": base64.b64encode(content_str.encode("utf-8")).decode("ascii"),
            "sha": sha,
            "branch": "main",
        }
        r = _req.put(url, json=payload,
                     headers={"Authorization": f"token {token}"}, timeout=10)
        if r.status_code in (200, 201):
            # Zaktualizuj SHA na nowe
            st.session_state["gh_sha"] = r.json()["content"]["sha"]
        else:
            st.warning(f"⚠️ GitHub sync: {r.status_code} — dane zapisane lokalnie.")
    except KeyError:
        pass  # Brak GH_TOKEN — środowisko lokalne, pominięcie push
    except Exception as e:
        st.warning(f"⚠️ GitHub sync error: {e}")

data = load()

# ── Autoryzacja ───────────────────────────────────────────────────────────────
def check_password():
    """Zwraca True jeśli użytkownik podał poprawne hasło."""
    if st.session_state.get("authenticated"):
        return True
    # Hasło pobierane z Streamlit Secrets (nigdy nie ma go w kodzie)
    try:
        correct = st.secrets["APP_PASSWORD"]
    except Exception:
        # Fallback lokalny — działa gdy nie ma secrets (np. na lokalnym komputerze)
        correct = "tatry"

    with st.sidebar:
        st.markdown("### 🔐 Logowanie")
        pwd = st.text_input("Hasło:", type="password", key="pwd_input")
        if st.button("Zaloguj", key="login_btn"):
            if pwd == correct:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Nieprawidłowe hasło.")
    return False

logged_in = check_password()

# ── Banner ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="width:100%;margin-bottom:18px;border-radius:14px;overflow:hidden;position:relative;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 200" style="width:100%;display:block;">
  <defs>
    <!-- Niebo: noc->świt->dzień -->
    <linearGradient id="sky" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%"   stop-color="#04101e"/>
      <stop offset="35%"  stop-color="#0a1e3a"/>
      <stop offset="60%"  stop-color="#7a3010"/>
      <stop offset="80%"  stop-color="#d06020"/>
      <stop offset="100%" stop-color="#e8a040"/>
    </linearGradient>
    <!-- Pasmo dalekiego tła (najwyższe) -->
    <linearGradient id="mtn1" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%"   stop-color="#0d1e32"/>
      <stop offset="35%"  stop-color="#1a2e48"/>
      <stop offset="60%"  stop-color="#6a2a18"/>
      <stop offset="80%"  stop-color="#a04828"/>
      <stop offset="100%" stop-color="#b86030"/>
    </linearGradient>
    <!-- Pasmo środkowe -->
    <linearGradient id="mtn2" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%"   stop-color="#071420"/>
      <stop offset="35%"  stop-color="#0e1e30"/>
      <stop offset="60%"  stop-color="#3a1a10"/>
      <stop offset="80%"  stop-color="#6a3018"/>
      <stop offset="100%" stop-color="#7a4020"/>
    </linearGradient>
    <!-- Pasmo pierwszego planu (ciemne) -->
    <linearGradient id="mtn3" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%"   stop-color="#020a10"/>
      <stop offset="50%"  stop-color="#050e18"/>
      <stop offset="100%" stop-color="#0a1820"/>
    </linearGradient>
    <!-- Gwiazdy – blur -->
    <filter id="glow"><feGaussianBlur stdDeviation="0.8" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>

  <!-- Niebo -->
  <rect width="900" height="200" fill="url(#sky)"/>

  <!-- Gwiazdy (lewa, ciemna strona) -->
  <g filter="url(#glow)" opacity="0.9">
    <circle cx="30"  cy="18" r="1.2" fill="white"/>
    <circle cx="75"  cy="10" r="0.9" fill="white"/>
    <circle cx="120" cy="22" r="1.1" fill="white"/>
    <circle cx="55"  cy="38" r="0.7" fill="white"/>
    <circle cx="95"  cy="30" r="1.0" fill="white"/>
    <circle cx="145" cy="14" r="0.8" fill="white"/>
    <circle cx="200" cy="26" r="0.6" fill="white"/>
    <circle cx="170" cy="42" r="0.9" fill="#ddeeff"/>
    <circle cx="15"  cy="55" r="0.7" fill="white"/>
    <circle cx="240" cy="18" r="0.7" fill="white"/>
    <circle cx="10"  cy="30" r="1.3" fill="#eef8ff"/>
    <circle cx="60"  cy="62" r="0.6" fill="white"/>
  </g>

  <!-- Księżyc -->
  <circle cx="48" cy="28" r="8" fill="#ddeeff" opacity="0.18"/>
  <circle cx="52" cy="26" r="8" fill="#04101e" opacity="0.95"/>

  <!-- Daleka grań (najwyższa, śnieg) -->
  <polygon points="0,130 40,85 80,105 130,60 180,90 230,50 280,75 330,40 380,70 420,45 460,80 500,55 540,90 580,65 620,95 660,70 700,100 740,80 780,110 830,75 870,100 900,85 900,200 0,200"
           fill="url(#mtn1)"/>
  <!-- Śniegowe czapy na najwyższej grani -->
  <polygon points="130,60 118,75 142,75" fill="#ddeeff" opacity="0.7"/>
  <polygon points="230,50 218,67 242,67" fill="#ddeeff" opacity="0.65"/>
  <polygon points="330,40 318,58 342,58" fill="#ddeeff" opacity="0.75"/>
  <polygon points="420,45 408,62 432,62" fill="#ddeeff" opacity="0.7"/>
  <polygon points="500,55 490,70 510,70" fill="#ddeeff" opacity="0.6"/>
  <polygon points="580,65 570,80 590,80" fill="#ddeeff" opacity="0.5"/>

  <!-- Środkowa grań -->
  <polygon points="0,155 50,120 110,140 160,105 210,125 260,95 310,118 360,100 410,120 460,105 510,130 560,110 610,140 660,118 710,148 760,125 810,150 860,132 900,155 900,200 0,200"
           fill="url(#mtn2)"/>

  <!-- Pierwszy plan (ciemny) -->
  <polygon points="0,175 60,155 120,168 180,148 240,162 300,142 360,158 420,145 480,160 540,150 600,165 660,148 720,168 780,152 840,170 900,155 900,200 0,200"
           fill="url(#mtn3)"/>

  <!-- Drzewa (lewa strona, ciemna) -->
  <g fill="#030c14" opacity="0.85">
    <polygon points="18,175 21,155 24,175"/>
    <polygon points="28,175 32,152 36,175"/>
    <polygon points="38,175 42,158 46,175"/>
    <polygon points="50,175 54,161 58,175"/>
    <polygon points="8,175  11,162 14,175"/>
  </g>

  <!-- Tekst -->
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        font-family="Georgia,serif" font-size="30" font-weight="700"
        fill="#e8f4ff" opacity="0.92" letter-spacing="4">Moje Tatry</text>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        font-family="Georgia,serif" font-size="30" font-weight="700"
        fill="none" stroke="#0a1e2e" stroke-width="3" stroke-linejoin="round"
        letter-spacing="4" opacity="0.5">Moje Tatry</text>
  <text x="50%" y="68%" dominant-baseline="middle" text-anchor="middle"
        font-family="Arial,sans-serif" font-size="11" font-weight="400"
        fill="#7aaac8" opacity="0.9" letter-spacing="5">DZIENNIK ZDOBYTYCH SZCZYTÓW</text>

  <!-- IG badge (prawa strona) -->
  <a href="https://www.instagram.com/hikewithmic/">
    <rect x="758" y="10" width="132" height="28" rx="7" fill="#000" opacity="0.35"/>
    <rect x="764" y="14" width="20" height="20" rx="5"
          fill="none" stroke="#ee2a7b" stroke-width="1.6"/>
    <circle cx="774" cy="24" r="4.5" fill="none" stroke="#ee2a7b" stroke-width="1.4"/>
    <circle cx="782" cy="16" r="1.3" fill="#f9ce34"/>
    <text x="790" y="28" font-family="Arial,sans-serif" font-size="11" font-weight="600"
          fill="#c8ddf0">@hikewithmic</text>
  </a>
</svg>
</div>
""", unsafe_allow_html=True)

# ── Nagłówek ──────────────────────────────────────────────────────────────────
col_h, col_ig = st.columns([4, 1])
with col_h:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
      <div>
        <div class="mw-sub">DZIENNIK ZDOBYTYCH SZCZYTÓW</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
with col_ig:
    st.markdown("""
    <div style="display:flex;justify-content:flex-end;align-items:center;margin-top:6px;">
      <a href="https://www.instagram.com/hikewithmic/" target="_blank" style="text-decoration:none;">
        <div style="display:inline-flex;align-items:center;gap:8px;padding:4px 0;">
          <svg width="22" height="22" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
            <defs><linearGradient id="ig2" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#f9ce34"/>
              <stop offset="30%" stop-color="#ee2a7b"/>
              <stop offset="100%" stop-color="#4f5bd5"/>
            </linearGradient></defs>
            <rect width="36" height="36" rx="9" fill="url(#ig2)"/>
            <rect x="7" y="7" width="22" height="22" rx="6" fill="none" stroke="white" stroke-width="2.2"/>
            <circle cx="18" cy="18" r="5.5" fill="none" stroke="white" stroke-width="2.2"/>
            <circle cx="25" cy="11" r="1.6" fill="white"/>
          </svg>
          <span style="font-family:-apple-system,'Segoe UI',system-ui,sans-serif;font-weight:600;font-size:0.78rem;color:#c8ddf0;">@hikewithmic</span>
        </div>
      </a>
    </div>
    """, unsafe_allow_html=True)

# ── Statystyki ────────────────────────────────────────────────────────────────
all_done   = [s for s in data if s.get("date")]
wkt_all    = [s for s in data if s.get("wkt")]
wkt_done   = [s for s in data if s.get("wkt") and s.get("date")]
max_e      = max((s["elevation"] for s in all_done), default=0)
last_date  = sorted(all_done, key=lambda x: x["date"], reverse=True)[0]["date"] if all_done else None

c1, c2, c3, c4 = st.columns(4)
c1.metric("⛰️ Zdobyte szczyty", f"{len(all_done)} / {len(data)}")
c2.metric("⭐ WKT", f"{len(wkt_done)} / {len(wkt_all)}")
c3.metric("🏆 Najwyższy", f"{max_e} m" if max_e else "—")
c4.metric("📅 Ostatnie wejście", last_date or "—")

# Pasek postępu WKT
wkt_pct = int(len(wkt_done) / len(wkt_all) * 100) if wkt_all else 0
st.markdown(f"""
<div style="margin:10px 0 4px;">
  <div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#7aaac8;margin-bottom:3px;">
    <span>Postęp WKT</span><span>{len(wkt_done)} / {len(wkt_all)} ({wkt_pct}%)</span>
  </div>
  <div class="prog-bar-bg"><div class="prog-bar-fill" style="width:{wkt_pct}%"></div></div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Dwa panele: lista szczytów | formularz ────────────────────────────────────
col_list, col_form = st.columns([2, 1], gap="large")

with col_form:
    st.markdown('<div class="mw-heading">✏️ Dodaj wejście</div>', unsafe_allow_html=True)

    if not logged_in:
        st.markdown("""
        <div style="background:#1a2a3a;border:1px solid #2a4a68;border-radius:8px;
             padding:14px 16px;text-align:center;color:#7aaac8;font-size:0.85rem;">
          🔐 Zaloguj się przez panel boczny<br>aby dodawać i edytować wejścia.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Sortowanie listy: WKT najpierw, potem wg wysokości
        sorted_all = sorted(data, key=lambda s: (-int(s.get("wkt", False)), -s["elevation"]))

        sel_name = st.selectbox(
            "Wybierz szczyt:",
            [s["name"] for s in sorted_all],
            format_func=lambda n: next(
                ("⭐ " if s["wkt"] else "   ") + f"{s['name']}  ({s['elevation']} m)"
                for s in sorted_all if s["name"] == n
            )
        )
        sel = next(s for s in data if s["name"] == sel_name)

        existing_date = date.fromisoformat(sel["date"]) if sel.get("date") else date.today()
        new_date  = st.date_input("Data wejścia:", value=existing_date,
                                   min_value=date(1990,1,1), max_value=date.today())
        new_notes = st.text_area("Notatki:", value=sel.get("notes",""),
                                  placeholder="np. trasa, pogoda, towarzystwo...",
                                  height=80)

        if st.button("💾 Zapisz", type="primary", use_container_width=True):
            for s in data:
                if s["name"] == sel_name:
                    s["date"]  = new_date.isoformat()
                    s["notes"] = new_notes.strip()
                    break
            save(data)
            st.success("✅ Zapisano!")
            st.rerun()

        if sel.get("date") and st.button("🗑️ Usuń wpis", use_container_width=True):
            for s in data:
                if s["name"] == sel_name:
                    s["date"]  = None
                    s["notes"] = ""
                    break
            save(data)
            st.info("Wpis usunięty.")
            st.rerun()

        # Podgląd wybranego szczytu
        st.markdown(f"""
        <div style="background:#0e2235;border:1px solid #1e3a58;border-radius:8px;padding:10px 13px;margin-top:10px;">
          <div style="font-size:0.72rem;color:#7aaac8;text-transform:uppercase;letter-spacing:1px;">Wybrany szczyt</div>
          <div style="font-family:'Cinzel',Georgia,serif;font-size:0.95rem;color:#e8f4ff;margin-top:3px;">
            {sel['name']}{'<span class="wkt-badge">⭐ WKT</span>' if sel.get('wkt') else ''}
          </div>
          <div style="font-size:0.8rem;color:#5a8ab0;margin-top:2px;">{sel['elevation']} m · {sel['range']}</div>
          {'<div style="font-size:0.8rem;color:#3a9a5a;margin-top:3px;">✅ Zdobyty: ' + sel["date"] + '</div>' if sel.get('date') else '<div style="font-size:0.8rem;color:#3a6080;margin-top:3px;">⬜ Jeszcze nie zdobyty</div>'}
        </div>
        """, unsafe_allow_html=True)

with col_list:
    st.markdown('<div class="mw-heading">📋 Wszystkie szczyty</div>', unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    with f1:
        filt_status = st.selectbox("Status:", ["Wszystkie", "Zdobyte ✅", "Niezdobyte ⬜"], key="filt_s")
    with f2:
        filt_wkt = st.selectbox("Typ:", ["Wszystkie", "Tylko WKT ⭐", "Bez WKT"], key="filt_w")

    disp = sorted(data, key=lambda s: (-int(s.get("wkt", False)), -s["elevation"]))
    if filt_status == "Zdobyte ✅":    disp = [s for s in disp if s.get("date")]
    if filt_status == "Niezdobyte ⬜": disp = [s for s in disp if not s.get("date")]
    if filt_wkt == "Tylko WKT ⭐":     disp = [s for s in disp if s.get("wkt")]
    if filt_wkt == "Bez WKT":          disp = [s for s in disp if not s.get("wkt")]

    # Nagłówek tabeli
    st.markdown("""
    <div style="display:grid;grid-template-columns:28px 1fr 110px 1fr 90px;gap:4px;
         font-size:0.72rem;color:#5a8ab0;text-transform:uppercase;letter-spacing:0.8px;
         padding:4px 8px;border-bottom:1px solid #1e3a58;margin-bottom:4px;">
      <div></div><div>Szczyt</div><div>Pasmo</div><div>Notatki</div><div style="text-align:right">Data</div>
    </div>
    """, unsafe_allow_html=True)

    for s in disp:
        done = bool(s.get("date"))
        check = "✅" if done else "⬜"
        wkt_b = '<span class="wkt-badge">⭐</span>' if s.get("wkt") else ""
        date_s = f'<span style="color:#3a9a5a">{s["date"]}</span>' if done else '<span style="color:#2a4a68">—</span>'
        notes_s = f'<span style="font-size:0.78rem;color:#6a9ab8;font-style:italic;">💬 {s["notes"]}</span>' if s.get("notes") else ""
        range_s = f'<span style="font-size:0.78rem;color:#5a8ab0;">{s["range"]}</span>'
        bg = "#0a1e0e" if done else "#0a1828"
        border = "#1a4a22" if done else "#1a2e42"
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:28px 1fr 110px 1fr 90px;gap:4px;align-items:center;
             background:{bg};border:1px solid {border};border-radius:7px;
             padding:6px 8px;margin-bottom:3px;">
          <div style="font-size:1rem">{check}</div>
          <div style="font-size:0.88rem;color:#e8f4ff;font-weight:500">{s['name']}{wkt_b}&nbsp;&nbsp;<span style="color:#5a8ab0;font-weight:400">{s['elevation']} m</span></div>
          <div>{range_s}</div>
          <div>{notes_s}</div>
          <div style="text-align:right;font-size:0.82rem">{date_s}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Chronologiczna lista zdobytych ────────────────────────────────────────────
st.markdown('<div class="mw-heading">📅 Historia wejść — posortowana chronologicznie</div>', unsafe_allow_html=True)

climbed = sorted([s for s in data if s.get("date")], key=lambda x: x["date"], reverse=True)

if not climbed:
    st.info("Brak zapisanych wejść. Dodaj pierwsze wejście po prawej stronie ➡️")
else:
    cols = st.columns(3)
    for i, s in enumerate(climbed):
        wkt_b = '<span class="wkt-badge">⭐ WKT</span>' if s.get("wkt") else ""
        notes_s = f'<div class="entry-notes">💬 {s["notes"]}</div>' if s.get("notes") else ""
        # Formatuj datę czytelnie
        try:
            d = date.fromisoformat(s["date"])
            date_fmt = d.strftime("%d %b %Y").replace("Jan","sty").replace("Feb","lut")\
                .replace("Mar","mar").replace("Apr","kwi").replace("May","maj")\
                .replace("Jun","cze").replace("Jul","lip").replace("Aug","sie")\
                .replace("Sep","wrz").replace("Oct","paź").replace("Nov","lis").replace("Dec","gru")
        except Exception:
            date_fmt = s["date"]

        cols[i % 3].markdown(f"""
        <div class="entry-card">
          <div class="entry-rank">#{i+1} · {date_fmt}</div>
          <div class="entry-name">{s['name']}{wkt_b}</div>
          <div class="entry-meta">{s['elevation']} m · {s['range']}</div>
          {notes_s}
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;font-size:0.72rem;color:#2a4a68;padding:10px 0 4px;">
  hikewithmic · Moje Tatry — Dziennik Szczytów
</div>
""", unsafe_allow_html=True)
