import os
import json
from utils.logger import logger

TESTSET_FILE = "evaluation/testset.json"

def save_test_entry(entry: dict):
    try:
        if not os.path.exists("evaluation"):
            os.makedirs("evaluation")
        if not os.path.exists(TESTSET_FILE):
            with open(TESTSET_FILE, "w") as f:
                json.dump([entry], f, indent=2)
        else:
            with open(TESTSET_FILE, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
        logger.info(f"Test entry saved for repo: {entry['repo']}")
    except Exception as e:
        logger.error(f"Failed to save test entry: {e}", exc_info=True)

def load_test_entry(repo: str) -> dict:
    try:
        with open("evaluation/testset.json", "r", encoding="utf-8") as f:
            all_tests = json.load(f)
        for entry in all_tests:
            if entry["repo"] == repo:
                return entry
        return None
    except Exception as e:
        logger.error(f"Failed to load test entry: {e}", exc_info=True)
        return None

