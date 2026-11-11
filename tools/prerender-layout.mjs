// Writes the shared header and footer (defined in assets/js/bf.js) straight into every page's HTML,
// so they show without JavaScript and the page doesn't shift when the script loads.
// Run after changing the menu or footer in bf.js:
//   npx -y -p playwright@1.56.1 node tools/prerender-layout.mjs   (uses your installed Google Chrome)
// It starts a local server, renders each page in v3bf/, and copies the generated markup back.
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.env.SITE_ROOT || path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const DIR = process.argv[2] || 'v3bf';
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg' };
const server = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(0);
const port = server.address().port;
const browser = await chromium.launch({ channel: 'chrome' });
const page = await browser.newPage();
await page.route(/fonts\.(googleapis|gstatic)\.com|google\.com\/maps/, (r) => r.abort());

const strip = (html) => html.replace(new RegExp(`http://localhost:${port}/assets/`, 'g'), '../assets/');
for (const name of fs.readdirSync(path.join(ROOT, DIR)).filter((f) => f.endsWith('.html')).sort()) {
  const file = path.join(ROOT, DIR, name);
  let src = fs.readFileSync(file, 'utf8');
  // Start from empty elements so the markup always comes from the current bf.js
  src = src.replace(/(<site-header[^>]*>)[\s\S]*?(<\/site-header>)/, '$1$2').replace(/(<site-footer[^>]*>)[\s\S]*?(<\/site-footer>)/, '$1$2');
  fs.writeFileSync(file, src);
  await page.goto(`http://localhost:${port}/${DIR}/${name}`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('site-header .site-header');
  const { header, footer } = await page.evaluate(() => ({
    header: document.querySelector('site-header').innerHTML,
    footer: document.querySelector('site-footer') ? document.querySelector('site-footer').innerHTML : null,
  }));
  src = src.replace(/(<site-header[^>]*>)(<\/site-header>)/, (_, a, b) => a + strip(header) + '\n  ' + b);
  if (footer) src = src.replace(/(<site-footer[^>]*>)(<\/site-footer>)/, (_, a, b) => a + strip(footer) + '\n  ' + b);
  fs.writeFileSync(file, src);
  console.log('prerendered', name);
}
await browser.close();
server.close();
