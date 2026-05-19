import pandas as pd
import plotly.graph_objects as go


def build_gap_figure(
    gap_data: pd.DataFrame,
    driver_info: pd.DataFrame,
    color_map: dict,
    selected_drivers: list = None,
    title: str = "Gap to Leader",
) -> go.Figure:
    abbrev_map = dict(zip(driver_info["Driver"], driver_info["Abbreviation"]))
    df = gap_data.copy()
    df["Abbreviation"] = df["Driver"].map(abbrev_map).fillna(df["Driver"])
    if selected_drivers:
        df = df[df["Abbreviation"].isin(selected_drivers)]

    fig = go.Figure()
    for abbr in sorted(df["Abbreviation"].unique()):
        drv = df[df["Abbreviation"] == abbr].sort_values("LapNumber")
        color = color_map.get(abbr, "#AAAAAA")
        fig.add_trace(go.Scatter(
            x=drv["LapNumber"],
            y=drv["GapToLeader"],
            mode="lines",
            line=dict(color=color, width=2),
            name=abbr,
            hovertemplate=(
                f"<b>{abbr}</b><br>"
                "Lap %{x}<br>"
                "Gap: +%{y:.2f}s"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="white"), x=0.5),
        xaxis=dict(title="Lap", gridcolor="#1e1e3a", color="white", zeroline=False),
        yaxis=dict(
            title="Gap to Leader (s)",
            gridcolor="#1e1e3a",
            color="white",
            zeroline=True,
            zerolinecolor="#e10600",
            zerolinewidth=2,
        ),
        paper_bgcolor="#0d0d1a",
        plot_bgcolor="#0d0d1a",
        font=dict(color="white", family="Arial"),
        legend=dict(bgcolor="rgba(26,26,46,0.85)", bordercolor="#333", borderwidth=1, font=dict(size=10)),
        height=500,
        margin=dict(l=60, r=20, t=60, b=60),
    )
    return fig
