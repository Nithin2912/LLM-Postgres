import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(override=True)

def _default_json_path() -> str:
    # brand_map.json in the project root (one level up from src/)
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, "..", "brand_map.json"))

@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "")
    schema: str = os.getenv("SCHEMA", "item_schema_prod")
    table: str = os.getenv("TABLE", "item_master_table")
    product_col: str = os.getenv("PRODUCT_COL", "product_name")
    brand_col: str = os.getenv("BRAND_COL", "brand")
    mfg_col: str = os.getenv("MFG_COL", "manufacturer")
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.60"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "2000"))
    dry_run: bool = os.getenv("DRY_RUN", "true").lower() == "true"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    # Where to store/read the JSON map
    json_map_path: str = os.getenv("JSON_MAP_PATH", _default_json_path())

settings = Settings()
