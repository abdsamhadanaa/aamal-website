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
    fh.write(open(f"{ROOT}/assets/css/bf.css", encoding="utf-8").read().split("/* Partners: balanced logos")[1].join(["/* Partners: balanced logos", ""]) if False else "\n/* Partners: balanced logos" + open(f"{ROOT}/assets/css/bf.css", encoding="utf-8").read().split("/* Partners: balanced logos", 1)[1])
js = open(f"{tmp}/assets/js/main.js", encoding="utf-8").read()
# Client: main service categories in the menu are headings, not links
js = js.replace('<a class="nav-mega__title" href="${g.href}">${esc(g.label)}</a>', '<span class="nav-mega__title">${esc(g.label)}</span>')
assert 'class="nav-mega__title" href' not in js
# Client: no "Services overview" link in the Services dropdown
js = js.replace('<a class="nav-drop__overview nav-mega__overview" href="${l.href}">Services overview →</a>', '')
assert 'Services overview' not in js
js = js.replace("A'amal Global Recognition", "Global Recognition")
js = js.replace("Project & Business Management", "Project Management Solution").replace("Project &amp; Business Management", "Project Management Solution")
# Client: About Us menu = About Us, Founder & CEO message, Mission and Vision
js = js.replace("about.sub = about.sub.filter((x) => x.href !== 'awards.html');",
                "about.sub = [{ label: 'Founder & CEO message', href: 'about.html#founder' }, { label: 'Mission and Vision', href: 'about.html#vision' }];")
js = js.replace('href="${l.href}">${esc(l.label)} overview</a>', 'href="${l.id === \'about\' ? \'about.html#overview\' : l.href}">${l.id === \'about\' ? \'About Us\' : esc(l.label) + \' overview\'}</a>')
assert "Mission and Vision" in js and "'About Us' : esc" in js
js = js.replace("{ label: \"A'amal at Global Stage\", href: 'awards.html#global-stage' },", "{ label: 'Global engagement', href: 'awards.html#global-engagement' },\n    { label: \"A'amal at Global Stage\", href: 'awards.html#global-stage' },")
assert 'awards.html#global-engagement' in js
# Client: keep Sustainability in the menu
js = js.replace("const strip = (arr) => arr.filter((l) => l.id !== 'responsibility');", "const strip = (arr) => arr;")
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
    # Project & Business Management: a working meeting at the table, no faces (replaces the photo of two men)
    # Project Management Solution sector: our own photo that shows the service (team reviewing project drawings)
    s = s.replace('pbm-business.webp 1100w', 'pm-plans.webp 1200w').replace('pbm-business', 'pm-plans')
    s = re.sub(r'(pm-plans\.webp"[^>]*?)alt="[^"]*"', r'\1alt="Project team reviewing engineering drawings"', s)
    s = s.replace('pm-plans.webp 1200w" style="object-position: 50% 30%"', 'pm-plans.webp 1200w" style="object-position: 50% 50%"')
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


PARTNER_TAGS = {"logo-crystal-lagoons": "Artificial lagoons technology", "logo-airswift": "Workforce &amp; recruitment",
                "logo-weel-sandvig": "Energy &amp; process innovation", "logo-duplays": "Sports facilities &amp; programming",
                "logo-experts-ei": "Electrical &amp; instrumentation"}


def partner_tiles(s):
    """Partners: logos at a balanced optical size, each with a one-line note on what the partner brings."""
    if "partners__grid--logos" not in s:
        return s
    def tag(m):
        key = re.search(r'partners/(logo-[a-z-]+)\.', m.group(0))
        t = PARTNER_TAGS.get(key.group(1)) if key else None
        if not t:
            return m.group(0)
        return m.group(0)[:-4] + f'<span class="partner-tag">{t}</span></a>'
    s = re.sub(r'<a href="[^"]*"[^>]*><img src="\.\./assets/img/partners/[^"]+"[^>]*></a>', tag, s)
    return s.replace("partners__grid partners__grid--logos", "partners__grid partners__grid--logos partners__grid--bf", 1)


# ---------- Global Recognition: Global Stage + Global Engagement (highest-resolution photos only) ----------
STAGE = [("founder/world-chambers-congress.webp", 1000, 750, "Speaker at the 12th World Chambers Congress — “Leading with vision”"),
         ("media/m10.webp", 746, 561, "Panel speaker as Chairman of ICC Saudi Arabia and ICC Executive Board Member"),
         ("media/m19.webp", 900, 600, "Address to the Singapore Business Federation"),
         ("media/m20.webp", 900, 596, "ICC and Qatar Chamber forum"),
         ("media/m21.webp", 900, 653, "Panel discussion at an ICC forum"),
         ("media/m18.webp", 900, 599, "Panel speaker at an international business conference")]
ENGAGE = [("media/m7.webp", 900, 669, "CNBC Arabia interview on the Saudi economy"),
          ("media/m8.webp", 900, 651, "CNBC Arabia interview at the Saudi Trade Finance Summit"),
          ("media/m12.webp", 900, 679, "Signing an agreement between A'amal Group and SMIT — Morocco's Tourism Engineering and Investment Company"),
          ("founder/award-dubai.webp", 954, 1000, "Receiving an award at a business leadership event in Dubai"),
          ("founder/who-meeting.webp", 750, 1000, "Meeting with the World Health Organization"),
          ("founder/sridf-agreement.webp", 750, 526, "Signing an agreement with the Silk Road International Development Fund (SRIDF)")]


def gs_section(sid, pill, title, lead, items, tint):
    cards = "".join(f'<figure class="gs-card"><span class="gs-card__img"><img src="../assets/img/{src}" width="{w}" height="{h}" alt="{cap}" loading="lazy" decoding="async"></span><figcaption>{cap}</figcaption></figure>' for src, w, h, cap in items)
    return (f'<section class="section{" section--tint" if tint else ""}" id="{sid}">\n      <div class="container stack" style="gap: 32px">\n'
            f'        <div class="section-head"><div><span class="s-pill">{pill}</span><h2 class="h2" style="margin-top: 12px">{title}</h2></div><p>{lead}</p></div>\n'
            f'        <div class="gs-grid">{cards}</div>\n      </div>\n    </section>')


def global_sections(s):
    if 'id="global-stage"' not in s:
        return s
    a = s.index('<section class="section" id="global-stage">'); b = s.index("</section>", a) + len("</section>")
    new = (gs_section("global-engagement", "Media &amp; partnerships", "Global engagement", "Television interviews, agreements and official meetings around the world.", ENGAGE, False)
           + "\n\n    " + gs_section("global-stage", "A'amal Group", "A'amal at Global Stage", "Conferences and forums where A'amal Group represents Saudi business.", STAGE, True))
    return s[:a] + new + s[b:]


PAGE = [""]
# Client: replace the orange-coverall site photo with the updated, faceless photos
SITE_TEAM = {"human-resource-management.html": ("hr-handshake", "Handshake over documents after a successful hire"),
             "management.html": ("hr-handshake", "Handshake over documents after a successful hire"),
             "project-solutions.html": ("pm-plans", "Project team reviewing engineering drawings"),
             "services.html": ("pm-plans", "Project team reviewing engineering drawings")}


def swap_site_team(s):
    new = SITE_TEAM.get(PAGE[0])
    if not new:
        return s
    n, alt = new
    w = "1100w" if n == "pbm-meeting" else "1200w"
    s = re.sub(r'src="\.\./assets/img/services/as-site-team\.webp" srcset="[^"]*"', f'src="../assets/img/services/{n}.webp" srcset="../assets/img/services/{n}-800.webp 800w, ../assets/img/services/{n}.webp {w}"', s)
    s = s.replace('src="../assets/img/services/as-site-team.webp"', f'src="../assets/img/services/{n}.webp"')
    return re.sub(r'(src="\.\./assets/img/services/' + n + r'\.webp"[^>]*?)alt="[^"]*"', r'\1alt="' + alt + '"', s)


def swap_engineers(s):
    # Client: replace the two-engineers hero (faces visible) with our faceless site photo
    if PAGE[0] == "index.html":
        return s
    if PAGE[0] == "human-resource-management.html":
        n, w = "hr-airswift", "1100w"
    else:
        n, w = "om-site-team", "960w"
    s = re.sub(r'as-engineers-plant\.webp 1200w', f'{n}.webp {w}', s)
    s = s.replace("as-engineers-plant", n)
    s = s.replace('alt="Two engineers in hi-vis reviewing a tablet at a plant at dusk"',
                  'alt="Aerial view of an A\'amal project site team" style="object-position:50% 22%"')
    return s


COBRAND = {
    "human-resource-management.html": ("hr-handshake", "logo-airswift.svg", 208, 89, "Airswift", "Strategic workforce partnership in Saudi Arabia"),
}


def cobrand(s):
    """Client: service hero as an A'amal x partner co-brand design."""
    c = COBRAND.get(PAGE[0])
    if not c:
        return s
    bg, logo, w, h, name, line = c
    html = ('<div class="s-hero__img cobrand" role="img" aria-label="A\'amal Group in partnership with ' + name + '" '
            'style="--cb-bg:url(../img/services/' + bg + '.webp)">'
            '<div class="cobrand__panel">'
            '<img src="../assets/img/logo-v2-large.png" alt="A\'amal Group" width="786" height="577" class="cobrand__aamal">'
            '<span class="cobrand__x" aria-hidden="true"></span>'
            '<img src="../assets/img/partners/' + logo + '" alt="' + name + '" width="' + str(w) + '" height="' + str(h) + '" class="cobrand__partner">'
            '</div><p class="cobrand__line">' + line + '</p></div>')
    return re.sub(r'<img class="s-hero__img" src="\.\./assets/img/services/' + re.escape(bg) + r'\.webp"[^>]*>', lambda m: html, s, count=1)


EI_CARD = ('\n          <div class="partner-card">\n'
  '            <div class="partner-card__logo"><img src="../assets/img/partners/logo-experts-ei.webp" width="560" height="64" alt="Experts e&amp;i logo" loading="lazy" decoding="async"></div>\n'
  '            <div class="partner-card__text">\n'
  '              <span class="eyebrow">Our partner</span>\n'
  '              <strong>Experts e&amp;i</strong>\n'
  '              <p>Our electrical and instrumentation partner. <a class="text-link" href="https://www.experts-ei.com/" target="_blank" rel="noopener">experts-ei.com</a></p>\n'
  '            </div>\n'
  '          </div>')

def ei_partner(s):
    if PAGE[0] != "electrical-instrumentation.html" or "logo-experts-ei" in s:
        return s
    i = s.index('<div class="downloads">')
    j = s.index('</div>', s.index('</a>', i)) + len('</div>')
    return s[:j] + EI_CARD + s[j:]

def duplays_photos(s):
    """Client: Sports Facilities page uses photos from our partner DUPLAYS (duplays.com)."""
    if PAGE[0] != "sports-facilities.html":
        return s
    def img(cls, n, w, h, alt, extra):
        return (f'<img class="{cls}" src="../assets/img/services/{n}.webp" srcset="../assets/img/services/{n}-800.webp 800w, '
                f'../assets/img/services/{n}.webp 1200w" sizes="{extra}" width="{w}" height="{h}" alt="{alt}"')
    s = re.sub(r'<img class="s-hero__img" src="\.\./assets/img/services/sports-hero\.webp"[^>]*?(?=( fetchpriority| loading|>))',
               img("s-hero__img", "dup-stadium", 1200, 800, "Aerial view of a sports campus with a stadium, track and pitches — DUPLAYS", "(max-width: 1240px) 100vw, 1200px"), s, count=1)
    s = re.sub(r'<img class="s-split__img" src="\.\./assets/img/services/sports-complex\.webp"[^>]*?(?= loading|>)',
               img("s-split__img", "dup-courts", 1200, 511, "Indoor padel and multi-sport courts — DUPLAYS", "(max-width: 900px) 100vw, 45vw"), s, count=1)
    s = re.sub(r'<img class="s-cta__img" src="\.\./assets/img/services/cl-hotel-aerial\.webp"[^>]*?(?= loading|>)',
               img("s-cta__img", "dup-dome", 1200, 783, "", "100vw"), s, count=1)
    return s.replace("sports-hero.webp", "dup-stadium.webp")


def swap_hr_hero(s):
    # Client: HR hero in Saudi style, faceless
    if PAGE[0] != "human-resource-management.html":
        return s
    s = s.replace("hr-airswift-800.webp 800w, ../assets/img/services/hr-airswift.webp 1100w",
                  "hr-handshake-800.webp 800w, ../assets/img/services/hr-handshake.webp 1200w")
    s = s.replace("hr-airswift", "hr-handshake")
    s = s.replace('alt="Two professionals in suits meeting over a laptop"', 'alt="Handshake over documents after a successful hire"')
    s = cobrand(s)
    return re.sub(r'(<img class="s-hero__img" src="\.\./assets/img/services/pbm-saudi-desk\.webp"[^>]*?)alt="[^"]*"',
                  r'\1alt="Handshake over documents after a successful hire"', s, count=1)


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
    s = partner_tiles(s)
    # Client: no buttons under the About hero
    s = re.sub(r'\s*<div class="btn-row"[^>]*>\s*<a class="btn btn--primary" href="#overview">About us</a>\s*<a class="btn btn--outline" href="services.html">Our services</a>\s*</div>', '', s)
    # Client: A'amal logo beside the About us overview
    # Client: the logo is the hero of this section (no pill or heading), as tall as the text
    s = re.sub(r'<div class="about-overview__head">\s*<span class="s-pill">About us</span>\s*<h2 class="h2">An impeccable track record since 1994</h2>\s*</div>',
               '<div class="about-overview__head about-overview__head--logo"><div class="about-overview__logo"><img src="../assets/img/logo-v2.png" width="409" height="300" alt="A\'amal Group — Arab Economic &amp; Business Group — We grow together" loading="lazy" decoding="async"></div></div>', s, count=1)
    # Client: "Global Recognition", without "A'amal"
    s = s.replace("A'amal Global Recognition", "Global Recognition").replace("A&#x27;amal Global Recognition", "Global Recognition")
    # Client: style the logo card like the Founder & CEO photo, with the same 1994 badge
    # (later: styled like the partner cards — logo, divider, one short line)
    badge = '<span class="about-overview__tag"><strong>Since 1994</strong><i> · </i>Al Khobar, Saudi Arabia</span>'
    s = s.replace('loading="lazy" decoding="async"></div></div>', 'loading="lazy" decoding="async">' + badge + '</div></div>', 1) if 'about-overview__logo' in s else s
    # (Read more on phones removed at the client's request: full text shows everywhere)
    # Client: no sector chips; the sectors go back into the sentence, as in the client's text
    s = re.sub(r'numerous sectors, including:</p>\s*<ul class="about-overview__sectors">.*?</ul>',
               "numerous sectors, including Real Estate, Hospitality, Construction Management, Energy Efficiency, Oil and Gas, HR Management, Industry Transformation and Investment.</p>", s, count=1, flags=re.S)
    s = global_sections(s)
    # Client: an "About Us" heading on the overview text
    s = s.replace('<div class="about-overview__body">\n          <p>Since our inception', '<div class="about-overview__body">\n          <h2 class="h2 about-overview__title">About Us</h2>\n          <p>Since our inception', 1)
    # Client: no photo strip under the Services hero
    s = re.sub(r'\s*<div class="container">\s*<div class="hero-strip hero-strip--svc">.*?</div>\s*</div>', '', s, count=1, flags=re.S)
    s = swap_site_team(s)
    s = swap_engineers(s)
    s = swap_hr_hero(s)
    s = cobrand(s)
    s = duplays_photos(s)
    s = ei_partner(s)
    # Client: DUPLAYS stadium photo for Sports Facilities everywhere (home slide/bento, service cards)
    s = s.replace('src="../assets/img/services/sports-hero.webp" width="791" height="442"',
                  'src="../assets/img/services/dup-stadium.webp" srcset="../assets/img/services/dup-stadium-800.webp 800w, ../assets/img/services/dup-stadium.webp 1200w" sizes="(max-width: 900px) 100vw, 50vw" width="1200" height="800"')
    s = s.replace('alt="Render of a sports complex with football pitches and padel courts"', 'alt="Aerial view of a sports campus with a stadium, track and pitches"')
    s = s.replace('alt="Sports complex render"', 'alt="Aerial view of a sports campus"')
    if PAGE[0] == "hospitality.html":  # Client: sector hero shows sport (DUPLAYS courts) instead of the lagoon
        s = re.sub(r'(<img class="s-hero__img" src="\.\./assets/img/services/)cl-hotel-aerial(\.webp" srcset="\.\./assets/img/services/)cl-hotel-aerial(-800\.webp 800w, \.\./assets/img/services/)cl-hotel-aerial(\.webp 1200w"[^>]*?)width="\d+" height="\d+" alt="[^"]*"',
                   r'\1dup-courts\2dup-courts\3dup-courts\4width="1200" height="511" alt="Indoor padel and multi-sport courts"', s, count=1)
        s = s.replace("cl-hotel-aerial", "dup-courts") if 'class="s-hero__img" src="../assets/img/services/dup-courts' in s else s
    if PAGE[0] == "index.html":  # Client: home Hospitality & Sports card uses a DUPLAYS photo
        s = s.replace('<img src="../assets/img/services/cl-hotel-aerial-800.webp" width="800" height="450" alt="Aerial view of a resort built around a crystal lagoon"',
                      '<img src="../assets/img/services/dup-stadium-800.webp" width="800" height="533" alt="Aerial view of a sports campus with a stadium, track and pitches"')
    # Client: the third sector is called "Project Management Solution" everywhere
    s = s.replace("Project &amp; Business Management", "Project Management Solution").replace("Project & Business Management", "Project Management Solution")
    s = s.replace("<span>Business Management</span></a>", "<span>Project Management Solution</span></a>")
    # Client: the Services page lists the 8 services like the menu — no sector (category) blocks or tags
    while '<h2 class="h2">See it in action</h2>' in s:
        s = bv3.drop_section(s, '<h2 class="h2">See it in action</h2>', required=False)
    if PAGE[0] == "services.html":
        s = bv3.drop_section(s, '<h2 class="h2">Hospitality &amp; Sports</h2>', required=False)
        s = bv3.drop_section(s, '<h2 class="h2">From plan to operation</h2>', required=False)
        s = re.sub(r'\s*<span class="svc-card__tag">[^<]*</span>', '', s)
        s = re.sub(r'<div class="s-head s-head--center">\s*<span class="s-pill">All services</span>\s*<h2 class="h2">Find the right service</h2>\s*</div>\s*', '', s, count=1)
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
        PAGE[0] = name
        s = common(s, "v3bf", lambda x: x.replace('<script src="../assets/js/bf.js', link + '\n  <script src="../assets/js/bf.js', 1), "bf.js")
        open(f"{d}/{name}", "w", encoding="utf-8").write(s)
    print("v3bf (V2 based):", len(os.listdir(d)))


def build_v4bf():  # V3 based
    d = f"{ROOT}/v4bf"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    H3 = h('assets/css/v3bf.css')
    for f in sorted(glob.glob(f"{tmp}/v3/*.html")):
        s = open(f, encoding="utf-8").read()
        PAGE[0] = os.path.basename(f)
        s = common(s, "v4bf", lambda x: re.sub(r'\.\./assets/css/v3\.css\?v=[0-9a-f]+', '../assets/css/v3bf.css?v=' + H3, x), "v3bf.js")
        open(f"{d}/{os.path.basename(f)}", "w", encoding="utf-8").write(s)
    print("v4bf (V3 based):", len(os.listdir(d)))


build_v3bf()
build_v4bf()
