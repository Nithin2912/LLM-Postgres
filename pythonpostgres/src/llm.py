import json
from typing import Dict, Any
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from httpx import HTTPError
from openai import OpenAI, APIError, RateLimitError, APITimeoutError
from .config import settings

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM = (
    "You are a precise product catalog normalizer. "
    "Return ONE JSON object ONLY with keys exactly: "
    "brand (string), manufacturer (string), confidence (number in [0,1]). "
    "If manufacturer is unclear, copy brand to manufacturer. No prose."
)

# IMPORTANT: escape { } with double braces {{ }} so .format() only replaces {product_name}
USER_TMPL = (
    'Product name: "{product_name}"\n'
    'Return exactly: {{"brand":"...","manufacturer":"...","confidence":0.0}}'
)

def _normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    brand = (data.get("brand") or "").strip() or None
    manufacturer = (data.get("manufacturer") or "").strip() or None
    if not manufacturer and brand:
        manufacturer = brand
    try:
        confidence = float(data.get("confidence", 0.0) or 0.0)
    except Exception:
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))
    return {"brand": brand, "manufacturer": manufacturer, "confidence": confidence}

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=20),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((HTTPError, APIError, RateLimitError, APITimeoutError)),
    reraise=True,
)
def _raw_call(product_name: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TMPL.format(product_name=product_name)},
        ],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content or ""

def call_llm(product_name: str) -> Dict[str, Any]:
    try:
        raw = _raw_call(product_name)
        data = json.loads(raw)  # clean JSON per test_llm.py
        return _normalize(data)
    except Exception:
        return {"brand": None, "manufacturer": None, "confidence": 0.0}
