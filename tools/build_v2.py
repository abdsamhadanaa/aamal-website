#!/usr/bin/env python3
"""Builds the Version 2 service pages and the SEO head of every V2 page.

    python3 tools/build_v2.py

- Writes one page per service (tools/content.py), the three sector pages and services.html.
- Rewrites the <head> of every page in /v2 (title + description are kept) with
  canonical, Open Graph, Twitter and JSON-LD tags.
- Writes v2/sitemap.xml.

SITE_URL: change to the real domain at launch (e.g. "https://www.aamal-group.com/")
PREVIEW:  True adds noindex so the preview copy is not indexed. Set False at launch.
"""
import html
import json
import os
import re
from datetime import date

from PIL import Image

import content as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2 = os.path.join(ROOT, "v2")
IMG = os.path.join(ROOT, "assets", "img")

SITE_URL = "https://abdsamhadanaa.github.io/aamal-website/v2/"
PREVIEW = True

ORG = {
    "@type": "Organization",
    "@id": SITE_URL + "#org",
    "name": "A'amal Group",
    "alternateName": "Arab Economic & Business Group",
    "url": SITE_URL,
    "logo": SITE_URL + "../assets/img/logo.png",
    "foundingDate": "1994",
    "email": "info@aamal-group.com",
    "telephone": "+966 13 897 3938",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "King Abdullah Road, Middle East Commercial Center, P.O. Box 4977",
        "addressLocality": "Al Khobar",
        "postalCode": "31952",
        "addressCountry": "SA",
    },
    "sameAs": ["https://twitter.com/AAMAL_GROUP_SA"],
}


SECTOR = {s["slug"]: s for s in C.SECTORS}

# Version tags so browsers fetch the new CSS/JS after every change (cache busting)
import hashlib
ASSET_V = {k: hashlib.md5(open(os.path.join(ROOT, "assets", f), "rb").read()).hexdigest()[:8]
           for k, f in (("css", "css/styles.css"), ("js", "js/main.js"))}


def e(s):
    return html.escape(s, quote=True)


def short(svc):
    return svc.get("short", svc["name"])


def img_size(name):
    with Image.open(os.path.join(IMG, name + ".webp")) as im:
        return im.size


def picture(name, alt, sizes="(max-width: 800px) 100vw, 50vw", cls="", eager=False):
    """<img> with a small and a full WebP source and fixed dimensions (no layout shift)."""
    w, h = img_size(name)
    small = os.path.exists(os.path.join(IMG, name + "-800.webp"))
    srcset = f' srcset="../assets/img/{name}-800.webp 800w, ../assets/img/{name}.webp {w}w" sizes="{sizes}"' if small and w > 800 else ""
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="../assets/img/{name}.webp"{srcset} width="{w}" height="{h}" alt="{e(alt)}"{load}>'


def head(title, desc, page, image="services/cl-cabo", extra_ld=None, preload=None):
    url = SITE_URL + ("" if page == "index.html" else page)
    img_url = SITE_URL + "../assets/img/" + image + ".webp"
    graph = [ORG, {"@type": "WebPage", "@id": url, "url": url, "name": title, "description": desc,
                   "isPartOf": {"@type": "WebSite", "url": SITE_URL, "name": "A'amal Group"},
                   "publisher": {"@id": SITE_URL + "#org"}}]
    graph += extra_ld or []
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    robots = '\n  <meta name="robots" content="noindex, follow">' if PREVIEW else ""
    pre = ""
    if preload:
        w, _ = img_size(preload)
        has_small = w > 800 and os.path.exists(os.path.join(IMG, preload + "-800.webp"))
        if has_small:
            pre = f'\n  <link rel="preload" as="image" href="../assets/img/{preload}.webp" imagesrcset="../assets/img/{preload}-800.webp 800w, ../assets/img/{preload}.webp {w}w" imagesizes="100vw" fetchpriority="high">'
        else:
            pre = f'\n  <link rel="preload" as="image" href="../assets/img/{preload}.webp" fetchpriority="high">'
    return f"""<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">{robots}
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="A'amal Group">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{img_url}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@AAMAL_GROUP_SA">
  <meta name="theme-color" content="#2E3133">
  <link rel="icon" href="../assets/img/logo.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>{pre}
  <link href="https://fonts.googleapis.com/css2?family=Readex+Pro:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/css/styles.css?v={ASSET_V["css"]}">
  <script src="../assets/js/main.js?v={ASSET_V["js"]}" defer></script>
  <script type="application/ld+json">{ld}</script>
</head>"""


def breadcrumb_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + ("" if p == "index.html" else p)}
        for i, (n, p) in enumerate(items)]}


def page(head_html, active, body):
    return f"""<!doctype html>
<html lang="en">
{head_html}
<body data-version="2">
  <site-header active="{active}"></site-header>

  <main id="main">
{body}
  </main>

  <site-footer></site-footer>
</body>
</html>
"""


def hero(img, alt, crumbs, tag, h1, lead):
    crumb_html = " / ".join(f'<a href="{p}">{e(n)}</a>' for n, p in crumbs[:-1]) + " / " + e(crumbs[-1][0])
    return f"""    <section class="page-hero">
      {picture(img, alt, sizes="100vw", cls="page-hero__img", eager=True)}
      <div class="page-hero__overlay"></div>
      <div class="container page-hero__inner">
        <nav class="breadcrumb" aria-label="Breadcrumb">{crumb_html}</nav>
        <span class="page-hero__tag">{e(tag)}</span>
        <h1 class="h1">{e(h1)}</h1>
        <p class="lead">{e(lead)}</p>
      </div>
    </section>"""


DOC_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5"/><path d="M12 11v6M9.5 14.5L12 17l2.5-2.5"/></svg>'
EXT_ICON = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/></svg>'


def partner_block(p):
    if not p:
        return ""
    if p.get("logo"):
        logo = f'<img src="../assets/img/{p["logo"]}" width="{p["logo_w"]}" height="{p["logo_h"]}" alt="{e(p["name"])} logo" loading="lazy" decoding="async">'
    else:
        logo = f'<span class="partner-card__wordmark">{e(p["name"])}</span>'
    link = (f'<a class="text-link" href="{p["url"]}" target="_blank" rel="noopener">Read more on the {e(p["name"])} website {EXT_ICON}</a>'
            if p.get("url") else "")
    return f"""
          <div class="partner-card">
            <div class="partner-card__logo">{logo}</div>
            <div class="partner-card__text">
              <span class="eyebrow">Our partner</span>
              <strong>{e(p["name"])}</strong>
              <p>{e(p["about"])}</p>
              {link}
            </div>
          </div>"""


def downloads_block(d):
    if not d:
        return ""
    links = "".join(f'<a class="download-link" href="{u}" target="_blank" rel="noopener">{DOC_ICON}<span>{e(n)}<small>PDF</small></span></a>' for n, u in d)
    return f'\n          <div class="downloads">{links}</div>'


def service_card(slug, sizes="(max-width: 800px) 100vw, 33vw"):
    s = C.SERVICES[slug]
    return f"""          <article class="service-card">
            {picture(s["hero"], s["hero_alt"], sizes=sizes)}
            <div class="service-card__body">
              <h3><a class="card-link" href="{slug}.html">{e(s["name"])}</a></h3>
              <p class="muted">{e(s["lead"])}</p>
              <span class="text-link" aria-hidden="true">Learn more →</span>
            </div>
          </article>"""


def build_service(slug, s):
    sec = SECTOR[s["sector"]]
    crumbs = [("Home", "index.html"), ("Services", "services.html"), (sec["name"], sec["slug"] + ".html"), (s["name"], slug + ".html")]
    ld = [breadcrumb_ld(crumbs), {
        "@type": "Service", "name": s["name"], "description": s["description"], "serviceType": s["name"],
        "provider": {"@id": SITE_URL + "#org"}, "areaServed": {"@type": "Country", "name": "Saudi Arabia"},
        "url": SITE_URL + slug + ".html",
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": s["name"], "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": o[0]}} for o in s["offer"]]},
    }]
    overview = "\n".join(f"          <p>{e(p)}</p>" for p in s["overview"])

    offers = []
    for title, intro, items in s["offer"]:
        ul = ('<ul class="dot-list">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>") if items else ""
        offers.append(f'          <article class="offer-card"><h3>{e(title)}</h3><p>{e(intro)}</p>{ul}</article>')

    steps = "".join(f'<li><span class="steps__num">{i + 1}</span><span class="steps__title">{e(t)}</span><span class="muted">{e(d)}</span></li>' for i, (t, d) in enumerate(s["steps"]))
    why = "".join(f"<div><strong>{e(t)}</strong><span>{e(d)}</span></div>" for t, d in s["why"])
    chips = "".join(f"<li>{e(i)}</li>" for i in s["industries"])

    cert = ""
    if s.get("certifications"):
        cert = f"""
    <section class="section" style="padding-bottom: 0">
      <div class="container">
        <div class="panel panel--tint" style="flex-direction: row; flex-wrap: wrap; gap: 16px 32px; align-items: center">
          <strong class="h3" style="font-size: 22px">Certifications</strong>
          <p style="flex: 1 1 320px">{e(s["certifications"])}</p>
        </div>
      </div>
    </section>"""

    gallery = ""
    if len(s["gallery"]) >= 2:
        pics = "".join(picture(n, a, sizes="(max-width: 600px) 100vw, 33vw") for n, a in s["gallery"])
        credit = f'\n        <p class="muted" style="font-size: 14px; margin: 0">{e(s["gallery_credit"])}</p>' if s.get("gallery_credit") else ""
        gallery = f"""
    <section class="section">
      <div class="container stack" style="gap: 32px">
        <h2 class="h2">Gallery</h2>
        <div class="gallery">{pics}</div>{credit}
      </div>
    </section>"""

    related = [x for x in sec["services"] if x != slug]
    if len(related) < 2:  # top up with services from other sectors
        related += [x for x in C.SERVICES if x not in related and x != slug][: 2 - len(related) + 1]
    related_html = "\n".join(service_card(r) for r in related[:3])

    p = s.get("partner")
    partner_btn = (f'<a class="btn btn--outline-light" href="{p["url"]}" target="_blank" rel="noopener">Visit {e(p["name"])}</a>'
                   if p and p.get("url") else "")

    body = f"""{hero(s["hero"], s["hero_alt"], crumbs, sec["name"], s["name"], s["lead"])}

    <section class="section">
      <div class="container split">
        <div class="split__head">
          <span class="eyebrow">Overview</span>
          <h2 class="h2">{e(s["name"])} with A'amal Group</h2>
        </div>
        <div class="split__body">
{overview}{partner_block(p)}{downloads_block(s["downloads"])}
        </div>
      </div>
    </section>

    <section class="section section--tint">
      <div class="container stack" style="gap: 40px">
        <div class="section-head">
          <div>
            <span class="eyebrow">Services</span>
            <h2 class="h2" style="margin-top: 8px">What we offer</h2>
          </div>
        </div>
        <div class="offer-grid">
{chr(10).join(offers)}
        </div>
      </div>
    </section>

    <section class="section" style="padding-bottom: 0">
      <div class="container industries">
        <h2 class="h3">Industries we serve</h2>
        <ul class="chips">{chips}</ul>
      </div>
    </section>

    <section class="section">
      <div class="container stack" style="gap: 32px">
        <h2 class="h2">How we work</h2>
        <ol class="steps steps--tint">{steps}</ol>
      </div>
    </section>

    <section class="section section--dark">
      <div class="container stack" style="gap: 40px">
        <h2 class="h2">Why A'amal Group</h2>
        <div class="grid grid--4 pillars">{why}</div>
      </div>
    </section>
{cert}{gallery}
    <section class="section--dark cta-section">
      <div class="container cta-band">
        <div>
          <h2>Planning a {e(short(s).lower() if s["name"] != "Artificial Lagoons" else "lagoon")} project?</h2>
          <p style="color: var(--on-dark)">Tell us what you need and our team will get back to you.</p>
        </div>
        <div class="btn-row">
          <a class="btn btn--primary" href="contact.html">Talk to our team</a>
          {partner_btn}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container stack" style="gap: 32px">
        <div class="section-head">
          <h2 class="h2">Related services</h2>
          <a class="text-link" href="{sec["slug"]}.html">All {e(sec["name"])} →</a>
        </div>
        <div class="grid grid--3">
{related_html}
        </div>
      </div>
    </section>"""
    return page(head(s["title"], s["description"], slug + ".html", s["hero"], ld, preload=s["hero"]), "services", body)


def build_sector(i, sec):
    crumbs = [("Home", "index.html"), ("Services", "services.html"), (sec["name"], sec["slug"] + ".html")]
    nxt = C.SECTORS[(i + 1) % len(C.SECTORS)]
    cards = "\n".join(service_card(x) for x in sec["services"])
    names = ", ".join(C.SERVICES[x]["name"] for x in sec["services"])
    title = f"{sec['name']} — {names} | A'amal Group"
    desc = f"A'amal Group {sec['name']}: {names}. {sec['lead']}"
    ld = [breadcrumb_ld(crumbs), {"@type": "ItemList", "name": sec["name"], "itemListElement": [
        {"@type": "ListItem", "position": k + 1, "url": SITE_URL + x + ".html", "name": C.SERVICES[x]["name"]} for k, x in enumerate(sec["services"])]}]
    body = f"""{hero(sec["hero"], "", crumbs, "Sector " + sec["num"], sec["name"], sec["lead"])}

    <section class="section">
      <div class="container stack" style="gap: 40px">
        <p class="lead" style="max-width: 820px; color: var(--text)">{e(sec["intro"])}</p>
        <div class="grid grid--{ {2: 2, 4: 4}.get(len(sec["services"]), 3) }">
{cards}
        </div>
      </div>
    </section>

    <section class="section--tint">
      <div class="container next-band">
        <div><span class="muted">Next sector</span><br><a class="next-band__link" href="{nxt["slug"]}.html">{e(nxt["name"])} →</a></div>
        <a class="btn btn--primary" href="contact.html">Discuss a project</a>
      </div>
    </section>"""
    return page(head(title, desc[:300], sec["slug"] + ".html", sec["hero"], ld, preload=sec["hero"]), "services", body)


def build_overview():
    crumbs = [("Home", "index.html"), ("Services", "services.html")]
    rows = []
    for i, sec in enumerate(C.SECTORS):
        links = "".join(f'<li><a href="{x}.html">{e(C.SERVICES[x]["name"])}</a></li>' for x in sec["services"])
        img = picture(sec["card_img"], "", sizes="(max-width: 800px) 100vw, 50vw")
        rev = " feature-row--reverse" if i % 2 else ""
        text = f"""<div class="feature-row__text">
            <span class="eyebrow">{sec["num"]}</span>
            <h2 class="h2">{e(sec["name"])}</h2>
            <p>{e(sec["intro"])}</p>
            <ul class="service-links">{links}</ul>
            <a class="btn btn--primary" href="{sec["slug"]}.html">Explore {e(sec["name"])}</a>
          </div>"""
        rows.append(f'        <div class="feature-row{rev}">\n          {text + img if i % 2 else img + text}\n        </div>')
    ld = [breadcrumb_ld(crumbs), {"@type": "ItemList", "name": "A'amal Group services", "itemListElement": [
        {"@type": "ListItem", "position": k + 1, "url": SITE_URL + x + ".html", "name": C.SERVICES[x]["name"]} for k, x in enumerate(C.SERVICES)]}]
    body = f"""{hero("hero-refinery", "", crumbs, "8 specialist services", "Our services", "Three sectors, one partner — from destinations people love to the plants that power industry and the people and systems that deliver projects.")}

    <section class="section">
      <div class="container stack" style="gap: 88px">
{chr(10).join(rows)}
      </div>
    </section>

    <section class="section section--tint">
      <div class="container stack">
        <h2 class="h2">One partner for the whole lifecycle</h2>
        <ol class="steps">
          <li><span class="steps__num">1</span><span class="steps__title">Plan</span><span class="muted">Feasibility, design and project set-up.</span></li>
          <li><span class="steps__num">2</span><span class="steps__title">Build</span><span class="muted">Construction, engineering and commissioning.</span></li>
          <li><span class="steps__num">3</span><span class="steps__title">Operate</span><span class="muted">Running facilities and staffing them well.</span></li>
          <li><span class="steps__num">4</span><span class="steps__title">Maintain</span><span class="muted">Keeping assets safe, efficient and compliant.</span></li>
        </ol>
      </div>
    </section>"""
    title = "Services — Artificial Lagoons, Industrial Services & Project Management | A'amal Group"
    desc = "A'amal Group services in Saudi Arabia: artificial lagoons, sports facilities, industrial O&M, electrical & instrumentation, waterproofing & coating, industry transformation, HR and project solutions."
    return page(head(title, desc, "services.html", "hero-refinery", ld, preload="hero-refinery"), "services", body)


# ---------------------------------------------------------------- existing hand-written pages
PAGE_IMAGE = {"index.html": "services/cl-cabo", "about.html": "hero-oil-gas", "contact.html": "hero-construction",
              "careers.html": "team-meeting", "responsibility.html": "hero-oil-gas", "awards.html": "services/cl-cabo",
              "media.html": "services/cl-cabo"}


def refresh_head(fname):
    path = os.path.join(V2, fname)
    src = open(path, encoding="utf-8").read()
    title = html.unescape(re.search(r"<title>(.*?)</title>", src, re.S).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="(.*?)">', src, re.S).group(1))
    m = re.search(r'<img class="page-hero__img"[^>]*src="\.\./assets/img/([\w/-]+)\.webp"', src) or \
        re.search(r'<img class="hero__slide is-active"[^>]*src="\.\./assets/img/([\w/-]+)\.webp"', src)
    preload = m.group(1) if m else None
    extra = [] if fname == "index.html" else [breadcrumb_ld([("Home", "index.html"), (title.split(" — ")[0].split(" | ")[0], fname)])]
    new_head = head(title, desc, fname, PAGE_IMAGE.get(fname, "services/cl-cabo"), extra, preload=preload)
    src = re.sub(r"<head>.*?</head>", lambda _: new_head, src, count=1, flags=re.S)
    open(path, "w", encoding="utf-8").write(src)


def main():
    generated = []
    for slug, s in C.SERVICES.items():
        open(os.path.join(V2, slug + ".html"), "w", encoding="utf-8").write(build_service(slug, s))
        generated.append(slug + ".html")
    for i, sec in enumerate(C.SECTORS):
        open(os.path.join(V2, sec["slug"] + ".html"), "w", encoding="utf-8").write(build_sector(i, sec))
        generated.append(sec["slug"] + ".html")
    open(os.path.join(V2, "services.html"), "w", encoding="utf-8").write(build_overview())
    generated.append("services.html")

    others = sorted(f for f in os.listdir(V2) if f.endswith(".html") and f not in generated)
    for f in others:
        refresh_head(f)

    today = date.today().isoformat()
    order = ["index.html", "about.html", "services.html"] + [s["slug"] + ".html" for s in C.SECTORS] + \
            [x + ".html" for x in C.SERVICES] + [f for f in others if f not in ("index.html", "about.html")]
    urls = "".join(f"  <url><loc>{SITE_URL}{'' if p == 'index.html' else p}</loc><lastmod>{today}</lastmod></url>\n" for p in order)
    open(os.path.join(V2, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    print("generated:", generated)
    print("head refreshed:", others)


if __name__ == "__main__":
    main()
