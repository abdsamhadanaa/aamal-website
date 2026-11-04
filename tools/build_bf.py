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
# Client: no "Services overview" link in the Services dropdown
js = js.replace('<a class="nav-drop__overview nav-mega__overview" href="${l.href}">Services overview →</a>', '')
assert 'Services overview' not in js
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
    # (client later asked to keep "Three sectors, one partner")
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
    # PM: a project team reviewing engineering drawings (no faces, shows the service)
    s = s.replace('pbm-saudi-desk.webp 1600w', 'pm-plans.webp 1200w').replace('pbm-saudi-desk', 'pm-plans')
    s = re.sub(r'(pm-plans\.webp"[^>]*?)alt="[^"]*"', r'\1alt="Project team reviewing engineering drawings"', s)
    s = re.sub(r'(hr-handshake\.webp"[^>]*?)alt="[^"]*"', r'\1alt="Handshake over documents after a successful hire"', s)
    return s


B20_IMG = '<img src="../assets/img/recognition/b20-usa-2026.webp" width="559" height="133" style="max-height:48px; width:auto" alt="B20 USA 2026 logo" loading="lazy" decoding="async">'


# ---------- Updated biography of Yassin Al Suroor (Nov 2026) ----------
BIO = """
    <section class="section" id="biography">
      <div class="container about-overview">
        <div class="about-overview__head">
          <span class="s-pill">Founder &amp; CEO</span>
          <h2 class="h2">Yassin Al Suroor</h2>
          <a class="text-link" href="https://sa.linkedin.com/in/yassin-al-suroor-840a551b" target="_blank" rel="noopener">LinkedIn profile →</a>
        </div>
        <div class="about-overview__body">
          <p>Yassin Al Suroor is an Entrepreneur, Founder &amp; CEO of A'amal Group, a diversified enterprise operating across the Middle East, Southeast Asia, and Africa. He actively invests strategically in innovative companies globally, particularly in the digital economy. He serves as Chairman of Airswift Saudi and Chairman of Study Group Saudi. In addition, he serves on the boards of numerous regional and international companies and has played a pivotal role in developing privatization and public-private partnership (PPP) projects.</p>
          <p>Yassin's contributions to the business world have earned him multiple awards, including the Best Entrepreneur in Investment Award, the Family Office Lifetime Achievement Award, the Global Inspirational Leaders Award, and recognition as one of the Successful Businessmen in Saudi Arabia by The Gulf Entrepreneur magazine in 2024, as well as recognition by the B20/G20 Saudi Arabia and the World Health Organization. His leadership and business acumen have garnered acclaim from international business communities, as well as governmental and non-governmental organizations.</p>
          <p>He has held key positions in global organizations, including Chairman of the International Chamber of Commerce in Saudi Arabia, Vice Chair of the International Chamber of Commerce (ICC) in Paris, the world's largest business organization representing 45 million companies globally. He served as an Executive Board member and G20 representative of the World Chambers Federation, the world's largest chamber organization representing 12,000 chambers globally. Yassin also sits on the board of the Arab-Belgian-Luxembourg Chamber of Commerce and is a member of the United Nations Global Compact, a voluntary initiative supporting UN goals. His involvement in global business extends to his role on the Executive Committee of B20 Saudi Arabia in 2020, as well as his membership in the B20 International Business Advocacy Caucus in Indonesia (2022), Brazil (2024), South Africa (2025), and as Co-Chair of the Economic Growth Task Force of B20 USA 2026.</p>
          <p>A recognized international speaker, Yassin is widely regarded for his expertise in Public-Private Partnerships. He has been a keynote speaker at numerous high-profile forums. Yassin advocates for businesses that contribute to peace and well-being through CSR. He is the co-founder and a board member of The National Role Model Society in Saudi Arabia and sits on the Board of Trustees of the Merchants of Peace Fund in Paris. He also supports humanitarian efforts focused on empowering the lives of children.</p>
        </div>
      </div>
    </section>
"""

MEDAL = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#1FB04B" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="9" r="6"/><path d="M8.5 13.5L7 22l5-3 5 3-1.5-8.5"/></svg>'


def role_card(logo, title, role, text, year=""):
    y = f'<span class="recog-card__year">{year}</span>' if year else ""
    return f'<article class="recog-card"><div class="recog-card__logo">{logo}</div>{y}<h3>{title}</h3><strong>{role}</strong><p>{text}</p></article>'


def bio_updates(s):
    # The biography text itself is not shown; it is only used to update roles and awards below.
    if 'id="roles"' in s and '<h3>ICC World Chambers Federation</h3>' in s:
        sub = bv3.sub1
        s = sub(s, "<p>Connecting a network of more than 3,000 chambers of commerce in over 100 countries.</p>",
                "<p>The world's largest chamber organisation, representing 12,000 chambers globally.</p>")
        s = s.replace("<h3>ICC World Chambers Federation</h3><strong>Executive Committee Member · G20 Representative</strong>",
                      "<h3>ICC World Chambers Federation</h3><strong>Executive Board Member · G20 Representative</strong>")
        s = sub(s, "<p>Continuing to represent global business priorities to G20 leaders, through Brazil and South Africa.</p>",
                "<p>Continuing to represent global business priorities to G20 leaders, in Brazil (2024) and South Africa (2025).</p>")
        s = re.sub(r'(<h3>B20 USA 2026</h3>)<p>[^<]*</p>', r'\1<strong>Co-Chair, Economic Growth Task Force</strong><p>Shaping business recommendations on economic growth for the United States G20 Presidency.</p>', s)
        # New chairmanships, after ICC Saudi Arabia
        i = s.index("<h3>ICC Saudi Arabia</h3>"); j = s.index("</article>", i) + len("</article>")
        new = (role_card('<img src="../assets/img/partners/logo-airswift.svg" width="208" height="89" style="max-height:48px" alt="Airswift logo" loading="lazy" decoding="async">',
                         "Airswift Saudi", "Chairman", "Workforce solutions for the energy, process and infrastructure industries in the Kingdom.")
               + role_card('<span class="logo-text">Study Group</span>', "Study Group Saudi", "Chairman", "Leading the Saudi arm of the international education group."))
        s = s[:j] + new + s[j:]
        n = s[s.index('id="roles"'):].split("</section>")[0].count('<article class="recog-card">')
        s = re.sub(r'<strong>\d+</strong><span>Global leadership roles</span>', f'<strong>{n}</strong><span>Global leadership roles</span>', s)
        s = s.replace("<strong>3</strong><span>B20 / G20 presidencies served</span>", "<strong>5</strong><span>B20 / G20 presidencies served</span>")
        # Awards and recognition
        s = sub(s, "<h3>Successful Entrepreneur</h3><span>Recognised by The Gulf Entrepreneur magazine</span>",
                "<h3>Successful Businessmen in Saudi Arabia</h3><span>The Gulf Entrepreneur magazine, 2024</span>")
        i = s.index("<h3>Successful Businessmen in Saudi Arabia</h3>"); j = s.index("</article>", i) + len("</article>")
        extra = "".join(f'<article class="award-item">{MEDAL}<div><h3>{t}</h3><span>{d}</span></div></article>' for t, d in
                        [("Recognition by B20 / G20 Saudi Arabia", "For contributions during the Kingdom's G20 Presidency"),
                         ("Recognition by the World Health Organization", "Awarded to Yassin Al Suroor")])
        s = s[:j] + extra + s[j:]
        a = s[s.index('id="awards"'):].split("</section>")[0].count('<article class="award-item">')
        s = re.sub(r'<strong>\d+</strong><span>International awards</span>', f'<strong>{a}</strong><span>Awards and recognitions</span>', s)
    return s


def common(s, folder, css, js_file):
    s = founder_ceo(s)
    s = s.replace(B20, B20_IMG)
    s = s.replace('<div><h2 class="x-h2">Our Businesses</h2></div>', '<div><span class="s-pill">Our Businesses</span><h2 class="x-h2">Three sectors, one partner</h2></div>')
    # Client: home intro lists each service, separated by dashes
    s = re.sub(r'A diversified Saudi group working across hospitality and sports, industrial services, and project and business management(?: —|,) with a firm commitment',
               'A diversified Saudi group working across Hospitality - Sports Facilities - Industrial Services - Project Management Solution, with a firm commitment', s)
    # Partners: Experts e&i (www.experts-ei.com) instead of the A'amal E&I text placeholder
    s = re.sub(r'<a href="electrical-instrumentation\.html" title="A\'amal E&amp;I"><span class="logo-text">A\'amal<small>E&amp;I</small></span></a>',
               '<a href="https://www.experts-ei.com/" target="_blank" rel="noopener" title="Experts e&amp;i"><img src="../assets/img/partners/logo-experts-ei.webp" width="560" height="64" alt="Experts e&amp;i" loading="lazy" decoding="async"></a>', s)
    s = bio_updates(s)
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
