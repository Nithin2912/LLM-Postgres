-- Creates the audit table inside item_schema_prod
CREATE TABLE IF NOT EXISTS item_schema_prod.item_brand_mfg_audit (
    audit_id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    new_brand TEXT,
    new_manufacture TEXT, -- audit column name stays 'new_manufacture'
    source TEXT,
    confidence NUMERIC(5,3),
    affected_rows INTEGER,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Helpful index for quick lookups
CREATE INDEX IF NOT EXISTS ix_item_brand_mfg_audit_pn
ON item_schema_prod.item_brand_mfg_audit (product_name);

-- Optional: index for speeding up search on main table
CREATE INDEX IF NOT EXISTS ix_item_master_missing_brand_mfg
ON item_schema_prod.item_master_table (product_name)
WHERE brand IS NULL OR manufacturer IS NULL;
