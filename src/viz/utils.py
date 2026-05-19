import pandas as pd
from src.viz.colors import team_color


def build_color_map(driver_info: pd.DataFrame) -> dict[str, str]:
    return {
        row["Abbreviation"]: team_color(row["TeamName"])
        for _, row in driver_info.iterrows()
    }


def lap_range(lap_positions: pd.DataFrame) -> tuple[int, int]:
    if lap_positions.empty:
        raise ValueError("No position data found for this session.")
    col = pd.to_numeric(lap_positions["LapNumber"], errors="coerce").dropna()
    if col.empty:
        raise ValueError("LapNumber column contains no valid data.")
    return int(col.min()), int(col.max())


def format_laptime(seconds: float) -> str:
    if pd.isna(seconds):
        return "N/A"
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins}:{secs:06.3f}"
