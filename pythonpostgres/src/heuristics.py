import re
from typing import Optional, Tuple

# Extend this map to normalize known brand -> manufacturer
CANONICAL_MAP = {
    # "dove": "Unilever",
    # "oreo": "Mondelez International",
}

BRAND_HINTS = [
    r"^\s*([A-Za-z0-9&'’\-\. ]{2,30})\s+[-–|]\s+",
    r"^\s*by\s+([A-Za-z0-9&'’\-\. ]{2,40})\b",
    r"\bbrand:\s*([A-Za-z0-9&'’\-\. ]{2,40})\b",
]

def clean(s: Optional[str]) -> Optional[str]:
    if not s:
        return s
    return re.sub(r"\s+", " ", s).strip()

def try_heuristics(product_name: str) -> Tuple[Optional[str], Optional[str], float]:
    pn = (product_name or "").strip()
    if not pn:
        return None, None, 0.0
    for pat in BRAND_HINTS:
        m = re.search(pat, pn, flags=re.IGNORECASE)
        if m:
            guess = clean(m.group(1))
            if guess and 2 <= len(guess) <= 40:
                brand = guess
                manufacture = CANONICAL_MAP.get(brand.lower(), brand)
                return brand, manufacture, 0.60
    m = re.match(r"^\s*([A-Za-z0-9&'’\-\.]{2,30})\b", pn)
    if m:
        token = m.group(1)
        generic = {"premium","original","classic","new","pack","combo","assorted"}
        if token.lower() not in generic:
            brand = token
            manufacture = CANONICAL_MAP.get(brand.lower(), brand)
            return brand, manufacture, 0.45
    return None, None, 0.0
