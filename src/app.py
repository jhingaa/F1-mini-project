import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.data.loader import load_session, load_session_with_telemetry
from src.data.processor import (
    get_lap_positions, get_driver_info, get_lap_times,
    get_gap_to_leader, get_session_results, get_fastest_lap_info,
)
from src.data.circuit_info import CIRCUIT_FLAGS, CIRCUIT_NAMES
from src.viz.replay import build_replay_figure
from src.viz.lap_times import build_lap_times_figure, build_duel_figure
from src.viz.gap_chart import build_gap_figure
from src.viz.track_map import build_track_speed_map, build_circuit_outline
from src.viz.utils import build_color_map
from src.viz.colors import team_color

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="F1 Race Replay", page_icon="🏎️", layout="wide")

st.markdown("""
<style>
/* ── base ── */
.stApp { background-color: #0d0d1a; }
.main .block-container { padding-top: 1rem; max-width: 1400px; }
h1,h2,h3 { color: white !important; }
p, li, label { color: #cccccc !important; }

/* ── sidebar ── */
section[data-testid="stSidebar"] { background-color: #111128 !important; border-right: 1px solid #2a2a4a; }
section[data-testid="stSidebar"] * { color: #cccccc !important; }

/* ── button ── */
.stButton > button {
    background: linear-gradient(135deg, #e10600, #a80000) !important;
    color: white !important; border: none !important;
    font-weight: 700 !important; border-radius: 8px !important;
    letter-spacing: 0.5px !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #111128; border-radius: 10px; padding: 4px; gap: 4px;
    border: 1px solid #2a2a4a;
}
.stTabs [data-baseweb="tab"] {
    color: #888 !important; border-radius: 7px; padding: 6px 18px;
    font-size: 0.9rem; font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #e10600 !important; color: white !important;
}

/* ── metric cards ── */
div[data-testid="metric-container"] {
    background: #111128; padding: 0.8rem 1.2rem;
    border-radius: 10px; border-left: 3px solid #e10600;
    border: 1px solid #2a2a4a;
}
div[data-testid="metric-container"] label { color: #888 !important; font-size: 0.78rem !important; }
div[data-testid="metric-container"] [data-testid="metric-value"] { color: white !important; font-size: 1.4rem !important; }

/* ── multiselect ── */
.stMultiSelect [data-baseweb="tag"] { background: #e10600 !important; }

/* ── selectbox ── */
.stSelectbox > div { background: #111128 !important; border-color: #2a2a4a !important; }

/* ── divider ── */
hr { border-color: #2a2a4a !important; margin: 1rem 0; }

/* ── info/warning/error ── */
.stAlert { border-radius: 8px !important; }

/* ── caption ── */
.stCaption { color: #666 !important; }
</style>
""", unsafe_allow_html=True)

# ── Title ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 0.5rem 0 1.2rem 0;">
  <span style="font-size:2.8rem; font-weight:900; letter-spacing:2px; color:white;">🏎️ F1 RACE REPLAY</span>
  <div style="height:3px; background:linear-gradient(90deg,transparent,#e10600,transparent); margin-top:6px;"></div>
</div>
""", unsafe_allow_html=True)

# ── GP list ────────────────────────────────────────────────────────────────────
GP_OPTIONS = [
    "Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami",
    "Emilia Romagna", "Monaco", "Canada", "Spain", "Austria", "Great Britain",
    "Hungary", "Belgium", "Netherlands", "Italy", "Azerbaijan", "Singapore",
    "United States", "Mexico City", "São Paulo", "Las Vegas", "Qatar", "Abu Dhabi",
]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗂 Session")
    year = st.selectbox("Year", list(range(2018, 2026))[::-1], key="sel_year")
    gp   = st.selectbox("Grand Prix", GP_OPTIONS, key="sel_gp")
    session_type = st.selectbox(
        "Session", ["R","Q","S","FP1","FP2","FP3"],
        format_func=lambda x: {"R":"Race","Q":"Qualifying","S":"Sprint",
                               "FP1":"Practice 1","FP2":"Practice 2","FP3":"Practice 3"}[x],
        key="sel_stype",
    )
    load_btn = st.button("⬇  Load Session", type="primary", use_container_width=True)

    if "meta" in st.session_state:
        m = st.session_state["meta"]
        st.markdown("---")
        st.markdown(f"**Loaded:** {m['event']}")
        st.markdown(f"{CIRCUIT_FLAGS.get(m['gp'],'🏁')}  {m['year']}  ·  {m['session_type']}")

    st.markdown("---")
    st.markdown(
        "<small style='color:#555'>Data via FastF1 API.<br>First load downloads & caches.</small>",
        unsafe_allow_html=True,
    )

# ── Load handler ───────────────────────────────────────────────────────────────
if load_btn:
    for k in ["lap_positions","driver_info","lap_times","gap_data","color_map",
              "title","meta","results","fastest","circuit_outline","track_map_fig"]:
        st.session_state.pop(k, None)

    with st.spinner(f"Loading {year} {gp} GP — {session_type} …"):
        try:
            session = load_session(year, gp, session_type)
            try:
                event_name = session.event.get("EventName", f"{gp} Grand Prix")
            except Exception:
                event_name = f"{gp} Grand Prix"

            lap_positions   = get_lap_positions(session)
            driver_info     = get_driver_info(session)
            lap_times       = get_lap_times(session)
            gap_data        = get_gap_to_leader(session)
            color_map       = build_color_map(driver_info)
            results         = get_session_results(session)
            fastest         = get_fastest_lap_info(session)
            circuit_outline = build_circuit_outline(session)   # no telemetry needed

            st.session_state.update({
                "lap_positions":   lap_positions,
                "driver_info":     driver_info,
                "lap_times":       lap_times,
                "gap_data":        gap_data,
                "color_map":       color_map,
                "title":           f"{year} {event_name}",
                "results":         results,
                "fastest":         fastest,
                "circuit_outline": circuit_outline,
                "meta": {
                    "event":        event_name,
                    "year":         year,
                    "gp":           gp,
                    "session_type": session_type,
                    "n_drivers":    len(session.drivers),
                    "n_laps":       int(lap_positions["LapNumber"].max()) if not lap_positions.empty else "—",
                },
            })
            st.success(f"Loaded **{event_name} {year}** — {len(session.drivers)} drivers")
            st.rerun()
        except Exception as exc:
            st.error(f"Failed to load session: {exc}")

# ── Main dashboard ─────────────────────────────────────────────────────────────
if "lap_positions" not in st.session_state:
    st.markdown("""
    <div style="text-align:center; padding:5rem 2rem; color:#444;">
        <div style="font-size:4rem; margin-bottom:1rem;">🏁</div>
        <h2 style="color:#666 !important;">Select a season, GP &amp; session in the sidebar</h2>
        <p style="color:#444 !important;">Then click <strong>Load Session</strong> to start.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

meta        = st.session_state["meta"]
color_map   = st.session_state["color_map"]
results     = st.session_state["results"]
fastest     = st.session_state["fastest"]
circuit_outline = st.session_state.get("circuit_outline")
flag        = CIRCUIT_FLAGS.get(meta["gp"], "🏁")
circuit_nm  = CIRCUIT_NAMES.get(meta["gp"], meta["event"])

_STYPE_LABELS = {"R": "Race", "Q": "Qualifying", "S": "Sprint",
                 "FP1": "Practice 1", "FP2": "Practice 2", "FP3": "Practice 3"}
session_label = _STYPE_LABELS.get(meta["session_type"], meta["session_type"])

if fastest:
    fastest_html = f"""
    <div style="background:#1a1a2e;border-radius:8px;padding:0.6rem 0.8rem;
                border-left:3px solid #ffd700;grid-column:1/-1;">
      <div style="font-size:0.7rem;color:#777;text-transform:uppercase;letter-spacing:1px;">⚡ Fastest Lap</div>
      <div style="font-size:1rem;font-weight:700;color:white;">
        {fastest.get("driver","?")}
        <span style="color:#ffd700;font-size:0.85rem;margin-left:6px;">{fastest.get("time","")}</span>
        <span style="color:#666;font-size:0.75rem;margin-left:4px;">Lap {fastest.get("lap","")}</span>
      </div>
    </div>"""
else:
    fastest_html = ""

# ── Circuit banner ─────────────────────────────────────────────────────────────
col_img, col_info = st.columns([3, 2], gap="medium")

with col_img:
    if circuit_outline is not None:
        st.plotly_chart(
            circuit_outline,
            use_container_width=True,
            config={"displayModeBar": False},
        )
    else:
        st.markdown(
            '<div style="width:100%;height:300px;border-radius:14px;border:1px solid #2a2a4a;'
            'background:#111128;display:flex;align-items:center;justify-content:center;'
            'font-size:4rem;">🏁</div>',
            unsafe_allow_html=True,
        )

with col_info:
    st.markdown(f"""
    <div style="padding:1.2rem 1.4rem; background:#111128; border-radius:14px;
                border:1px solid #2a2a4a; height:300px; box-sizing:border-box;
                display:flex; flex-direction:column; justify-content:space-between;">

      <div>
        <div style="font-size:1.8rem; margin-bottom:0.2rem;">{flag}</div>
        <div style="font-size:1.4rem; font-weight:800; color:white; line-height:1.2;">
          {circuit_nm}
        </div>
        <div style="font-size:1rem; color:#e10600; font-weight:600; margin-top:0.3rem;">
          {meta['event']}
        </div>
        <div style="font-size:0.85rem; color:#888; margin-top:0.2rem;">
          {meta['year']} &nbsp;·&nbsp; {session_label}
        </div>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; margin-top:0.8rem;">
        <div style="background:#1a1a2e; border-radius:8px; padding:0.6rem 0.8rem; border-left:3px solid #e10600;">
          <div style="font-size:0.7rem; color:#777; text-transform:uppercase; letter-spacing:1px;">Laps</div>
          <div style="font-size:1.2rem; font-weight:700; color:white;">{meta['n_laps']}</div>
        </div>
        <div style="background:#1a1a2e; border-radius:8px; padding:0.6rem 0.8rem; border-left:3px solid #e10600;">
          <div style="font-size:0.7rem; color:#777; text-transform:uppercase; letter-spacing:1px;">Drivers</div>
          <div style="font-size:1.2rem; font-weight:700; color:white;">{meta['n_drivers']}</div>
        </div>
        {fastest_html}
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Podium (race only) ─────────────────────────────────────────────────────────
if meta["session_type"] in ("R", "S") and not results.empty:
    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
    podium_cols = st.columns(3, gap="medium")
    podium_order = [(1, "🥈", podium_cols[0]),
                    (0, "🥇", podium_cols[1]),   # P1 in centre
                    (2, "🥉", podium_cols[2])]
    medals_label = {0: "🥇 P1", 1: "🥈 P2", 2: "🥉 P3"}
    highlight = {0: "#ffd700", 1: "#c0c0c0", 2: "#cd7f32"}

    for idx, medal, col in podium_order:
        if idx < len(results):
            r = results.iloc[idx]
            clr = team_color(r.get("TeamName",""))
            accent = highlight[idx]
            time_txt = str(r.get("Time","")).split(".")
            time_disp = time_txt[0] if time_txt[0] not in ("NaT","nan","None","") else r.get("Status","")
            col.markdown(f"""
            <div style="
                background:linear-gradient(135deg, {clr}18, #111128);
                border:2px solid {accent};
                border-radius:14px; padding:1.5rem 1rem;
                text-align:center;
                box-shadow: 0 4px 24px {clr}30;
            ">
              <div style="font-size:1.8rem; margin-bottom:0.3rem;">{medals_label[idx]}</div>
              <div style="font-size:2.2rem; font-weight:900; color:white; letter-spacing:3px;">
                {r.get("Abbreviation","?")}
              </div>
              <div style="font-size:0.85rem; color:{clr}; font-weight:600; margin:0.3rem 0;">
                {r.get("TeamName","—")}
              </div>
              <div style="font-size:0.78rem; color:#777;">{time_disp}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Driver filter ──────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
all_abbrevs = sorted(st.session_state["driver_info"]["Abbreviation"].tolist())
driver_filter = st.multiselect(
    "🎯 Highlight drivers — applies to all charts (empty = show all)",
    all_abbrevs,
    key="global_driver_filter",
    help="Filter all charts to these drivers only",
)
active_drivers = driver_filter if driver_filter else None

st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_replay, tab_track, tab_laps, tab_gap, tab_duel = st.tabs([
    "📊 Position Replay", "🗺️ Track Map", "⏱ Lap Times", "📈 Gap to Leader", "🥊 Driver Duel",
])

# ── Tab: Position Replay ───────────────────────────────────────────────────────
with tab_replay:
    lp = st.session_state["lap_positions"]
    if lp.empty:
        st.warning("No position data for this session type. Try selecting Race.")
    else:
        fig = build_replay_figure(
            lp if not active_drivers else lp[lp["Driver"].isin(
                st.session_state["driver_info"].loc[
                    st.session_state["driver_info"]["Abbreviation"].isin(active_drivers), "Driver"
                ].tolist()
            )],
            st.session_state["driver_info"],
            title=st.session_state["title"],
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Press ▶ Play to animate · drag the lap slider · click legend to toggle drivers")

# ── Tab: Track Map ─────────────────────────────────────────────────────────────
with tab_track:
    if "track_map_fig" not in st.session_state:
        st.markdown("""
        <div style="background:#111128; border:1px solid #2a2a4a; border-radius:14px;
                    padding:2.5rem; text-align:center; margin:1rem 0;">
          <div style="font-size:2.5rem; margin-bottom:0.8rem;">🗺️</div>
          <h3 style="color:white !important; margin:0 0 0.5rem 0;">Circuit Speed Map</h3>
          <p style="color:#666 !important; margin-bottom:1.5rem;">
            Draws the circuit outline coloured by speed from the fastest lap telemetry.<br>
            Requires downloading additional data (~30 s first time, instant from cache).
          </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⬇  Load Telemetry & Generate Track Map", use_container_width=False):
            m = st.session_state["meta"]
            with st.spinner("Downloading telemetry — this may take 30–90 s …"):
                try:
                    tel_sess = load_session_with_telemetry(m["year"], m["gp"], m["session_type"])
                    fig = build_track_speed_map(tel_sess)
                    st.session_state["track_map_fig"] = fig
                    st.rerun()
                except Exception as exc:
                    st.error(f"Track map failed: {exc}")
    else:
        st.plotly_chart(st.session_state["track_map_fig"], use_container_width=True)
        st.caption("Colour = speed · white circles = corner numbers · fastest lap of the session")
        if st.button("🔄 Reload Track Map"):
            del st.session_state["track_map_fig"]
            st.rerun()

# ── Tab: Lap Times ─────────────────────────────────────────────────────────────
with tab_laps:
    lt = st.session_state["lap_times"]
    if lt.empty:
        st.warning("No lap time data for this session.")
    else:
        col_l, col_r = st.columns([3, 1])
        with col_r:
            st.markdown("**Tyre legend**")
            for compound, color in [("Soft","#FF3333"),("Medium","#FFD700"),
                                     ("Hard","#EBEBEB"),("Inter","#39B54A"),("Wet","#0067FF")]:
                st.markdown(
                    f'<span style="display:inline-block;width:12px;height:12px;'
                    f'border-radius:50%;background:{color};margin-right:6px;"></span>'
                    f'<small style="color:#ccc">{compound}</small>',
                    unsafe_allow_html=True,
                )
        with col_l:
            st.plotly_chart(
                build_lap_times_figure(
                    lt, st.session_state["driver_info"], color_map,
                    selected_drivers=active_drivers,
                    title=f"{st.session_state['title']} — Lap Times",
                ),
                use_container_width=True,
            )
        st.caption("Line = team colour · dot = tyre compound colour · hover for exact time")

# ── Tab: Gap to Leader ─────────────────────────────────────────────────────────
with tab_gap:
    gd = st.session_state["gap_data"]
    if gd.empty:
        st.warning("No gap data — try a Race session.")
    else:
        st.plotly_chart(
            build_gap_figure(
                gd, st.session_state["driver_info"], color_map,
                selected_drivers=active_drivers,
                title=f"{st.session_state['title']} — Gap to Leader",
            ),
            use_container_width=True,
        )
        st.caption("Red line = race leader (0 s) · hover for exact gap · gaps from cumulative lap times")

# ── Tab: Driver Duel ──────────────────────────────────────────────────────────
with tab_duel:
    col_d1, col_d2 = st.columns(2)
    d1 = col_d1.selectbox("Driver 1", all_abbrevs, index=0, key="duel_d1")
    d2 = col_d2.selectbox("Driver 2", all_abbrevs,
                           index=min(1, len(all_abbrevs) - 1), key="duel_d2")
    if d1 == d2:
        st.info("Select two different drivers to compare.")
    elif st.session_state["lap_times"].empty:
        st.warning("No lap time data available.")
    else:
        st.plotly_chart(
            build_duel_figure(
                st.session_state["lap_times"],
                st.session_state["driver_info"], color_map,
                d1, d2,
                title=f"{st.session_state['title']} — {d1} vs {d2}",
            ),
            use_container_width=True,
        )
        st.caption(f"Bar below zero → {d1} faster that lap · above zero → {d2} faster")
