import csv
import json
import os
from datetime import datetime
from typing import List, Dict
from config import DATA_DIR


def timestamp_slug() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d_%H%M")


def write_leads(leads: List[Dict], source: str) -> str:
    """Write leads to timestamped JSON + CSV. Returns the JSON file path."""
    slug = timestamp_slug()
    json_path = os.path.join(DATA_DIR, f"leads_{source}_{slug}.json")
    csv_path = os.path.join(DATA_DIR, f"leads_{source}_{slug}.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)

    if leads:
        all_keys = set()
        for lead in leads:
            all_keys.update(lead.keys())
        fieldnames = sorted(all_keys)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(leads)

    return json_path


def append_job_log(source: str, status: str, leads_found: int, error: str = ""):
    line = f"{datetime.utcnow().isoformat()} | {source} | {status} | leads={leads_found}"
    if error:
        line += f" | error={error[:200]}"
    with open(JOBS_LOG := os.path.join(DATA_DIR, "jobs.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")
