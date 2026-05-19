import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.viz.colors import compound_color


def build_lap_times_figure(
    lap_times: pd.DataFrame,
    driver_info: pd.DataFrame,
    color_map: dict,
    selected_drivers: list = None,
    title: str = "Lap Times",
) -> go.Figure:
    abbrev_map = dict(zip(driver_info["Driver"], driver_info["Abbreviation"]))
    df = lap_times.copy()
    df["Abbreviation"] = df["Driver"].map(abbrev_map).fillna(df["Driver"])
    if selected_drivers:
        df = df[df["Abbreviation"].isin(selected_drivers)]

    df["LapTimeStr"] = df["LapTimeSeconds"].apply(
        lambda s: f"{int(s // 60)}:{s % 60:06.3f}" if pd.notna(s) else "N/A"
    )
    df["MarkerColor"] = df["Compound"].apply(compound_color)

    fig = go.Figure()
    for abbr in sorted(df["Abbreviation"].unique()):
        drv = df[df["Abbreviation"] == abbr].sort_values("LapNumber")
        color = color_map.get(abbr, "#AAAAAA")
        fig.add_trace(go.Scatter(
            x=drv["LapNumber"],
            y=drv["LapTimeSeconds"],
            mode="lines+markers",
            line=dict(color=color, width=1.5),
            marker=dict(
                size=7,
                color=drv["MarkerColor"].tolist(),
                line=dict(color=color, width=1.2),
            ),
            name=abbr,
            customdata=drv[["LapTimeStr", "Compound"]].values,
            hovertemplate=(
                f"<b>{abbr}</b><br>"
                "Lap %{x}<br>"
                "Time: %{customdata[0]}<br>"
                "Tyre: %{customdata[1]}"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="white"), x=0.5),
        xaxis=dict(title="Lap", gridcolor="#1e1e3a", color="white", zeroline=False),
        yaxis=dict(title="Lap Time (s)", gridcolor="#1e1e3a", color="white", zeroline=False),
        paper_bgcolor="#0d0d1a",
        plot_bgcolor="#0d0d1a",
        font=dict(color="white", family="Arial"),
        legend=dict(bgcolor="rgba(26,26,46,0.85)", bordercolor="#333", borderwidth=1, font=dict(size=10)),
        height=500,
        margin=dict(l=60, r=20, t=60, b=60),
    )
    return fig


def build_duel_figure(
    lap_times: pd.DataFrame,
    driver_info: pd.DataFrame,
    color_map: dict,
    driver1_abbr: str,
    driver2_abbr: str,
    title: str = "Driver Duel",
) -> go.Figure:
    abbrev_map = dict(zip(driver_info["Driver"], driver_info["Abbreviation"]))
    df = lap_times.copy()
    df["Abbreviation"] = df["Driver"].map(abbrev_map).fillna(df["Driver"])
    df["LapTimeStr"] = df["LapTimeSeconds"].apply(
        lambda s: f"{int(s // 60)}:{s % 60:06.3f}" if pd.notna(s) else "N/A"
    )

    d1 = df[df["Abbreviation"] == driver1_abbr].sort_values("LapNumber")
    d2 = df[df["Abbreviation"] == driver2_abbr].sort_values("LapNumber")
    color1 = color_map.get(driver1_abbr, "#FFFFFF")
    color2 = color_map.get(driver2_abbr, "#FF8800")

    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.65, 0.35],
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=["Lap Times", f"Delta  {driver2_abbr} − {driver1_abbr}  (s)"],
    )

    for drv_df, abbr, color in [(d1, driver1_abbr, color1), (d2, driver2_abbr, color2)]:
        fig.add_trace(go.Scatter(
            x=drv_df["LapNumber"],
            y=drv_df["LapTimeSeconds"],
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=6, color=drv_df["Compound"].apply(compound_color).tolist(),
                        line=dict(color=color, width=1.2)),
            name=abbr,
            customdata=drv_df[["LapTimeStr", "Compound"]].values,
            hovertemplate=f"<b>{abbr}</b><br>Lap %{{x}}<br>%{{customdata[0]}}<br>%{{customdata[1]}}<extra></extra>",
        ), row=1, col=1)

    # Delta bars
    common = pd.merge(
        d1[["LapNumber", "LapTimeSeconds"]],
        d2[["LapNumber", "LapTimeSeconds"]],
        on="LapNumber", suffixes=("_d1", "_d2"),
    ).dropna()
    if not common.empty:
        common["Delta"] = common["LapTimeSeconds_d2"] - common["LapTimeSeconds_d1"]
        bar_colors = [color1 if d < 0 else color2 for d in common["Delta"]]
        fig.add_trace(go.Bar(
            x=common["LapNumber"],
            y=common["Delta"],
            marker_color=bar_colors,
            showlegend=False,
            hovertemplate="Lap %{x}<br>Δ %{y:.3f}s<extra></extra>",
        ), row=2, col=1)
        fig.add_hline(y=0, line=dict(color="white", width=1, dash="dot"), row=2, col=1)

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="white"), x=0.5),
        paper_bgcolor="#0d0d1a",
        plot_bgcolor="#0d0d1a",
        font=dict(color="white", family="Arial"),
        legend=dict(bgcolor="rgba(26,26,46,0.85)", bordercolor="#333", borderwidth=1),
        height=600,
        margin=dict(l=60, r=20, t=80, b=60),
    )
    fig.update_xaxes(gridcolor="#1e1e3a", color="white", zeroline=False)
    fig.update_yaxes(gridcolor="#1e1e3a", color="white", zeroline=False)
    return fig
