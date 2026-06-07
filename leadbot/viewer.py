#!/usr/bin/env python3
"""
viewer.py - Generate a local HTML page listing all leads from data/*.json
Usage:
    python viewer.py            # writes templates/leads_view.html
    python viewer.py --open     # writes then opens in default browser
"""
import os
import json
import glob
import argparse
import webbrowser
from jinja2 import Template
from datetime import datetime
from config import DATA_DIR


TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><title>LeadBot Leads</title>
<style>
body{font-family:system-ui,sans-serif;max-width:1400px;margin:24px auto;padding:0 16px;background:#0f1115;color:#e6e6e6}
h1{margin-bottom:4px}.sub{color:#888;margin-bottom:24px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid #2a2d35;vertical-align:top}
th{background:#1a1d24;position:sticky;top:0}
tr:hover{background:#161922}
a{color:#7cc4ff;text-decoration:none}
.badge{display:inline-block;padding:2px 6px;border-radius:4px;font-size:12px;font-weight:600}
.b-bark{background:#1e3a5f;color:#9ecbff}
.b-goodfirms{background:#3d1e5f;color:#d09ecb}
.b-hiring{background:#1e5f3d;color:#9ecba8}
.b-outdated{background:#5f3d1e;color:#cbb19e}
.b-frontend_dev{background:#5f1e3d;color:#cb9eb3}
.b-yellowpages{background:#1e3a5f;color:#9ecbff}
.b-clutch{background:#3d1e5f;color:#d09ecb}
.b-github{background:#1e5f3d;color:#9ecba8}
.score{font-weight:600}.score-hi{color:#7fff9f}.score-md{color:#ffd97f}.score-lo{color:#ff8e8e}
input,select{padding:6px;background:#1a1d24;border:1px solid #2a2d35;color:#e6e6e6;border-radius:4px;margin-right:8px;font-family:inherit}
.filters{margin-bottom:16px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.type-tag{font-size:11px;padding:2px 6px;border-radius:3px;background:#2a2d35;color:#9ecbff;margin-left:4px}
.signals{font-size:11px;color:#ffb59e}
</style></head>
<body>
<h1>🕷️ LeadBot Leads</h1>
<div class="sub">Generated {{ generated }} · {{ leads|length }} total leads · sorted by score</div>
<div class="filters">
<input id="q" placeholder="Filter (company, email, country)..." style="width:300px">
<select id="src"><option value="">All sources</option>{% for s in sources %}<option>{{s}}</option>{% endfor %}</select>
<select id="type">
  <option value="">All lead types</option>
  <option value="service_request">🎯 Service requests (Bark)</option>
  <option value="hiring_signal">💼 Hiring signals (Job boards)</option>
  <option value="outdated_site">🔧 Outdated sites (Redesign)</option>
  <option value="agency">🏢 Agencies (Partnerships)</option>
  <option value="designer">🎨 Designers</option>
</select>
<select id="min">
  <option value="0">Any score</option>
  <option value="30">≥30 (decent)</option>
  <option value="50">≥50 (good)</option>
  <option value="70">≥70 (hot)</option>
</select>
<select id="hasemail">
  <option value="">All leads</option>
  <option value="yes">Has email only</option>
</select>
</div>
<table>
<thead><tr>
<th style="width:60px">Score</th>
<th>Company / Title</th>
<th>Contact</th>
<th>Email / Phone</th>
<th>Website</th>
<th>Country</th>
<th>Type</th>
<th>Source</th>
</tr></thead>
<tbody id="rows">
{% for l in leads %}
<tr data-src="{{l.source or '?'}}" data-score="{{(l.score or 0)|int}}" data-type="{{l.lead_type or 'unknown'}}"
    data-hasemail="{{ 'yes' if l.email else 'no' }}"
    data-text="{{ ((l.company_name or '') ~ ' ' ~ (l.title or '') ~ ' ' ~ (l.email or '') ~ ' ' ~ (l.country or ''))|lower }}">
<td><span class="score {% if (l.score or 0) >= 60 %}score-hi{% elif (l.score or 0) >= 30 %}score-md{% else %}score-lo{% endif %}">{{ "%.0f"|format(l.score or 0) }}</span></td>
<td>
  <b>{{ l.company_name or (l.title or '—')[:80] }}</b>
  {% if l.title and l.company_name and l.title != l.company_name %}<br><small style="color:#888">{{ l.title[:80] }}</small>{% endif %}
  {% if l.niche %}<br><small style="color:#7f9ecb">{{ l.niche }}</small>{% endif %}
</td>
<td>{{ l.contact_name or '—' }}{% if l.title %}<br><small style="color:#888">{{ l.title[:50] }}</small>{% endif %}</td>
<td>
  {% if l.email %}<a href="mailto:{{l.email}}">{{l.email}}</a>{% endif %}
  {% if l.phone %}<br><small>{{l.phone}}</small>{% endif %}
  {% if l.outdated_signals %}<br><small class="signals">⚠️ {{ l.outdated_signals|join(', ') }}</small>{% endif %}
</td>
<td>{% if l.website %}<a href="{{l.website}}" target="_blank">↗</a>{% else %}—{% endif %}</td>
<td>{{ l.country or '—' }}</td>
<td><span class="type-tag">{{ (l.lead_type or 'unknown').replace('_', ' ') }}</span></td>
<td><span class="badge b-{{(l.source or '?')|lower}}">{{ l.source or '?' }}</span></td>
</tr>
{% endfor %}
</tbody></table>
<script>
const q=document.getElementById('q'),src=document.getElementById('src'),
      type=document.getElementById('type'),mn=document.getElementById('min'),
      he=document.getElementById('hasemail');
function filter(){
  const t=q.value.toLowerCase(),s=src.value,tp=type.value,
        m=parseInt(mn.value),em=he.value;
  document.querySelectorAll('#rows tr').forEach(r=>{
    const okSrc=!s||r.dataset.src===s;
    const okType=!tp||r.dataset.type===tp;
    const okMin=parseInt(r.dataset.score)>=m;
    const okEm=!em||r.dataset.hasemail===em;
    const okQ=!t||r.dataset.text.includes(t);
    r.style.display=(okSrc&&okType&&okMin&&okEm&&okQ)?'':'none';
  });
}
[q,src,type,mn,he].forEach(e=>e.addEventListener('input',filter));
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(DATA_DIR, "leads_*.json")))
    leads = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    leads.extend(data)
        except Exception:
            pass

    leads.sort(key=lambda l: l.get("score", 0) or 0, reverse=True)
    sources = sorted({l.get("source", "?") for l in leads})

    out = os.path.join(os.path.dirname(__file__), "templates", "leads_view.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(Template(TEMPLATE).render(
            leads=leads, sources=sources,
            generated=datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

    # Stats
    by_type = {}
    for l in leads:
        t = l.get("lead_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    print(f"Wrote {len(leads)} leads -> {out}")
    print(f"By type: {by_type}")
    if args.open:
        webbrowser.open("file://" + os.path.abspath(out))


if __name__ == "__main__":
    main()
