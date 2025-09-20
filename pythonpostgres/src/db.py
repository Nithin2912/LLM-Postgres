from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import pandas as pd
from .config import settings
from .logger import get_logger

log = get_logger()

def engine() -> Engine:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL not set")
    return create_engine(settings.database_url, pool_pre_ping=True)

def fetch_distinct_products(eng: Engine):
    # pulls distinct product names with missing brand/manufacturer
    q = text(f"""
        SELECT DISTINCT {settings.product_col} AS pn
        FROM {settings.schema}.{settings.table}
        WHERE ({settings.brand_col} IS NULL OR {settings.mfg_col} IS NULL)
          AND {settings.product_col} IS NOT NULL
        ORDER BY pn
    """)
    return pd.read_sql(q, eng)["pn"].dropna().astype(str).tolist()

def update_one(eng: Engine, product_name: str, brand: Optional[str], mfg: Optional[str]) -> int:
    # only fills NULLs; never overwrites existing non-NULL values
    if not (brand or mfg):
        return 0
    with eng.begin() as conn:
        if settings.dry_run:
            ct = conn.execute(text(f"""
                SELECT COUNT(*)
                FROM {settings.schema}.{settings.table}
                WHERE {settings.product_col} = :pn
                  AND ({settings.brand_col} IS NULL OR {settings.mfg_col} IS NULL)
            """), {"pn": product_name}).scalar_one()
            return int(ct)
        res = conn.execute(text(f"""
            UPDATE {settings.schema}.{settings.table}
            SET {settings.brand_col} = COALESCE({settings.brand_col}, :brand),
                {settings.mfg_col}  = COALESCE({settings.mfg_col},  :mfg)
            WHERE {settings.product_col} = :pn
              AND ({settings.brand_col} IS NULL OR {settings.mfg_col} IS NULL)
        """), {"brand": brand, "mfg": mfg, "pn": product_name})
        return res.rowcount or 0

