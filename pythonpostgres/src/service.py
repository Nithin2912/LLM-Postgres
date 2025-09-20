from typing import Dict, Any
import json, os, tempfile

from sqlalchemy import text

from .config import settings
from .logger import get_logger
from .db import engine, fetch_distinct_products, update_one
from .llm import call_llm

log = get_logger()

# ---------------- JSON map helpers ----------------

def _json_path() -> str:
    return settings.json_map_path

def _load_product_map() -> Dict[str, Dict[str, str]]:
    path = _json_path()
    folder = os.path.dirname(path) or "."
    if not os.path.exists(path):
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        log.warning(f"Could not read JSON map {path}: {e}")
        return {}

def _save_product_map(product_map: Dict[str, Dict[str, str]]) -> None:
    """Atomic write; avoids half-written files on Windows."""
    path = _json_path()
    folder = os.path.dirname(path) or "."
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="brand_map_", suffix=".json", dir=folder)
    os.close(fd)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(product_map, f, ensure_ascii=False, indent=2)
        if os.path.exists(path):
            os.replace(tmp, path)
        else:
            os.rename(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass

def _upsert_json_entry(product_map: Dict[str, Dict[str, str]], pn: str, brand: str, mfg: str) -> None:
    product_map[pn] = {"brand": brand, "manufacturer": mfg}

# ---------------- main process ----------------

def process():
    eng = engine()

    # SQLAlchemy 2.x ping
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))

    # Load existing JSON (so we append to it), but we DO NOT read from it for inference.
    product_map = _load_product_map()
    log.info(f"JSON map loaded with {len(product_map)} existing entries at {_json_path()}")

    products = fetch_distinct_products(eng)
    log.info(f"Found {len(products)} distinct product_name needing fill.")

    total_rows = 0

    for i, pn in enumerate(products, start=1):
        # --- LLM FIRST ---
        try:
            r = call_llm(pn)
            brand = (r.get("brand") or "").strip() or None
            # accept either key from the model: "manufacture" or "manufacturer"
            mfg   = (r.get("manufacture") or r.get("manufacturer") or "").strip() or None
            conf  = float(r.get("confidence") or 0.0)
        except Exception as e:
            log.warning(f"LLM error for '{pn}': {e}")
            brand = None
            mfg   = None
            conf  = 0.0

        # Only act if confident enough and we have something to write
        if conf >= settings.confidence_threshold and (brand or mfg):
            # --- JSON FIRST ---
            _upsert_json_entry(product_map, pn, brand or "", mfg or "")
            # save periodically to avoid losing progress (even in dry-run)
            if i % 200 == 0:
                _save_product_map(product_map)

            # --- THEN DB ---
            affected = 0 if settings.dry_run else update_one(eng, pn, brand, mfg)
            total_rows += affected

        if i % 1000 == 0:
            log.info(f"Progress: {i}/{len(products)} (updated rows so far: {total_rows})")

    # final save of JSON map
    _save_product_map(product_map)
    log.info(f"Saved JSON map with {len(product_map)} entries to {_json_path()}")
    log.info(f"Done. Updated rows: {total_rows}. {'(DRY RUN)' if settings.dry_run else ''}")


