"""Builds the animated SVGs for the nick10-05 profile README.

Run by .github/workflows/build-profile.yml. Standard library only.

  python3 scripts/build_profile.py assets                # live data from the GitHub API
  python3 scripts/build_profile.py assets --sample s.json  # offline, for local testing
"""
import json
import os
import sys
import urllib.request
from html import escape

USER = os.environ.get("PROFILE_USER", "nick10-05")

THEMES = {
    "dark": dict(bg="#0B1020", grid="#1A2236", ink="#F2F4F8", sub="#9AA4B8", dim="#5B667D",
                 accent="#F5A524", teal="#2DD4BF", ok="#34D399", node="#141B2E", line="#2A3550",
                 win="#0F1528", bar="#151D33", border="#232C45", shine="#FFFFFF"),
    "light": dict(bg="#FBFAF6", grid="#ECE8DD", ink="#14182A", sub="#4A5268", dim="#8A90A0",
                  accent="#C97A00", teal="#0F8F80", ok="#0E9F6E", node="#FFFFFF", line="#D6D1C4",
                  win="#FFFFFF", bar="#F3F1EA", border="#E2DED2", shine="#C97A00"),
}

MONO = 'ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace'
SANS = '-apple-system, "Segoe UI", Inter, Helvetica, Arial, sans-serif'


def typed_clip(cid, x, y, h, chars, char_w, begin, per_char=0.045):
    """A clipPath whose width grows one character at a time (typewriter effect)."""
    widths = ";".join(str(round(i * char_w, 1)) for i in range(chars + 1))
    dur = max(chars * per_char, 0.1)
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" height="{h}" width="0">'
            f'<animate attributeName="width" values="{widths}" dur="{dur:.2f}s" begin="{begin}s" '
            f'fill="freeze" calcMode="discrete"/></rect></clipPath>')


# ---------------------------------------------------------------- banner

def banner(t):
    xs, y, dur = [740, 860, 980, 1100], 150, 4
    stages = [("commit", 0.0), ("test", 0.25), ("deploy", 0.5), ("live", 0.75)]
    nodes = []
    for (label, k), x in zip(stages, xs):
        nodes.append(f'''
    <circle cx="{x}" cy="{y}" r="22" fill="{t['node']}" stroke="{t['line']}" stroke-width="2">
      <animate attributeName="stroke" dur="{dur}s" repeatCount="indefinite" calcMode="discrete"
        values="{t['line']};{t['ok']};{t['line']}" keyTimes="0;{k:.2f};1"/>
    </circle>
    <circle cx="{x}" cy="{y}" r="6" fill="{t['line']}">
      <animate attributeName="fill" dur="{dur}s" repeatCount="indefinite" calcMode="discrete"
        values="{t['line']};{t['ok']};{t['line']}" keyTimes="0;{k:.2f};1"/>
    </circle>
    <text x="{x}" y="{y + 50}" text-anchor="middle" font-family='{MONO}' font-size="15" fill="{t['sub']}">{label}</text>''')
    # ripple on the "live" node each time the dot arrives
    ripple = f'''
    <circle cx="{xs[-1]}" cy="{y}" r="22" fill="none" stroke="{t['ok']}" stroke-width="2" opacity="0">
      <animate attributeName="r" dur="{dur}s" repeatCount="indefinite" values="22;22;44" keyTimes="0;0.75;1"/>
      <animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" values="0;0.9;0" keyTimes="0;0.75;1"/>
    </circle>'''
    sub_text = "Full-stack engineer. I ship software real people use."
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" width="1200" height="300" role="img" aria-label="Nikhil Chandrakanti, full-stack engineer who ships software real people use">
  <style>
    .fade {{ opacity: 0; animation: in .8s ease-out forwards; }}
    .d1 {{ animation-delay: .1s; }} .d2 {{ animation-delay: .35s; }} .d4 {{ animation-delay: 3.1s; }} .d5 {{ animation-delay: .9s; }}
    @keyframes in {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
  </style>
  <defs>
    <pattern id="g" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M24 0H0V24" fill="none" stroke="{t['grid']}" stroke-width="1"/>
    </pattern>
    <linearGradient id="veil" x1="0" x2="1">
      <stop offset="0" stop-color="{t['bg']}"/>
      <stop offset=".45" stop-color="{t['bg']}" stop-opacity=".92"/>
      <stop offset="1" stop-color="{t['bg']}" stop-opacity=".5"/>
    </linearGradient>
    <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="-400" y1="0" x2="0" y2="0">
      <stop offset="0" stop-color="{t['ink']}"/>
      <stop offset=".45" stop-color="{t['ink']}"/>
      <stop offset=".5" stop-color="{t['shine']}"/>
      <stop offset=".55" stop-color="{t['ink']}"/>
      <stop offset="1" stop-color="{t['ink']}"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="0;1400;1400" keyTimes="0;0.35;1" dur="7s" begin="1.2s" repeatCount="indefinite"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{t['accent']}" stop-opacity=".18"/>
      <stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/>
    </radialGradient>
    {typed_clip("type", 64, 166, 32, len(sub_text), 11.4, 1.2, 0.035)}
  </defs>
  <rect width="1200" height="300" rx="16" fill="{t['bg']}"/>
  <rect width="1200" height="300" rx="16" fill="url(#g)"/>
  <circle cx="920" cy="150" r="260" fill="url(#glow)">
    <animate attributeName="r" values="240;280;240" dur="6s" repeatCount="indefinite"/>
  </circle>
  <rect width="1200" height="300" rx="16" fill="url(#veil)"/>

  <g class="fade d1">
    <text x="64" y="86" font-family='{MONO}' font-size="18" fill="{t['accent']}">~/nick10-05 $ <tspan fill="{t['sub']}">whoami</tspan><tspan class="cursor"> ▍</tspan></text>
  </g>
  <g class="fade d2">
    <text x="62" y="146" font-family='{SANS}' font-size="52" font-weight="700" fill="url(#shine)" letter-spacing="-1">Nikhil Chandrakanti</text>
  </g>
  <g clip-path="url(#type)">
    <text x="64" y="188" font-family='{SANS}' font-size="22" fill="{t['sub']}">Full-stack engineer. I ship software <tspan fill="{t['ink']}" font-weight="600">real people use.</tspan></text>
  </g>
  <g class="fade d4">
    <text x="64" y="236" font-family='{MONO}' font-size="15" fill="{t['dim']}">React · Node.js · TypeScript · PostgreSQL · Hyderabad, IN</text>
  </g>

  <g class="fade d5">
    <text x="{xs[0] - 22}" y="92" font-family='{MONO}' font-size="13" fill="{t['dim']}">// every change: PR → CI → deploy</text>
    <path id="p" d="M{xs[0]} {y} H{xs[-1]}" stroke="{t['line']}" stroke-width="2" stroke-dasharray="4 6" fill="none">
      <animate attributeName="stroke-dashoffset" values="0;-20" dur="1s" repeatCount="indefinite"/>
    </path>
    {''.join(nodes)}
    {ripple}
    <circle r="5" fill="{t['accent']}">
      <animateMotion dur="{dur}s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;0.75;1" calcMode="linear">
        <mpath href="#p"/>
      </animateMotion>
    </circle>
    <text x="{xs[-1]}" y="222" text-anchor="middle" font-family='{MONO}' font-size="12" fill="{t['ok']}">200 users</text>
  </g>
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
      <tspan fill="{t['accent']}">{escape(c["sha"][:7])}</tspan><tspan x="148" fill="{t['teal']}">{escape(c["repo"] if len(c["repo"]) <= 19 else c["repo"][:18] + "…")}</tspan><tspan x="385" fill="{t['ink']}">{escape(msg)}</tspan>
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
  </style>
  <defs>{typed_clip("cmd", 48, top, 36, len(cmd) + 2, cw, 0.4, 0.028)}</defs>
  <rect x="1" y="1" width="1198" height="{h - 2}" rx="14" fill="{t['win']}" stroke="{t['border']}" stroke-width="2"/>
  <path d="M1 15a14 14 0 0 1 14-14h1170a14 14 0 0 1 14 14v37H1z" fill="{t['bar']}"/>
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
    <text x="48" y="{end_y}" font-family='{MONO}' font-size="18" fill="{t['ok']}">$<tspan class="cursor" fill="{t['accent']}"> ▍</tspan></text>
  </g>
  <text x="1152" y="{h - 16}" text-anchor="end" font-family='{MONO}' font-size="12" fill="{t['dim']}">synced from the GitHub API by GitHub Actions · latest push {escape(latest)}</text>
</svg>
'''


# ---------------------------------------------------------------- divider

def divider(t):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 20" width="1200" height="20" aria-hidden="true">
  <defs>
    <linearGradient id="d" x1="0" x2="1">
      <stop offset="0" stop-color="{t['accent']}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{t['accent']}"/>
      <stop offset="1" stop-color="{t['teal']}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <line x1="0" y1="10" x2="1200" y2="10" stroke="{t['line']}" stroke-width="1"/>
  <rect x="-300" y="9" width="300" height="2" fill="url(#d)">
    <animate attributeName="x" values="-300;1200" dur="5s" repeatCount="indefinite"/>
  </rect>
</svg>
'''


# ---------------------------------------------------------------- data

def api(path, token):
    req = urllib.request.Request(f"https://api.github.com{path}",
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


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    os.makedirs(out, exist_ok=True)
    if "--sample" in sys.argv:
        commits = json.load(open(sys.argv[sys.argv.index("--sample") + 1]))
    else:
        commits = fetch_commits(os.environ.get("GITHUB_TOKEN"))
    if not commits:
        sys.exit("no commits found; leaving existing assets alone")
    latest = commits[0]["date"]
    for name, t in THEMES.items():
        for kind, svg in (("banner", banner(t)), ("terminal", terminal(t, commits, latest)),
                          ("divider", divider(t))):
            with open(os.path.join(out, f"{kind}-{name}.svg"), "w", encoding="utf-8") as f:
                f.write(svg)
    print(f"wrote assets for {len(commits)} commits, latest {latest}")


if __name__ == "__main__":
    main()
