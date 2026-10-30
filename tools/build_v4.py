"""Build v4 (design exploration) from the generated v3 pages.

v4 blends three references: Olayan (calm, light headings, generous space),
Abdul Latif Jameel (an identity colour per sector) and Al Rushaid (one dark
industrial band with glass cards). No projects are shown: trust comes from
industries served, how A'amal delivers, partners, roles and client logos.
Run after tools/build_v3.py.
"""
import os, re, shutil, hashlib, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V3, V4 = os.path.join(ROOT, "v3"), os.path.join(ROOT, "v4")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import content as C

CSS_V = hashlib.md5(open(os.path.join(ROOT, "assets", "css", "v4.css"), "rb").read()).hexdigest()[:8]
SECTOR_OF = {s: v["sector"] for s, v in C.SERVICES.items()}
SECTOR_CLASS = {"hospitality": "sec-h", "industrial-services": "sec-i", "management": "sec-p"}

ICON = lambda d: f'<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
INDUSTRIES = [
    ("Oil &amp; gas", '<path d="M12 2c1 3 4 5 4 9a4 4 0 0 1-8 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3-1-5 0-8z"/><path d="M6 21h12"/>'),
    ("Petrochemicals", '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/><path d="M7 15h10"/>'),
    ("Power &amp; utilities", '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>'),
    ("Water", '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>'),
    ("Industrial plants", '<path d="M3 21h18M5 21V10l5 3V10l5 3V6l4 2v13"/>'),
    ("Hotels &amp; resorts", '<path d="M3 21h18M5 21V8l7-5 7 5v13"/><path d="M10 21v-5h4v5"/>'),
    ("Real estate developers", '<rect x="4" y="3" width="10" height="18" rx="1"/><path d="M14 9h6v12h-6M8 7h2M8 11h2M8 15h2"/>'),
    ("Tourism &amp; entertainment", '<circle cx="12" cy="12" r="9"/><path d="M12 3c2.5 2.5 3.5 5.5 3.5 9s-1 6.5-3.5 9c-2.5-2.5-3.5-5.5-3.5-9s1-6.5 3.5-9zM3 12h18"/>'),
    ("Clubs &amp; academies", '<circle cx="12" cy="12" r="9"/><path d="M12 7l3 2-1 4h-4l-1-4z"/>'),
    ("Government &amp; enterprise PMOs", '<path d="M3 21h18M4 10h16M12 3l8 5H4z"/><path d="M6 10v8M10 10v8M14 10v8M18 10v8"/>'),
]
STEPS = [("Plan", "Feasibility, design and project set-up."), ("Build", "Construction, engineering and commissioning."),
         ("Operate", "Running facilities and staffing them well."), ("Maintain", "Keeping assets safe, efficient and compliant.")]
IND_SERVICES = [("operations-maintenance", "Operations &amp; Maintenance"), ("electrical-instrumentation", "Electrical &amp; Instrumentation"),
                ("waterproofing-industrial-coating", "Waterproofing &amp; Industrial Coating"), ("industry-transformation", "Industry Transformation")]

HOME_EXTRA = f'''
    <section class="section v4-industries">
      <div class="container stack" style="gap: 40px">
        <div class="x-head"><div><span class="s-pill">Industries we serve</span><h2 class="x-h2">Trusted across the Kingdom's core industries</h2></div><p>From oil, gas and power to hospitality and real estate, A'amal supports the sectors that drive the Saudi economy.</p></div>
        <ul class="v4-ind-grid">{"".join(f'<li><span class="v4-ind-ico">{ICON(d)}</span><span>{n}</span></li>' for n, d in INDUSTRIES)}</ul>
      </div>
    </section>

    <section class="v4-dark">
      <img class="v4-dark__bg" src="../assets/img/services/ws-refinery-night.webp" alt="" loading="lazy" decoding="async">
      <div class="v4-dark__veil"></div>
      <div class="container v4-dark__inner">
        <div class="v4-dark__head"><span class="s-pill s-pill--dark">Sector 02 · Industrial Services</span><h2 class="x-h2">Keeping the Kingdom's plants safe, efficient and running</h2><p>Support for oil, gas, petrochemical, power and water operators across the full asset lifecycle.</p><a class="btn btn--white" href="industrial-services.html">Explore Industrial Services</a></div>
        <div class="v4-glass-grid">{"".join(f'<a class="v4-glass" href="{s}.html"><span class="v4-glass__n">0{i+1}</span><strong>{n}</strong><span class="v4-glass__more">View service →</span></a>' for i, (s, n) in enumerate(IND_SERVICES))}</div>
      </div>
    </section>

    <section class="section">
      <div class="container stack" style="gap: 40px">
        <div class="x-head"><div><span class="s-pill">How we deliver</span><h2 class="x-h2">One partner for the whole lifecycle</h2></div><p>The same team stays with you from the first study to years of operation.</p></div>
        <ol class="v4-steps">{"".join(f'<li><span class="v4-steps__n">0{i+1}</span><strong>{t}</strong><span>{d}</span></li>' for i, (t, d) in enumerate(STEPS))}</ol>
      </div>
    </section>
'''


def transform(html, name):
    html = html.replace("/aamal-website/v3/", "/aamal-website/v4/")
    html = re.sub(r'(<link rel="stylesheet" href="\.\./assets/css/v3\.css\?v=\w+">)',
                  rf'\1\n  <link rel="stylesheet" href="../assets/css/v4.css?v={CSS_V}">', html, count=1)
    slug = name[:-5]
    sec = SECTOR_OF.get(slug) or (slug if slug in SECTOR_CLASS else None)
    cls = "v3 v4" + (f" {SECTOR_CLASS[sec]}" if sec else "")
    html = html.replace('class="v3"', f'class="{cls}"', 1)
    if name == "index.html":
        anchor = '\n    <section class="section section--tint">\n      <div class="container x-founder">'
        assert anchor in html, "founder anchor"
        html = html.replace(anchor, HOME_EXTRA + anchor, 1)
        html = html.replace('<span class="biz__tag tag--h">', '<span class="biz__tag tag--h">', 1)
    return html


def main():
    if os.path.isdir(V4):
        shutil.rmtree(V4)
    os.makedirs(V4)
    for f in sorted(os.listdir(V3)):
        if f.endswith(".html"):
            open(os.path.join(V4, f), "w", encoding="utf-8").write(transform(open(os.path.join(V3, f), encoding="utf-8").read(), f))
    print("v4 pages:", len(os.listdir(V4)))


if __name__ == "__main__":
    main()
