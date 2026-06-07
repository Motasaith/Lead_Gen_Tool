import os
import sys
from dotenv import load_dotenv

# Force UTF-8 stdout (fixes Windows charmap errors on unicode chars)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

load_dotenv()

# ---------------------------------------------------------------------------
# LLM — use your Ollama cloud model (minimax-m3:cloud) — no API key needed
# Alternative: "ollama/llama3.3" if you pull a local model
# Or paid: "openai/gpt-4o-mini", "groq/llama-3.3-70b"
# ---------------------------------------------------------------------------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama/minimax-m3:cloud")
LLM_API_KEY = os.getenv("LLM_API_KEY") or None

# Crawl politeness (seconds between requests)
CRAWL_DELAY_MIN = float(os.getenv("CRAWL_DELAY_MIN", 3))
CRAWL_DELAY_MAX = float(os.getenv("CRAWL_DELAY_MAX", 8))

# ---------------------------------------------------------------------------
# YOUR SERVICES — drives targeting across all crawlers
# ---------------------------------------------------------------------------
SERVICES_OFFERED = [
    "frontend web design",
    "full stack web development",
    "react development",
    "next.js development",
    "wordpress development",
]

# Niches to search for clients
TARGET_NICHES = [
    "small business website redesign",
    "restaurant website",
    "law firm website",
    "real estate website",
    "medical practice website",
    "ecommerce website redesign",
    "saas landing page",
    "startup mvp",
    "agency needing frontend dev",
    "woocommerce store",
]

# Locations (priority = English-speaking + high freelance rates)
TARGET_LOCATIONS = [
    "United States", "United Kingdom", "Australia", "Canada",
    "UAE", "Singapore", "New Zealand", "Ireland",
]

# Job-board tech keywords (for hiring-signal crawler)
HIRING_KEYWORDS = [
    "frontend developer", "frontend engineer", "react developer",
    "next.js developer", "full stack developer", "fullstack engineer",
    "wordpress developer", "web developer", "ui engineer",
    "vue developer", "angular developer",
]

# Outdated-tech fingerprints (for outdated-website detector)
OUTDATED_SIGNALS = [
    "jquery-1.", "jquery-2.", "jquery-3.0", "jquery-3.1",  # old jQuery
    "wp-content/themes/twenty",                          # old WP themes
    "powered by .* 201[0-5]",                            # old copyright
    "no https",                                          # no SSL
    "viewport.*not set",                                 # not mobile responsive
    "table-layout",                                      # table-based layout
]

# Max leads per source per run
MAX_LEADS_PER_SOURCE = int(os.getenv("MAX_LEADS_PER_SOURCE", 100))

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Allow override via env var (used by .exe when run from a different directory)
DATA_DIR = os.getenv("LEADBOT_DATA_DIR")
if not DATA_DIR:
    # Default: look for data/ next to the .exe first, then in BASE_DIR
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else None
    candidate = os.path.join(exe_dir, "data") if exe_dir else None
    if exe_dir and os.path.isdir(candidate):
        DATA_DIR = candidate
    else:
        DATA_DIR = os.path.join(BASE_DIR, "data")
SEEN_FILE = os.path.join(DATA_DIR, "seen.json")
JOBS_LOG = os.path.join(DATA_DIR, "jobs.log")

os.makedirs(DATA_DIR, exist_ok=True)
