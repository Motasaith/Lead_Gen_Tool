"""
dashboard.py — Web dashboard for LeadBot
FastAPI app that runs in the background and provides:
  - Live lead list with filtering
  - "Run pipeline now" button
  - Real-time log streaming via Server-Sent Events
  - Stats dashboard
  - Webhook settings (Discord/Telegram/Slack)
  - System tray icon (Windows) to open dashboard
"""
import os
import sys
import json
import glob
import asyncio
import threading
import subprocess
import webbrowser
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi import FastAPI, HTTPException, Request
import csv
import io
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from config import DATA_DIR
from notifier import Notifier


# ---------------------------------------------------------------------------
# Log streaming (in-memory)
# ---------------------------------------------------------------------------
class LogBuffer:
    def __init__(self, max_lines: int = 500):
        self.lines: List[str] = []
        self.subscribers: List[asyncio.Queue] = []
        self.max = max_lines
        self.lock = threading.Lock()

    def add(self, line: str):
        with self.lock:
            line = line.rstrip()
            self.lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")
            if len(self.lines) > self.max:
                self.lines = self.lines[-self.max:]
            for q in self.subscribers:
                try:
                    q.put_nowait(line)
                except Exception:
                    pass

    def recent(self, n: int = 200) -> List[str]:
        with self.lock:
            return self.lines[-n:]

    async def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        with self.lock:
            self.subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        with self.lock:
            if q in self.subscribers:
                self.subscribers.remove(q)


logs = LogBuffer()


# ---------------------------------------------------------------------------
# Run state
# ---------------------------------------------------------------------------
class RunState:
    def __init__(self):
        self.is_running = False
        self.current_source = ""
        self.last_started: Optional[datetime] = None
        self.last_finished: Optional[datetime] = None
        self.last_error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "is_running": self.is_running,
            "current_source": self.current_source,
            "last_started": self.last_started.isoformat() if self.last_started else None,
            "last_finished": self.last_finished.isoformat() if self.last_finished else None,
            "last_error": self.last_error,
        }


state = RunState()


# ---------------------------------------------------------------------------
# Helper: load all leads
# ---------------------------------------------------------------------------
def load_all_leads() -> List[Dict]:
    leads = []
    for f in glob.glob(os.path.join(DATA_DIR, "leads_*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    leads.extend(data)
        except Exception:
            pass
    leads.sort(key=lambda l: l.get("score", 0) or 0, reverse=True)
    return leads


def load_jobs_log() -> List[str]:
    p = os.path.join(DATA_DIR, "jobs.log")
    if not os.path.exists(p):
        return []
    with open(p, "r", encoding="utf-8") as f:
        return f.readlines()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="LeadBot Dashboard", version="2.0")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the dashboard HTML."""
    html_path = os.path.join(PROJECT_ROOT, "templates", "dashboard.html")
    if not os.path.exists(html_path):
        return HTMLResponse("<h1>LeadBot</h1><p>Dashboard template missing</p>")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/api/leads")
async def api_leads(
    source: Optional[str] = None,
    lead_type: Optional[str] = None,
    min_score: Optional[float] = None,
    has_email: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 200,
):
    leads = load_all_leads()
    if source:
        leads = [l for l in leads if l.get("source") == source]
    if lead_type:
        leads = [l for l in leads if l.get("lead_type") == lead_type]
    if min_score is not None:
        leads = [l for l in leads if (l.get("score", 0) or 0) >= min_score]
    if has_email:
        leads = [l for l in leads if l.get("email")]
    if search:
        s = search.lower()
        leads = [l for l in leads if any(
            s in (str(l.get(k) or "")).lower() for k in ["company_name", "title", "email", "country", "niche"]
        )]
    return {"total": len(leads), "results": leads[:limit]}


@app.get("/api/stats")
async def api_stats():
    leads = load_all_leads()
    by_source = {}
    by_type = {}
    by_country = {}
    score_buckets = {"0-30": 0, "30-60": 0, "60-100": 0}
    for l in leads:
        s = l.get("source", "?")
        by_source[s] = by_source.get(s, 0) + 1
        t = l.get("lead_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        c = l.get("country", "Unknown")
        by_country[c] = by_country.get(c, 0) + 1
        sc = l.get("score", 0) or 0
        if sc < 30:
            score_buckets["0-30"] += 1
        elif sc < 60:
            score_buckets["30-60"] += 1
        else:
            score_buckets["60-100"] += 1

    return {
        "total_leads": len(leads),
        "with_email": sum(1 for l in leads if l.get("email")),
        "with_phone": sum(1 for l in leads if l.get("phone")),
        "by_source": dict(sorted(by_source.items(), key=lambda x: -x[1])),
        "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])),
        "by_country": dict(sorted(by_country.items(), key=lambda x: -x[1])[:10]),
        "score_distribution": score_buckets,
        "run_state": state.to_dict(),
    }


@app.get("/api/status")
async def api_status():
    return state.to_dict()


@app.get("/api/logs")
async def api_logs():
    return {"lines": logs.recent(200)}


@app.get("/api/jobs")
async def api_jobs():
    return {"lines": load_jobs_log()[-50:]}


@app.post("/api/run")
async def api_run():
    """Trigger a pipeline run in background."""
    if state.is_running:
        raise HTTPException(409, "Pipeline already running")
    thread = threading.Thread(target=_run_pipeline_sync, daemon=True)
    thread.start()
    return {"started": True, "message": "Pipeline started"}


@app.get("/api/export/csv")
async def api_export_csv(
    source: Optional[str] = None,
    lead_type: Optional[str] = None,
    min_score: Optional[float] = None,
    has_email: Optional[bool] = None,
):
    """Download all leads (optionally filtered) as a CSV file."""
    leads = load_all_leads()
    if source:
        leads = [l for l in leads if l.get("source") == source]
    if lead_type:
        leads = [l for l in leads if l.get("lead_type") == lead_type]
    if min_score is not None:
        leads = [l for l in leads if (l.get("score", 0) or 0) >= min_score]
    if has_email:
        leads = [l for l in leads if l.get("email")]

    # Collect all unique keys across all leads (for a flat CSV)
    all_keys = set()
    for l in leads:
        all_keys.update(l.keys())
    # Order important fields first
    priority = ["score", "company_name", "title", "email", "phone", "website", "country", "city", "niche", "lead_type", "source", "source_url", "yc_batch", "salary_range", "role_category", "outdated_signals", "outdated_score", "fetched_at"]
    fieldnames = [k for k in priority if k in all_keys] + sorted(k for k in all_keys if k not in priority)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for l in leads:
        # Convert list/dict values to JSON strings for CSV
        row = {}
        for k in fieldnames:
            v = l.get(k)
            if isinstance(v, (list, dict)):
                row[k] = json.dumps(v, ensure_ascii=False)
            else:
                row[k] = v
        writer.writerow(row)

    output.seek(0)
    filename = f"leadbot_leads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/enrich")
async def api_enrich_leads(
    min_score: float = 30,
    limit: int = 20,
    use_llm: bool = False,
):
    """
    Enrich leads with email addresses.
    ⚠️ WARNING: Free tier APIs are LIMITED (25-50 searches/month).
    Use sparingly on your TOP leads only.
    """
    leads = load_all_leads()
    leads = [l for l in leads if (l.get("score", 0) or 0) >= min_score]
    leads = leads[:limit]

    from enricher import EmailEnricher
    enricher = EmailEnricher()
    enriched = enricher.enrich_leads(leads)
    return {
        "results": enriched,
        "stats": {
            "total": len(enriched),
            "found": sum(1 for l in enriched if l.get("enrichment_status") == "found"),
            "guessed": sum(1 for l in enriched if l.get("enrichment_status") == "guessed"),
            "failed": sum(1 for l in enriched if l.get("enrichment_status") in ("failed", "no_domain", "already_had_email")),
        },
    }


@app.post("/api/email_sequence")
async def api_email_sequence(request: Request):
    """
    Generate a 3-email cold outreach sequence for a lead.
    Returns a DRAFT - you should review and personalize before sending.
    """
    body = await request.json()
    lead = body.get("lead", {})
    use_llm = body.get("use_llm", False)
    custom_services = body.get("services")

    from email_writer import generate_sequence, generate_template
    if use_llm:
        result = generate_sequence(lead, custom_services=custom_services)
    else:
        result = generate_template(lead)

    return {
        "lead": lead,
        "sequence": result,
        "warning": "AI-generated draft. Always personalize before sending. Generic AI emails get <2% reply rates vs 3-8% for hand-written ones.",
    }


@app.post("/api/open_data_folder")
async def api_open_data_folder():
    """Open the data folder in the OS file explorer."""
    import subprocess
    if sys.platform == "win32":
        subprocess.Popen(["explorer", DATA_DIR])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", DATA_DIR])
    else:
        subprocess.Popen(["xdg-open", DATA_DIR])
    return {"opened": DATA_DIR}


@app.post("/api/notify")
async def api_notify(min_score: float = 30):
    """Send a notification of all current leads to configured webhooks."""
    leads = load_all_leads()
    notifier = Notifier()
    results = notifier.notify(leads, source="manual")
    return {"results": results, "leads_sent": sum(1 for l in leads if l.get("score", 0) >= min_score)}


# Settings
class Settings(BaseModel):
    discord_webhook: Optional[str] = None
    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    slack_webhook: Optional[str] = None
    generic_webhook: Optional[str] = None
    notify_min_score: Optional[float] = 30


@app.get("/api/settings")
async def api_get_settings():
    return {
        "discord_webhook": os.getenv("DISCORD_WEBHOOK_URL", ""),
        "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
        "slack_webhook": os.getenv("SLACK_WEBHOOK_URL", ""),
        "generic_webhook": os.getenv("GENERIC_WEBHOOK_URL", ""),
        "notify_min_score": float(os.getenv("NOTIFY_MIN_SCORE", "30")),
    }


@app.post("/api/settings")
async def api_save_settings(settings: Settings):
    """Save settings to .env file."""
    env_path = os.path.join(PROJECT_ROOT, ".env")
    # Read existing .env
    existing = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

    # Update with new values (if provided)
    if settings.discord_webhook is not None:
        existing["DISCORD_WEBHOOK_URL"] = settings.discord_webhook
        os.environ["DISCORD_WEBHOOK_URL"] = settings.discord_webhook
    if settings.telegram_token is not None:
        existing["TELEGRAM_BOT_TOKEN"] = settings.telegram_token
        os.environ["TELEGRAM_BOT_TOKEN"] = settings.telegram_token
    if settings.telegram_chat_id is not None:
        existing["TELEGRAM_CHAT_ID"] = settings.telegram_chat_id
        os.environ["TELEGRAM_CHAT_ID"] = settings.telegram_chat_id
    if settings.slack_webhook is not None:
        existing["SLACK_WEBHOOK_URL"] = settings.slack_webhook
        os.environ["SLACK_WEBHOOK_URL"] = settings.slack_webhook
    if settings.generic_webhook is not None:
        existing["GENERIC_WEBHOOK_URL"] = settings.generic_webhook
        os.environ["GENERIC_WEBHOOK_URL"] = settings.generic_webhook
    if settings.notify_min_score is not None:
        existing["NOTIFY_MIN_SCORE"] = str(settings.notify_min_score)
        os.environ["NOTIFY_MIN_SCORE"] = str(settings.notify_min_score)

    # Write back
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# LeadBot environment\n")
        for k, v in existing.items():
            f.write(f"{k}={v}\n")

    return {"saved": True, "path": env_path}


# ---------------------------------------------------------------------------
# Pipeline runner (in thread, captures logs)
# ---------------------------------------------------------------------------
def _run_pipeline_sync():
    """Run main.py in subprocess and stream its output to logs buffer."""
    state.is_running = True
    state.current_source = "all"
    state.last_started = datetime.now()
    state.last_error = None
    logs.add("=== Pipeline started (manual) ===")
    try:
        proc = subprocess.Popen(
            [sys.executable, "-B", "main.py"],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
        )
        for line in iter(proc.stdout.readline, ""):
            if line:
                logs.add(line.rstrip())
        proc.wait()
        if proc.returncode == 0:
            logs.add("=== Pipeline completed successfully ===")
            # Auto-notify on completion
            try:
                leads = load_all_leads()
                notifier = Notifier()
                notifier.notify(leads, source="auto")
            except Exception as e:
                logs.add(f"[Notify] Error: {e}")
        else:
            state.last_error = f"Exit code {proc.returncode}"
            logs.add(f"=== Pipeline failed (exit {proc.returncode}) ===")
    except Exception as e:
        state.last_error = str(e)
        logs.add(f"=== Pipeline error: {e} ===")
    finally:
        state.is_running = False
        state.last_finished = datetime.now()
        state.current_source = ""


# ---------------------------------------------------------------------------
# Server-Sent Events for live log streaming
# ---------------------------------------------------------------------------
@app.get("/api/stream")
async def stream_logs():
    from fastapi.responses import StreamingResponse

    async def event_generator():
        q = await logs.subscribe()
        try:
            # Send recent history first
            for line in logs.recent(50):
                yield f"data: {line}\n\n"
            # Then stream new
            while True:
                try:
                    line = await asyncio.wait_for(q.get(), timeout=30.0)
                    yield f"data: {line}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            logs.unsubscribe(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
os.makedirs(os.path.join(PROJECT_ROOT, "templates"), exist_ok=True)


def run_server(host: str = "127.0.0.1", port: int = 7860):
    """Start the dashboard server."""
    print(f"\n{'='*60}")
    print(f"  LeadBot Dashboard running at: http://{host}:{port}")
    print(f"  Open in browser to control the bot")
    print(f"{'='*60}\n")
    uvicorn.run(app, host=host, port=port, log_level="warning")


def open_browser_then_run(host: str = "127.0.0.1", port: int = 7860):
    """Open the browser, then start the server."""
    import time
    def _open():
        time.sleep(1.5)
        webbrowser.open(f"http://{host}:{port}")
    threading.Thread(target=_open, daemon=True).start()
    run_server(host=host, port=port)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    ap.add_argument("--data-dir", default=None, help="Override data directory (default: ./data)")
    args = ap.parse_args()

    # Override data dir before importing config
    if args.data_dir:
        os.environ["LEADBOT_DATA_DIR"] = args.data_dir

    if args.no_browser:
        run_server(args.host, args.port)
    else:
        open_browser_then_run(args.host, args.port)
