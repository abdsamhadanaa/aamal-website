"""Client-review previews (M. Waqas comments, Nov 2026). Live v2/v3/v4 are untouched.
/v3bf/ = V2 (classic) + client feedback
/v4bf/ = V3 (modern, from the v3-audit branch) + client feedback
Both are noindex, nofollow."""
import os, re, sys, glob, shutil, hashlib, subprocess, tempfile, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmp = tempfile.mkdtemp()
subprocess.run(f"git -C {ROOT} archive v3-audit v3 tools/build_v3.py assets/css/v3.css assets/js/main.js | tar -x -C {tmp}", shell=True, check=True)
shutil.copy(f"{tmp}/assets/css/v3.css", f"{ROOT}/assets/css/v3bf.css")
with open(f"{ROOT}/assets/css/v3bf.css", "a") as fh:
    fh.write("\n.site-nav span.nav-mega__title { display: block; cursor: default; }\n")
js = open(f"{tmp}/assets/js/main.js", encoding="utf-8").read()
# Client: main service categories in the menu are headings, not links
js = js.replace('<a class="nav-mega__title" href="${g.href}">${esc(g.label)}</a>', '<span class="nav-mega__title">${esc(g.label)}</span>')
assert 'class="nav-mega__title" href' not in js
open(f"{ROOT}/assets/js/v3bf.js", "w").write(js)
open(f"{ROOT}/assets/js/bf.js", "w").write(js.replace("const V3 = document.body.classList.contains('v3');",
    "const V3 = document.body.classList.contains('v3') || document.body.classList.contains('bf');"))
h = lambda p: hashlib.md5(open(f"{ROOT}/{p}", 'rb').read()).hexdigest()[:8]

# client_edits() from the v3-audit build, pointed at the live V2 pages
spec = importlib.util.spec_from_file_location("bv3", f"{tmp}/tools/build_v3.py")
bv3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(bv3)
bv3.V2 = os.path.join(ROOT, "v2")
B20 = bv3.B20_TEXT


def home_v2(s):
    sub = bv3.sub1
    # Banner: HR slide in Saudi attire
    s = re.sub(r'<img class="hero__slide" src="\.\./assets/img/services/as-engineers-plant\.webp" srcset="[^"]*"(.*?)alt="[^"]*"',
               r'<img class="hero__slide" src="../assets/img/services/pbm-saudi-coffee.webp" srcset="../assets/img/services/pbm-saudi-coffee-800.webp 800w, ../assets/img/services/pbm-saudi-coffee.webp 1200w"\1alt="Saudi professionals in traditional dress"', s, count=1, flags=re.S)
    # Our story
    s = sub(s, "<p>Founded in Al Khobar in 1994 by Yassin Al Suroor, A'amal Group — the Arab Economic &amp; Business Group — has built its reputation on delivering projects on time and within budget, with an unwavering focus on safety, sustainability and quality.</p>",
            "<p>Since our inception in 1994, A'amal Group has established an impeccable track record of delivering exceptional projects. We're strategically headquartered in the thriving Eastern Province of Saudi Arabia, hub of superior oil producing, refining and exporting zone of the world. We're a dynamic, transparent and socially responsible group that is committed to walk an extra mile to fuel the regional economy and improve lives through its various business activities. We understand that each project and client has individual needs and objectives.</p>")
    s = sub(s, '<a class="text-link" href="about.html">Read the Founder &amp; CEO message →</a>\n            <a class="text-link" href="awards.html">A\'amal Global Recognition →</a>',
            '<a class="btn btn--primary" href="about.html#overview">Read more about A\'amal</a>\n            <a class="text-link" href="about.html#founder">Founder &amp; CEO message →</a>')
    # Recognition: G2T -> B20 USA
    s = re.sub(r'<li><span class="recog__logo"><img src="\.\./assets/img/recognition/g2t-awards\.png"[^>]*></span><strong>G2T Awards</strong><span>[^<]*</span></li>',
               '<li><span class="recog__logo">' + B20 + '</span><strong>B20 USA 2026</strong><span>United States G20 Presidency</span></li>', s)
    # Our Businesses
    s = sub(s, '<span class="eyebrow">Our Businesses</span>\n            <h2 class="h2">Three sectors, one partner</h2>', '<h2 class="h2">Our Businesses</h2>')
    # Partners
    s = sub(s, '<a href="sports-facilities.html" title="Apex"><img src="../assets/img/partners/logo-apex.png" width="240" height="225" alt="Apex" loading="lazy" decoding="async"></a>',
            '<a href="https://duplays.com/" target="_blank" rel="noopener" title="Duplays"><img src="../assets/img/partners/logo-duplays.png" width="480" height="112" alt="Duplays" loading="lazy" decoding="async"></a>\n'
            '            <a href="electrical-instrumentation.html" title="A\'amal E&amp;I"><span class="logo-text">A\'amal<small>E&amp;I</small></span></a>')
    # Remove Sustainability, CSR and Media Centre sections
    for m in ('<span class="eyebrow">Sustainability</span>', '<span class="eyebrow">Corporate Social Responsibility</span>', '<h2 class="h2">Media Centre</h2>'):
        s = bv3.drop_section(s, m)
    return s


def founder_ceo(s):
    """Client: use "Founder & CEO", never "our Founder & CEO"."""
    s = s.replace('>On the world stage</h2>', '>Founder &amp; CEO on the world stage</h2>').replace('>In the news</h2>', '>Founder &amp; CEO in the news</h2>')
    return re.sub(r'\b[Oo]ur (Founder (?:&amp;|&|and) CEO)', r'\1', s)


def drop_about_stats(s):
    """Client: remove the stats row (30+ / 3 / 3 / 2021) under the About hero."""
    s = re.sub(r'\s*<div class="container s-stats">.*?</div></div>', '', s, count=1, flags=re.S)
    # Client: remove "Journey and achievements" (roles and awards stay on the Global Recognition page)
    s = re.sub(r'\n\s*<!-- Founder & CEO: journey and achievements -->', '', s)
    return bv3.drop_section(s, 'id="journey"', required=False)


def saudi_photos(s):
    """Client: Saudi (not Gulf) style attire — thobe, shemagh/ghutra with agal and bisht."""
    # No faces, and the photo should say what the business does:
    # HR = handshake over documents (thobe sleeve); PM = Saudi professional with shemagh and agal at his desk, seen from above
    s = s.replace('pbm-saudi-coffee', 'hr-handshake')
    s = re.sub(r'(hr-handshake\.webp"[^>]*?)alt="[^"]*"', r'\1alt="Handshake over documents after a successful hire"', s)
    return s


def common(s, folder, css, js_file):
    s = founder_ceo(s)
    s = saudi_photos(s)
    if '<span class="s-pill">All services</span>' in s:
        # Services overview page: client asked to remove the stats row
        s = re.sub(r'\s*<div class="container s-stats">.*?</div></div>', '', s, count=1, flags=re.S)
    if '<title>About' in s or 'href="#overview">About us</a>' in s:
        s = drop_about_stats(s)
    s = s.replace('/aamal-website/v2/', f'/aamal-website/{folder}/').replace('/aamal-website/v3/', f'/aamal-website/{folder}/')
    s = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex, nofollow">', s)
    if '<meta name="robots"' not in s:
        s = s.replace("<head>", '<head>\n  <meta name="robots" content="noindex, nofollow">', 1)
    s = re.sub(r'\.\./assets/js/main\.js(\?v=[0-9a-f]+)?', f'../assets/js/{js_file}?v=' + h(f'assets/js/{js_file}'), s)
    return css(s)


def build_v3bf():  # V2 based
    d = f"{ROOT}/v3bf"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    link = '<link rel="stylesheet" href="../assets/css/bf.css?v=' + h('assets/css/bf.css') + '">'
    for f in sorted(glob.glob(f"{ROOT}/v2/*.html")):
        name = os.path.basename(f)
        if name == "home-v3.html":
            continue
        s = open(f, encoding="utf-8").read()
        s = bv3.client_edits(s, name)
        if name == "index.html":
            s = home_v2(s)
        s = s.replace('<body data-version="2">', '<body data-version="2" class="bf">', 1)
        s = common(s, "v3bf", lambda x: x.replace('<script src="../assets/js/bf.js', link + '\n  <script src="../assets/js/bf.js', 1), "bf.js")
        open(f"{d}/{name}", "w", encoding="utf-8").write(s)
    print("v3bf (V2 based):", len(os.listdir(d)))


def build_v4bf():  # V3 based
    d = f"{ROOT}/v4bf"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    H3 = h('assets/css/v3bf.css')
    for f in sorted(glob.glob(f"{tmp}/v3/*.html")):
        s = open(f, encoding="utf-8").read()
        s = common(s, "v4bf", lambda x: re.sub(r'\.\./assets/css/v3\.css\?v=[0-9a-f]+', '../assets/css/v3bf.css?v=' + H3, x), "v3bf.js")
        open(f"{d}/{os.path.basename(f)}", "w", encoding="utf-8").write(s)
    print("v4bf (V3 based):", len(os.listdir(d)))


build_v3bf()
build_v4bf()
