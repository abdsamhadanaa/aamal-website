# A'amal Group — Website

Static website for A'amal Group (Arab Economic & Business Group). Plain HTML, CSS and JavaScript —
no framework. It will replace the current site at **www.aamal-group.com**.

| Where | What |
|---|---|
| `v3bf/` | The website pages (the version under client review). Edit these. |
| `assets/` | Shared CSS (`styles.css`, `services.css`, `bf.css`), script (`js/bf.js`), images and PDFs |
| `tools/build_production.py` | Builds the site for the real domain into `dist/` |
| `tools/prerender-layout.mjs` | Copies the shared header and footer into every page (run after changing them) |
| `index.html` (root) | Review page for the github.io preview only — not part of the live site |

Preview while in development: https://abdsamhadanaa.github.io/aamal-website/v3bf/ (hidden from search engines).

> `tools/build_bf.py`, `build_v2.py`, `build_v3.py`, `build_v4.py` and `content.py` produced the earlier
> versions. They need the old `v2/` folder and `v3-audit` branch, which no longer exist, so **don't run
> them** — they would overwrite `v3bf/`. The pages in `v3bf/` are now the source.

## Header and footer

The menu and footer are defined once in `assets/js/bf.js` (`NAV`, `SiteHeader`, `SiteFooter`) and are also
written into each page's HTML, so they appear instantly and without JavaScript. After changing them in
`bf.js`, refresh the pages (needs Node and Google Chrome):

```
npx -y -p playwright@1.56.1 node tools/prerender-layout.mjs
```

## Contact form

`v3bf/contact.html` checks the fields, then sends the message to the URL in the form's `action`.

1. Create a free form at [formspree.io](https://formspree.io) (or Web3Forms) that delivers to info@aamal-group.com.
2. In `v3bf/contact.html` set `action="https://formspree.io/f/YOUR_ID"` on `<form id="contact-form">`.
   (For Web3Forms, use `action="https://api.web3forms.com/submit"` and add
   `<input type="hidden" name="access_key" value="YOUR_KEY">` inside the form.)

Until an `action` is set, submitting opens the visitor's email app with the message filled in, so no
enquiry is lost. A hidden "website" field catches spam bots. If you use another service, add its domain
to `connect-src` in the Content-Security-Policy meta tag of every page.

## Going live on www.aamal-group.com

```
python3 tools/build_production.py            # test build: everything except search engines
python3 tools/build_production.py --launch   # launch build: pages become indexable
```

The build writes `dist/` with the pages at the site root, canonical/Open Graph URLs on
`https://www.aamal-group.com/`, one merged stylesheet per page, only the images that are used,
`robots.txt`, `sitemap.xml`, `404.html`, `CNAME` and `_headers`. Upload the **contents** of `dist/`
to the web root.

- **Cloudflare Pages or Netlify (recommended):** build command `python3 tools/build_production.py --launch`,
  output folder `dist`. The `_headers` file gives real security headers (HSTS, X-Frame-Options, CSP, …).
- **GitHub Pages:** publish the contents of `dist/` from a separate repository or branch and add the
  custom domain; `CNAME` is already included. GitHub Pages ignores `_headers`; the CSP and referrer
  policy still apply through meta tags.
- **The current host of aamal-group.com:** upload the contents of `dist/` by FTP/SFTP.

Launch checklist:
1. Contact form `action` set and a test message received.
2. Privacy Policy (`v3bf/privacy.html`) reviewed by A'amal's legal team (it is a draft under Saudi PDPL).
3. The three PDFs on the old site (`A'amal - CSS.pdf`, `A'amal - E&I.pdf`, `A'amal - Airswift.pdf`) copied
   into `assets/docs/` and the links on the Operations & Maintenance, Electrical & Instrumentation and
   Human Resource Management pages pointed at them — the build warns while any link points at a file
   only the old site has.
4. Build with `--launch`, deploy, then point the domain's DNS at the new host.
5. In Google Search Console, submit `https://www.aamal-group.com/sitemap.xml`.
6. Old-site URLs that no longer exist land on the 404 page, which links to the home, services and contact
   pages. Add redirects for any old pages that get significant traffic.

## Brand colours (`styles.css` → `:root`)
- `--green: #1FB04B` — logo green, for accents and bars
- `--green-dark: #157F36` — buttons and link text (meets contrast on white)
- `--charcoal: #2E3133` — dark sections and headings
