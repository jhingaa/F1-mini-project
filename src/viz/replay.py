import pandas as pd
import plotly.graph_objects as go
from src.viz.utils import build_color_map, lap_range


def build_replay_figure(
    lap_positions: pd.DataFrame,
    driver_info: pd.DataFrame,
    title: str = "Race Position Replay",
) -> go.Figure:
    color_map = build_color_map(driver_info)
    abbrev_map = dict(zip(driver_info["Driver"], driver_info["Abbreviation"]))
    df = lap_positions.copy()
    df["Abbreviation"] = df["Driver"].map(abbrev_map).fillna(df["Driver"])

    min_lap, max_lap = lap_range(df)
    all_laps = list(range(min_lap, max_lap + 1))

    pivot = df.pivot_table(
        index="LapNumber", columns="Abbreviation", values="Position", aggfunc="first"
    ).reindex(all_laps)
    driver_list = list(pivot.columns)
    n = len(driver_list)
    n_pos = int(df["Position"].max())

    # Ghost traces — static full-race paths, indices 0..n-1
    ghost_traces = []
    for abbr in driver_list:
        color = color_map.get(abbr, "#AAAAAA")
        col_data = pivot[abbr]
        valid_laps = [l for l, y in zip(all_laps, col_data) if pd.notna(y)]
        valid_pos = [int(y) for y in col_data if pd.notna(y)]
        ghost_traces.append(go.Scatter(
            x=valid_laps, y=valid_pos,
            mode="lines",
            line=dict(color=color, width=1),
            opacity=0.12,
            showlegend=False,
            hoverinfo="skip",
            name=f"_g_{abbr}",
        ))

    # Animated line traces — indices n..2n-1
    init_line_traces = []
    for abbr in driver_list:
        color = color_map.get(abbr, "#AAAAAA")
        y0 = pivot.at[min_lap, abbr] if min_lap in pivot.index else None
        init_line_traces.append(go.Scatter(
            x=[min_lap] if pd.notna(y0) else [],
            y=[int(y0)] if pd.notna(y0) else [],
            mode="lines",
            line=dict(color=color, width=2.5),
            showlegend=False,
            hoverinfo="skip",
            name=f"_l_{abbr}",
        ))

    # Animated dot+label traces — indices 2n..3n-1
    init_dot_traces = []
    for abbr in driver_list:
        color = color_map.get(abbr, "#AAAAAA")
        y0 = pivot.at[min_lap, abbr] if min_lap in pivot.index else None
        init_dot_traces.append(go.Scatter(
            x=[min_lap] if pd.notna(y0) else [],
            y=[int(y0)] if pd.notna(y0) else [],
            mode="markers+text",
            marker=dict(size=16, color=color, line=dict(color="white", width=1.5)),
            text=[abbr] if pd.notna(y0) else [],
            textposition="middle right",
            textfont=dict(size=10, color="white"),
            name=abbr,
            showlegend=True,
            hovertemplate=f"<b>{abbr}</b><br>Lap %{{x}}<br>P%{{y}}<extra></extra>",
        ))

    all_init_traces = ghost_traces + init_line_traces + init_dot_traces
    animated_indices = list(range(n, 3 * n))

    def build_frame_data(up_to_lap: int):
        laps_shown = [l for l in all_laps if l <= up_to_lap]
        line_traces, dot_traces = [], []
        for abbr in driver_list:
            vals = [
                (l, int(pivot.at[l, abbr]))
                for l in laps_shown
                if pd.notna(pivot.at[l, abbr])
            ]
            xs = [v[0] for v in vals]
            ys = [v[1] for v in vals]
            line_traces.append(go.Scatter(x=xs, y=ys))
            dot_traces.append(go.Scatter(
                x=[xs[-1]] if xs else [],
                y=[ys[-1]] if ys else [],
                text=[abbr] if xs else [],
            ))
        return line_traces + dot_traces

    frames = [
        go.Frame(data=build_frame_data(lap), traces=animated_indices, name=str(lap))
        for lap in all_laps
    ]

    ytick_vals = list(range(1, n_pos + 1))
    ytick_text = [f"P{p}" for p in ytick_vals]

    fig = go.Figure(
        data=all_init_traces,
        frames=frames,
        layout=go.Layout(
            title=dict(text=title, font=dict(size=20, color="white"), x=0.5),
            xaxis=dict(
                title="Lap",
                range=[min_lap - 0.5, max_lap + 3.5],
                gridcolor="#1e1e3a",
                color="white",
                zeroline=False,
            ),
            yaxis=dict(
                title="Position",
                autorange="reversed",
                tickvals=ytick_vals,
                ticktext=ytick_text,
                gridcolor="#1e1e3a",
                color="white",
                dtick=1,
            ),
            paper_bgcolor="#0d0d1a",
            plot_bgcolor="#0d0d1a",
            font=dict(color="white", family="Arial"),
            legend=dict(
                bgcolor="rgba(26,26,46,0.85)",
                bordercolor="#333",
                borderwidth=1,
                font=dict(size=10),
                itemsizing="constant",
                orientation="v",
                x=1.01,
            ),
            height=660,
            margin=dict(l=70, r=130, t=70, b=110),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                x=0.0, xanchor="left",
                y=-0.14, yanchor="top",
                buttons=[
                    dict(
                        label="▶  Play",
                        method="animate",
                        args=[None, {
                            "frame": {"duration": 450, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 200, "easing": "linear"},
                        }],
                    ),
                    dict(
                        label="⏸  Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}],
                    ),
                ],
                font=dict(color="white", size=13),
                bgcolor="#1a1a2e",
                bordercolor="#e10600",
                borderwidth=2,
            )],
            sliders=[dict(
                active=0,
                steps=[
                    dict(
                        method="animate",
                        args=[[str(lap)], {
                            "mode": "immediate",
                            "frame": {"duration": 0, "redraw": True},
                            "transition": {"duration": 0},
                        }],
                        label=str(lap),
                    )
                    for lap in all_laps
                ],
                x=0.0, len=1.0,
                y=-0.06,
                currentvalue=dict(prefix="Lap: ", font=dict(color="white", size=13)),
                font=dict(color="white", size=10),
                bgcolor="#1a1a2e",
                activebgcolor="#e10600",
                bordercolor="#333",
                pad={"t": 10},
            )],
        ),
    )
    return fig
