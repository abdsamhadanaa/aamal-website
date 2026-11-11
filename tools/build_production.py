"""Build the production website for www.aamal-group.com from the v3bf/ pages.

    python3 tools/build_production.py            # preview build: search engines blocked (noindex)
    python3 tools/build_production.py --launch   # launch build: indexable, sitemap submitted via robots.txt

Output goes to dist/ — upload that folder's contents to the web root of the domain
(see README "Going live"). v3bf/ itself is left untouched, so the github.io preview keeps working.

What it does
- Moves the pages to the site root (../assets/ -> assets/).
- Points canonical, Open Graph and structured-data URLs at the real domain.
- Merges the three stylesheets into one cache-busted file (one render-blocking request instead of three).
- Copies only the images and documents the pages actually use.
- Writes robots.txt, sitemap.xml, CNAME, .nojekyll and a _headers file (security headers for hosts
  that support it, such as Cloudflare Pages or Netlify).
- Makes 404.html work from any URL (root-absolute links), for visitors following old-site links.
"""
import datetime
import hashlib
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "v3bf")
OUT = os.path.join(ROOT, "dist")

DOMAIN = "www.aamal-group.com"
SITE_URL = f"https://{DOMAIN}/"
PREVIEW_URLS = ("https://abdsamhadanaa.github.io/aamal-website/v3bf/", "https://abdsamhadanaa.github.io/aamal-website/")
LAUNCH = "--launch" in sys.argv

CSS_FILES = ["styles.css", "services.css", "bf.css"]  # allowed stylesheets, merged in page order
JS_FILES = ["bf.js"]
# Images the header/footer script loads by name (assets/js/bf.js)
ALWAYS = ["assets/img/logo-v2.png", "assets/img/logo-v2-white.png", "assets/img/logo.png", "assets/img/logo-white.png"]

SECURITY_HEADERS = """/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
  Content-Security-Policy: {csp}; frame-ancestors 'self'

/assets/*
  Cache-Control: public, max-age=31536000, immutable
"""


def digest(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()[:8]


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)  # comments
    lines = (ln.strip() for ln in css.splitlines())
    return "\n".join(ln for ln in lines if ln) + "\n"


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "assets", "css"))
    os.makedirs(os.path.join(OUT, "assets", "js"))

    # Each page's stylesheets become one file (pages that load the same set share it),
    # named by content so browsers can cache it for a year
    bundles = {}
    css = ""

    def bundle(files):
        nonlocal css
        if files not in bundles:
            text = "".join(minify_css(open(os.path.join(ROOT, "assets", "css", f), encoding="utf-8").read()) for f in files)
            name = f"site.{hashlib.md5(text.encode()).hexdigest()[:8]}.css"
            open(os.path.join(OUT, "assets", "css", name), "w", encoding="utf-8").write(text)
            bundles[files] = name
            css += text
        return bundles[files]
    js_names = {}
    for f in JS_FILES:
        name = f"{f[:-3]}.{digest(os.path.join(ROOT, 'assets', 'js', f))}.js"
        shutil.copy(os.path.join(ROOT, "assets", "js", f), os.path.join(OUT, "assets", "js", name))
        js_names[f] = name

    used = set(ALWAYS)
    pages = sorted(f for f in os.listdir(SRC) if f.endswith(".html"))
    old_site_links = set()
    csp = None
    for name in pages:
        s = open(os.path.join(SRC, name), encoding="utf-8").read()

        # Real domain everywhere
        for u in PREVIEW_URLS:
            s = s.replace(u + "assets/", SITE_URL + "assets/").replace(u, SITE_URL)
        s = s.replace(f'href="{SITE_URL}index.html"', f'href="{SITE_URL}"').replace(f'"{SITE_URL}index.html"', f'"{SITE_URL}"')

        # Three stylesheets -> one; versioned script
        links = re.findall(r'(\s*<link rel="stylesheet" href="\.\./assets/css/([\w-]+\.css)(?:\?v=[0-9a-f]+)?">)', s)
        assert links and all(f in CSS_FILES for _, f in links), f"{name}: unexpected stylesheets {links}"
        css_name = bundle(tuple(f for _, f in links))
        s = s.replace(links[0][0], f'\n  <link rel="stylesheet" href="../assets/css/{css_name}">', 1)
        for ln, _ in links[1:]:
            s = s.replace(ln, "", 1)
        for f, hashed in js_names.items():
            s = re.sub(r"\.\./assets/js/" + re.escape(f) + r"(\?v=[0-9a-f]+)?", f"../assets/js/{hashed}", s)

        # Search engines: blocked until launch; 404 never indexed
        robots = "index, follow" if LAUNCH and name != "404.html" else "noindex, nofollow"
        s = re.sub(r'<meta name="robots" content="[^"]*">', f'<meta name="robots" content="{robots}">', s)

        # Collect the files this page uses
        for m in re.findall(r'\.\./(assets/(?:img|docs)/[^"\'?#\s,)]+)', s):
            used.add(m)
        for m in re.findall(re.escape(SITE_URL) + r'(assets/(?:img|docs)/[^"\'?#\s,)]+)', s):  # og:image, logo in structured data
            used.add(m)

        # Pages move from v3bf/ to the site root. 404.html is served at any URL, so its links are root-absolute.
        if name == "404.html":
            s = s.replace("../assets/", "/assets/")
            s = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/)([^"]+)"', r'\1="/\2"', s)
        else:
            s = s.replace("../assets/", "assets/")

        old_site_links |= set(re.findall(r'https?://(?:www\.)?aamal-group\.com/[^"\s<]+', s))
        m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', s)
        csp = csp or (m and m.group(1))
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(s)

    # Images referenced from CSS
    for m in re.findall(r"url\(['\"]?\.\./(img/[^'\")]+)", css):
        used.add("assets/" + m)

    missing = []
    for rel in sorted(used):
        src = os.path.join(ROOT, rel)
        if not os.path.isfile(src):
            missing.append(rel)
            continue
        dst = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    # The CSS now lives in assets/css/, same depth as before, so ../img/ paths still resolve.

    today = datetime.date.today().isoformat()
    urls = [p for p in pages if p not in ("404.html",)]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in urls:
        loc = SITE_URL if p == "index.html" else SITE_URL + p
        sitemap.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod></url>")
    sitemap.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sitemap) + "\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n" if LAUNCH else "User-agent: *\nDisallow: /\n")
    open(os.path.join(OUT, "CNAME"), "w").write(DOMAIN + "\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    open(os.path.join(OUT, "_headers"), "w").write(SECURITY_HEADERS.format(csp=csp))

    files = sum(len(fs) for _, _, fs in os.walk(OUT))
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
    print(f"{'LAUNCH' if LAUNCH else 'PREVIEW (noindex)'} build -> dist/  {len(pages)} pages, {files} files, {size / 1e6:.1f} MB")
    if missing:
        print("MISSING files referenced by pages:", *missing, sep="\n  ")
    # Links to the domain that this build doesn't serve (files that only exist on the old site)
    from urllib.parse import unquote, urlsplit
    old_site_links = {u for u in old_site_links
                      if urlsplit(u).path not in ("", "/") and not os.path.exists(os.path.join(OUT, unquote(urlsplit(u).path).lstrip("/")))}
    if old_site_links:
        print("WARNING: links to the old aamal-group.com site will break when this site replaces it:", *sorted(old_site_links), sep="\n  ")
    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
