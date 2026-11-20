"""Builds the animated SVGs for the nick10-05 profile README.

Run by .github/workflows/build-profile.yml. Standard library only.

  python3 scripts/build_profile.py assets                 # live data from the GitHub API
  python3 scripts/build_profile.py assets --sample s.json --calendar c.json   # offline

Writes, in a dark and a light version each:
  banner     aurora hero with the project orbit
  card-*     one card per flagship project
  contrib    radial 'year ring' of weekly contributions + streak stats (last 12 months)
  terminal   my latest commits across repos
  divider    animated section divider
"""
import json
import math
import os
import random
import re
import sys
import urllib.request
from datetime import date, timedelta
from html import escape

USER = os.environ.get("PROFILE_USER", "nick10-05")

THEMES = {
    "dark": dict(bg="#060814", bg2="#0C1028", grid="#151B36", ink="#F4F5FB", sub="#A3ABC8", dim="#5E6788",
                 violet="#8B5CF6", cyan="#22D3EE", pink="#F472B6", amber="#F5A524", ok="#34D399",
                 glass="#FFFFFF", glass_a=".05", glass_s=".12", blob_a=".30", star="#FFFFFF",
                 win="#0A0E20", bar="#10162E", border="#1E2647", node="#11183A",
                 iso0=("#141A33", "#0E1328", "#0B1022"),
                 iso=[("#3B2A7A", "#2A1E5C", "#21184A"), ("#6D4AFF", "#4F33C8", "#3E28A0"),
                      ("#2E9BF0", "#1E74BE", "#175C98"), ("#3DE3F7", "#1FB3C9", "#168E9F")]),
    "light": dict(bg="#FBFAFF", bg2="#F1EEFF", grid="#E7E3F7", ink="#12142B", sub="#4B5170", dim="#8A8FA8",
                  violet="#6D3AF0", cyan="#0891B2", pink="#DB2777", amber="#C2780A", ok="#059669",
                  glass="#FFFFFF", glass_a=".65", glass_s=".9", blob_a=".28", star="#6D3AF0",
                  win="#FFFFFF", bar="#F5F3FF", border="#E4E0F5", node="#FFFFFF",
                  iso0=("#ECEAF7", "#DCD8EE", "#D0CBE6"),
                  iso=[("#C9B8FF", "#AE97F5", "#9C83EC"), ("#8B6CFF", "#6F4FE8", "#5F3FD6"),
                       ("#3BA4F5", "#2384D2", "#1A70B7"), ("#22D3EE", "#13A9C2", "#0E8CA2")]),
}

MONO = 'ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace'
SANS = '-apple-system, "Segoe UI", Inter, Helvetica, Arial, sans-serif'

PROJECTS = [
    dict(slug="relayforge", rank="01", name="RelayForge", badge="DEPLOYED · FLAGSHIP", dot="#818CF8",
         grad=("#A78BFA", "#6366F1", "#38BDF8"),
         tagline="Durable webhook relay. No event is ever lost.",
         sub="Outbox · Postgres queue with leases · SSRF-safe signed delivery",
         stats=[("555", "tests on real Postgres"), ("665/s", "peak ingest, local k6"),
                ("100%", "delivered in crash test")],
         tech=["Node.js 24", "TypeScript", "Fastify", "PostgreSQL", "Drizzle", "React", "Docker", "k6"]),
    dict(slug="hostelconnect", rank="02", name="HostelConnect", badge="DEPLOYED · BUILT FOR MY HOSTEL", dot="#EC4899",
         grad=("#FB923C", "#EC4899", "#8B5CF6"),
         tagline="Built to replace my hostel's WhatsApp chaos.",
         sub="Complaints · notices · UPI fees · polls · up to 200 students",
         stats=[("160+", "test files"), ("24", "SQL migrations"), ("₹0", "infra per month")],
         tech=["React", "TypeScript", "Express", "PostgreSQL", "Supabase", "Tailwind", "Docker"]),
    dict(slug="driveradar", rank="03", name="DriveRadar", badge="DEPLOYED · AI", dot="#22D3EE",
         grad=("#10B981", "#22D3EE", "#6366F1"),
         tagline="AI placement-drive radar for my batch.",
         sub="Guarded LLM extraction · eligibility engine · Telegram alerts",
         stats=[("99%", "backend test coverage"), ("24h·3h", "deadline alerts"), ("1×", "exactly-once reminders")],
         tech=["Python", "FastAPI", "SQLAlchemy", "PostgreSQL", "React", "TypeScript", "LLM"]),
]


def typed_clip(cid, x, y, h, chars, char_w, begin, per_char=0.045):
    """A clipPath whose width grows one character at a time (typewriter effect)."""
    widths = ";".join(str(round(i * char_w, 1)) for i in range(chars + 1))
    dur = max(chars * per_char, 0.1)
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" height="{h}" width="0">'
            f'<animate attributeName="width" values="{widths}" dur="{dur:.2f}s" begin="{begin}s" '
            f'fill="freeze" calcMode="discrete"/></rect></clipPath>')


def stars(t, n, w, h, seed=7):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([0.6, 0.8, 1.0, 1.3])
        d = rnd.uniform(2.5, 6)
        b = rnd.uniform(0, 5)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{t["star"]}" opacity=".2">'
                   f'<animate attributeName="opacity" values=".08;.6;.08" dur="{d:.1f}s" begin="-{b:.1f}s" '
                   f'repeatCount="indefinite"/></circle>')
    return "".join(out)


def aurora(t, w, h):
    """Three blurred colour blobs drifting slowly: the 'aurora' background."""
    blobs = [(t["violet"], [(260, 60), (420, 140), (300, 240), (260, 60)], 260, 18),
             (t["cyan"], [(900, 260), (760, 120), (1020, 80), (900, 260)], 230, 22),
             (t["pink"], [(640, 330), (560, 200), (760, 300), (640, 330)], 200, 16)]
    out = []
    for i, (c, pts, r, dur) in enumerate(blobs):
        cx = ";".join(str(p[0] * w // 1200) for p in pts)
        cy = ";".join(str(p[1] * h // 360) for p in pts)
        out.append(f'<circle cx="{pts[0][0]}" cy="{pts[0][1]}" r="{r}" fill="{c}" opacity="{t["blob_a"]}" filter="url(#blur)">'
                   f'<animate attributeName="cx" values="{cx}" dur="{dur}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="cy" values="{cy}" dur="{dur}s" repeatCount="indefinite"/></circle>')
    return "".join(out)


def border_defs(t, gid):
    return (f'<linearGradient id="{gid}" gradientUnits="objectBoundingBox" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{t["violet"]}"/><stop offset=".5" stop-color="{t["cyan"]}"/>'
            f'<stop offset="1" stop-color="{t["pink"]}"/>'
            f'<animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" '
            f'dur="20s" repeatCount="indefinite"/></linearGradient>')


# ---------------------------------------------------------------- banner

def banner(t):
    W, H = 1200, 360
    cx, cy = 860, 184
    orbits = [(122, 48, PROJECTS[0], 24, 0), (160, 68, PROJECTS[2], 36, -14), (192, 92, PROJECTS[1], 48, -30)]
    orbit_svg = []
    for i, (rx, ry, p, dur, off) in enumerate(orbits):
        pid = f"o{i}"
        d = f"M{cx - rx} {cy} a{rx} {ry} 0 1 0 {2 * rx} 0 a{rx} {ry} 0 1 0 {-2 * rx} 0"
        c = p["dot"]
        orbit_svg.append(f'''
    <path id="{pid}" d="{d}" fill="none" stroke="{t['sub']}" stroke-opacity=".22" stroke-width="1.2" stroke-dasharray="3 7">
      <animate attributeName="stroke-dashoffset" values="0;-40" dur="{3 + i}s" repeatCount="indefinite"/>
    </path>
    <g class="still" transform="translate({cx + [rx, -rx * .6, rx * .3][i]:.0f} {cy + [0, ry * .8, -ry][i]:.0f})"><circle r="6" fill="{c}"/>
      <text x="12" y="-10" font-family='{MONO}' font-size="16" font-weight="600" fill="{t['ink']}">{p['name']}</text></g>
    <g class="motion">
      <animateMotion dur="{dur}s" begin="{off}s" repeatCount="indefinite"><mpath href="#{pid}"/></animateMotion>
      <circle r="13" fill="{c}" opacity=".18"><animate attributeName="r" values="9;15;9" dur="2.4s" repeatCount="indefinite"/></circle>
      <circle r="6" fill="{c}"/>
      <text x="12" y="-10" font-family='{MONO}' font-size="16" font-weight="600" fill="{t['ink']}">{p['name']}</text>
    </g>''')
    roles = ["Full-stack engineer.", "Backend reliability nerd.", "I ship software real people use."]
    role_svg = "".join(
        f'<text class="role role{i}" style="animation-delay:{i * 5}s" x="64" y="214" font-family=\'{SANS}\' font-size="28" '
        f'fill="{t["sub"]}"><tspan fill="{t["cyan"]}" font-family=\'{MONO}\'>&gt; </tspan>{escape(r)}</text>'
        for i, r in enumerate(roles))
    chips = [("3", "deployed apps"), ("240+", "test files"), ("₹0", "/ month infra")]
    chip_svg, x = [], 64
    for i, (big, small) in enumerate(chips):
        wdt = 44 + len(big) * 15 + len(small) * 9.4
        chip_svg.append(f'''
    <g class="fade" style="animation-delay:{1.4 + i * .18:.2f}s">
      <rect x="{x}" y="270" width="{wdt:.0f}" height="46" rx="23" fill="{t['glass']}" fill-opacity="{t['glass_a']}" stroke="{t['glass']}" stroke-opacity="{t['glass_s']}"/>
      <text x="{x + 20}" y="300" font-family='{SANS}' font-size="21"><tspan font-weight="800" fill="url(#name)">{big}</tspan><tspan dx="8" fill="{t['sub']}" font-size="18">{small}</tspan></text>
    </g>''')
        x += wdt + 12
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Nikhil Chandrakanti: full-stack engineer who ships software real people use. Projects: RelayForge, HostelConnect, DriveRadar.">
  <style>
    .fade {{ opacity: 0; animation: in .9s cubic-bezier(.2,.7,.2,1) forwards; }}
    @keyframes in {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
    .role {{ opacity: 0; animation: role 15s infinite; }}
    @keyframes role {{ 0% {{ opacity: 0; transform: translateY(12px); }} 4%,29% {{ opacity: 1; transform: none; }}
                      33%,100% {{ opacity: 0; transform: translateY(-12px); }} }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .fade, .bar, .row, .end {{ animation: none !important; opacity: 1 !important; }}
      .role {{ animation: none !important; opacity: 0; }} .role0 {{ opacity: 1; }}
      .motion {{ display: none; }} .still {{ display: inline; }}
    }}
    .still {{ display: none; }}
  </style>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg']}"/><stop offset="1" stop-color="{t['bg2']}"/></linearGradient>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
    <pattern id="g" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{t['grid']}" stroke-width="1"/></pattern>
    <radialGradient id="gm" cx=".3" cy=".4" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <mask id="gridmask"><rect width="{W}" height="{H}" fill="url(#gm)"/></mask>
    <linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="700" y2="0" spreadMethod="reflect">
      <stop offset="0" stop-color="{t['violet']}"/><stop offset=".35" stop-color="{t['cyan']}"/>
      <stop offset=".7" stop-color="{t['pink']}"/><stop offset="1" stop-color="{t['violet']}"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="0;700;0" dur="16s" repeatCount="indefinite"/>
    </linearGradient>
    <radialGradient id="core"><stop offset="0" stop-color="{t['cyan']}"/><stop offset=".6" stop-color="{t['violet']}"/><stop offset="1" stop-color="{t['violet']}" stop-opacity="0"/></radialGradient>
    {border_defs(t, "edge")}
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    {aurora(t, W, H)}
    <rect width="{W}" height="{H}" fill="url(#g)" mask="url(#gridmask)" opacity=".7"/>
    {stars(t, 28, W, H)}
  </g>
  <rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="21" fill="none" stroke="url(#edge)" stroke-width="2" stroke-opacity=".55"/>

  <g class="fade" style="animation-delay:.1s">
    <rect x="64" y="50" width="300" height="34" rx="17" fill="{t['ok']}" fill-opacity=".12" stroke="{t['ok']}" stroke-opacity=".45"/>
    <circle cx="82" cy="67" r="5" fill="{t['ok']}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
    <circle cx="82" cy="67" r="5" fill="none" stroke="{t['ok']}"><animate attributeName="r" values="5;11" dur="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="1.6s" repeatCount="indefinite"/></circle>
    <text x="98" y="73" font-family='{MONO}' font-size="15" font-weight="600" fill="{t['ok']}" letter-spacing="1">OPEN TO SDE ROLES · 2027</text>
  </g>
  <g class="fade" style="animation-delay:.35s">
    <text x="61" y="152" font-family='{SANS}' font-size="62" font-weight="800" fill="url(#name)" letter-spacing="-1.5">Nikhil Chandrakanti</text>
  </g>
  {role_svg}
  <g class="fade" style="animation-delay:1.1s">
    <text x="64" y="250" font-family='{MONO}' font-size="18" fill="{t['sub']}">React · Node.js · TypeScript · Python · PostgreSQL<tspan class="cursor" fill="{t['cyan']}"> ▍</tspan></text>
  </g>
  {''.join(chip_svg)}

  <g class="fade" style="animation-delay:.6s">
    {''.join(orbit_svg)}
    <circle cx="{cx}" cy="{cy}" r="58" fill="url(#core)" opacity=".35" filter="url(#glow)">
      <animate attributeName="r" values="50;64;50" dur="4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{cx}" cy="{cy}" r="30" fill="{t['node']}" stroke="url(#edge)" stroke-width="2.5"/>
    <text x="{cx}" y="{cy + 6}" text-anchor="middle" font-family='{MONO}' font-size="18" font-weight="700" fill="{t['ink']}">&lt;/&gt;</text>
    <circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{t['cyan']}" opacity="0">
      <animate attributeName="r" values="30;70" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".7;0" dur="3s" repeatCount="indefinite"/>
    </circle>
  </g>
</svg>
'''


# ---------------------------------------------------------------- project cards

def card(t, p):
    W, H = 1200, 300
    g0, g1, g2 = p["grad"]
    sl = p["slug"]
    per = 2 * (W - 4 + H - 4)
    stats_svg = []
    for i, (big, small) in enumerate(p["stats"]):
        x = 780 + i * 134
        stats_svg.append(f'''
    <g class="fade" style="animation-delay:{.5 + i * .15:.2f}s">
      <rect x="{x}" y="40" width="124" height="132" rx="18" fill="{t['glass']}" fill-opacity="{t['glass_a']}" stroke="{t['glass']}" stroke-opacity="{t['glass_s']}"/>
      <text x="{x + 62}" y="{96}" text-anchor="middle" font-family='{SANS}' font-size="{34 if len(big) <= 4 else 27}" font-weight="800" fill="url(#pg-{sl})">{escape(big)}</text>
      {small_lines(t, x + 62, small)}
    </g>''')
    pills, x = [], 56
    for i, tech in enumerate(p["tech"]):
        w = 26 + len(tech) * 9.2
        pills.append(f'<g class="fade" style="animation-delay:{.8 + i * .06:.2f}s"><rect x="{x:.0f}" y="228" width="{w:.0f}" height="36" rx="18" '
                     f'fill="{g1}" fill-opacity=".12" stroke="{g1}" stroke-opacity=".4"/>'
                     f'<text x="{x + w / 2:.0f}" y="252" text-anchor="middle" font-family=\'{MONO}\' font-size="15.5" fill="{t["ink"]}">{escape(tech)}</text></g>')
        x += w + 9
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(p['name'])}: {escape(p['tagline'])}">
  <style>
    .fade {{ opacity: 0; animation: in .8s cubic-bezier(.2,.7,.2,1) forwards; }}
    @keyframes in {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
    @media (prefers-reduced-motion: reduce) {{ .fade {{ animation: none !important; opacity: 1 !important; }} .motion {{ display: none; }} }}
  </style>
  <defs>
    <linearGradient id="bg-{sl}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg']}"/><stop offset="1" stop-color="{t['bg2']}"/></linearGradient>
    <linearGradient id="pg-{sl}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="460" y2="0" spreadMethod="reflect">
      <stop offset="0" stop-color="{g0}"/><stop offset=".5" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="0;460;0" dur="14s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="sw-{sl}" x1="0" x2="1"><stop offset="0" stop-color="{g0}"/><stop offset=".5" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient>
    <filter id="b-{sl}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
    <clipPath id="c-{sl}"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  </defs>
  <g clip-path="url(#c-{sl})">
    <rect width="{W}" height="{H}" fill="url(#bg-{sl})"/>
    <circle cx="1060" cy="60" r="180" fill="{g1}" opacity="{float(t['blob_a']) * .55:.2f}" filter="url(#b-{sl})">
      <animate attributeName="cx" values="1060;920;1060" dur="20s" repeatCount="indefinite"/>
    </circle>
    <circle cx="120" cy="300" r="150" fill="{g2}" opacity="{float(t['blob_a']) * .4:.2f}" filter="url(#b-{sl})">
      <animate attributeName="cy" values="300;240;300" dur="16s" repeatCount="indefinite"/>
    </circle>
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="21" fill="none" stroke="{t['border']}" stroke-width="2"/>
  <rect class="motion" x="2" y="2" width="{W - 4}" height="{H - 4}" rx="20" fill="none" stroke="url(#sw-{sl})" stroke-width="2" stroke-opacity=".75"
        stroke-dasharray="{per * .16:.0f} {per * .84:.0f}" stroke-linecap="round">
    <animate attributeName="stroke-dashoffset" values="0;-{per}" dur="12s" repeatCount="indefinite"/>
  </rect>

  <g class="fade" style="animation-delay:.05s">
    <text x="56" y="62" font-family='{MONO}' font-size="17" font-weight="700" fill="{g1}" letter-spacing="2">{p['rank']} /</text>
    <rect x="112" y="40" width="{30 + len(p['badge']) * 10.2:.0f}" height="32" rx="16" fill="{t['ok']}" fill-opacity=".12" stroke="{t['ok']}" stroke-opacity=".45"/>
    <circle cx="129" cy="56" r="5" fill="{t['ok']}"><animate attributeName="opacity" values="1;.3;1" dur="2s" repeatCount="indefinite"/></circle>
    <text x="142" y="62" font-family='{MONO}' font-size="14.5" font-weight="700" fill="{t['ok']}" letter-spacing="1">{escape(p['badge'])}</text>
  </g>
  <g class="fade" style="animation-delay:.2s">
    <text x="53" y="132" font-family='{SANS}' font-size="58" font-weight="800" letter-spacing="-1.5" fill="url(#pg-{sl})">{escape(p['name'])}</text>
  </g>
  <g class="fade" style="animation-delay:.35s">
    <text x="56" y="172" font-family='{SANS}' font-size="24" font-weight="600" fill="{t['ink']}">{escape(p['tagline'])}</text>
    <text x="56" y="204" font-family='{SANS}' font-size="18" fill="{t['sub']}">{escape(p['sub'])}</text>
  </g>
  {''.join(stats_svg)}
  {''.join(pills)}
</svg>
'''


def small_lines(t, x, text):
    return "".join(f'<text x="{x}" y="{128 + j * 19}" text-anchor="middle" font-family=\'{SANS}\' font-size="15.5" '
                   f'fill="{t["sub"]}">{escape(line)}</text>' for j, line in enumerate(wrap(text, 13)))


def wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return lines[:2]


# ---------------------------------------------------------------- 3D contribution city

def stats_of(cal):
    counts = [d["count"] for d in cal]
    total = sum(counts)
    longest = cur = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today not started yet: streak still alive from yesterday
        i -= 1
    while i >= 0 and counts[i]:
        cur += 1
        i -= 1
    best = max(cal, key=lambda d: d["count"]) if cal else {"date": "-", "count": 0}
    active = sum(1 for c in counts if c)
    return total, cur, longest, best, active


def levels(cal):
    nz = sorted(d["count"] for d in cal if d["count"])
    if not nz:
        return [0] * len(cal)
    q = [nz[int(len(nz) * k)] for k in (.25, .5, .75)]
    out = []
    for d in cal:
        c = d["count"]
        out.append(0 if c == 0 else 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4)
    return out


def contrib(t, cal):
    """A radial 'year ring': one bar per week around a circle, total in the middle."""
    W, H = 1200, 470
    cx, cy, r0, rmax = 300, 238, 84, 178
    weeks = [cal[i:i + 7] for i in range(0, len(cal), 7)]
    wsum = [sum(d["count"] for d in w) for w in weeks]
    n, mx = len(weeks), max(wsum) or 1
    nz = sorted(v for v in wsum if v)
    q = [nz[int(len(nz) * k)] for k in (.25, .5, .75)] if nz else [0, 0, 0]
    cols = [t["violet"], t["violet"], t["cyan"], t["cyan"], t["pink"]]
    bars, labels = [], []
    seen_month = None
    for i, (w, v) in enumerate(zip(weeks, wsum)):
        ang = math.radians(-90 + (i + .5) * 360 / n)
        ca, sa = math.cos(ang), math.sin(ang)
        x1, y1 = cx + r0 * ca, cy + r0 * sa
        m = date.fromisoformat(w[0]["date"])
        if m.month != seen_month and i < n - 3:
            seen_month = m.month
            lx, ly = cx + (rmax + 26) * ca, cy + (rmax + 26) * sa
            labels.append(f'<text x="{lx:.0f}" y="{ly + 4:.0f}" text-anchor="middle" font-family=\'{MONO}\' font-size="12" fill="{t["dim"]}">{m.strftime("%b").upper()}</text>')
        if v == 0:
            bars.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x1 + 8 * ca:.1f}" y2="{y1 + 8 * sa:.1f}" stroke="{t["dim"]}" stroke-opacity=".35" stroke-width="6" stroke-linecap="round"/>')
            continue
        lvl = 1 if v <= q[0] else 2 if v <= q[1] else 3 if v <= q[2] else 4
        L = 14 + math.sqrt(v / mx) * (rmax - r0 - 14)
        x2, y2 = cx + (r0 + L) * ca, cy + (r0 + L) * sa
        delay = .3 + i * .025
        bars.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{cols[lvl]}" stroke-width="9" stroke-linecap="round" opacity=".95">'
                    f'<animate attributeName="x2" from="{x1:.1f}" to="{x2:.1f}" dur=".9s" begin="{delay:.2f}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/>'
                    f'<animate attributeName="y2" from="{y1:.1f}" to="{y2:.1f}" dur=".9s" begin="{delay:.2f}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></line>')
    total, cur, longest, bestd, active = stats_of(cal)
    best_label = date.fromisoformat(bestd["date"]).strftime("%d %b") if bestd["count"] else "-"
    days = [0] * 7
    for d in cal:
        days[date.fromisoformat(d["date"]).weekday()] += d["count"]
    top_day = ["Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays", "Sundays"][days.index(max(days))] if total else "-"
    tiles = [(str(cur), "current streak (days)"), (str(longest), "longest streak (days)"),
             (str(active), "active days"), (str(bestd["count"]), f"best day · {best_label}")]
    tile_svg = []
    for i, (big, small) in enumerate(tiles):
        tx, ty = 640 + (i % 2) * 262, 166 + (i // 2) * 116
        tile_svg.append(f'''
    <g class="fade" style="animation-delay:{1.2 + i * .15:.2f}s">
      <rect x="{tx}" y="{ty}" width="248" height="102" rx="18" fill="{t['glass']}" fill-opacity="{t['glass_a']}" stroke="{t['glass']}" stroke-opacity="{t['glass_s']}"/>
      <text x="{tx + 24}" y="{ty + 54}" font-family='{SANS}' font-size="38" font-weight="800" fill="url(#cg)">{big}</text>
      <text x="{tx + 24}" y="{ty + 82}" font-family='{SANS}' font-size="16" fill="{t['sub']}">{escape(small)}</text>
    </g>''')
    end = date.fromisoformat(cal[-1]["date"]).strftime("%d %b %Y")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total} contributions in the last 12 months as a ring of weekly bars; longest streak {longest} days, current streak {cur} days">
  <style>
    .fade {{ opacity: 0; animation: in .8s ease-out forwards; }}
    @keyframes in {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
    @media (prefers-reduced-motion: reduce) {{ .fade {{ animation: none !important; opacity: 1 !important; }} .motion {{ display: none; }} }}
  </style>
  <defs>
    <linearGradient id="cbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg']}"/><stop offset="1" stop-color="{t['bg2']}"/></linearGradient>
    <linearGradient id="cg" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1160" y2="0" spreadMethod="reflect">
      <stop offset="0" stop-color="{t['violet']}"/><stop offset=".5" stop-color="{t['cyan']}"/><stop offset="1" stop-color="{t['pink']}"/>
    </linearGradient>
    <linearGradient id="arc" x1="0" x2="1"><stop offset="0" stop-color="{t['cyan']}" stop-opacity="0"/><stop offset="1" stop-color="{t['cyan']}" stop-opacity=".9"/></linearGradient>
    <filter id="cb" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
    <clipPath id="cc"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  </defs>
  <g clip-path="url(#cc)">
    <rect width="{W}" height="{H}" fill="url(#cbg)"/>
    <circle cx="{cx}" cy="{cy}" r="190" fill="{t['violet']}" opacity="{float(t['blob_a']) * .45:.2f}" filter="url(#cb)"/>
    <circle cx="1000" cy="110" r="150" fill="{t['cyan']}" opacity="{float(t['blob_a']) * .35:.2f}" filter="url(#cb)"/>
    {stars(t, 22, W, H, seed=3)}
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="21" fill="none" stroke="{t['border']}" stroke-width="2"/>

  <circle cx="{cx}" cy="{cy}" r="{r0 - 10}" fill="none" stroke="{t['border']}" stroke-width="1.5"/>
  <circle cx="{cx}" cy="{cy}" r="{rmax + 6}" fill="none" stroke="{t['border']}" stroke-width="1" stroke-dasharray="2 6"/>
  <g class="motion">
    <path d="M{cx} {cy - r0 + 10} A{r0 - 10} {r0 - 10} 0 0 1 {cx + r0 - 10} {cy}" fill="none" stroke="url(#arc)" stroke-width="3" stroke-linecap="round"/>
    <animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" dur="14s" repeatCount="indefinite"/>
  </g>
  {''.join(bars)}
  {''.join(labels)}
  <g class="fade" style="animation-delay:.8s">
    <text x="{cx}" y="{cy + 8}" text-anchor="middle" font-family='{SANS}' font-size="{44 if total < 10000 else 36}" font-weight="800" letter-spacing="-1" fill="url(#cg)">{total:,}</text>
    <text x="{cx}" y="{cy + 32}" text-anchor="middle" font-family='{SANS}' font-size="14" fill="{t['sub']}">contributions</text>
  </g>

  <g class="fade" style="animation-delay:.3s">
    <text x="640" y="96" font-family='{MONO}' font-size="17" font-weight="700" fill="{t['cyan']}" letter-spacing="2">MY YEAR IN ORBIT</text>
    <text x="640" y="126" font-family='{SANS}' font-size="17" fill="{t['sub']}">One bar per week · to {end} · busiest on {top_day}</text>
  </g>
  {''.join(tile_svg)}
</svg>
'''


# ---------------------------------------------------------------- terminal

def terminal(t, commits, latest):
    n = len(commits)
    line_h, top = 36, 66
    h = top + (n + 2) * line_h + 40
    cmd = f"git log --author={USER} --all-repos --oneline -n {n}"
    cw = 10.85  # approx monospace advance at 18px
    rows = []
    for i, c in enumerate(commits):
        yy = top + (i + 1) * line_h + 24
        delay = 1.9 + i * 0.32
        msg = c["msg"] if len(c["msg"]) <= 56 else c["msg"][:55] + "…"
        rows.append(f'''
  <g class="row" style="animation-delay:{delay:.2f}s">
    <text x="48" y="{yy}" font-family='{MONO}' font-size="18">
      <tspan fill="{t['amber']}">{escape(c["sha"][:7])}</tspan><tspan x="148" fill="{t['cyan']}">{escape(c["repo"] if len(c["repo"]) <= 19 else c["repo"][:18] + "…")}</tspan><tspan x="385" fill="{t['ink']}">{escape(msg)}</tspan>
    </text>
    <text x="1152" y="{yy}" text-anchor="end" font-family='{MONO}' font-size="15" fill="{t['dim']}">{escape(c["date"])}</text>
  </g>''')
    end_y = top + (n + 1) * line_h + 24
    end_delay = 1.9 + n * 0.32 + 0.2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {h}" width="1200" height="{h}" role="img" aria-label="My most recent commits across my public repositories">
  <style>
    .row {{ opacity: 0; animation: in .45s ease-out forwards; }}
    @keyframes in {{ from {{ opacity: 0; transform: translateX(-10px); }} to {{ opacity: 1; transform: none; }} }}
    .end {{ opacity: 0; animation: show 0s forwards {end_delay:.2f}s; }}
    @keyframes show {{ to {{ opacity: 1; }} }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .fade, .bar, .row, .end {{ animation: none !important; opacity: 1 !important; }}
      .role {{ animation: none !important; opacity: 0; }} .role0 {{ opacity: 1; }}
      .motion {{ display: none; }} .still {{ display: inline; }}
    }}
    .still {{ display: none; }}
  </style>
  <defs>{typed_clip("cmd", 48, top, 36, len(cmd) + 2, cw, 0.4, 0.028)}{border_defs(t, "tedge")}</defs>
  <rect x="1" y="1" width="1198" height="{h - 2}" rx="16" fill="{t['win']}" stroke="url(#tedge)" stroke-opacity=".6" stroke-width="2"/>
  <path d="M2 17a15 15 0 0 1 15-15h1166a15 15 0 0 1 15 15v35H2z" fill="{t['bar']}"/>
  <circle cx="30" cy="27" r="7" fill="#FF5F57"/><circle cx="54" cy="27" r="7" fill="#FEBC2E"/><circle cx="78" cy="27" r="7" fill="#28C840"/>
  <text x="600" y="33" text-anchor="middle" font-family='{MONO}' font-size="14" fill="{t['dim']}">nikhil@github: ~ · recent commits</text>
  <g>
    <circle cx="1120" cy="27" r="5" fill="{t['ok']}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
    <text x="1132" y="32" font-family='{MONO}' font-size="13" fill="{t['ok']}">live</text>
  </g>
  <g clip-path="url(#cmd)">
    <text x="48" y="{top + 24}" font-family='{MONO}' font-size="18" fill="{t['ink']}"><tspan fill="{t['ok']}">$</tspan> {escape(cmd)}</text>
  </g>
  {''.join(rows)}
  <g class="end">
    <text x="48" y="{end_y}" font-family='{MONO}' font-size="18" fill="{t['ok']}">$<tspan class="cursor" fill="{t['violet']}"> ▍</tspan></text>
  </g>
  <text x="1152" y="{h - 16}" text-anchor="end" font-family='{MONO}' font-size="12" fill="{t['dim']}">synced from the GitHub API by GitHub Actions · latest push {escape(latest)}</text>
</svg>
'''


# ---------------------------------------------------------------- divider

def divider(t):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 24" width="1200" height="24" aria-hidden="true">
  <defs>
    <linearGradient id="d" x1="0" x2="1">
      <stop offset="0" stop-color="{t['violet']}" stop-opacity="0"/>
      <stop offset=".35" stop-color="{t['violet']}"/><stop offset=".65" stop-color="{t['cyan']}"/>
      <stop offset="1" stop-color="{t['pink']}" stop-opacity="0"/>
    </linearGradient>
    <filter id="dg" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="3"/></filter>
  </defs>
  <line x1="0" y1="12" x2="1200" y2="12" stroke="{t['border']}" stroke-width="1"/>
  <g>
    <rect x="0" y="10" width="360" height="4" rx="2" fill="url(#d)" filter="url(#dg)"/>
    <rect x="0" y="11" width="360" height="2" fill="url(#d)"/>
    <animateTransform attributeName="transform" type="translate" values="-360 0;1200 0" dur="8s" repeatCount="indefinite"/>
  </g>
</svg>
'''


# ---------------------------------------------------------------- data

def api(path, token, body=None):
    req = urllib.request.Request(f"https://api.github.com{path}",
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Accept": "application/vnd.github+json",
                                          "User-Agent": f"{USER}-profile-builder"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_commits(token, limit=6, per_repo=2):
    repos = api(f"/users/{USER}/repos?type=owner&sort=pushed&per_page=30", token)
    repos = [r for r in repos if not r["fork"] and r["name"] != USER][:8]
    commits = []
    for r in repos:
        try:
            items = api(f"/repos/{USER}/{r['name']}/commits?author={USER}&per_page=10", token)
        except Exception as e:  # empty repo, etc.
            print(f"skip {r['name']}: {e}", file=sys.stderr)
            continue
        kept = 0
        for c in items:
            msg = c["commit"]["message"].split("\n")[0]
            if msg.startswith("Merge "):
                continue
            commits.append({"sha": c["sha"], "repo": r["name"], "msg": msg,
                            "when": c["commit"]["author"]["date"],
                            "date": c["commit"]["author"]["date"][:10]})
            kept += 1
            if kept == per_repo:  # show range across projects, not one busy repo
                break
    commits.sort(key=lambda c: c["when"], reverse=True)
    return commits[:limit]


def fetch_calendar(token):
    """Contribution calendar: GraphQL first, the public contributions page as a fallback."""
    if token:
        try:
            q = ('query($u:String!){user(login:$u){contributionsCollection{contributionCalendar'
                 '{weeks{contributionDays{date contributionCount}}}}}}')
            data = api("/graphql", token, {"query": q, "variables": {"u": USER}})
            weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            return [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]
        except Exception as e:
            print(f"graphql calendar failed, trying the public page: {e}", file=sys.stderr)
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                                 headers={"User-Agent": f"{USER}-profile-builder"})
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    dates = dict(re.findall(r'data-date="(\d{4}-\d\d-\d\d)"[^>]*id="([^"]+)"', html))
    dates.update({d: i for i, d in re.findall(r'id="([^"]+)"[^>]*data-date="(\d{4}-\d\d-\d\d)"', html)})
    tips = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html))
    cal = []
    for d, cid in sorted(dates.items()):
        m = re.match(r"(\d+)", tips.get(cid, ""))
        cal.append({"date": d, "count": int(m.group(1)) if m else 0})
    return cal


def calendar_from_days(days, end=None):
    """Turn {date: count} into a 53-week calendar ending today (used for offline builds)."""
    end = end or date.today()
    start = end - timedelta(days=364 + (end.weekday() + 1) % 7)
    return [{"date": (start + timedelta(i)).isoformat(), "count": days.get((start + timedelta(i)).isoformat(), 0)}
            for i in range((end - start).days + 1)]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    os.makedirs(out, exist_ok=True)
    token = os.environ.get("GITHUB_TOKEN")
    if "--sample" in sys.argv:
        commits = json.load(open(sys.argv[sys.argv.index("--sample") + 1]))
    else:
        commits = fetch_commits(token)
    cal = None
    try:
        if "--calendar" in sys.argv:
            raw = json.load(open(sys.argv[sys.argv.index("--calendar") + 1]))
            cal = calendar_from_days(raw) if isinstance(raw, dict) else raw
        else:
            cal = fetch_calendar(token)
    except Exception as e:
        print(f"no calendar ({e}); keeping the existing contribution SVGs", file=sys.stderr)
    for name, t in THEMES.items():
        files = [("banner", banner(t)), ("divider", divider(t))]
        files += [(f"card-{p['slug']}", card(t, p)) for p in PROJECTS]
        if commits:
            files.append(("terminal", terminal(t, commits, commits[0]["date"])))
        if cal:
            files.append(("contrib", contrib(t, cal)))
        for kind, svg in files:
            with open(os.path.join(out, f"{kind}-{name}.svg"), "w", encoding="utf-8") as f:
                f.write(svg)
    print(f"wrote assets: {len(commits)} commits, calendar days: {len(cal) if cal else 0}")


if __name__ == "__main__":
    main()
