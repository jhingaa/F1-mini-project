import fastf1
from fastf1.core import Session
from src.data.cache_manager import setup_cache


def load_session(year: int, gp: str, session_type: str = "R") -> Session:
    setup_cache()
    session = fastf1.get_session(year, gp, session_type)
    session.load(telemetry=False, weather=False, messages=False)
    return session


def load_session_with_telemetry(year: int, gp: str, session_type: str = "R") -> Session:
    setup_cache()
    session = fastf1.get_session(year, gp, session_type)
    session.load(telemetry=True, weather=False, messages=False)
    return session
