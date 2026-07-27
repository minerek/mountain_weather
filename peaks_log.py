import streamlit as st
import streamlit.components.v1 as components
import json
import os
from datetime import date, datetime

# ── Favicon ──────────────────────────────────────────────────────────────────
_FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%230a2a3a'/%3E%3Cpolygon points='16,4 28,26 4,26' fill='%234a7a9b'/%3E%3Cpolygon points='16,4 21,13 11,13' fill='%23ddeeff' opacity='0.9'/%3E%3Cpolygon points='11,13 13,18 4,26 28,26 21,13 19,18' fill='%23144a5e'/%3E%3C/svg%3E"

st.set_page_config(
    page_title="Moje Tatry — Dziennik Szczytów",
    page_icon=_FAVICON,
    layout="wide",
)

components.html("""<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap" rel="stylesheet">""", height=0)

st.markdown("""
<style>
[data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0e1e2f !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stAppViewBlockContainer"] { padding-top: 75px !important; }

.mw-heading {
    font-family: 'Cinzel', Georgia, serif !important;
    color: #90bce0 !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    border-bottom: 1px solid #1e3a58;
    padding-bottom: 5px;
    margin-top: 1.2rem !important;
    margin-bottom: 0.7rem !important;
}
/* Ogólny tekst */
body, .stMarkdown, .stText, p, li, span {
    color: #c8ddf0 !important;
}
/* Dataframe */
[data-testid="stDataFrame"] table { background: #0e1e2f !important; }
/* Selectbox / input */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div > input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input {
    background: #142840 !important;
    color: #e8f4ff !important;
    border: 1px solid #2a4a68 !important;
    border-radius: 6px !important;
}
/* Button */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #1e5c8a, #0e3a5a) !important;
    color: #e8f4ff !important;
    border: 1px solid #3a7aaa !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #2a7ab8, #1a5080) !important;
}
/* Metric */
[data-testid="stMetric"] {
    background: #0e2235 !important;
    border: 1px solid #1e3a58 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
}
/* Tags WKT */
.tag-wkt {
    display:inline-block;background:#1a4a2e;border:1px solid #2a7a4a;
    color:#7fd4a0;border-radius:5px;font-size:0.7rem;padding:1px 7px;
    margin-left:6px;font-weight:600;letter-spacing:0.5px;vertical-align:middle;
}
.tag-done {
    display:inline-block;background:#1a3a5a;border:1px solid #2a6a9a;
    color:#7ab8e0;border-radius:5px;font-size:0.7rem;padding:1px 7px;
    margin-left:4px;font-weight:600;letter-spacing:0.5px;vertical-align:middle;
}
/* Karty szczytów */
.peak-card {
    background:#0e2235;border:1px solid #1e3a58;border-radius:10px;
    padding:10px 14px;margin-bottom:6px;
}
.peak-card.done {
    background:#0a2218;border-color:#1a5a30;
}
.peak-name {
    font-family:'Cinzel',Georgia,serif;font-size:1.0rem;font-weight:700;
    color:#e8f4ff;letter-spacing:0.5px;
}
.peak-date { font-size:0.8rem;color:#7aaac8;margin-top:2px; }
.peak-notes { font-size:0.82rem;color:#8ab4cc;margin-top:3px;font-style:italic; }
a { color:#5a9ecf !important; text-decoration:none !important; }
a:hover { text-decoration:underline !important; }
</style>
""", unsafe_allow_html=True)

# ── Ścieżka do pliku danych ───────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "summits.json")

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── Nagłówek ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
  <svg width="36" height="36" viewBox="0 0 38 38" xmlns="http://www.w3.org/2000/svg">
    <polygon points="19,4 35,32 3,32" fill="#4a7a9b" stroke="#5a96c0" stroke-width="1"/>
    <polygon points="19,4 27,17 11,17" fill="#ddeeff" opacity="0.9"/>
    <polygon points="11,17 15,24 3,32 35,32 27,17 23,24" fill="#144a5e"/>
  </svg>
  <div>
    <div style="font-family:'Cinzel',Georgia,serif;font-size:1.6rem;font-weight:700;color:#e8f4ff;letter-spacing:1px;line-height:1.1;">Moje Tatry</div>
    <div style="font-size:0.72rem;color:#7aaac8;letter-spacing:3px;">DZIENNIK ZDOBYTYCH SZCZYTÓW</div>
  </div>
</div>
""", unsafe_allow_html=True)

data = load_data()

# ── Statystyki ────────────────────────────────────────────────────────────────
total = len(data)
done = sum(1 for s in data if s.get("date"))
wkt_total = sum(1 for s in data if s.get("wkt"))
wkt_done  = sum(1 for s in data if s.get("wkt") and s.get("date"))
max_elev  = max((s["elevation"] for s in data if s.get("date")), default=0)

c1, c2, c3, c4 = st.columns(4)
c1.metric("⛰️ Zdobyte szczyty", f"{done} / {total}")
c2.metric("⭐ WKT", f"{wkt_done} / {wkt_total}")
c3.metric("🏆 Najwyższy zdobyty", f"{max_elev} m" if max_elev else "—")
c4.metric("📅 Ostatnie wejście", next(
    (s["date"] for s in sorted(
        [s for s in data if s.get("date")],
        key=lambda x: x["date"], reverse=True
    )[:1]), "—"
))

st.divider()

# ── Formularz dodawania wejścia ───────────────────────────────────────────────
st.markdown('<div class="mw-heading">✏️ Dodaj lub edytuj wejście</div>', unsafe_allow_html=True)

names = [s["name"] for s in data]
col_sel, col_date, col_notes = st.columns([2, 1, 3])

with col_sel:
    selected_name = st.selectbox(
        "Szczyt:",
        names,
        format_func=lambda n: next(
            f"{'⭐ ' if s['wkt'] else ''}{s['name']}  ({s['elevation']} m)"
            for s in data if s["name"] == n
        )
    )

selected = next(s for s in data if s["name"] == selected_name)

with col_date:
    existing_date = date.fromisoformat(selected["date"]) if selected.get("date") else None
    new_date = st.date_input("Data wejścia:", value=existing_date, min_value=date(1990, 1, 1), max_value=date.today())

with col_notes:
    new_notes = st.text_input("Notatki (opcjonalnie):", value=selected.get("notes", ""),
                               placeholder="np. trasa, pogoda, towarzystwo...")

col_save, col_clear = st.columns([1, 1])
with col_save:
    if st.button("💾 Zapisz wejście", type="primary"):
        for s in data:
            if s["name"] == selected_name:
                s["date"] = new_date.isoformat()
                s["notes"] = new_notes
                break
        save_data(data)
        st.success(f"✅ Zapisano: {selected_name} — {new_date.strftime('%d.%m.%Y')}")
        st.rerun()

with col_clear:
    if st.button("🗑️ Usuń datę (niezdobyty)"):
        for s in data:
            if s["name"] == selected_name:
                s["date"] = None
                s["notes"] = ""
                break
        save_data(data)
        st.info(f"Usunięto wpis dla: {selected_name}")
        st.rerun()

st.divider()

# ── Lista WKT ────────────────────────────────────────────────────────────────
st.markdown('<div class="mw-heading">⭐ Wielka Korona Tatr (14 szczytów ≥ 2440 m)</div>', unsafe_allow_html=True)

wkt_peaks = sorted([s for s in data if s.get("wkt")], key=lambda x: -x["elevation"])

# Postęp WKT jako pasek
wkt_pct = int(wkt_done / wkt_total * 100) if wkt_total else 0
st.markdown(f"""
<div style="margin-bottom:12px;">
  <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#7aaac8;margin-bottom:4px;">
    <span>Postęp WKT</span><span>{wkt_done}/{wkt_total} szczytów ({wkt_pct}%)</span>
  </div>
  <div style="background:#0e2235;border-radius:8px;height:12px;overflow:hidden;border:1px solid #1e3a58;">
    <div style="background:linear-gradient(90deg,#2a7a4a,#3aaa6a);height:100%;width:{wkt_pct}%;border-radius:8px;transition:width 0.5s;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

cols_wkt = st.columns(3)
for i, peak in enumerate(wkt_peaks):
    done_flag = bool(peak.get("date"))
    card_class = "peak-card done" if done_flag else "peak-card"
    check = "✅" if done_flag else "⬜"
    date_str = f'<div class="peak-date">📅 {peak["date"]}</div>' if done_flag else '<div class="peak-date" style="color:#3a6080;">— nie zdobyty —</div>'
    notes_str = f'<div class="peak-notes">💬 {peak["notes"]}</div>' if peak.get("notes") else ""
    rank = i + 1
    cols_wkt[i % 3].markdown(f"""
    <div class="{card_class}">
      <div class="peak-name">{check} {rank}. {peak["name"]}</div>
      <div style="font-size:0.78rem;color:#5a8ab0;margin-top:1px;">{peak["elevation"]} m · {peak["range"]}</div>
      {date_str}{notes_str}
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Pozostałe szczyty ─────────────────────────────────────────────────────────
st.markdown('<div class="mw-heading">🏔️ Pozostałe szczyty tatrzańskie</div>', unsafe_allow_html=True)

other_peaks = sorted([s for s in data if not s.get("wkt")], key=lambda x: -x["elevation"])
other_done = sum(1 for s in other_peaks if s.get("date"))

# Filtr
col_f1, col_f2 = st.columns([1, 2])
with col_f1:
    filter_status = st.selectbox("Filtr:", ["Wszystkie", "Tylko zdobyte", "Tylko niezdobyte"])
with col_f2:
    ranges_available = sorted(set(s["range"] for s in other_peaks))
    filter_range = st.multiselect("Pasmo:", ranges_available, default=ranges_available)

filtered = [s for s in other_peaks
            if s["range"] in filter_range
            and (filter_status == "Wszystkie"
                 or (filter_status == "Tylko zdobyte" and s.get("date"))
                 or (filter_status == "Tylko niezdobyte" and not s.get("date")))]

st.caption(f"Wyświetlane: {len(filtered)} szczytów · Zdobyte: {other_done} / {len(other_peaks)}")

cols_other = st.columns(3)
for i, peak in enumerate(filtered):
    done_flag = bool(peak.get("date"))
    card_class = "peak-card done" if done_flag else "peak-card"
    check = "✅" if done_flag else "⬜"
    date_str = f'<div class="peak-date">📅 {peak["date"]}</div>' if done_flag else '<div class="peak-date" style="color:#3a6080;">— nie zdobyty —</div>'
    notes_str = f'<div class="peak-notes">💬 {peak["notes"]}</div>' if peak.get("notes") else ""
    cols_other[i % 3].markdown(f"""
    <div class="{card_class}">
      <div class="peak-name">{check} {peak["name"]}</div>
      <div style="font-size:0.78rem;color:#5a8ab0;margin-top:1px;">{peak["elevation"]} m · {peak["range"]}</div>
      {date_str}{notes_str}
    </div>
    """, unsafe_allow_html=True)

# ── Stopka ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center;font-size:0.75rem;color:#3a6080;padding:8px 0;">
  hikewithmic · Moje Tatry — Dziennik Szczytów
</div>
""", unsafe_allow_html=True)
