from functools import lru_cache
import requests

CIRCUIT_FLAGS = {
    "Bahrain": "🇧🇭", "Saudi Arabia": "🇸🇦", "Australia": "🇦🇺",
    "Japan": "🇯🇵", "China": "🇨🇳", "Miami": "🇺🇸",
    "Emilia Romagna": "🇮🇹", "Monaco": "🇲🇨", "Canada": "🇨🇦",
    "Spain": "🇪🇸", "Austria": "🇦🇹", "Great Britain": "🇬🇧",
    "Hungary": "🇭🇺", "Belgium": "🇧🇪", "Netherlands": "🇳🇱",
    "Italy": "🇮🇹", "Azerbaijan": "🇦🇿", "Singapore": "🇸🇬",
    "United States": "🇺🇸", "Mexico City": "🇲🇽", "São Paulo": "🇧🇷",
    "Las Vegas": "🇺🇸", "Qatar": "🇶🇦", "Abu Dhabi": "🇦🇪",
}

CIRCUIT_NAMES = {
    "Bahrain": "Bahrain International Circuit",
    "Saudi Arabia": "Jeddah Corniche Circuit",
    "Australia": "Albert Park Circuit",
    "Japan": "Suzuka International Racing Course",
    "China": "Shanghai International Circuit",
    "Miami": "Miami International Autodrome",
    "Emilia Romagna": "Autodromo Enzo e Dino Ferrari",
    "Monaco": "Circuit de Monaco",
    "Canada": "Circuit Gilles Villeneuve",
    "Spain": "Circuit de Barcelona-Catalunya",
    "Austria": "Red Bull Ring",
    "Great Britain": "Silverstone Circuit",
    "Hungary": "Hungaroring",
    "Belgium": "Circuit de Spa-Francorchamps",
    "Netherlands": "Circuit Zandvoort",
    "Italy": "Autodromo Nazionale di Monza",
    "Azerbaijan": "Baku City Circuit",
    "Singapore": "Marina Bay Street Circuit",
    "United States": "Circuit of the Americas",
    "Mexico City": "Autódromo Hermanos Rodríguez",
    "São Paulo": "Autódromo José Carlos Pace",
    "Las Vegas": "Las Vegas Strip Circuit",
    "Qatar": "Lusail International Circuit",
    "Abu Dhabi": "Yas Marina Circuit",
}

CIRCUIT_WIKI = {
    "Bahrain": "Bahrain_International_Circuit",
    "Saudi Arabia": "Jeddah_Street_Circuit",
    "Australia": "Albert_Park_Circuit",
    "Japan": "Suzuka_International_Racing_Course",
    "China": "Shanghai_International_Circuit",
    "Miami": "Miami_International_Autodrome",
    "Emilia Romagna": "Autodromo_Enzo_e_Dino_Ferrari",
    "Monaco": "Circuit_de_Monaco",
    "Canada": "Circuit_Gilles_Villeneuve",
    "Spain": "Circuit_de_Barcelona-Catalunya",
    "Austria": "Red_Bull_Ring",
    "Great Britain": "Silverstone_Circuit",
    "Hungary": "Hungaroring",
    "Belgium": "Circuit_de_Spa-Francorchamps",
    "Netherlands": "Circuit_Zandvoort",
    "Italy": "Autodromo_Nazionale_Monza",
    "Azerbaijan": "Baku_City_Circuit",
    "Singapore": "Marina_Bay_Street_Circuit",
    "United States": "Circuit_of_the_Americas",
    "Mexico City": "Autodromo_Hermanos_Rodriguez",
    "São Paulo": "Autodromo_Jose_Carlos_Pace",
    "Las Vegas": "Las_Vegas_Strip_Circuit",
    "Qatar": "Lusail_International_Circuit",
    "Abu Dhabi": "Yas_Marina_Circuit",
}

_F1CDN = (
    "https://media.formula1.com/image/upload/c_fit,h_704/q_auto/v1740000001"
    "/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/"
)

CIRCUIT_LAYOUT_IMAGES = {
    "Bahrain":        _F1CDN + "Bahrain_Circuit.webp",
    "Saudi Arabia":   _F1CDN + "Saudi_Arabia_Circuit.webp",
    "Australia":      _F1CDN + "Australia_Circuit.webp",
    "Japan":          _F1CDN + "Japan_Circuit.webp",
    "China":          _F1CDN + "China_Circuit.png",
    "Miami":          _F1CDN + "Miami_Circuit.webp",
    "Emilia Romagna": _F1CDN + "Emilia_Romagna_Circuit.webp",
    "Monaco":         _F1CDN + "Monaco_Circuit.webp",
    "Canada":         _F1CDN + "Canada_Circuit.webp",
    "Spain":          _F1CDN + "Spain_Circuit.webp",
    "Austria":        _F1CDN + "Austria_Circuit.webp",
    "Great Britain":  _F1CDN + "Great_Britain_Circuit.webp",
    "Hungary":        _F1CDN + "Hungary_Circuit.webp",
    "Belgium":        _F1CDN + "Belgium_Circuit.webp",
    "Netherlands":    _F1CDN + "Netherlands_Circuit.webp",
    "Italy":          _F1CDN + "Italy_Circuit.webp",
    "Azerbaijan":     _F1CDN + "Baku_Circuit.webp",
    "Singapore":      _F1CDN + "Singapore_Circuit.webp",
    "United States":  _F1CDN + "USA_Circuit.webp",
    "Mexico City":    _F1CDN + "Mexico_Circuit.webp",
    "São Paulo":      _F1CDN + "Brazil_Circuit.webp",
    "Las Vegas":      _F1CDN + "Las_Vegas_Circuit.webp",
    "Qatar":          _F1CDN + "Qatar_Circuit.webp",
    "Abu Dhabi":      _F1CDN + "Abu_Dhabi_Circuit.png",
}


@lru_cache(maxsize=32)
def get_circuit_image_url(gp_name: str) -> str | None:
    wiki_page = CIRCUIT_WIKI.get(gp_name)
    if not wiki_page:
        return None
    try:
        resp = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_page}",
            headers={"User-Agent": "F1RaceReplay/1.0 (open-source educational project)"},
            timeout=6,
        )
        if resp.status_code == 200:
            data = resp.json()
            img = data.get("originalimage") or data.get("thumbnail")
            if img:
                return img["source"]
    except Exception:
        pass
    return None
