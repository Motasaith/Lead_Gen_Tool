"""
scorer.py — Lead scoring with separate logic per lead type
Different lead sources mean different opportunities:
  - service_request (Bark):  HIGH value (active buyer)
  - hiring_signal (job boards): HIGH value (budget exists)
  - outdated_site:           HIGH value (clear pain point)
  - agency (GoodFirms):       MEDIUM (partnership prospect)
  - designer (Dribbble):      MEDIUM (partner or competitor intel)
"""
import uuid
from datetime import datetime
from typing import Dict


def score_service_request(lead: Dict) -> float:
    """Bark-style leads — active service requests."""
    s = 30.0  # base value: this is someone actively asking
    if lead.get("email"):
        s += 35
    if lead.get("phone"):
        s += 25
    if lead.get("company_name"):
        s += 10
    if lead.get("niche") and "design" in lead.get("niche", "").lower():
        s += 5
    return min(s, 100.0)


def score_hiring_signal(lead: Dict) -> float:
    """Job-board leads — companies with budget for devs."""
    s = 40.0  # base: budget proven by job posting
    if lead.get("company_name"):
        s += 15
    # WordPress roles are easier wins
    if "wordpress" in lead.get("title", "").lower():
        s += 15
    if any(kw in lead.get("title", "").lower() for kw in ["frontend", "react", "next"]):
        s += 10
    if "senior" in lead.get("title", "").lower():
        s += 5
    if "junior" in lead.get("title", "").lower() or "intern" in lead.get("title", "").lower():
        s -= 10  # harder to land
    return min(max(s, 0), 100.0)


def score_outdated_site(lead: Dict) -> float:
    """Outdated-website leads — redesign opportunities."""
    s = float(lead.get("outdated_score", 0) or 0) * 0.8
    if lead.get("email"):
        s += 30
    if lead.get("phone"):
        s += 20
    if lead.get("company_name") and lead["company_name"] != "Unknown":
        s += 10
    # High signal count = more desperate for redesign
    signals = lead.get("outdated_signals", [])
    if len(signals) >= 4:
        s += 10
    return min(s, 100.0)


def score_agency(lead: Dict) -> float:
    """Agency directory leads — partnership prospects."""
    s = 20.0
    if lead.get("email"):
        s += 30
    if lead.get("phone"):
        s += 15
    if lead.get("website"):
        s += 10
    if lead.get("country"):
        s += 5
    if lead.get("hourly_rate"):
        s += 5
    return min(s, 100.0)


def score_designer(lead: Dict) -> float:
    """Designer community leads — partnership/learning prospects."""
    s = 15.0
    if lead.get("contact_name"):
        s += 10
    if lead.get("email"):
        s += 25
    if lead.get("website"):
        s += 10
    return min(s, 100.0)


SCORERS = {
    "service_request": score_service_request,
    "hiring_signal": score_hiring_signal,
    "outdated_site": score_outdated_site,
    "agency": score_agency,
    "designer": score_designer,
}


def score_lead(lead: Dict) -> float:
    """Pick the right scorer based on lead_type, fallback to base score."""
    lead_type = lead.get("lead_type", "unknown")
    scorer = SCORERS.get(lead_type)
    if scorer:
        return scorer(lead)
    # Generic fallback
    s = 0.0
    if lead.get("email"):
        s += 30
    if lead.get("phone"):
        s += 20
    if lead.get("website"):
        s += 10
    if lead.get("company_name"):
        s += 10
    return min(s, 100.0)


JUNK_EMAIL_MARKERS = (
    "example.com", "test@", "noreply@", "no-reply@",
    "yourcompany.com", "domain.com", "email.com",
)


def enrich_lead(lead: Dict) -> Dict:
    """Clean and normalize lead data, then add score + id."""
    # Clean email
    email = (lead.get("email") or "").strip().lower()
    if email and any(j in email for j in JUNK_EMAIL_MARKERS):
        email = ""
    lead["email"] = email or None

    # Clean phone
    phone = lead.get("phone") or ""
    if phone:
        lead["phone"] = "".join(c for c in phone if c.isdigit() or c in "+-() ").strip() or None
    else:
        lead["phone"] = None

    # Normalize website
    website = (lead.get("website") or "").strip()
    if website and not website.startswith(("http://", "https://")):
        lead["website"] = "https://" + website

    # Strip empty strings to None
    for k, v in list(lead.items()):
        if v == "":
            lead[k] = None

    # Default lead_type
    if not lead.get("lead_type"):
        # Guess from source
        src = lead.get("source", "")
        if src in ("bark",):
            lead["lead_type"] = "service_request"
        elif src in ("weworkremotely", "remotive", "jobicy"):
            lead["lead_type"] = "hiring_signal"
        elif src in ("outdated_detector",):
            lead["lead_type"] = "outdated_site"
        elif src in ("goodfirms", "awwwards"):
            lead["lead_type"] = "agency"
        elif src in ("dribbble", "behance"):
            lead["lead_type"] = "designer"
        else:
            lead["lead_type"] = "unknown"

    lead["score"] = score_lead(lead)
    lead["id"] = f"lead_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
    lead["fetched_at"] = datetime.utcnow().isoformat() + "Z"
    return lead
