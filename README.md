# 🕷️ LeadBot — AI Lead Generation Pipeline for Web Designers & Developers

> A 24/7 autonomous lead generator that finds **customers for your web design, full-stack dev, and WordPress services**. Built with [Crawl4AI](https://github.com/unclecode/crawl4ai) (the #1 open-source LLM-friendly web crawler, 68K+ stars). Comes with a **web dashboard**, **system tray app**, **standalone .exe**, **Discord/Telegram/Slack notifications**, **email enrichment**, and **AI-drafted cold email sequences** — all for $0/month.

---

## 📖 Table of Contents

1. [What is LeadBot?](#1-what-is-leadbot)
2. [Why LeadBot Exists (and Why You Might Not Need It)](#2-why-leadbot-exists-and-why-you-might-not-need-it)
3. [What It Finds](#3-what-it-finds)
4. [Key Features](#4-key-features)
5. [How It Works (Architecture)](#5-how-it-works-architecture)
6. [The 7 Lead Sources Explained](#6-the-7-lead-sources-explained)
7. [Installation (3 Ways)](#7-installation-3-ways)
8. [Usage Guide](#8-usage-guide)
9. [Email Enrichment & Cold Outreach](#9-email-enrichment--cold-outreach)
10. [Notifications Setup](#10-notifications-setup)
11. [Build a Standalone .exe](#11-build-a-standalone-exe)
12. [Project Structure](#12-project-structure)
13. [Costs & API Limits](#13-costs--api-limits)
14. [Configuration Reference](#14-configuration-reference)
15. [Troubleshooting](#15-troubleshooting)
16. [FAQ](#16-faq)
17. [Why Open Source + Privacy](#17-why-open-source--privacy)
18. [Roadmap & Limitations](#18-roadmap--limitations)
19. [Honest Take: How to Actually Get Clients](#19-honest-take-how-to-actually-get-clients)
20. [License & Credits](#20-license--credits)

---

## 1. What is LeadBot?

**LeadBot** is a Python-based autonomous system that crawls 7+ sources around the clock to find businesses and individuals who might need your web services. It uses AI (via your local Ollama or any LLM) to extract structured lead data — company name, role they're hiring for, location, contact info — and writes everything to JSON/CSV files on your computer. You can then view leads in a beautiful web dashboard, get Discord/Telegram/Slack notifications, enrich missing emails, and even draft personalized cold email sequences with AI.

### Who is this for?

| ✅ Perfect for | ❌ Probably not for |
|---|---|
| Freelance web designers | People who already get clients through referrals |
| Full-stack devs offering React/Next.js/Node services | People looking for B2C consumer data |
| WordPress developers | Anyone who hates writing 5-line config tweaks |
| Small agencies doing client work | People who want a "magic button" — this is a tool, not a service |
| Solo founders building lead-gen systems | |
| **People who want to learn** crawlers + LLM extraction | |
| **People who already have** 1+ client and want to scale | |

---

## 2. Why LeadBot Exists (and Why You Might Not Need It)

### The problem

If you're a freelance web designer or full-stack dev, you know the **#1 challenge isn't building websites** — it's **finding people who want to pay you to build websites**.

The traditional solutions:

- **Job boards (Upwork, Fiverr)** — race to the bottom, $5/hour competition
- **Cold outreach (LinkedIn, email)** — works but takes 5-10 hours/week
- **Content marketing (Twitter, blog, YouTube)** — works but takes 3-6 months to build audience
- **Paid lead lists (Apollo, ZoomInfo)** — $100-500/month
- **Agencies (referrals)** — slow, dependent on luck

### Why most "AI lead gen" tools fail

Most commercial tools in this space are:
1. **Overpriced** — $99-499/month for what's essentially a scraper
2. **Black boxes** — you don't know what they're doing with your data
3. **Locked in** — your leads are in their database, not yours
4. **Limited sources** — just LinkedIn or just Google Maps, no diversity

### Why LeadBot is different

1. **$0/month** — uses free public APIs and your local Ollama LLM
2. **Open source** — you see every line of code, modify anything
3. **Your data stays on your machine** — JSON/CSV files in your `data/` folder
4. **7+ diverse sources** — Y Combinator, Remotive, Arbeitnow, Bark, GoodFirms, GitHub, Bing/DDG
5. **File-based, not database** — no PostgreSQL, no Redis, no Docker, no API keys for the crawler itself

### ⚠️ Honest take: do you actually need this?

**Read this before installing:**

1. **Have you validated your offer?** If you can't articulate "I help [specific person] do [specific outcome] better than [alternative]" in one sentence, LeadBot won't help you. The bottleneck is your offer, not your lead source.

2. **Have you emailed 10 prospects manually this month?** If not, automate later. The hard part of cold outreach isn't finding emails — it's writing the email, dealing with rejection, and iterating on your message.

3. **Do you have time to personalize AI-generated emails?** AI cold emails get 0.5-2% reply rates. Hand-written ones get 3-8%. The difference: specific details only you know. LeadBot includes email generation, but you'll spend 5-10 min per email personalizing.

**If you said "no" to any of the above:** close this README, go find 1 client through Twitter/LinkedIn/Upwork first. Come back when you have signal.

**If you said "yes" to all 3:** LeadBot will save you 5-10 hours/week of manual lead sourcing.

---

## 3. What It Finds

LeadBot finds 5 types of leads, each with different value for your freelance business:

| # | Lead type | Where | Why it's a lead | Avg lead score |
|---|---|---|---|---|
| 1 | 💼 **Hiring signals** (companies posting jobs) | Y Combinator, Remotive, Arbeitnow, Jobicy, 4dayweek | They have **budget for dev work right now** — they're literally spending $150-200K/year on a dev | 50-70 |
| 2 | 🎯 **Service requests** (people asking for help) | Bark.com | **Highest intent** — they're saying "I need a website" and looking for someone to do it | 70-90 (when email is captured) |
| 3 | 🔧 **Outdated sites** (businesses with bad websites) | Bing/DDG search + Playwright | **Clear pain point** — they have a site, but it loads slow, no HTTPS, not mobile responsive. Easy pitch for redesign. | 60-80 |
| 4 | 🏢 **Agencies** (other dev agencies) | GoodFirms.co | **Partnerships** — they may have overflow work they subcontract to you | 40-60 |
| 5 | 🎨 **Designers** (individuals) | Dribbble, Awwwards, Behance | **Community intel + partnerships** — find designers to refer work to you or vice versa | 30-50 |
| 6 | 👤 **Devs** (people with public emails) | GitHub profile search | **Indie hackers, founders** with public bios — they might need a frontend dev or know someone who does | 40-60 |

**Real example leads LeadBot found in the test runs:**

| Company | Title | Source | Score | Salary range |
|---|---|---|---|---|
| Method Financial | Senior Software Engineer | YC (S19) | 60 | $185-225K |
| LiveFlow | Senior Full Stack Engineer | YC (W21) | 60 | $100-200K |
| Palla | Senior Full-Stack Engineer, Payments | YC (S21) | 60 | $80-200K |
| Lemon.io | Senior Full-stack React Developer | Remotive | 70 | — |
| A.Team | Senior Independent Software Developer | Remotive | 60 | — |
| BlueCargo | Senior/Staff Backend Engineer | Remotive | 60 | $160-220K |
| Encord | Full-Stack Engineer | YC (W21) | 55 | — |
| Glimpse | Software Engineer | YC (S20) | 55 | $130-200K |
| Runway | Full Stack Engineer | YC (W21) | 55 | $80-150K |
| OneChronos | Software Engineer, Data Platform | YC (S16) | 55 | $115-200K |

**The Y Combinator angle is the gold mine** — these are vetted, funded startups that have already raised $1-50M. They have actual budgets and are actively hiring.

---

## 4. Key Features

### 🤖 Autonomous 24/7 crawling
- Runs every 6 hours automatically (configurable)
- 7+ lead sources, each with smart extraction logic
- Anti-bot detection: user-agent rotation, browser stealth mode, magic mode
- Graceful failure handling — if one source blocks you, the others continue

### 🖥️ Web Dashboard (`dashboard.py`)
- Live lead list with **search, filter by source, lead type, score, country**
- **"Run Pipeline Now"** button — triggers a full crawl from the browser
- **Real-time log streaming** via Server-Sent Events
- **Live stats** — total leads, by source, by type, score distribution
- **CSV export** (all leads or filtered subset)
- **Lead detail modal** — click any lead to see all data + enrich + draft email

### 🖱️ System Tray App (`launcher.py`)
- **Spider 🕷️ icon in your Windows taskbar**
- Right-click menu: Open Dashboard / Run Now / Test Notification / Open Data Folder / Quit
- Double-click icon → opens dashboard in browser
- Auto-start on Windows login (optional via `shell:startup`)

### 📦 Standalone .exe (`dist/LeadBotDashboard.exe`)
- **25 MB single file**, no Python required
- Works on any Windows 10/11 machine
- One-click build with `build.bat`

### 🔔 Notifications (`notifier.py`)
- **Discord** (easiest, 2 min setup)
- **Telegram** (5 min, via @BotFather)
- **Slack** (3 min, via Incoming Webhooks)
- **Generic webhook** (Make.com, n8n, Zapier, custom)
- Auto-sent at end of every pipeline run, with rich embeds

### 📧 Email Enrichment (`enricher.py`)
- **Apollo.io** (10K free credits/month — best for personal emails)
- **Hunter.io** (25 free searches/month)
- **Snov.io** (50 free credits/month)
- **Pattern guessing** (free, no API — `hello@`, `careers@`, etc.)
- Smart fallback: skips leads with no real domain (job board URLs)
- Returns confidence score so you know what to trust

### ✉️ Email Sequence Generator (`email_writer.py`)
- **3-email cold outreach sequence** per lead
- Two modes: **template** (no LLM needed) or **LLM** (uses your Ollama)
- Anti-pattern protections built in:
  - ❌ No "I noticed we have a mutual connection" (lie detector)
  - ❌ No "I saw your job posting" as opener
  - ❌ No fake urgency
  - ✅ Always under 100 words
  - ✅ Always returns explicit "personalization notes"

### 📊 Smart Scoring (`pipeline/scorer.py`)
- Different scoring per lead type:
  - Service requests: 30 (base value) + email bonus + phone bonus
  - Hiring signals: 40 (base) + role-type bonus
  - Outdated sites: 80% of detection score + email bonus
  - Agencies: 20 base + contact bonus
- Filters out junk emails (`noreply@`, `example.com`, etc.)
- Normalizes phone numbers, website URLs

### 🔁 Deduplication (`pipeline/dedup.py`)
- File-based (in-memory + JSON snapshot)
- Dedupes by email, domain, company name, source URL
- Smart per-type: hiring leads use company_name (not job board URL)
- 30-day TTL (you can re-crawl after that)

### 🗓️ Scheduler (`scheduler.py`)
- APScheduler-based, runs every 6h
- Tracks per-source job status
- Logs to `data/jobs.log`

---

## 5. How It Works (Architecture)

```
┌────────────────────────────────────────────────────────────────────┐
│                       LEADBOT PRO SYSTEM                           │
├─────────────┬─────────────┬─────────────┬──────────────────────────┤
│  SCHEDULER  │   CRAWLER   │ AI EXTRACTOR│      FILE STORAGE        │
│             │             │             │                          │
│ APScheduler │ Crawl4AI    │ Ollama      │ data/leads_*.json        │
│ (cron-like) │ (Playwright │  OR         │ data/leads_*.csv         │
│             │  + async)   │ Groq API    │ data/seen.json           │
│             │             │  (1 key)    │ data/jobs.log            │
│             │             │             │                          │
│ Every 6h    │ 7 sources:  │ Schema      │ Local disk               │
│             │ YC, Remotive│ extraction  │ No DB needed             │
│             │ Arbeitnow,  │ per lead    │                          │
│             │ Bark, etc.  │             │                          │
└─────────────┴─────────────┴─────────────┴──────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                              │
│  • Web Dashboard (FastAPI) - http://localhost:7860               │
│  • System Tray App (pystray) - Windows taskbar spider icon      │
│  • Standalone .exe (PyInstaller) - 25 MB single file             │
│  • CSV exports for Excel                                        │
└─────────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────────┐
│  INTEGRATION LAYER                                               │
│  • Discord / Telegram / Slack webhooks                          │
│  • Email enrichment (Apollo / Hunter / Snov)                    │
│  • AI email drafts (Ollama / Groq)                              │
└─────────────────────────────────────────────────────────────────┘
```

**Key architectural decisions:**

1. **No database** — leads are JSON files. Easy to backup (`cp -r data/`), grep, open in Excel.
2. **No Docker** — just Python. Runs anywhere Python runs.
3. **No proxy service** — most sources work without one. The 2-3 that need proxies (YellowPages, Yelp) gracefully skip.
4. **No SaaS API** — Crawl4AI does the crawling. Your Ollama does the extraction. You're not paying anyone $0.001/lead.
5. **Open source end-to-end** — every line of code is yours to read, modify, audit.

---

## 6. The 7 Lead Sources Explained

### 1. Y Combinator (`crawlers/yc.py`) ⭐ The Gold Mine
- **URL:** https://www.workatastartup.com
- **What:** All jobs at YC-funded startups
- **Why good:** YC companies have raised $1-50M, they're actively hiring, they have budget
- **Volume:** 30+ jobs per run from the `/companies` page
- **Limitations:** Only server-rendered HTML (not the role-filtered URLs which are JS-loaded)
- **Best for:** Targeting funded startups with money to spend on dev work

### 2. Remotive.io (`crawlers/hiring.py`)
- **URL:** https://remotive.com/api/remote-jobs (public JSON API)
- **What:** All remote job listings, free public API, no key
- **Why good:** High-quality leads, fully remote (matches your freelance model)
- **Volume:** 15+ dev jobs per run
- **Limitations:** Mostly US/EU companies, many startups
- **Best for:** Remote-friendly dev work

### 3. Arbeitnow (`crawlers/hiring.py`)
- **URL:** https://www.arbeitnow.com/api/job-board-api
- **What:** EU-focused job board, public API
- **Why good:** EU companies often pay well, English-friendly
- **Volume:** 20+ matches per run
- **Best for:** European clients

### 4. Bark.com (`crawlers/bark.py`)
- **URL:** https://www.bark.com/en/{us,gb,au,ca}/{category}/
- **What:** Service marketplace — people POST jobs ("I need a website")
- **Why good:** **Highest intent** — these people are actively looking for a service provider
- **Volume:** Currently limited (1 per run — JS-rendered, hard to extract)
- **Best for:** Service requests
- **Note:** If this works well for you, consider BarkPro for full automation

### 5. GoodFirms (`crawlers/goodfirms.py`)
- **URL:** https://www.goodfirms.co/directory/category/...
- **What:** Agency directory — 50,000+ dev agencies listed
- **Why good:** Find agencies to partner with / subcontract work
- **Volume:** 30+ profiles discovered per run
- **Best for:** B2B partnerships, white-label work

### 6. Outdated Website Detector (`crawlers/outdated.py`)
- **URL:** Bing/DDG search for "small business website"
- **What:** Discovers websites, then checks for outdated signals
- **Why good:** **Clear pain point** — they have a site, but it's terrible
- **Signals detected:** no HTTPS, old jQuery, old WordPress themes, no mobile responsive, no schema.org
- **Volume:** 1-5 per run (limited by search engine quotas)
- **Best for:** Cold pitching redesign services

### 7. GitHub (`crawlers/github.py`)
- **URL:** https://github.com/search?q=...&type=users
- **What:** Developer profiles with public emails
- **Why good:** Indie hackers, founders with public bios
- **Limitations:** Slow (uses LLM extraction), search needs LLM
- **Best for:** Finding indie founders who might need a frontend dev

### Disabled (but coded)
- **YellowPages.com** — blocked by Cloudflare, gracefully skipped
- **Clutch.co** — slow due to LLM extraction per profile (~70s each)
- **Jobicy / 4dayweek** — empty data sets in their free APIs

---

## 7. Installation (3 Ways)

### Prerequisites
- **Windows 10/11**, **macOS**, or **Linux**
- **Python 3.10-3.12** (3.14 has no prebuilt wheels for some packages yet)
- **2GB free disk space** (for Chromium + models)

### Option A: Standalone .exe (no Python required)

1. Copy `LeadBotDashboard.exe` (25 MB) to your computer
2. Double-click it
3. Browser opens to `http://localhost:7860`
4. To view existing leads, run from command line:
   ```cmd
   LeadBotDashboard.exe --data-dir "D:\path\to\your\leadbot\data"
   ```

That's it. No Python, no terminal, no setup.

### Option B: Windows quick setup (uses .bat scripts)

1. Copy the entire `leadbot/` folder to your computer
2. Make sure Python 3.10+ is installed (https://www.python.org/downloads/) and **checked "Add to PATH"** during install
3. Double-click `setup.bat` — this:
   - Creates a virtual environment at `..\venv\`
   - Installs all Python packages
   - Downloads Playwright Chromium browser (~200 MB)
   - Creates `.env` from `.env.example`
4. Double-click `start.bat` — this launches the system tray app
5. The 🕷️ spider appears in your taskbar. Right-click for menu.

### Option C: Manual (Linux / macOS / advanced users)

```bash
# 1. Clone or copy the project
cd /path/to/leadbot

# 2. Create virtual environment
python3 -m venv ../venv
source ../venv/bin/activate  # On Windows: ..\venv\Scripts\activate

# 3. Install dependencies
pip install -U crawl4ai apscheduler pydantic python-dotenv jinja2
pip install fastapi "uvicorn[standard]" pystray Pillow  # for dashboard + tray
python -m playwright install chromium

# 4. Configure
cp .env.example .env
# Edit .env to add your Discord webhook or LLM key

# 5. Run
python dashboard.py        # Web dashboard
python launcher.py         # System tray app (Windows only)
python main.py             # CLI single run
python scheduler.py        # 24/7 mode
```

---

## 8. Usage Guide

### First run

```bash
cd D:\try\Lead_Generator
.\venv\Scripts\activate
cd leadbot

# Quick test
python main.py
```

This will:
1. Run all 7 crawlers in sequence
2. Dedupe against `data/seen.json`
3. Score and rank leads
4. Write timestamped JSON + CSV files to `data/`
5. Send notifications if any webhooks configured

Expected time: 5-15 minutes (depends on which sources are reachable)
Expected output: 10-30 unique leads per run

### Daily workflow (recommended)

**Morning (5 min):**
1. Open dashboard at http://localhost:7860
2. Sort by score, look at top 5
3. Read each company's website
4. For the best 1-2, click "Enrich Email" → "Draft Email Sequence"
5. Personalize the AI draft (5-10 min each)
6. Send

**Afternoon (5 min):**
1. Check Discord/Telegram for new high-score leads
2. Repeat

**Weekly:**
- Review `data/jobs.log` — what sources are working?
- Adjust `.env` to focus on sources that produce the best leads
- A/B test your email opener

### Dashboard tour

| Section | What it shows |
|---|---|
| **Stats** | Total leads, with-email count, by source, by type |
| **Leads table** | Sortable, filterable, click any lead to expand |
| **Filters** | Search box, source dropdown, type dropdown, score threshold, has-email checkbox |
| **Live Logs** | Real-time log stream from the running pipeline |
| **Webhooks tab** | Configure Discord/Telegram/Slack |
| **Actions tab** | Export CSV, copy emails to clipboard, open data folder |

### Run a single source

```bash
python -c "
import asyncio
from crawlers.yc import YCCrawler
from pipeline.dedup import DedupStore
from pipeline.scorer import enrich_lead
from pipeline.writer import write_leads

async def main():
    c = YCCrawler()
    raw = await c.crawl()
    dedup = DedupStore()
    enriched = [enrich_lead(l) for l in raw]
    unique = [l for l in enriched if not dedup.is_duplicate(l) and not dedup.mark_seen(l)]
    unique.sort(key=lambda x: x.get('score', 0), reverse=True)
    if unique:
        write_leads(unique, source='yc')
        print(f'Saved {len(unique)} YC leads')
asyncio.run(main())
"
```

---

## 9. Email Enrichment & Cold Outreach

LeadBot has two new features in v2.0: **email enrichment** and **AI-drafted cold email sequences**. Both are wired into the dashboard.

### Email Enrichment

**Click any lead in the dashboard** → "📧 Enrich Email" button.

LeadBot tries 4 providers in order (whichever you have API keys for):

1. **Apollo.io** (recommended, 10K free credits/month) — best for finding personal emails of CEOs/founders
2. **Hunter.io** (25 free searches/month) — finds any email at a domain
3. **Snov.io** (50 free credits/month) — similar to Hunter
4. **Pattern guessing** (free, no API) — tries `hello@`, `careers@`, `info@`, etc.

**Setting up Apollo.io (recommended):**
1. Sign up at https://app.apollo.io
2. Go to Settings → Integrations → API
3. Copy your API key
4. Add to `.env`: `APOLLO_API_KEY=your_key_here`

**Honest limitation:** For "we're hiring a dev" leads, you usually want `careers@` or `hello@` anyway — not the CEO's personal email. The hiring manager is whoever responds to the job posting, not necessarily the founder. For these leads, the free pattern guessing is often enough.

### Cold Email Sequence Generator

**Click any lead** → "✉️ Draft Email Sequence" button.

LeadBot generates a 3-email sequence:
- **Email 1** (Day 0) — question-based opener, asks about their pain point
- **Email 2** (Day 3) — reply to same thread, share a specific example
- **Email 3** (Day 8) — breakup email, give them an out

**Two modes:**
- **Template mode** (default, no LLM needed) — pre-written professional template with placeholders
- **LLM mode** (opt-in) — uses your Ollama model to personalize based on lead data

**⚠️ Important warnings built into the system:**
- AI-generated cold emails get **0.5-2% reply rates**
- Hand-written cold emails get **3-8% reply rates**
- The LLM is prompted to **avoid clickbait, fake urgency, "I saw your job posting" openers**
- Each sequence includes explicit **personalization notes** telling you what to add

**Recommended workflow:**
1. Generate the sequence (1 min)
2. Add SPECIFIC details from your past work and their company (5-10 min)
3. Replace `[First Name]` with the actual person (find on LinkedIn)
4. Send from your real email address (not a tool)
5. Track replies in a spreadsheet

**Don't:**
- ❌ Send the AI draft unmodified
- ❌ Send 100+ emails per day from day 1 (will hurt your domain reputation)
- ❌ Use fake names or pretend to be someone else

---

## 10. Notifications Setup

### Discord (easiest, 2 min)

1. Open Discord, go to your server
2. **Server Settings** → **Integrations** → **Webhooks** → **New Webhook**
3. Name it "LeadBot", pick a channel, copy the URL
4. In LeadBot dashboard: **Webhooks** tab → paste URL → **Save Settings** → **Test Notification**

You should see a rich embed in your Discord channel like:

```
🕷️ LeadBot — New Hot Leads
Found 5 new leads (score >= 30)

┌────────────────────────────────────┐
│ 🎯 Hiring Signal — Score 60       │
│ Method Financial — Senior Software │
│ 📍 USA                            │
│ 💰 $185K - $225K                  │
└────────────────────────────────────┘
```

### Telegram (5 min)

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`, follow prompts, copy the **bot token**
3. Message [@userinfobot](https://t.me/userinfobot), copy your **chat ID**
4. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   TELEGRAM_CHAT_ID=123456789
   ```

### Slack (3 min)

1. Go to https://api.slack.com/apps
2. **Create New App** → **From scratch** → name it "LeadBot"
3. **Incoming Webhooks** → toggle on → **Add New Webhook to Workspace**
4. Pick a channel, copy URL
5. Add to `.env`: `SLACK_WEBHOOK_URL=https://hooks.slack.com/...`

### Generic Webhook (Make, n8n, Zapier)

Add to `.env`: `GENERIC_WEBHOOK_URL=https://your-webhook-url`

LeadBot will POST a JSON payload:
```json
{
  "leads": [...],
  "count": 5
}
```

### Auto-trigger

Notifications are automatically sent at the end of every pipeline run. To control which leads get sent, set `NOTIFY_MIN_SCORE=50` (only high-quality leads).

---

## 11. Build a Standalone .exe

Want to share LeadBot with non-technical friends, or use it on a machine without Python?

```powershell
cd D:\try\Lead_Generator\leadbot
build.bat
```

This:
1. Installs PyInstaller
2. Cleans previous builds
3. Bundles dashboard.py + Python interpreter into `dist\LeadBotDashboard.exe` (25 MB)
4. Excludes heavy dependencies (crawl4ai, playwright) since the .exe is for the dashboard

**Distribution:** Copy `dist\LeadBotDashboard.exe` anywhere. Double-click to run. The .exe auto-opens your browser to `http://localhost:7860`.

**Caveat:** The .exe is the **dashboard only** — it doesn't run the pipeline (no browser bundled). For pipeline running, use the system tray app or scheduler.

---

## 12. Project Structure

```
D:\try\Lead_Generator\
├── venv\                          # Python 3.12 virtual environment
│   ├── Lib\site-packages\         # 200+ packages installed
│   └── Scripts\python.exe
└── leadbot\
    ├── main.py                    # Single-run pipeline orchestrator
    ├── scheduler.py               # 24/7 APScheduler (every 6h)
    ├── dashboard.py               # FastAPI web dashboard
    ├── launcher.py                # Windows system tray app
    ├── notifier.py                # Discord/Telegram/Slack webhooks
    ├── enricher.py                # Email enrichment (Apollo/Hunter/Snov/guess)
    ├── email_writer.py            # Cold email sequence generator
    ├── viewer.py                  # Static HTML lead viewer (legacy)
    ├── config.py                  # Settings from .env
    ├── leadbot.spec               # PyInstaller build spec
    ├── build.bat                  # Build .exe
    ├── setup.bat                  # First-time Windows setup
    ├── start.bat                  # Launch system tray app
    ├── README.md                  # You are here
    ├── requirements.txt
    ├── .env / .env.example        # Configuration
    │
    ├── templates/
    │   └── dashboard.html         # Dashboard UI
    │
    ├── crawlers/                  # 7 lead source crawlers
    │   ├── yc.py                  # Y Combinator Work at a Startup
    │   ├── hiring.py              # 4 free public APIs
    │   ├── bark.py                # Bark.com service requests
    │   ├── goodfirms.py           # Agency directory
    │   ├── outdated.py            # Outdated-website detector
    │   ├── frontend_dev.py        # Dribbble/Behance/Awwwards
    │   ├── github.py              # GitHub profile search
    │   ├── yellowpages.py         # (Cloudflare-blocked, graceful skip)
    │   └── clutch.py              # (slow LLM extraction, off by default)
    │
    ├── extractors/
    │   └── llm_extractor.py       # Crawl4AI LLM extraction wrapper
    │
    ├── pipeline/                  # Data processing
    │   ├── dedup.py               # File-based dedup
    │   ├── scorer.py              # Per-lead-type scoring
    │   └── writer.py              # JSON + CSV writer
    │
    └── data/                      # Output (auto-created)
        ├── leads_yc_2026-06-07_1521.json
        ├── leads_yc_2026-06-07_1521.csv
        ├── leads_hiring_*.json / .csv
        ├── leads_outdated_*.json / .csv
        ├── seen.json               # Dedup state
        └── jobs.log                # Run history
```

---

## 13. Costs & API Limits

| Service | Cost | Free Tier Limit | Enough for solo freelancer? |
|---|---|---|---|
| **Crawl4AI** | $0 | Unlimited (Apache 2.0) | ✅ Forever |
| **Playwright Chromium** | $0 | Unlimited (bundled) | ✅ Forever |
| **Ollama cloud LLM** | $0 | Unlimited (your `minimax-m3:cloud`) | ✅ Forever |
| **Groq API** | $0 | 6,000 requests/day | ✅ More than enough |
| **OpenAI/Anthropic** | Paid | — | Optional, very cheap |
| **Remotive API** | $0 | Unlimited (public) | ✅ |
| **Arbeitnow API** | $0 | Unlimited (public) | ✅ |
| **Jobicy / 4dayweek** | $0 | Unlimited (public) | ✅ |
| **Y Combinator data** | $0 | Server-rendered HTML | ✅ |
| **Discord webhooks** | $0 | Unlimited | ✅ |
| **Telegram bot API** | $0 | Unlimited | ✅ |
| **Slack webhooks** | $0 | Unlimited | ✅ |
| **Apollo.io** | $0 | **10,000 credits/month** | ✅ ~1000 enrichments |
| **Hunter.io** | $0 | **25 searches/month** | ⚠️ ~25 leads/month |
| **Snov.io** | $0 | **50 credits/month** | ⚠️ ~50 leads/month |
| **VPS hosting (optional)** | $4-5/month | — | Only for 24/7 |
| **TOTAL** | **$0/month** possible | | |

**⚠️ Watch out for free tier limits:**
- Hunter.io and Snov.io free tiers are SMALL (25-50/month)
- Use them on your TOP 10-20 leads per month, not all leads
- Pattern guessing (no API) is unlimited — use that as default

---

## 14. Configuration Reference

All configuration is in `.env` (copy from `.env.example`):

```env
# === LLM ===
LLM_PROVIDER=ollama/minimax-m3:cloud    # Your local Ollama model
LLM_API_KEY=                              # Empty for Ollama, or your API key

# === Crawl politeness ===
CRAWL_DELAY_MIN=3    # Min seconds between requests
CRAWL_DELAY_MAX=8    # Max seconds between requests

# === Targeting ===
TARGET_NICHES=web design agency,digital marketing agency,SaaS startup,IT consulting
TARGET_LOCATIONS=United Kingdom,United States,Australia,UAE
MAX_LEADS_PER_SOURCE=100

# === Hiring signals ===
HIRING_KEYWORDS=frontend developer,react developer,full stack developer,wordpress developer

# === Notifications ===
DISCORD_WEBHOOK_URL=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
SLACK_WEBHOOK_URL=
GENERIC_WEBHOOK_URL=
NOTIFY_MIN_SCORE=30

# === Email enrichment ===
HUNTER_API_KEY=
SNOV_CLIENT_ID=
SNOV_CLIENT_SECRET=
APOLLO_API_KEY=
```

**LLM provider examples:**
```env
# Ollama (local, free)
LLM_PROVIDER=ollama/llama3.3
# or
LLM_PROVIDER=ollama/minimax-m3:cloud

# Groq (cloud, free 6K req/day)
LLM_PROVIDER=groq/llama-3.3-70b-versatile
LLM_API_KEY=gsk_your_key

# OpenAI (paid)
LLM_PROVIDER=openai/gpt-4o-mini
LLM_API_KEY=sk_your_key

# Anthropic (paid)
LLM_PROVIDER=anthropic/claude-3-5-sonnet-20241022
LLM_API_KEY=sk-ant-your_key
```

---

## 15. Troubleshooting

### "Python not found" on Windows setup
- Install Python 3.10-3.12 from https://www.python.org/downloads/
- **Check "Add Python to PATH"** during installation
- Restart your terminal

### `pip install` fails with "Microsoft Visual C++ 14.0 required"
- This happens on Python 3.13+ (no prebuilt wheels for lxml)
- Use Python 3.12 instead
- Or install "Microsoft C++ Build Tools" from https://visualstudio.microsoft.com/visual-cpp-build-tools/

### "Address already in use" when starting dashboard
- Port 7860 is taken. Run with a different port: `python dashboard.py --port 7861`
- Or kill the other process: `Get-Process python | Stop-Process -Force`

### YellowPages/Clutch returning 0 leads
- They block datacenter IPs via Cloudflare
- This is **expected** — LeadBot skips them gracefully
- Use the other 5 sources which are less protected

### Notifications not arriving
- Check `.env` has the correct webhook URL
- Test with the dashboard's "Test Notification" button
- For Discord: make sure the webhook hasn't been deleted from your server
- For Telegram: make sure you started a chat with your bot first

### Browser doesn't open automatically
- Run with explicit browser: `python dashboard.py` (no `--no-browser`)
- Or open manually: `http://localhost:7860`

### Dashboard shows 0 leads
- Make sure `data/leads_*.json` files exist
- Run a pipeline: click "▶ Run Pipeline" or run `python main.py` from terminal

### "No module named X" errors
- Activate venv: `..\venv\Scripts\activate` (Windows) or `source ../venv/bin/activate` (Linux/Mac)
- Reinstall: `pip install -r requirements.txt`

---

## 16. FAQ

**Q: Is this legal?**
A: Yes, if you respect robots.txt and don't overload servers. We add 3-8s delays between requests. Don't use scraped data to spam — use it to find relevant people to have real conversations with.

**Q: Can I get banned from these sites?**
A: Possibly, if you scrape aggressively. LeadBot uses:
- Realistic user agents
- 3-8s delays between requests
- Magic mode (Crawl4AI's stealth)
- Single browser instance
For high-volume needs, consider proxies (~$5/month from ThorData or NstProxy).

**Q: How does this compare to commercial tools like Apollo or ZoomInfo?**
A: Those tools are $99-500/month but offer more sources, verified emails, and LinkedIn integration. LeadBot is $0/month but covers the main free public sources. If you scale beyond 100 leads/month, consider Apollo.

**Q: Can I add more lead sources?**
A: Yes! Create a new file in `crawlers/` (e.g., `crawlers/linkedin.py`), implement a class with a `crawl()` async method, and add it to `main.py`. See `crawlers/yc.py` or `crawlers/hiring.py` for examples.

**Q: How accurate is the LLM extraction?**
A: Crawl4AI's schema-based extraction is ~80-90% accurate. Always review the extracted data — the LLM can make mistakes, especially with unusual formats.

**Q: Does this work without an LLM?**
A: Yes! The CSS-based extractors (YellowPages, etc.) work without LLM. The LLM is only used for semantic extraction. The hiring crawler uses pure API calls, no LLM.

**Q: Can I run this on a server?**
A: Yes. See "VPS deployment" in the Deployment section above.

**Q: How do I update LeadBot?**
A: `cd leadbot && git pull` (if you cloned from git) or just download the new files.

**Q: My LLM takes too long / times out. What now?**
A: Reduce the number of pages crawled (edit `MAX_LEADS_PER_SOURCE`). Or use a faster LLM (Groq is faster than Ollama for most models).

**Q: Can I get caught scraping?**
A: Sites use rate limiting + IP detection. LeadBot:
- Uses random user agents
- Adds 3-8s delays
- Uses a single browser instance
- Sets a realistic viewport
For zero risk, use proxies.

---

## 17. Why Open Source + Privacy

### Why open source

1. **Trust** — you can see exactly what data is collected, how it's stored, what calls are made
2. **Customization** — modify anything: add sources, change scoring, customize emails
3. **No vendor lock-in** — your data is in JSON files YOU control
4. **Education** — learn how modern AI + web scraping work in production
5. **Community** — fork it, build features, share back

### Privacy

- **No telemetry** — LeadBot doesn't phone home, doesn't track you
- **Your data stays local** — leads are in `data/` on YOUR computer
- **No accounts** — no logins, no API keys for the crawlers themselves (only for enrichment/notifications)
- **No SaaS dependency** — works fully offline if you use Ollama local

### License

MIT — do whatever you want, just don't blame us if it breaks.

---

## 18. Roadmap & Limitations

### What LeadBot does well
- ✅ 7+ free lead sources
- ✅ Smart anti-bot handling
- ✅ File-based (no DB)
- ✅ Beautiful web dashboard
- ✅ Standalone .exe
- ✅ Discord/Telegram/Slack notifications
- ✅ Email enrichment (3 providers + free fallback)
- ✅ AI email drafts (with safety rails)

### Current limitations
- ❌ No LinkedIn scraper (LinkedIn blocks most crawlers; would need LinkedIn Sales Navigator or Phantombuster)
- ❌ No email *sending* (intentionally — sends are risky, should be in a dedicated tool like Instantly/Smartlead)
- ❌ No reply tracking (would need email integration)
- ❌ LLM extraction is slow (~70-130s per profile for Clutch)
- ❌ No multi-user / team support (single-process)
- ❌ Bark.com extraction is poor (JS-rendered)
- ❌ YellowPages/Clutch are blocked by Cloudflare

### Possible future features (not currently built)
- 🔮 Reply tracking (would require IMAP integration)
- 🔮 A/B testing for email openers
- 🔮 LinkedIn scraper (via Phantombuster or Sales Navigator)
- 🔮 Lead qualification via LLM (rate leads 1-10 based on likelihood to convert)
- 🔮 Auto-schedule emails via Instantly/Smartlead/Apollo
- 🔮 Multi-user support (login, role-based access)
- 🔮 Webhook for new leads (Make.com, n8n workflows)

**These are easy to add** if you have a use case. Just ask.

---

## 19. Honest Take: How to Actually Get Clients

**I'm going to be direct, because I think it's the most useful thing I can tell you.**

### What LeadBot is

A tool to **automate lead discovery** so you can spend more time on the parts of freelancing that actually make money: **sales calls, building great work, and getting referrals**.

### What LeadBot is NOT

- ❌ A replacement for understanding your customer
- ❌ A way to spam 1000 people with the same AI-generated email and expect results
- ❌ A magic solution to "I'm not getting clients"
- ❌ A reason to skip the hard work of becoming a good seller

### The real math of freelancing success

For most web designers / full-stack devs, the **bottleneck is NOT lead generation**. It's:

1. **Clarifying your offer** — "I help [specific type of business] get [specific outcome] via [specific deliverable]"
2. **Building trust quickly** — case studies, testimonials, specific examples
3. **Asking for the sale** — most freelancers don't follow up enough
4. **Pricing correctly** — too cheap = no clients trust you; too expensive = no leads convert

LeadBot helps with #0 (more leads) but doesn't help with 1-4.

### My actual recommended workflow (do this, not "build more tools")

**Week 1 (4 hours total):**
- Day 1 (1 hour): Install LeadBot, run it once, look at the leads
- Day 1 (30 min): Pick 5 leads you'd actually want to work with
- Day 2 (1 hour): Research those 5 companies — visit their sites, read their LinkedIn, see what they're building
- Day 3 (1 hour): Hand-write 5 emails. Not AI-generated. Your words. Your voice. Be specific.
- Day 4 (30 min): Send all 5
- Day 7 (30 min): Follow up if no reply

**Week 2-3:**
- Repeat the cycle with 5 new leads per week
- Track open rate, reply rate, call rate, conversion rate
- After 20+ emails, you have real data on what works

**After you have signal (1+ reply, 1+ call):**
- THEN use LeadBot to scale — get 50+ leads/week instead of 5
- THEN use the email enrichment + AI drafts (with your hand-written opener as a guide)
- THEN add notifications so you can react in real-time

**If you get 0 replies after 20 emails:** your offer or your targeting is wrong. Fix that BEFORE building more tools.

### Why I built LeadBot anyway

I built LeadBot because:
1. **You asked** — multiple times
2. **It's a great learning project** — even if you don't use it, you learn about crawlers, LLMs, FastAPI, system tray apps, .exe packaging
3. **Some people DO need scale** — if you have $10K/month from existing clients and want to grow, automation helps
4. **It's open source** — others can use it, modify it, learn from it

But for **1 person starting freelance, the highest ROI is:**
1. Pick a niche (e.g., "React developers for YC fintech startups")
2. Get 1 client through cold outreach or referrals
3. Do great work
4. Get 2 more clients through referrals
5. NOW use tools like LeadBot to scale beyond referrals

---

## 20. License & Credits

### License

MIT License — use freely, modify freely, sell if you want, just don't blame us.

### Built with

- [Crawl4AI](https://github.com/unclecode/crawl4ai) — #1 open-source LLM-friendly web crawler (68K+ ⭐, Apache 2.0)
- [ScrapeGraphAI](https://github.com/ScrapeGraphAI/Scrapegraph-ai) — reference for the extractor pattern
- [FastAPI](https://fastapi.tiangolo.com/) — web dashboard backend
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [APScheduler](https://apscheduler.readthedocs.io/) — 24/7 scheduling
- [pystray](https://github.com/moses-palmer/pystray) — system tray app
- [PyInstaller](https://www.pyinstaller.org/) — .exe packaging
- [Jinja2](https://jinja.palletsprojects.com/) — dashboard templates
- [Pydantic](https://docs.pydantic.dev/) — data validation
- [Playwright](https://playwright.dev/) — headless browser (via Crawl4AI)

### Data sources (all free public APIs or server-rendered HTML)

- [Y Combinator Work at a Startup](https://www.workatastartup.com)
- [Remotive.io](https://remotive.com)
- [Arbeitnow](https://www.arbeitnow.com)
- [Jobicy](https://jobicy.com)
- [4dayweek.io](https://4dayweek.io)
- [Bark.com](https://www.bark.com)
- [GoodFirms.co](https://www.goodfirms.co)
- [Dribbble](https://dribbble.com)
- [Awwwards](https://www.awwwards.com)
- [Behance](https://www.behance.net)
- [GitHub](https://github.com)
- [DuckDuckGo](https://duckduckgo.com) / [Bing](https://www.bing.com)

### Built by

Bina Codes / Abdul Rauf

### Last updated

June 2026

---

## 🚀 Ready to start?

**For most people:** close this README, go to your terminal, and run `setup.bat`. Then come back when you want to add the next source or the .exe build.

**For serious automation:** start with `python main.py`, see the leads, customize for your niche.

**For learning:** read `crawlers/yc.py` and `pipeline/scorer.py` to understand the architecture. Then try adding your own crawler.

**For the .exe:** run `build.bat` and share the standalone with non-technical friends.

**Most importantly:** send 5 emails this week. Not 50. Not 100. Just 5. Track replies. Iterate.

The best tool is the one that gets you to send real outreach. LeadBot is that tool — if you use it. If you don't, close this tab and go do the work. Either way, the next 2 hours of your time are more valuable than any crawler. 🎯
