"""
main.py — LeadBot pipeline runner
Runs all 6 crawlers in sequence, enriches, dedupes, scores, and writes JSON+CSV per source.

Sources:
  1. bark.py           - Service marketplace requests (Bark.com)
  2. goodfirms.py      - Agency directory (GoodFirms.co)
  3. hiring.py         - Job boards = companies with dev budget
  4. outdated.py       - Detector for businesses with old websites
  5. frontend_dev.py   - Design communities (Dribbble, Awwwards, Behance)
  6. github.py         - Developer leads from GitHub
"""
import sys
import asyncio
import logging
from config import MAX_LEADS_PER_SOURCE
from crawlers.bark import BarkCrawler
from crawlers.goodfirms import GoodFirmsCrawler
from crawlers.hiring import HiringCrawler
from crawlers.outdated import OutdatedDetector
from crawlers.frontend_dev import FrontendDevCrawler
from crawlers.yc import YCCrawler
from crawlers.github import GitHubCrawler
from crawlers.yellowpages import YellowPagesCrawler
from crawlers.clutch import ClutchCrawler
from pipeline.dedup import DedupStore
from pipeline.scorer import enrich_lead
from pipeline.writer import write_leads, append_job_log
from notifier import Notifier

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("leadbot")


async def run_source(name: str, coro):
    """Run a single crawler source, dedupe + score, write to data/."""
    log.info(f"=== Starting {name} ===")
    dedup = DedupStore()
    try:
        raw = await coro
        log.info(f"[{name}] Raw leads: {len(raw)}")

        cleaned = [enrich_lead(l) for l in raw if isinstance(l, dict)]
        log.info(f"[{name}] After enrich: {len(cleaned)}")

        unique = []
        for lead in cleaned:
            if dedup.is_duplicate(lead):
                continue
            dedup.mark_seen(lead)
            unique.append(lead)
            if len(unique) >= MAX_LEADS_PER_SOURCE:
                break

        # Sort by score (highest first)
        unique.sort(key=lambda x: x.get("score", 0), reverse=True)

        if unique:
            path = write_leads(unique, source=name)
            log.info(f"[{name}] Saved {len(unique)} leads -> {path}")
        else:
            log.info(f"[{name}] No new leads")

        append_job_log(name, "ok", len(unique))
        dedup.commit()
    except Exception as e:
        log.exception(f"[{name}] Failed: {e}")
        append_job_log(name, "failed", 0, str(e))


async def run_all():
    log.info("=" * 60)
    log.info("LeadBot Pro - Web Design / Full-Stack Dev Lead Pipeline")
    log.info("=" * 60)

    # 1. BARK - service requests (highest intent leads)
    await run_source("bark", BarkCrawler().crawl())
    await asyncio.sleep(30)

    # 2. HIRING - companies with dev budget
    await run_source("hiring", HiringCrawler().crawl())
    await asyncio.sleep(30)

    # 3. YC - funded startups hiring devs (gold mine)
    try:
        from crawlers.yc import YCCrawler
        await run_source("yc", YCCrawler().crawl())
    except Exception as e:
        log.error(f"yc: {e}")
    await asyncio.sleep(30)

    # 4. OUTDATED - redesign opportunities
    await run_source("outdated", OutdatedDetector().crawl())
    await asyncio.sleep(30)

    # 5. GOODFIRMS - agency directory
    await run_source("goodfirms", GoodFirmsCrawler().crawl())
    await asyncio.sleep(30)

    # 6. FRONTEND_DEV - design communities
    await run_source("frontend_dev", FrontendDevCrawler().crawl())
    await asyncio.sleep(30)

    # 6. YELLOWPAGES - business directory (Cloudflare-blocked, will skip gracefully)
    try:
        yp = YellowPagesCrawler()
        from config import TARGET_NICHES, TARGET_LOCATIONS
        urls = yp.build_urls(TARGET_NICHES[:1], TARGET_LOCATIONS[:1], pages_per_combo=1)[:2]
        await run_source("yellowpages", yp.crawl(urls))
    except Exception as e:
        log.error(f"yellowpages: {e}")
    await asyncio.sleep(30)

    # 7. CLUTCH - agency profiles (uses LLM, slow)
    try:
        from crawlers.clutch import ClutchCrawler
        await run_source("clutch", ClutchCrawler().crawl())
    except Exception as e:
        log.error(f"clutch: {e}")
    await asyncio.sleep(30)

    # 8. GITHUB - developer profiles
    try:
        from crawlers.github import GitHubCrawler
        await run_source("github", GitHubCrawler().crawl())
    except Exception as e:
        log.error(f"github: {e}")

    # 9. NOTIFY - send notifications for high-score leads
    try:
        import glob, json
        all_leads = []
        for f in glob.glob("data/leads_*.json"):
            with open(f) as fh:
                data = json.load(fh)
            if isinstance(data, list):
                all_leads.extend(data)
        if all_leads:
            from notifier import Notifier
            notifier = Notifier()
            results = notifier.notify(all_leads, source="auto")
            log.info(f"[Notify] {results}")
    except Exception as e:
        log.error(f"notifier: {e}")

    log.info("=" * 60)
    log.info("LeadBot run complete. Check data/ for output.")
    log.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all())
