# A'amal Group — Website

Static website for A'amal Group (Arab Economic & Business Group), built from the redesign.
Plain HTML, CSS and JavaScript — no framework, no build step. Open any `.html` file in a browser,
or serve the folder with any web server.

## Two design versions

| Folder | Version | Pages |
|---|---|---|
| `v1/` | Original redesign | 11 |
| `v2/` | Competitor-informed (founder story, Vision 2030, Projects, group companies, reports & policies) | 12 |

`index.html` at the root is a review page linking to both. Once a version is chosen, move its
files to the site root, fix the `../assets/` paths to `assets/`, and delete the other folder and the review page.

## Structure

```
assets/
  css/styles.css   all styles: design tokens (colours, fonts) at the top, then components
  js/main.js       shared header + footer, mobile menu, hero slider, filters, form handling
  img/             logo, white logo, hero and section photos
v1/  v2/           the pages for each version
```

### Shared header and footer
Every page uses `<site-header active="about"></site-header>` and `<site-footer></site-footer>`.
They are defined once in `assets/js/main.js`. The `active` value underlines the current menu item.
`<body data-version="2">` switches the menu and footer to the Version 2 links.

### Brand colours (in `styles.css` → `:root`)
- `--green: #1FB04B` — logo green, for accents and bars
- `--green-dark: #157F36` — buttons and link text (meets contrast on white)
- `--charcoal: #2E3133` — dark sections and headings

## Still to do before launch

- **Content in [brackets]** — vision and mission, founder quote and portrait, award names, news,
  job titles, office addresses in Malaysia and Romania, office hours, project names and photos,
  partner and group-company logos, report PDFs.
- **Forms** — `contact.html` and `careers.html` validate and show a thank-you message, but don't
  send anything yet. Point each `<form>` at your backend or a form service (e.g. add `action` and
  `method="post"`, and remove the `preventDefault` in `initForms()` in `main.js`).
- **Map** — replace the map placeholder on `contact.html` with a Google Maps embed.
- **Arabic version** — the `العربية` link is a placeholder; an RTL Arabic copy of the chosen version is the next step.
- **Photos** — the energy, construction and service photos are from Unsplash (free to use). Swap in
  A'amal's own project photography when available.
