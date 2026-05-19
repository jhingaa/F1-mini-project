import os
import fastf1

# Always resolve the cache directory relative to the project root (two levels up from this file)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CACHE_DIR = os.path.join(_PROJECT_ROOT, "cache")
_cache_enabled = False


def setup_cache() -> None:
    global _cache_enabled
    if _cache_enabled:
        return
    os.makedirs(_CACHE_DIR, exist_ok=True)
    fastf1.Cache.enable_cache(_CACHE_DIR)
    _cache_enabled = True
