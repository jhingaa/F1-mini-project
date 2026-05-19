import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fastf1.core import Session


# ── Catmull-Rom helper ─────────────────────────────────────────────────────────

def _catmull_rom(points: np.ndarray, n_per_seg: int = 40) -> np.ndarray:
    """Return a closed smooth curve through *points* using a Catmull-Rom spline."""
    n = len(points)
    result = []
    for i in range(n):
        p0 = points[(i - 1) % n]
        p1 = points[i % n]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n]
        t_vals = np.linspace(0, 1, n_per_seg, endpoint=False)
        t2, t3 = t_vals ** 2, t_vals ** 3
        q = 0.5 * (
            2 * p1
            + (-p0 + p2)[:, None].T * t_vals
            + (2*p0 - 5*p1 + 4*p2 - p3)[:, None].T * t2
            + (-p0 + 3*p1 - 3*p2 + p3)[:, None].T * t3
        )
        result.append(q.T)
    pts = np.vstack(result)
    return np.vstack([pts, pts[0]])   # close the loop


# ── Compact circuit outline (no telemetry needed) ──────────────────────────────

def build_circuit_outline(session: Session) -> go.Figure | None:
    """
    Draw a compact circuit outline from corner positions only.
    Works on any session loaded with telemetry=False.
    Returns None if circuit info is unavailable.
    """
    try:
        ci = session.get_circuit_info()
        corners = ci.corners.sort_values("Distance").reset_index(drop=True)
        if len(corners) < 3:
            return None

        x = corners["X"].values.astype(float)
        y = corners["Y"].values.astype(float)

        # Orient so the circuit is upright
        rad = np.deg2rad(float(getattr(ci, "rotation", 0) or 0))
        if rad:
            x_r = x * np.cos(rad) - y * np.sin(rad)
            y_r = x * np.sin(rad) + y * np.cos(rad)
        else:
            x_r, y_r = x.copy(), y.copy()

        smooth = _catmull_rom(np.column_stack([x_r, y_r]), n_per_seg=50)

        fig = go.Figure()

        # Dark glow / shadow behind the line
        fig.add_trace(go.Scatter(
            x=smooth[:, 0], y=smooth[:, 1],
            mode="lines",
            line=dict(color="#3a3a5c", width=14),
            showlegend=False, hoverinfo="skip",
        ))

        # White track outline
        fig.add_trace(go.Scatter(
            x=smooth[:, 0], y=smooth[:, 1],
            mode="lines",
            line=dict(color="white", width=4),
            showlegend=False, hoverinfo="skip",
        ))

        # Red corner markers with corner numbers
        fig.add_trace(go.Scatter(
            x=x_r.tolist(), y=y_r.tolist(),
            mode="markers+text",
            marker=dict(size=14, color="#e10600",
                        line=dict(color="white", width=1.5)),
            text=[str(int(n)) for n in corners["Number"]],
            textfont=dict(size=6, color="white"),
            textposition="middle center",
            showlegend=False,
            hovertemplate="Turn %{text}<extra></extra>",
        ))

        # Start/finish stripe (gold star near T1)
        fig.add_trace(go.Scatter(
            x=[x_r[0]], y=[y_r[0]],
            mode="markers",
            marker=dict(size=14, color="#ffd700", symbol="star",
                        line=dict(color="white", width=1)),
            showlegend=False,
            hovertemplate="Start / Finish<extra></extra>",
        ))

        fig.update_layout(
            xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
            yaxis=dict(visible=False),
            paper_bgcolor="#0d0d1a",
            plot_bgcolor="#0d0d1a",
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
        )
        return fig
    except Exception:
        return None


def build_track_speed_map(session: Session) -> go.Figure:
    fastest = session.laps.pick_fastest()
    tel = fastest.get_telemetry()

    if tel is None or tel.empty:
        raise ValueError("No telemetry data — reload the session with telemetry enabled.")

    try:
        drv_abbr = session.get_driver(str(fastest["DriverNumber"]))["Abbreviation"]
    except Exception:
        drv_abbr = str(fastest.get("Driver", "?"))

    lap_t = fastest["LapTime"]
    lap_str = (
        f"{int(lap_t.total_seconds() // 60)}:{lap_t.total_seconds() % 60:06.3f}"
        if pd.notna(lap_t) else "N/A"
    )

    x = tel["X"].values.astype(float)
    y = tel["Y"].values.astype(float)
    speed = tel["Speed"].values.astype(float)

    # Apply circuit rotation so the track is upright
    rotation_deg = 0.0
    circuit_info = None
    try:
        circuit_info = session.get_circuit_info()
        rotation_deg = float(circuit_info.rotation)
    except Exception:
        pass

    if rotation_deg:
        rad = np.deg2rad(rotation_deg)
        x_r = x * np.cos(rad) - y * np.sin(rad)
        y_r = x * np.sin(rad) + y * np.cos(rad)
        x, y = x_r, y_r

    # Down-sample to ~2500 pts for snappy rendering
    step = max(1, len(x) // 2500)
    xs, ys, sp = x[::step], y[::step], speed[::step]

    speed_norm = (sp - sp.min()) / max(sp.max() - sp.min(), 1)

    fig = go.Figure()

    # Dark track shadow
    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="markers",
        marker=dict(size=11, color="#1a1a2e"),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Speed heatmap layer
    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="markers",
        marker=dict(
            size=5,
            color=sp,
            colorscale=[
                [0.00, "#0051ff"],
                [0.30, "#00b4d8"],
                [0.60, "#90e0ef"],
                [0.80, "#ffd60a"],
                [1.00, "#e63946"],
            ],
            colorbar=dict(
                title=dict(text="Speed (km/h)", font=dict(color="#cccccc", size=12)),
                tickfont=dict(color="#cccccc"),
                thickness=14,
                len=0.65,
                x=1.01,
            ),
            showscale=True,
            cmin=float(sp.min()),
            cmax=float(sp.max()),
        ),
        hovertemplate="Speed: %{marker.color:.0f} km/h<extra></extra>",
        showlegend=False,
    ))

    # Corner number badges
    if circuit_info is not None:
        try:
            corners = circuit_info.corners
            cx = corners["X"].values.astype(float)
            cy = corners["Y"].values.astype(float)
            if rotation_deg:
                rad = np.deg2rad(rotation_deg)
                cx2 = cx * np.cos(rad) - cy * np.sin(rad)
                cy2 = cx * np.sin(rad) + cy * np.cos(rad)
                cx, cy = cx2, cy2
            fig.add_trace(go.Scatter(
                x=cx.tolist(), y=cy.tolist(),
                mode="markers+text",
                marker=dict(size=16, color="white",
                            line=dict(color="#0d0d1a", width=1.5)),
                text=[str(int(n)) for n in corners["Number"]],
                textfont=dict(size=7, color="#0d0d1a"),
                textposition="middle center",
                showlegend=False,
                hovertemplate="Corner %{text}<extra></extra>",
            ))
        except Exception:
            pass

    fig.update_layout(
        title=dict(
            text=f"⚡ {drv_abbr} — Fastest Lap {lap_str}",
            font=dict(size=17, color="white"),
            x=0.5,
        ),
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        paper_bgcolor="#0d0d1a",
        plot_bgcolor="#0d0d1a",
        font=dict(color="white"),
        height=640,
        margin=dict(l=10, r=100, t=70, b=10),
    )
    return fig
