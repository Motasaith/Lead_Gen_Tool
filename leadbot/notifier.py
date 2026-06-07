"""
notifier.py — Discord / Telegram / Slack / Webhook notifications
Discord and Slack support incoming webhooks (no bot user, no OAuth).
Telegram uses a bot token + chat_id (very simple).
"""
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Optional
import os


def _post_json(url: str, payload: dict, headers: dict = None) -> bool:
    """POST JSON to a URL, return True on success."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json",
        "User-Agent": "LeadBot/1.0",
        **(headers or {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except Exception as e:
        print(f"[Notify] POST failed: {e}")
        return False


def send_discord(webhook_url: str, leads: List[Dict], min_score: float = 30) -> bool:
    """
    Send a batch of high-score leads to a Discord webhook.
    Discord webhooks support rich embeds. Limit: 10 embeds per message, 4096 chars.
    """
    if not webhook_url or not webhook_url.startswith("https://discord.com/api/webhooks/"):
        print("[Notify] Invalid Discord webhook URL")
        return False

    hot = [l for l in leads if l.get("score", 0) >= min_score]
    if not hot:
        return False

    # Discord allows up to 10 embeds per message
    embeds = []
    for lead in hot[:10]:
        # Build description
        score = int(lead.get("score", 0))
        company = lead.get("company_name", "Unknown")[:80]
        title = lead.get("title", "")[:120]
        lead_type = lead.get("lead_type", "unknown").replace("_", " ").title()
        source = lead.get("source", "?").upper()
        url = lead.get("source_url") or lead.get("website", "")
        location = lead.get("country") or ""
        salary = lead.get("salary_range") or ""
        email = lead.get("email") or ""

        desc = f"**{company}** — {title}"
        if location:
            desc += f"\n📍 {location}"
        if salary:
            desc += f"\n💰 {salary}"
        if email:
            desc += f"\n📧 {email}"

        # Color based on score
        if score >= 60:
            color = 0x2ecc71  # green
        elif score >= 30:
            color = 0xf39c12  # orange
        else:
            color = 0x95a5a6  # gray

        embeds.append({
            "title": f"🎯 {lead_type} — Score {score}",
            "description": desc[:2000],
            "url": url[:500] if url else None,
            "color": color,
            "footer": {"text": f"Source: {source}"},
        })

    # Summary embed
    summary = {
        "title": "🕷️ LeadBot — New Hot Leads",
        "description": f"Found **{len(hot)}** new leads (score >= {min_score})",
        "color": 0x9b59b6,
    }
    payload = {
        "content": None,
        "embeds": [summary] + embeds,
        "username": "LeadBot",
    }
    return _post_json(webhook_url, payload)


def send_telegram(bot_token: str, chat_id: str, leads: List[Dict], min_score: float = 30) -> bool:
    """Send a Telegram message via bot."""
    if not bot_token or not chat_id:
        return False
    hot = [l for l in leads if l.get("score", 0) >= min_score]
    if not hot:
        return False

    lines = [f"🕷️ *LeadBot — {len(hot)} new hot leads*\n"]
    for lead in hot[:10]:
        score = int(lead.get("score", 0))
        company = (lead.get("company_name") or "?")[:50]
        title = (lead.get("title") or "")[:80]
        url = lead.get("source_url") or ""
        emoji = "🎯" if score >= 60 else "📌"
        lines.append(f"{emoji} *{score}* — *{company}*\n    {title}\n    {url}")

    text = "\n".join(lines)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text[:4000],
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    return _post_json(url, payload)


def send_slack(webhook_url: str, leads: List[Dict], min_score: float = 30) -> bool:
    """Send to Slack webhook."""
    if not webhook_url or "hooks.slack.com" not in webhook_url:
        return False
    hot = [l for l in leads if l.get("score", 0) >= min_score]
    if not hot:
        return False

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"🕷️ LeadBot — {len(hot)} new hot leads"}
        }
    ]
    for lead in hot[:8]:
        score = int(lead.get("score", 0))
        company = lead.get("company_name", "?")[:50]
        title = lead.get("title", "")[:80]
        url = lead.get("source_url") or ""
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{score}* — *{company}*\n{title}\n<{url}|Open>"
            }
        })
    payload = {"blocks": blocks}
    return _post_json(webhook_url, payload)


def send_generic_webhook(webhook_url: str, leads: List[Dict], min_score: float = 30) -> bool:
    """Send JSON to any webhook (Make.com, n8n, Zapier, etc.)."""
    if not webhook_url:
        return False
    hot = [l for l in leads if l.get("score", 0) >= min_score]
    if not hot:
        return False
    return _post_json(webhook_url, {"leads": hot, "count": len(hot)})


class Notifier:
    """Reads webhook config from env and dispatches notifications."""

    def __init__(self):
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL", "")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat = os.getenv("TELEGRAM_CHAT_ID", "")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")
        self.generic_webhook = os.getenv("GENERIC_WEBHOOK_URL", "")
        self.min_score = float(os.getenv("NOTIFY_MIN_SCORE", "30"))

    def notify(self, leads: List[Dict], source: str = "") -> Dict[str, bool]:
        """Send notifications to all configured channels. Returns {channel: success}."""
        results = {}
        if not leads:
            return results
        count = len(leads)
        print(f"[Notify] {count} leads, min_score={self.min_score}")
        if self.discord_webhook:
            ok = send_discord(self.discord_webhook, leads, self.min_score)
            results["discord"] = ok
            print(f"[Notify] Discord: {'OK' if ok else 'FAILED'}")
        if self.telegram_token and self.telegram_chat:
            ok = send_telegram(self.telegram_token, self.telegram_chat, leads, self.min_score)
            results["telegram"] = ok
            print(f"[Notify] Telegram: {'OK' if ok else 'FAILED'}")
        if self.slack_webhook:
            ok = send_slack(self.slack_webhook, leads, self.min_score)
            results["slack"] = ok
            print(f"[Notify] Slack: {'OK' if ok else 'FAILED'}")
        if self.generic_webhook:
            ok = send_generic_webhook(self.generic_webhook, leads, self.min_score)
            results["generic"] = ok
            print(f"[Notify] Generic: {'OK' if ok else 'FAILED'}")
        return results
