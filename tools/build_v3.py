"""Build v3 (enhanced design option) from the generated v2 pages.

v3 keeps every page's content and adds the enhanced look (assets/css/v3.css):
calmer headings, softer page heroes, larger rounded photos, and a careers
band before the footer. The v3 home page comes from tools/v3_home.html.
Run after tools/build_v2.py.
"""
import os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2, V3 = os.path.join(ROOT, "v2"), os.path.join(ROOT, "v3")
import hashlib
CSS = '<link rel="stylesheet" href="../assets/css/v3.css?v=' + hashlib.md5(open(os.path.join(ROOT, 'assets', 'css', 'v3.css'), 'rb').read()).hexdigest()[:8] + '">'
SVC = re.compile(r'<link rel="stylesheet" href="\.\./assets/css/services\.css\?v=[0-9a-f]+">')

CAREERS = '''
    <section class="section v3-careers-wrap">
      <div class="container">
        <div class="x-careers">
          <div><span class="s-pill">Careers</span><h2 class="x-h2">Grow with A'amal</h2><p>Join a Saudi group that builds, operates and invests across the Kingdom and beyond.</p></div>
          <div class="btn-row"><a class="btn btn--primary" href="careers.html">View careers</a><a class="btn btn--outline" href="contact.html">Contact us</a></div>
        </div>
      </div>
    </section>
  </main>'''


def transform(html, name):
    html = html.replace("/aamal-website/v2/", "/aamal-website/v3/")
    if '<meta name="robots"' not in html:
        html = html.replace("<head>", '<head>\n  <meta name="robots" content="noindex, follow">', 1)
    if "services.css" not in html:
        # every v3 page needs the rounded base layer
        v = re.search(r'services\.css\?v=[0-9a-f]+', open(os.path.join(V2, "about.html"), encoding="utf-8").read()).group(0)
        html = html.replace('<script src="../assets/js/main.js', f'<link rel="stylesheet" href="../assets/css/{v}">\n  <script src="../assets/js/main.js', 1)
    html = re.sub(r'<link rel="stylesheet" href="\.\./assets/css/v3\.css[^"]*">\n?\s*', "", html)
    if True:
        html = html.replace('<script src="../assets/js/main.js', CSS + '\n  <script src="../assets/js/main.js', 1)
    html = html.replace('<body data-version="2">', '<body data-version="2" class="v3">', 1)
    if name not in ("careers.html", "contact.html", "index.html") and "x-careers" not in html:
        html = html.replace("\n  </main>", CAREERS, 1)
    return html


def main():
    if os.path.isdir(V3):
        shutil.rmtree(V3)
    os.makedirs(V3)
    for f in sorted(os.listdir(V2)):
        if f in ("home-v3.html", "index.html"):
            continue
        src = os.path.join(V2, f)
        if f.endswith(".html"):
            html = open(src, encoding="utf-8").read()
            open(os.path.join(V3, f), "w", encoding="utf-8").write(transform(html, f))
    home = open(os.path.join(ROOT, "tools", "v3_home.html"), encoding="utf-8").read()
    home = re.sub(r"<title>.*?</title>", "<title>A'amal Group | Artificial Lagoons, Industrial Services &amp; Project Management in Saudi Arabia</title>", home, count=1)
    open(os.path.join(V3, "index.html"), "w", encoding="utf-8").write(transform(home, "index.html"))
    print("v3 pages:", len(os.listdir(V3)))


if __name__ == "__main__":
    main()
