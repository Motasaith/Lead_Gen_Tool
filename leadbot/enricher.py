"""
enricher.py - Email enrichment module
=====================================

WHAT THIS DOES:
Finds contact emails for leads using free public APIs.

PROVIDERS (all have free tiers, no card required):
  1. Hunter.io     - 25 searches/month free (best for finding emails by domain)
  2. Snov.io       - 50 credits/month free
  3. Apollo.io     - 10,000 credits/month free (best for finding PEOPLE at a company)
  4. Email pattern guessing - free, no API, just tries common patterns (john@, ceo@, etc.)

HONEST LIMITATIONS:
  - These APIs find info@/support@/sales@ emails easily but NOT hiring manager emails
  - For "we're hiring a dev" leads, you usually want careers@ or hello@ anyway
  - For B2B outreach, you need Apollo.io + LinkedIn Sales Navigator
  - Free tiers are LIMITED - 25-50 searches/month means you can enrich ~5 leads/day

RECOMMENDED WORKFLOW:
  1. Run LeadBot to get ~50 leads
  2. Pick top 10 by score
  3. Manually enrich each (one Hunter.io search each)
  4. Hand-write emails to those 10
  5. Track replies, iterate on your offer
  DON'T try to "enrich all 500 leads" - you'll burn through free tier in a day
"""
import json
import re
import urllib.request
import urllib.parse
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class EmailResult:
    email: Optional[str] = None
    source: str = "none"  # hunter | snov | apollo | guess | none
    confidence: float = 0.0  # 0-100
    type: str = "unknown"  # generic | personal | role
    notes: str = ""


# Common email patterns to try (free, no API)
COMMON_PATTERNS = [
    "hello@", "hi@", "info@", "contact@", "team@", "office@",
    "careers@", "jobs@", "hr@", "recruiting@",
    "ceo@", "founder@", "owner@", "admin@",
    "sales@", "hello@", "support@",
]


def _fetch_json(url: str, headers: Dict = None, timeout: int = 15) -> Optional[dict]:
    """Safely fetch JSON from a URL."""
    req = urllib.request.Request(url, headers=headers or {
        "User-Agent": "LeadBot/2.0",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        print(f"[Enrich] HTTP error: {e}")
        return None


def extract_domain(url_or_company: str) -> Optional[str]:
    """Extract a clean domain from a URL or guess from company name."""
    if not url_or_company:
        return None
    s = url_or_company.lower().strip()
    # If it's a URL
    s = re.sub(r'^https?://', '', s)
    s = s.split('/')[0]
    # Remove www.
    s = re.sub(r'^www\.', '', s)
    # Filter out job board domains
    skip = {
        "linkedin.com", "ycombinator.com", "workatastartup.com",
        "remotive.com", "arbeitnow.com", "jobicy.com", "4dayweek.io",
        "bark.com", "goodfirms.co", "clutch.co", "yellowpages.com",
        "yelp.com", "google.com", "github.com", "twitter.com",
        "facebook.com", "indeed.com", "glassdoor.com",
    }
    if any(skip_domain in s for skip_domain in skip):
        return None
    # If it's a company name (no dot), try to guess
    if "." not in s:
        # Common TLDs for companies
        for tld in [".com", ".co", ".io", ".ai", ".co.uk", ".de", ".fr"]:
            guess = s.replace(" ", "").lower() + tld
            return guess
        return s + ".com"
    return s


# ============================================================================
# Provider 1: Hunter.io (domain -> emails)
# ============================================================================
def enrich_hunter(domain: str, api_key: str) -> Optional[EmailResult]:
    """
    Hunter.io Domain Search API.
    Free tier: 25 searches/month.
    Docs: https://hunter.io/api-documentation/v2#domain-search
    """
    if not api_key or not domain:
        return None
    url = f"https://api.hunter.io/v2/domain-search?domain={urllib.parse.quote(domain)}&api_key={urllib.parse.quote(api_key)}"
    data = _fetch_json(url)
    if not data or "data" not in data:
        return None

    emails = data["data"].get("emails", [])
    if not emails:
        return None

    # Pick the most relevant email
    best = None
    for e in emails:
        email_value = e.get("value", "")
        email_type = e.get("type", "unknown")  # generic or personal
        department = (e.get("department") or "").lower()
        position = (e.get("position") or "").lower()

        # Prefer personal emails, then generic in this order:
        # 1. CEO/Founder/HR personal
        # 2. Personal "any"
        # 3. HR/Recruiting/Careers generic
        # 4. Other generic
        if any(role in position for role in ["ceo", "founder", "owner", "head", "director", "hr", "recruit"]):
            best = EmailResult(
                email=email_value, source="hunter", confidence=85,
                type="personal" if email_type == "personal" else "role",
                notes=f"{position or department or 'key person'} (Hunter.io)"
            )
            break
        if email_type == "personal" and not best:
            best = EmailResult(
                email=email_value, source="hunter", confidence=70,
                type="personal", notes="Personal email (Hunter.io)"
            )
        if any(d in department for d in ["hr", "recruiting", "marketing", "sales"]):
            if not best or best.confidence < 60:
                best = EmailResult(
                    email=email_value, source="hunter", confidence=55,
                    type="role", notes=f"{department} team (Hunter.io)"
                )

    if not best and emails:
        first = emails[0]
        best = EmailResult(
            email=first.get("value"),
            source="hunter",
            confidence=40,
            type="generic",
            notes="First available (Hunter.io)"
        )

    return best


# ============================================================================
# Provider 2: Snov.io
# ============================================================================
def enrich_snov(domain: str, client_id: str, client_secret: str) -> Optional[EmailResult]:
    """
    Snov.io Email Finder API.
    Free tier: 50 credits/month.
    """
    if not client_id or not client_secret or not domain:
        return None

    # Step 1: Get access token
    token_url = "https://api.snov.io/v1/oauth/access_token"
    token_data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(token_url, data=token_data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
        access_token = token_data.get("access_token")
        if not access_token:
            return None
    except Exception:
        return None

    # Step 2: Find email
    url = f"https://api.snov.io/v1/get-emails-from-names?access_token={urllib.parse.quote(access_token)}&domain={urllib.parse.quote(domain)}&firstName=CEO&lastName=Founder"
    data = _fetch_json(url)
    if data and "data" in data and data["data"]:
        emails = data["data"]
        if emails and emails[0].get("email"):
            return EmailResult(
                email=emails[0]["email"], source="snov", confidence=60,
                type="personal", notes="Snov.io lookup"
            )
    return None


# ============================================================================
# Provider 3: Apollo.io (best for finding people at a company)
# ============================================================================
def enrich_apollo(domain: str, api_key: str) -> Optional[EmailResult]:
    """
    Apollo.io People API.
    Free tier: 10,000 credits/month (about 1000 enrichments).
    Docs: https://apolloio.github.io/apollo-api-docs/
    """
    if not api_key or not domain:
        return None

    url = "https://api.apollo.io/v1/people/match"
    payload = {
        "api_key": api_key,
        "domain": domain,
        "person_titles": ["CEO", "CTO", "Founder", "Co-Founder", "Head of Engineering", "VP Engineering", "Head of Product", "VP Product", "Head of Design"],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if result.get("person"):
            p = result["person"]
            email = p.get("email") or ""
            if not email:
                # Apollo can give a "email_status" hint even if not verified
                status = p.get("email_status", "")
                if status and p.get("email_not_required"):
                    return EmailResult(
                        email=None, source="apollo", confidence=30,
                        type="unknown", notes=f"Apollo: {p.get('title','?')} found but no email"
                    )
                return None
            return EmailResult(
                email=email, source="apollo", confidence=90,
                type="personal",
                notes=f"{p.get('title','Decision-maker')} at {domain} (Apollo)"
            )
    except Exception as e:
        print(f"[Enrich] Apollo error: {e}")
    return None


# ============================================================================
# Provider 4: Email pattern guessing (free, no API)
# ============================================================================
def enrich_guess(domain: str) -> List[EmailResult]:
    """
    Generate likely email addresses using common patterns.
    No API call - just suggests what to TRY.
    """
    if not domain:
        return []
    results = []
    for prefix in COMMON_PATTERNS[:8]:  # top 8 most common
        results.append(EmailResult(
            email=f"{prefix}{domain}",
            source="guess",
            confidence=20,
            type="role" if prefix not in ["ceo", "founder"] else "role",
            notes="Pattern guess (verify before sending)"
        ))
    return results


# ============================================================================
# Main enricher - tries all providers in order
# ============================================================================
class EmailEnricher:
    """Multi-provider email enrichment."""

    def __init__(self):
        self.hunter_key = os.getenv("HUNTER_API_KEY", "")
        self.snov_id = os.getenv("SNOV_CLIENT_ID", "")
        self.snov_secret = os.getenv("SNOV_CLIENT_SECRET", "")
        self.apollo_key = os.getenv("APOLLO_API_KEY", "")
        self.providers_used = []

    def enrich_lead(self, lead: Dict) -> Dict:
        """
        Try to find an email for a lead.
        Returns updated lead dict with enriched email + metadata.
        """
        # Skip if already has email
        if lead.get("email") and "@" in str(lead.get("email", "")):
            lead["enrichment_status"] = "already_had_email"
            return lead

        # Extract domain
        website = lead.get("website") or lead.get("source_url") or lead.get("company_name") or ""
        domain = extract_domain(website)
        if not domain:
            lead["enrichment_status"] = "no_domain"
            return lead
        lead["enriched_domain"] = domain

        # Try Apollo first (best for finding people)
        if self.apollo_key:
            self.providers_used.append("apollo")
            result = enrich_apollo(domain, self.apollo_key)
            if result and result.email:
                lead["email"] = result.email
                lead["enrichment_status"] = "found"
                lead["enrichment_source"] = result.source
                lead["enrichment_confidence"] = result.confidence
                lead["enrichment_notes"] = result.notes
                return lead

        # Then Hunter.io
        if self.hunter_key:
            self.providers_used.append("hunter")
            result = enrich_hunter(domain, self.hunter_key)
            if result and result.email:
                lead["email"] = result.email
                lead["enrichment_status"] = "found"
                lead["enrichment_source"] = result.source
                lead["enrichment_confidence"] = result.confidence
                lead["enrichment_notes"] = result.notes
                return lead

        # Then Snov.io
        if self.snov_id and self.snov_secret:
            self.providers_used.append("snov")
            result = enrich_snov(domain, self.snov_id, self.snov_secret)
            if result and result.email:
                lead["email"] = result.email
                lead["enrichment_status"] = "found"
                lead["enrichment_source"] = result.source
                lead["enrichment_confidence"] = result.confidence
                lead["enrichment_notes"] = result.notes
                return lead

        # Fall back to guesses (no API cost)
        guesses = enrich_guess(domain)
        if guesses:
            # Use the most-likely guess
            lead["email"] = guesses[0].email
            lead["enrichment_status"] = "guessed"
            lead["enrichment_source"] = "guess"
            lead["enrichment_confidence"] = guesses[0].confidence
            lead["enrichment_notes"] = guesses[0].notes
            lead["enrichment_guesses"] = [g.email for g in guesses[:5]]

        return lead

    def enrich_leads(self, leads: List[Dict], min_score: float = 0) -> List[Dict]:
        """Enrich a batch of leads, return stats."""
        results = {"found": 0, "guessed": 0, "failed": 0, "skipped": 0}
        enriched = []
        for lead in leads:
            if lead.get("score", 0) < min_score:
                results["skipped"] += 1
                continue
            result = self.enrich_lead(lead)
            enriched.append(result)
            status = result.get("enrichment_status", "")
            if status == "found":
                results["found"] += 1
            elif status == "guessed":
                results["guessed"] += 1
            else:
                results["failed"] += 1
        return enriched
