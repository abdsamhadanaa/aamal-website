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

# Client: "What we offer" as an icon grid (Dribbble reference), long lists behind "View full scope"
_I = {
 "pen": '<path d="M3 21l3-1 11-11-2-2L4 18z"/><path d="M14 6l2-2 4 4-2 2"/>',
 "gauge": '<circle cx="12" cy="13" r="8"/><path d="M12 13l4-4"/><path d="M8 5l-1-2M16 5l1-2"/>',
 "box": '<path d="M3 7l9-4 9 4v10l-9 4-9-4z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
 "monitor": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4M7 10h2l2-3 2 6 2-3h2"/>',
 "helmet": '<path d="M3 18h18"/><path d="M5 18v-3a7 7 0 0114 0v3"/><path d="M10 9V6h4v3"/>',
 "wrench": '<path d="M14.7 6.3a4 4 0 015 5L12 19l-4 1 1-4z"/><path d="M5 5l4 4"/>',
 "wave": '<path d="M2 12c2.5-2 4.5-2 7 0s4.5 2 7 0 4.5-2 6 0"/><path d="M2 17c2.5-2 4.5-2 7 0s4.5 2 7 0 4.5-2 6 0"/><path d="M2 7c2.5-2 4.5-2 7 0s4.5 2 7 0 4.5-2 6 0"/>',
 "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>',
 "bed": '<path d="M3 18V7M21 18v-5a3 3 0 00-3-3H10v8"/><path d="M3 14h18"/><circle cx="6.5" cy="11" r="1.5"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
 "user": '<circle cx="10" cy="8" r="4"/><path d="M3 20a7 7 0 0114 0"/><path d="M17 4l2 2 3-3"/>',
 "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 010 18M12 3a14 14 0 000 18"/>',
 "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
 "chart": '<path d="M4 20V4M4 20h16"/><path d="M8 15l3-4 3 2 5-6"/>',
 "factory": '<path d="M3 21V10l6 3V9l6 3V5h6v16z"/><path d="M7 17h2M12 17h2M17 17h2"/>',
 "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 01-12 0c0-4.5 6-11 6-11z"/>',
 "flame": '<path d="M12 3c1 4 5 5 5 10a5 5 0 01-10 0c0-3 2-4 2-7 2 1 3 2 3 4"/>',
 "ship": '<path d="M3 17l2 3h14l2-3H3z"/><path d="M6 17V11h12v6M12 4v7M9 7h6"/>',
 "cpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
 "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.7 2.7L16.5 9"/>',
 "play": '<circle cx="12" cy="12" r="9"/><path d="M10 8l6 4-6 4z"/>',
 "power": '<path d="M12 3v8"/><path d="M6.3 7a8 8 0 1011.4 0"/>',
 "doc": '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 13h7M9 17h5"/>',
 "people": '<circle cx="9" cy="8" r="3.5"/><circle cx="17" cy="9" r="2.5"/><path d="M2.5 20a6.5 6.5 0 0113 0M15 14.5a5 5 0 016.5 5"/>',
 "headset": '<path d="M4 14v-2a8 8 0 0116 0v2"/><rect x="3" y="14" width="4" height="6" rx="1.5"/><rect x="17" y="14" width="4" height="6" rx="1.5"/>',
 "chat": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8"/>',
 "link": '<path d="M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1-1"/>',
 "ball": '<circle cx="12" cy="12" r="9"/><path d="M12 7l4 3-1.5 5h-5L8 10z"/><path d="M12 3v4M21 10l-5 0M17.5 19l-3-4M6.5 19l3-4M3 10h5"/>',
 "bag": '<path d="M5 8h14l-1 13H6z"/><path d="M9 8V6a3 3 0 016 0v2"/>',
 "flag": '<path d="M5 21V4"/><path d="M5 4h12l-2 4 2 4H5"/>',
 "brush": '<path d="M19 3l2 2-9 9-3-3z"/><path d="M8 13a3 3 0 00-3 3c0 2-2 3-2 3h4a4 4 0 004-4z"/>',
 "pipe": '<path d="M3 9h10a4 4 0 014 4v8"/><path d="M3 15h7a1 1 0 011 1v5"/><path d="M3 7v10M15 21h8"/>',
}
_RULES = [
 ("electrical design","pen"),("instrumentation design","gauge"),("electrical procurement","box"),("instrumentation procurement","monitor"),
 ("construction","helmet"),("maintenance","wrench"),("public access","wave"),("real estate","home"),("hospitality","bed"),("beach","sun"),
 ("experiences","star"),("talent","user"),("global","globe"),("managed","layers"),("pems","chart"),("oil","flame"),("energy","factory"),
 ("shipping","ship"),("technolog","cpu"),("pre-commissioning","check"),("commissioning","power"),("start-up","play"),("turnkey","helmet"),
 ("proprietary","cpu"),("implementation","layers"),("procedures","doc"),("outsourcing","people"),("technical support","headset"),
 ("consultancy","chat"),("integration","link"),("clubhouse","home"),("design","pen"),("fit-out","ball"),("consumables","bag"),
 ("contracting","doc"),("operate","power"),("event","flag"),("polyurethane","drop"),("acrylic","brush"),("cementitious","layers"),
 ("bituminous","drop"),("industrial coating","factory"),("pipe","pipe"),
]
def _icon(title):
    t = title.lower()
    for k, v in _RULES:
        if k in t:
            return _I[v]
    return _I["check"]

def offer_icons(s):
    if 'id="offer"' not in s or "offer-card__icon" in s:
        return s
    i = s.index('id="offer"'); j = s.index('</section>', i)
    sec = s[i:j]
    sec = re.sub(r'\s*<ul class="s-included">.*?</ul>', '', sec, count=1, flags=re.S)
    def card(m):
        a = m.group(0)
        title = re.search(r'<h3>(.*?)</h3>', a, re.S).group(1)
        a = re.sub(r'<span class="offer-card__num">\d+</span>',
                   '<span class="offer-card__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + _icon(title) + '</svg></span>', a, count=1)
        def wrap(u):
            n = u.group(0).count('<li>')
            return '<details class="offer-card__more"><summary>View full scope (' + str(n) + ')</summary>' + u.group(0) + '</details>'
        a = re.sub(r'<ul class="dot-list">.*?</ul>', wrap, a, count=1, flags=re.S)
        return a
    sec = re.sub(r'<article class="offer-card">.*?</article>', card, sec, flags=re.S)
    return s[:i] + sec + s[j:]

# Client pick (option B): "What we offer" as tabs with a photo panel — E&I page first for review
OFFER_TABS_DRAFT = {
    "electrical-instrumentation.html": ["services/pm-plans", "services/ws-refinery-night", "services/ei-hero",
                                        "hero-refinery", "hero-construction", "hero-oil-gas"],
}
OFFER_TABS = {}  # client reviewing a private draft (draft-offer/) first
_CK = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9.5"/><path d="M8 12.5l2.7 2.7L16.5 9"/></svg>'
_TABS_JS = """<script>
document.querySelectorAll('.otabs').forEach(function (w) {
  var tabs = w.querySelectorAll('[role=tab]'), panels = w.querySelectorAll('[role=tabpanel]');
  function show(i, focus) {
    tabs.forEach(function (t, j) { var on = i === j; t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1; t.classList.toggle('is-on', on); });
    panels.forEach(function (p, j) { p.hidden = i !== j; });
    if (focus) tabs[i].focus();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { show(i); });
    t.addEventListener('keydown', function (e) {
      var k = e.key, n = tabs.length;
      if (k === 'ArrowDown' || k === 'ArrowRight') { e.preventDefault(); show((i + 1) % n, true); }
      if (k === 'ArrowUp' || k === 'ArrowLeft') { e.preventDefault(); show((i - 1 + n) % n, true); }
    });
  });
});
</script>"""

def offer_tabs(s):
    imgs = OFFER_TABS.get(PAGE[0])
    if not imgs or 'class="otabs"' in s:
        return s
    i = s.index('id="offer"'); j = s.index('</section>', i)
    sec = s[i:j]
    cards = re.findall(r'<article class="offer-card">(.*?)</article>', sec, re.S)
    tabs, panels = [], []
    for n, c in enumerate(cards):
        t = re.search(r'<h3>(.*?)</h3>', c, re.S).group(1)
        d = re.search(r'<p>(.*?)</p>', c, re.S).group(1)
        lis = re.findall(r'<li>(.*?)</li>', c, re.S)
        im = imgs[n % len(imgs)]
        on = n == 0
        tabs.append('<button type="button" role="tab" id="ot-%d" aria-controls="op-%d" aria-selected="%s" tabindex="%d" class="otabs__tab%s"><span>%02d</span>%s</button>'
                    % (n, n, "true" if on else "false", 0 if on else -1, " is-on" if on else "", n + 1, t))
        lst = ('<ul class="otabs__list">' + "".join('<li>' + _CK + '<span>' + l + '</span></li>' for l in lis) + '</ul>') if lis else ''
        panels.append('<div role="tabpanel" id="op-%d" aria-labelledby="ot-%d" class="otabs__panel"%s>'
                      '<img class="otabs__img" src="../assets/img/%s-800.webp" srcset="../assets/img/%s-800.webp 800w, ../assets/img/%s.webp 1200w" sizes="(max-width: 900px) 100vw, 800px" width="1200" height="800" alt="" loading="lazy" decoding="async">'
                      '<div class="otabs__body"><h3>%s</h3><p>%s</p>%s</div></div>'
                      % (n, n, "" if on else " hidden", im, im, im, t, d, lst))
    block = ('<div class="otabs"><div class="otabs__nav" role="tablist" aria-label="Our services">' + "".join(tabs) +
             '</div><div class="otabs__panels">' + "".join(panels) + '</div></div>')
    sec = re.sub(r'\s*<ul class="s-included">.*?</ul>', '', sec, count=1, flags=re.S)
    k = sec.index('<div class="offer-grid">')
    e = sec.index('</article>\n        </div>', k) + len('</article>\n        </div>') if '</article>\n        </div>' in sec[k:] else None
    if e is None:
        m = re.search(r'<div class="offer-grid">.*?</article>\s*</div>', sec[k:], re.S)
        e = k + m.end()
    sec = sec[:k] + block + sec[e:]
    s = s[:i] + sec + s[j:]
    return s.replace('</body>', _TABS_JS + '\n</body>', 1)

def about_class(s):
    # Client: bigger text on About Us
    if PAGE[0] != "about.html":
        return s
    return re.sub(r'<body([^>]*?)class="([^"]*)"', r'<body\1class="\2 page-about"', s, count=1)

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
    # s = offer_icons(s)  # client: not liked, kept for reference
    s = offer_tabs(s)
    # Client: DUPLAYS stadium photo for Sports Facilities everywhere (home slide/bento, service cards)
    if PAGE[0] != "index.html":  # Client: home keeps the original sports render (hero slider) and lagoon card
        s = s.replace('src="../assets/img/services/sports-hero.webp" width="791" height="442"',
                      'src="../assets/img/services/dup-stadium.webp" srcset="../assets/img/services/dup-stadium-800.webp 800w, ../assets/img/services/dup-stadium.webp 1200w" sizes="(max-width: 900px) 100vw, 50vw" width="1200" height="800"')
        s = s.replace('alt="Render of a sports complex with football pitches and padel courts"', 'alt="Aerial view of a sports campus with a stadium, track and pitches"')
        s = s.replace('alt="Sports complex render"', 'alt="Aerial view of a sports campus"')
    if PAGE[0] == "hospitality.html":  # Client: sector hero shows sport (DUPLAYS courts) instead of the lagoon
        s = re.sub(r'(<img class="s-hero__img" src="\.\./assets/img/services/)cl-hotel-aerial(\.webp" srcset="\.\./assets/img/services/)cl-hotel-aerial(-800\.webp 800w, \.\./assets/img/services/)cl-hotel-aerial(\.webp 1200w"[^>]*?)width="\d+" height="\d+" alt="[^"]*"',
                   r'\1dup-courts\2dup-courts\3dup-courts\4width="1200" height="511" alt="Indoor padel and multi-sport courts"', s, count=1)
        s = s.replace("cl-hotel-aerial", "dup-courts") if 'class="s-hero__img" src="../assets/img/services/dup-courts' in s else s
    if False and PAGE[0] == "index.html":  # (reverted by client) home Hospitality & Sports card used a DUPLAYS photo
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
