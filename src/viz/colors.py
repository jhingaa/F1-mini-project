TEAM_COLORS: dict[str, str] = {
    "Red Bull Racing": "#3671C6",
    "Ferrari": "#E8002D",
    "Mercedes": "#27F4D2",
    "McLaren": "#FF8000",
    "Aston Martin": "#229971",
    "Alpine": "#FF87BC",
    "Williams": "#64C4FF",
    "Racing Bulls": "#6692FF",
    "RB": "#6692FF",
    "Kick Sauber": "#52E252",
    "Sauber": "#52E252",
    "Alfa Romeo": "#C92D4B",
    "AlphaTauri": "#5E8FAA",
    "Toro Rosso": "#469BFF",
    "Force India": "#F596C8",
    "Racing Point": "#F596C8",
    "Renault": "#FFF500",
    "Haas F1 Team": "#B6BABD",
    "Haas": "#B6BABD",
}

COMPOUND_COLORS: dict[str, str] = {
    "SOFT": "#FF3333",
    "MEDIUM": "#FFD700",
    "HARD": "#EBEBEB",
    "INTERMEDIATE": "#39B54A",
    "WET": "#0067FF",
    "UNKNOWN": "#888888",
}

FALLBACK_COLOR = "#AAAAAA"


def team_color(team_name: str) -> str:
    if not team_name:
        return FALLBACK_COLOR
    for key, color in TEAM_COLORS.items():
        if key.lower() in team_name.lower():
            return color
    return FALLBACK_COLOR


def compound_color(compound: str) -> str:
    return COMPOUND_COLORS.get((compound or "UNKNOWN").upper(), COMPOUND_COLORS["UNKNOWN"])
