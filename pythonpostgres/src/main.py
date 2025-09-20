
import argparse
from src.config import settings as default_settings
from src.logger import get_logger
import src.service as service

log = get_logger()

def parse_args():
    p = argparse.ArgumentParser(description="Fill missing brand/manufacture from product_name.")
    p.add_argument("--dry-run", type=bool, default=default_settings.dry_run, help="If true, no DB writes.")
    p.add_argument("--batch-size", type=int, default=default_settings.batch_size, help="(kept for compatibility; single-pass here)")
    p.add_argument("--threshold", type=float, default=default_settings.confidence_threshold, help="Confidence threshold 0..1")
    return p.parse_args()

def main():
    args = parse_args()
    from .config import settings
    object.__setattr__(settings, "dry_run", args.dry_run)
    object.__setattr__(settings, "confidence_threshold", args.threshold)
    log.info(f"Starting (dry_run={settings.dry_run}, threshold={settings.confidence_threshold})")
    service.process()

if __name__ == "__main__":
    main()
