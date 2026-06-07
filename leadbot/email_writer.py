"""
email_writer.py - LLM-powered cold email DRAFTER (not auto-sender)
===================================================================

WHAT THIS DOES:
  Takes a lead (company name, role, source URL) and generates a 3-email
  cold outreach sequence as a DRAFT you can review and personalize.

WHAT IT DOES NOT DO:
  - Does NOT send emails (you should always review + personalize first)
  - Does NOT pretend to know things it doesn't
  - Does NOT use clickbait / manipulative patterns
  - Does NOT pretend to be someone you're not

HONEST REALITY CHECK (please read):
  AI-generated cold emails get 0.5-2% reply rates.
  Hand-written cold emails get 3-8% reply rates.
  The reason: AI emails are GENERIC. They sound like every other cold email.
  Your advantage as a human: you can be SPECIFIC, PERSONAL, AUTHENTIC.

  THIS TOOL IS BEST USED AS A STARTING POINT - edit each email before sending.
  Treat the LLM output like a first draft from a junior assistant.
  Your job: add the specific details only you know (your past work,
  specific angle on their problem, mutual connection, etc.)

RECOMMENDED WORKFLOW:
  1. Run LeadBot, get 10-20 leads
  2. For each lead, generate a sequence
  3. Spend 5 minutes per email adding personal touches
  4. Send 5-10 personalized emails per day
  5. Track replies, iterate on your opener
"""
import json
import os
from typing import Dict, List, Optional
from config import LLM_PROVIDER, LLM_API_KEY

# Default sender profile (edit these to match YOU)
DEFAULT_SENDER = {
    "name": "[Your Name]",
    "title": "[Your Title, e.g. Senior Full-Stack Developer]",
    "company": "[Your Brand / Studio Name, or 'Independent']",
    "services": "frontend web design, full-stack development (React, Next.js, Node)",
    "proof": "[1-2 specific projects or clients you've helped, e.g. 'Built the checkout flow for Acme that increased conversions 30%']",
    "differentiator": "[What makes you different, e.g. 'I work async with daily updates, fixed-scope pricing, no agency overhead']",
    "calendar_link": "[Your Calendly or scheduling link]",
    "website": "[Your website URL]",
}

SEQUENCE_PROMPT = """You are a cold email copywriter for a freelance web developer.
Write a 3-email outreach sequence for the lead below.

RULES (very important - do not break these):
1. NO clickbait, no fake urgency, no "I noticed we have a mutual connection"
2. NO "I saw your job posting" as opener - too generic, gets deleted
3. Be SPECIFIC to this lead's business, not generic
4. Keep each email under 100 words
5. First email: ask a question, not a meeting
6. Second email (sent 3 days later if no reply): provide a specific insight or example
7. Third email (sent 5 days later): breakup email, give them an out

SENDER PROFILE:
{sender}

LEAD INFO:
- Company: {company}
- Role they're hiring for: {title}
- Source: {source}
- Lead URL: {url}
- Country: {country}
- Lead type: {lead_type}

SERVICE I'M OFFERING: {services}

OUTPUT FORMAT (return ONLY valid JSON, no other text):
{{
  "subject_1": "...",
  "body_1": "...",
  "subject_2": "...",
  "body_2": "...",
  "subject_3": "...",
  "body_3": "...",
  "personalization_notes": "1-2 specific things to add before sending (e.g. 'Reference their recent product launch on X')"
}}
"""


def _call_llm(prompt: str) -> Optional[str]:
    """Call the configured LLM via crawl4ai's LLMExtractionStrategy (uses same provider as main pipeline)."""
    try:
        # Reuse the same LLM config the pipeline uses
        from crawl4ai import LLMConfig
        from litellm import completion

        cfg = LLMConfig(provider=LLM_PROVIDER, api_token=LLM_API_KEY)
        # Resolve to a model name for litellm
        model_name = LLM_PROVIDER.replace("/", "/")
        if LLM_PROVIDER.startswith("ollama/"):
            # Use the configured ollama model directly
            pass

        response = completion(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            api_key=LLM_API_KEY,
            temperature=0.7,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[EmailWriter] LLM call failed: {e}")
        return None


def _extract_json(text: str) -> Optional[Dict]:
    """Extract JSON from LLM response (handles ```json blocks)."""
    if not text:
        return None
    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try extracting from code fence
    m = None
    for pattern in [r"```json\s*(.*?)\s*```", r"```\s*(.*?)\s*```", r"\{.*\}"]:
        m = re.search(pattern, text, re.DOTALL) if "```" in pattern or "\\{" in pattern else None
        if m:
            try:
                return json.loads(m.group(1) if "```" in pattern else m.group(0))
            except Exception:
                continue
    return None


import re


def generate_sequence(lead: Dict, sender: Optional[Dict] = None, custom_services: Optional[str] = None) -> Dict:
    """
    Generate a 3-email cold outreach sequence for a lead.

    Returns a dict with subject_1/2/3, body_1/2/3, personalization_notes.
    Returns error info if generation failed.
    """
    s = sender or DEFAULT_SENDER
    services = custom_services or s.get("services", DEFAULT_SENDER["services"])

    # Build lead description
    company = lead.get("company_name") or "the company"
    title = lead.get("title") or "[unknown role]"
    source = lead.get("source", "?")
    url = lead.get("source_url") or lead.get("website") or ""
    country = lead.get("country") or "?"
    lead_type = lead.get("lead_type", "unknown")

    # Add YC batch context if available
    yc_context = ""
    if lead.get("yc_batch"):
        yc_context = f"\nNote: This company is a Y Combinator {lead['yc_batch']} startup (funded)."

    prompt = SEQUENCE_PROMPT.format(
        sender=json.dumps(s, indent=2),
        company=company,
        title=title,
        source=source,
        url=url,
        country=country,
        lead_type=lead_type,
        services=services + yc_context,
    )

    print(f"[EmailWriter] Generating sequence for {company}...")
    raw = _call_llm(prompt)
    if not raw:
        return {
            "error": "LLM call failed - check your LLM_PROVIDER and LLM_API_KEY settings",
            "subject_1": None, "body_1": None,
            "subject_2": None, "body_2": None,
            "subject_3": None, "body_3": None,
        }

    parsed = _extract_json(raw)
    if not parsed:
        return {
            "error": "Failed to parse LLM response as JSON. Raw output saved.",
            "raw": raw[:2000],
        }

    return parsed


def generate_template(lead: Dict, sender: Optional[Dict] = None) -> Dict:
    """
    Generate a PLAIN TEXT TEMPLATE (no LLM) as a fallback.
    Use this when LLM is unavailable or you want full control.
    """
    s = sender or DEFAULT_SENDER
    company = lead.get("company_name") or "your company"
    title = lead.get("title") or "[the role]"

    return {
        "subject_1": f"Quick question for {company}",
        "body_1": f"""Hi [First Name],

{s.get('name')} here. I work with {s.get('services', 'frontend/full-stack dev')}.

I saw {company} is hiring for {title} - which usually means there's enough work to consider outside help too.

Quick question: what's the most painful part of your dev workflow right now?

{s.get('name')}
{s.get('title')}
{s.get('website')}""",
        "subject_2": f"Re: Quick question for {company}",
        "body_2": f"""Hi [First Name],

Following up. Here's a specific example: I recently helped a {lead.get('niche', 'similar')} company with [X outcome - EDIT THIS].

If you're hitting a similar wall with {title} work, happy to share what worked.

{s.get('name')}""",
        "subject_3": "Closing the loop",
        "body_3": f"""Hi [First Name],

Last note from me - I know hiring eats bandwidth. If your dev needs are bursting at the seams, I'm one call away: {s.get('calendar_link', '[calendar]')}.

If not, no worries - good luck with the {title} search.

{s.get('name')}""",
        "personalization_notes": (
            "1. Replace [First Name] with the actual person's name (find on LinkedIn)\n"
            "2. Add a SPECIFIC example of work you did - generic = deleted\n"
            "3. Mention something unique about their company from their website\n"
            "4. If you have a mutual connection, mention it in the first line"
        ),
    }
