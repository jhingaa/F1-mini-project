import pandas as pd
from fastf1.core import Session


def get_lap_positions(session: Session) -> pd.DataFrame:
    laps = session.laps[["Driver", "LapNumber", "Position", "LapTime", "Team"]].copy()
    laps["LapNumber"] = pd.to_numeric(laps["LapNumber"], errors="coerce")
    laps["Position"] = pd.to_numeric(laps["Position"], errors="coerce")
    laps = laps.dropna(subset=["Position", "LapNumber"])
    laps["LapNumber"] = laps["LapNumber"].astype(int)
    laps["Position"] = laps["Position"].astype(int)
    laps = laps.sort_values(["LapNumber", "Position"]).reset_index(drop=True)
    return laps


def get_driver_info(session: Session) -> pd.DataFrame:
    rows = []
    for drv in session.drivers:
        info = session.get_driver(drv)
        rows.append({
            "Driver": drv,
            "Abbreviation": info.get("Abbreviation", drv),
            "FullName": info.get("FullName", ""),
            "TeamName": info.get("TeamName", ""),
        })
    return pd.DataFrame(rows)


def get_lap_times(session: Session) -> pd.DataFrame:
    available = session.laps.columns.tolist()
    cols = [c for c in ["Driver", "LapNumber", "LapTime", "Compound", "IsAccurate"] if c in available]
    laps = session.laps[cols].copy()
    laps["LapNumber"] = pd.to_numeric(laps["LapNumber"], errors="coerce")
    laps = laps.dropna(subset=["LapNumber", "LapTime"])
    laps["LapNumber"] = laps["LapNumber"].astype(int)
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
    if "IsAccurate" in laps.columns:
        laps = laps[laps["IsAccurate"] == True]
    median_t = laps["LapTimeSeconds"].median()
    if not pd.isna(median_t):
        laps = laps[laps["LapTimeSeconds"].between(median_t * 0.85, median_t * 2.2)]
    laps["Compound"] = laps["Compound"].fillna("UNKNOWN") if "Compound" in laps.columns else "UNKNOWN"
    return laps.sort_values(["Driver", "LapNumber"]).reset_index(drop=True)


def get_session_results(session: Session) -> pd.DataFrame:
    try:
        cols = [c for c in ["Abbreviation", "TeamName", "Position", "Time", "Status", "Points", "GridPosition"]
                if c in session.results.columns]
        results = session.results[cols].copy()
        results["Position"] = pd.to_numeric(results["Position"], errors="coerce")
        return results.dropna(subset=["Position"]).sort_values("Position").reset_index(drop=True)
    except Exception:
        return pd.DataFrame()


def get_fastest_lap_info(session: Session) -> dict:
    try:
        fastest = session.laps.pick_fastest()
        info = session.get_driver(str(fastest["DriverNumber"]))
        t = fastest["LapTime"].total_seconds()
        return {
            "driver": info.get("Abbreviation", "?"),
            "team": info.get("TeamName", ""),
            "time": f"{int(t // 60)}:{t % 60:06.3f}",
            "lap": int(fastest["LapNumber"]),
        }
    except Exception:
        return {}


def get_gap_to_leader(session: Session) -> pd.DataFrame:
    laps = session.laps[["Driver", "LapNumber", "LapTime"]].copy()
    laps["LapNumber"] = pd.to_numeric(laps["LapNumber"], errors="coerce")
    laps = laps.dropna(subset=["LapNumber", "LapTime"])
    laps["LapNumber"] = laps["LapNumber"].astype(int)
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
    median_t = laps["LapTimeSeconds"].median()
    if not pd.isna(median_t):
        laps = laps[laps["LapTimeSeconds"] < median_t * 3.0]
    laps = laps.sort_values(["Driver", "LapNumber"])
    laps["CumTime"] = laps.groupby("Driver")["LapTimeSeconds"].cumsum()
    min_cum = laps.groupby("LapNumber")["CumTime"].min().rename("LeaderCumTime")
    laps = laps.join(min_cum, on="LapNumber")
    laps["GapToLeader"] = (laps["CumTime"] - laps["LeaderCumTime"]).clip(lower=0)
    return laps.reset_index(drop=True)
