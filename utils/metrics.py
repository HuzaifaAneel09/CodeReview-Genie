import json
import os
from datetime import datetime
from utils.logger import logger

METRICS_FILE = "metrics.jsonl"

def log_metrics(data: dict):
    try:
        data["timestamp"] = datetime.utcnow().isoformat()
        with open("metrics.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2) + ",\n")
        logger.info("Metrics logged successfully.")
    except Exception as e:
        logger.error(f"Failed to log metrics: {e}", exc_info=True)

