/* =========================================================
   A'amal Group — site scripts
   - <site-header> / <site-footer>: shared header and footer
   - Mobile menu toggle
   - Home hero slider
   - Media filters
   - Contact / careers form handling (front-end only)
   ========================================================= */

/* Images live in /assets/img, next to this script's folder. */
const IMG = new URL('../img/', document.currentScript.src).href;

/* Which design version this page belongs to: <body data-version="2"> */
const VERSION = document.body.dataset.version === '2' ? 2 : 1;

/* Logo files: Version 2 uses the updated logo with the "We grow together" tagline */
const LOGO = VERSION === 2
  ? { light: 'logo-v2.png', dark: 'logo-v2-white.png', w: 409, h: 300 }
  : { light: 'logo.png', dark: 'logo-white.png', w: 661, h: 276 };

const NAV = {
  1: [
    { id: 'home', label: 'Home', href: 'index.html' },
    { id: 'about', label: 'About Us', href: 'about.html' },
    { id: 'services', label: 'Services', href: 'services.html' },
    { id: 'responsibility', label: 'Social Responsibility', href: 'responsibility.html' },
    { id: 'media', label: 'Media', href: 'media.html' },
    { id: 'careers', label: 'Careers', href: 'careers.html' },
  ],
  2: [
    { id: 'home', label: 'Home', href: 'index.html' },
    { id: 'about', label: 'About Us', href: 'about.html', sub: [
      { label: 'Founder & CEO message', href: 'about.html#founder' },
      { label: 'Social work & responsibility', href: 'responsibility.html' },
      { label: "A'amal Global Recognition", href: 'awards.html' },
    ] },
    { id: 'services', label: 'Services', href: 'services.html', mega: [
      { label: 'Hospitality & Sports', href: 'hospitality.html', items: [
        { label: 'Artificial Lagoons', href: 'artificial-lagoons.html' },
        { label: 'Sports Facilities', href: 'sports-facilities.html' },
      ] },
      { label: 'Industrial Services', href: 'industrial-services.html', items: [
        { label: 'Operations & Maintenance', href: 'operations-maintenance.html' },
        { label: 'Electrical & Instrumentation', href: 'electrical-instrumentation.html' },
        { label: 'Waterproofing & Industrial Coating', href: 'waterproofing-industrial-coating.html' },
        { label: 'Industry Transformation', href: 'industry-transformation.html' },
      ] },
      { label: 'Project & Business Management', href: 'management.html', items: [
        { label: 'Human Resource Management', href: 'human-resource-management.html' },
        { label: 'Project Solutions', href: 'project-solutions.html' },
      ] },
    ] },
    { id: 'recognition', label: 'Global Recognition', href: 'awards.html', sub: [
      { label: 'Global leadership roles', href: 'awards.html#roles' },
      { label: 'Awards and honours', href: 'awards.html#awards' },
      { label: 'Company commitments', href: 'awards.html#company' },
      { label: 'Milestones', href: 'awards.html#milestones' },
    ] },
    { id: 'responsibility', label: 'Sustainability', href: 'responsibility.html' },
    { id: 'media', label: 'Media', href: 'media.html' },
    { id: 'careers', label: 'Careers', href: 'careers.html' },
  ],
}[VERSION];

/* Version 3 (design option): business-led navigation, "Get in Touch" call to action */
const IS_V3 = document.body.classList.contains('v3');
if (IS_V3) {
  const about = NAV.find((l) => l.id === 'about');
  if (about) about.sub = [
    { label: 'Founder & CEO message', href: 'about.html#founder' },
    { label: "A'amal Global Recognition", href: 'awards.html' },
    { label: 'Social work & responsibility', href: 'responsibility.html' },
  ];
  const svc = NAV.find((l) => l.id === 'services');
  if (svc) svc.label = 'Our Businesses';
  const keep = ['home', 'about', 'services', 'responsibility', 'media', 'careers'];
  const order = keep.map((id) => NAV.find((l) => l.id === id)).filter(Boolean);
  order.push({ id: 'contact', label: 'Contact', href: 'contact.html' });
  NAV.splice(0, NAV.length, ...order);
}

/* ---------- Shared header ---------- */
class SiteHeader extends HTMLElement {
  connectedCallback() {
    const active = this.getAttribute('active') || '';
    const esc = (t) => t.replace(/&/g, '&amp;');
    const caret = '<svg class="nav-caret" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>';
    const links = NAV.map((l, i) => {
      const cur = l.id === active ? ' aria-current="page"' : '';
      if (!l.sub && !l.mega) return `<a href="${l.href}"${cur}>${esc(l.label)}</a>`;
      const panel = l.mega
        ? `<div class="nav-drop__panel nav-drop__panel--mega" id="drop-${i}"><a class="nav-drop__overview nav-mega__overview" href="${l.href}">${IS_V3 ? 'All businesses and services →' : 'Services overview →'}</a>${l.mega.map((g) =>
            `<div class="nav-mega__col"><a class="nav-mega__title" href="${g.href}">${esc(g.label)}</a>${g.items.map((x) => `<a href="${x.href}">${esc(x.label)}</a>`).join('')}</div>`).join('')}
            <a class="nav-mega__all" href="${l.href}#all-services">View all 8 services →</a></div>`
        : `<div class="nav-drop__panel" id="drop-${i}"><a class="nav-drop__overview" href="${l.href}">${esc(l.label)} overview</a>${l.sub.map((x) => `<a href="${x.href}">${esc(x.label)}</a>`).join('')}</div>`;
      return `<div class="nav-drop"><div class="nav-drop__head"><a href="${l.href}"${cur}>${esc(l.label)}</a><button class="nav-drop__btn" type="button" aria-expanded="false" aria-controls="drop-${i}" aria-label="Show ${esc(l.label)} links">${caret}</button></div>${panel}</div>`;
    }).join('');

    this.innerHTML = `
      <a class="skip-link" href="#main">Skip to content</a>
      <header class="site-header">
        <div class="container site-header__inner">
          <a class="site-header__logo" href="index.html">
            <img src="${IMG}${LOGO.light}" alt="A'amal Group — Arab Economic &amp; Business Group, home" width="${LOGO.w}" height="${LOGO.h}">
          </a>
          <nav class="site-nav" id="site-nav" aria-label="Main navigation">${links}</nav>
          <div class="site-header__actions">
            ${VERSION === 1 ? '<a class="lang-link" href="#" lang="ar">العربية</a>' : ''}
            <a class="btn btn--primary" href="contact.html"${active === 'contact' ? ' aria-current="page"' : ''}>${IS_V3 ? 'Get in Touch' : 'Contact Us'}</a>
            <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
            </button>
          </div>
        </div>
      </header>`;

    // Dropdowns: open on hover (desktop, via CSS) or by the caret button (touch, keyboard, mobile)
    const closeAll = (except) => this.querySelectorAll('.nav-drop.is-open').forEach((o) => {
      if (o === except) return;
      o.classList.remove('is-open'); o.querySelector('.nav-drop__btn').setAttribute('aria-expanded', 'false');
    });
    this.querySelectorAll('.nav-drop').forEach((d) => {
      const btn = d.querySelector('.nav-drop__btn');
      const label = d.querySelector('.nav-drop__head > a');
      const toggleDrop = (e) => {
        e.preventDefault();
        const open = !d.classList.contains('is-open');
        closeAll(d);
        d.classList.toggle('is-open', open);
        btn.setAttribute('aria-expanded', String(open));
      };
      // Clicking the category name or the arrow pins the menu open; it stays until you click elsewhere
      btn.addEventListener('click', toggleDrop);
      label.addEventListener('click', toggleDrop);
    });
    document.addEventListener('click', (e) => { if (!e.target.closest('.nav-drop')) this.querySelectorAll('.nav-drop.is-open').forEach((o) => { o.classList.remove('is-open'); o.querySelector('.nav-drop__btn').setAttribute('aria-expanded', 'false'); }); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') this.querySelectorAll('.nav-drop.is-open').forEach((o) => { o.classList.remove('is-open'); o.querySelector('.nav-drop__btn').setAttribute('aria-expanded', 'false'); }); });

    const toggle = this.querySelector('.nav-toggle');
    const nav = this.querySelector('.site-nav');
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
  }
}

/* ---------- Shared footer ---------- */
class SiteFooter extends HTMLElement {
  connectedCallback() {
    const year = new Date().getFullYear();
    const v2 = VERSION === 2;
    this.innerHTML = `
      <footer class="site-footer">
        <div class="container site-footer__inner">
          <div class="site-footer__cols">
            <div class="site-footer__brand">
              <img src="${IMG}${LOGO.dark}" alt="A'amal Group" width="${LOGO.w}" height="${LOGO.h}" loading="lazy" decoding="async">
              <h2>Let's build the future together</h2>
              <a class="btn btn--primary" href="contact.html">Get in Touch</a>
            </div>
            <nav class="site-footer__col" aria-label="Company">
              <span class="site-footer__title">Company</span>
              <a href="about.html">About Us</a>
              <a href="responsibility.html">${v2 ? 'Sustainability' : 'Social Responsibility'}</a>
              <a href="awards.html">${v2 ? "A'amal Global Recognition" : 'Awards'}</a>
              <a href="media.html">Media</a>
              <a href="careers.html">Careers</a>
            </nav>
            ${v2 ? `<nav class="site-footer__col" aria-label="Services">
              <span class="site-footer__title">Services</span>
              <a href="artificial-lagoons.html">Artificial Lagoons</a>
              <a href="sports-facilities.html">Sports Facilities</a>
              <a href="operations-maintenance.html">Operations &amp; Maintenance</a>
              <a href="electrical-instrumentation.html">Electrical &amp; Instrumentation</a>
              <a href="waterproofing-industrial-coating.html">Waterproofing &amp; Coating</a>
              <a href="industry-transformation.html">Industry Transformation</a>
              <a href="human-resource-management.html">Human Resource Management</a>
              <a href="project-solutions.html">Project Solutions</a>
            </nav>` : `<nav class="site-footer__col" aria-label="Services">
              <span class="site-footer__title">Services</span>
              <a href="hospitality.html">Hospitality &amp; Sports</a>
              <a href="contracting.html">Contracting &amp; Technical</a>
              <a href="management.html">Project &amp; Business Management</a>
            </nav>`}
            <div class="site-footer__col">
              <span class="site-footer__title">Contact</span>
              <a href="tel:+966138973938">+966 13 897 3938</a>
              <a href="mailto:info@aamal-group.com">info@aamal-group.com</a>
              <address>King Abdullah Road, Middle East Commercial Center<br>P.O. Box 4977, Al Khobar 31952<br>Kingdom of Saudi Arabia</address>
            </div>
          </div>
          <div class="site-footer__bottom">
            <span>© ${year} A'amal Group. All rights reserved.</span>
            <nav aria-label="Legal and social">
              ${IS_V3 ? '' : '<a href="#">Privacy Policy</a>'}
              ${v2 ? '<a href="responsibility.html#speak-up">Report a Concern</a>' : ''}
              <a href="https://twitter.com/AAMAL_GROUP_SA" target="_blank" rel="noopener">X / Twitter</a>
              ${IS_V3 ? '' : '<a href="#">LinkedIn</a>'}
            </nav>
          </div>
        </div>
      </footer>`;
  }
}

customElements.define('site-header', SiteHeader);
customElements.define('site-footer', SiteFooter);

/* ---------- Home hero slider ---------- */
function initHeroSlider() {
  const hero = document.querySelector('[data-hero]');
  if (!hero) return;

  const slides = [...hero.querySelectorAll('.hero__slide')];
  const label = hero.querySelector('[data-hero-label]');
  const count = hero.querySelector('[data-hero-count]');
  const dotsWrap = hero.querySelector('[data-hero-dots]');
  const interval = Number(hero.dataset.interval || 4000);
  hero.style.setProperty('--hero-interval', `${interval}ms`);
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let index = 0;
  let timer;

  const dots = slides.map((slide, i) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'hero__dot';
    btn.setAttribute('aria-label', `Show slide ${i + 1}: ${slide.dataset.label}`);
    btn.innerHTML = '<span></span>';
    btn.addEventListener('click', () => { go(i); restart(); });
    dotsWrap.appendChild(btn);
    return btn;
  });

  function go(i) {
    index = (i + slides.length) % slides.length;
    slides.forEach((s, k) => s.classList.toggle('is-active', k === index));
    dots.forEach((d, k) => d.setAttribute('aria-current', String(k === index)));
    label.textContent = slides[index].dataset.label;
    count.textContent = `${index + 1} / ${slides.length}`;
    label.classList.remove('is-swap'); void label.offsetWidth; label.classList.add('is-swap');
  }

  function restart() {
    clearInterval(timer);
    if (!reduceMotion) timer = setInterval(() => go(index + 1), interval);
  }

  // Pause while the tab is hidden or the user is interacting with the hero.
  hero.addEventListener('mouseenter', () => clearInterval(timer));
  hero.addEventListener('mouseleave', restart);
  hero.addEventListener('focusin', () => clearInterval(timer));
  hero.addEventListener('focusout', restart);
  document.addEventListener('visibilitychange', () => (document.hidden ? clearInterval(timer) : restart()));

  go(0);
  restart();
}

/* ---------- Media filters ---------- */
function initFilters() {
  const group = document.querySelector('[data-filters]');
  if (!group) return;
  const items = [...document.querySelectorAll('[data-type]')];
  // data-type may hold one value; buttons filter by exact match ('all' shows everything).
  group.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-filter]');
    if (!btn) return;
    const f = btn.dataset.filter;
    group.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
    items.forEach((it) => { it.hidden = f !== 'all' && it.dataset.type !== f; });
  });
}

/* ---------- Forms ----------
   Front-end only: checks required fields, then shows a thank-you message.
   Connect `form.action` to your backend or a form service to actually send. */
function initForms() {
  document.querySelectorAll('form[data-form]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      form.querySelectorAll('.field-error').forEach((el) => el.remove());
      let firstInvalid = null;

      form.querySelectorAll('[required]').forEach((input) => {
        if (!input.checkValidity()) {
          const msg = document.createElement('span');
          msg.className = 'field-error';
          msg.id = `${input.name}-error`;
          msg.textContent = input.type === 'email' && input.value ? 'Please enter a valid email address.' : 'This field is required.';
          input.setAttribute('aria-invalid', 'true');
          input.setAttribute('aria-describedby', msg.id);
          input.closest('.field').appendChild(msg);
          firstInvalid = firstInvalid || input;
        } else {
          input.removeAttribute('aria-invalid');
          input.removeAttribute('aria-describedby');
        }
      });

      if (firstInvalid) { firstInvalid.focus(); return; }

      const success = document.getElementById(form.dataset.success);
      form.hidden = true;
      success.hidden = false;
      success.focus();
    });
  });

  document.querySelectorAll('[data-form-reset]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const form = document.getElementById(btn.dataset.formReset);
      form.reset();
      form.hidden = false;
      btn.closest('.form-success').hidden = true;
      form.querySelector('input, select, textarea').focus();
    });
  });
}


/* ---------- Motion: scroll reveal, count-up numbers (respects reduced motion) ---------- */
const REVEAL_SELECTORS = [
  '.s-head', '.section-head', '.s-split__text', '.s-split__img', '.s-split > img',
  '.svc-card', '.offer-card', '.recog-card', '.award-item', '.c-card', '.c-office', '.c-routes a',
  '.tile', '.press-card', '.founder-gallery > *', '.media-photo', '.gallery img', '.timeline li',
  '.v2030', '.who-mosaic', '.brand-showcase', '.hero-logos', '.panel-card', '.focus-grid > div',
  '.s-included li', '.vm-item', '.feature-row', '.s-cta', '.office-card', '.pillars > div',
  '.recog__logos li', '.impact', '.social-band', '.leader', '.heritage'
].join(',');

function initMotion() {
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) return;
  document.documentElement.classList.add('motion-ok');

  // Scroll reveal with a small stagger between siblings
  const els = Array.from(document.querySelectorAll(REVEAL_SELECTORS))
    .filter((el) => !el.closest('.site-header, .site-footer, .hero, .nav-drop__panel'));
  const seen = new Map();
  els.forEach((el) => {
    const parent = el.parentElement;
    const i = seen.get(parent) || 0;
    seen.set(parent, i + 1);
    el.classList.add('rv');
    el.style.setProperty('--rv-delay', `${Math.min(i, 6) * 70}ms`);
  });
  // Big photos get a curtain-wipe reveal; clipped elements can't be observed, so watch their parent
  const WIPE = '.s-split__img, .s-split > img, .feature-row > img, .rounded-img';
  els.forEach((el) => { if (el.matches(WIPE)) el.classList.add('wipe'); });
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const t = e.target;
      if (t.classList.contains('rv')) t.classList.add('is-in');
      t.querySelectorAll(':scope > .wipe').forEach((w) => w.classList.add('is-in'));
      io.unobserve(t);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  els.forEach((el) => io.observe(el.classList.contains('wipe') ? el.parentElement : el));

  // Headings: words rise in one after another when they scroll into view
  const heads = Array.from(document.querySelectorAll('main h2, .s-hero__title'))
    .filter((h) => !h.closest('.hero, .s-cta, .nav-drop__panel, .form-success'));
  heads.forEach((h) => {
    let n = 0;
    const walk = (node) => {
      Array.from(node.childNodes).forEach((c) => {
        if (c.nodeType === 3) {
          const frag = document.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach((part) => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            const w = document.createElement('span');
            w.className = 'tw';
            w.style.setProperty('--tw', `${Math.min(n++, 14) * 55}ms`);
            w.textContent = part;
            frag.appendChild(w);
          });
          c.replaceWith(frag);
        } else if (c.nodeType === 1 && c.tagName !== 'BR') walk(c);
      });
    };
    walk(h);
    h.classList.add('tw-wrap');
  });
  const hio = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('tw-in'); hio.unobserve(e.target); } });
  }, { threshold: 0.3 });
  heads.forEach((h) => hio.observe(h));

  // Scroll progress bar + header shadow + gentle parallax on large images
  const bar = document.createElement('div');
  bar.className = 'scroll-progress';
  bar.setAttribute('aria-hidden', 'true');
  document.body.appendChild(bar);
  const header = document.querySelector('.site-header');
  const para = Array.from(document.querySelectorAll('.s-cta__img, .social-band img, .impact img'));
  let ticking = false;
  const onScroll = () => {
    ticking = false;
    const y = window.scrollY;
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = `scaleX(${max > 0 ? Math.min(1, y / max) : 0})`;
    if (header) header.classList.toggle('is-scrolled', y > 12);
    para.forEach((img) => {
      const r = img.parentElement.getBoundingClientRect();
      if (r.bottom < 0 || r.top > innerHeight) return;
      const k = (r.top + r.height / 2 - innerHeight / 2) / innerHeight;
      img.style.transform = `translateY(${(k * -40).toFixed(1)}px) scale(1.12)`;
    });
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();


  // Count-up for stats (skips years such as 1994 / 2021 and ranges)
  const nums = document.querySelectorAll('.s-stat strong, .stat__value, .brand-showcase__facts strong');
  const cio = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      cio.unobserve(e.target);
      const el = e.target;
      el.classList.add('num-in');
      const m = el.textContent.trim().match(/^(\d+)(\+?)$/);
      if (!m) return;
      const end = parseInt(m[1], 10);
      if (end >= 1900 || end < 2) return;
      const suffix = m[2];
      const t0 = performance.now();
      const dur = 1200;
      el.style.fontVariantNumeric = 'tabular-nums';
      const tick = (t) => {
        const p = Math.min(1, (t - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(end * eased) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      el.textContent = '0' + suffix;
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.6 });
  nums.forEach((n) => cio.observe(n));
}

document.addEventListener('DOMContentLoaded', () => {
  initMotion();
  initHeroSlider();
  initFilters();
  initForms();
});
