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
    { id: 'about', label: 'About Us', href: 'about.html' },
    { id: 'services', label: 'Services', href: 'services.html' },
    { id: 'projects', label: 'Projects', href: 'projects.html' },
    { id: 'responsibility', label: 'Sustainability', href: 'responsibility.html' },
    { id: 'media', label: 'Media', href: 'media.html' },
    { id: 'careers', label: 'Careers', href: 'careers.html' },
  ],
}[VERSION];

/* ---------- Shared header ---------- */
class SiteHeader extends HTMLElement {
  connectedCallback() {
    const active = this.getAttribute('active') || '';
    const links = NAV.map(
      (l) => `<a href="${l.href}"${l.id === active ? ' aria-current="page"' : ''}>${l.label}</a>`
    ).join('');

    this.innerHTML = `
      <a class="skip-link" href="#main">Skip to content</a>
      <header class="site-header">
        <div class="container site-header__inner">
          <a class="site-header__logo" href="index.html">
            <img src="${IMG}logo.png" alt="A'amal Group — Arab Economic &amp; Business Group, home" width="661" height="276">
          </a>
          <nav class="site-nav" id="site-nav" aria-label="Main navigation">${links}</nav>
          <div class="site-header__actions">
            <a class="lang-link" href="#" lang="ar">العربية</a>
            <a class="btn btn--primary" href="contact.html"${active === 'contact' ? ' aria-current="page"' : ''}>Contact Us</a>
            <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
            </button>
          </div>
        </div>
      </header>`;

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
              <img src="${IMG}logo-white.png" alt="A'amal Group" width="661" height="276">
              <h2>Let's build the future together</h2>
              <a class="btn btn--primary" href="contact.html">Get in Touch</a>
            </div>
            <nav class="site-footer__col" aria-label="Company">
              <span class="site-footer__title">Company</span>
              <a href="about.html">About Us</a>
              <a href="responsibility.html">${v2 ? 'Sustainability' : 'Social Responsibility'}</a>
              <a href="awards.html">Awards</a>
              <a href="media.html">Media</a>
              <a href="careers.html">Careers</a>
            </nav>
            <nav class="site-footer__col" aria-label="${v2 ? 'Businesses' : 'Services'}">
              <span class="site-footer__title">${v2 ? 'Businesses' : 'Services'}</span>
              <a href="hospitality.html">Hospitality &amp; Sports</a>
              <a href="contracting.html">Contracting &amp; Technical</a>
              <a href="management.html">Project &amp; Business Management</a>
              ${v2 ? '<a href="projects.html">Our Projects</a>' : ''}
            </nav>
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
              <a href="#">Privacy Policy</a>
              ${v2 ? '<a href="responsibility.html#policies">Code of Conduct</a><a href="responsibility.html#speak-up">Report a Concern</a>' : ''}
              <a href="#">X / Twitter</a>
              <a href="#">LinkedIn</a>
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

document.addEventListener('DOMContentLoaded', () => {
  initHeroSlider();
  initFilters();
  initForms();
});
