import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'site.config.json'), 'utf8'));
const postsDir = path.join(__dirname, 'content', 'posts');
const distDir = path.join(__dirname, 'dist');

const esc = (str = '') =>
  String(str)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');

const ensureDir = (dir) => fs.mkdirSync(dir, { recursive: true });

const buildAmazonUrl = (item) => {
  const tag = encodeURIComponent(config.amazonTag || '');
  if (item.asin) {
    return `https://www.amazon.com/dp/${encodeURIComponent(item.asin)}?tag=${tag}`;
  }
  const q = encodeURIComponent(item.amazonSearchQuery || item.name);
  return `https://www.amazon.com/s?k=${q}&tag=${tag}`;
};

const basePath = (config.basePath || '').replace(/\/$/, '');
const withBase = (p) => `${basePath}${p.startsWith('/') ? p : '/' + p}`;

const layout = ({ title, description, canonicalPath = '/', body, ogType = 'website' }) => {
  const fullTitle = title === config.siteName ? `${config.siteName} — ${config.tagline}` : `${title} | ${config.siteName}`;
  const canonical = `${config.baseUrl.replace(/\/$/, '')}${canonicalPath}`;
  const pinterestMeta = config.pinterestVerifyMeta
    ? `\n  <meta name="p:domain_verify" content="${esc(config.pinterestVerifyMeta)}">`
    : '';

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${esc(fullTitle)}</title>
  <meta name="description" content="${esc(description || config.description)}">
  <link rel="canonical" href="${esc(canonical)}">
  <meta property="og:type" content="${esc(ogType)}">
  <meta property="og:title" content="${esc(title)}">
  <meta property="og:description" content="${esc(description || config.description)}">
  <meta property="og:url" content="${esc(canonical)}">
  <meta property="og:site_name" content="${esc(config.siteName)}">${pinterestMeta}
  <link rel="stylesheet" href="${esc(withBase('/styles.css'))}">
</head>
<body>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="${esc(withBase('/'))}">${esc(config.siteName.slice(0, 4))}<span>${esc(config.siteName.slice(4))}</span></a>
      <nav class="main-nav">
        <a href="${esc(withBase('/'))}">All Guides</a>
        <a href="${esc(withBase('/about/'))}">About</a>
        <a href="${esc(withBase('/disclosure/'))}">Affiliate Disclosure</a>
        <a href="${esc(withBase('/privacy/'))}">Privacy</a>
      </nav>
    </div>
  </header>
  <main>
    ${body}
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-links">
        <a href="${esc(withBase('/'))}">Home</a>
        <a href="${esc(withBase('/about/'))}">About</a>
        <a href="${esc(withBase('/disclosure/'))}">Affiliate Disclosure</a>
        <a href="${esc(withBase('/privacy/'))}">Privacy Policy</a>
      </div>
      <p>${esc(config.disclosureShort)}</p>
      <p>&copy; ${new Date().getFullYear()} ${esc(config.siteName)}. All rights reserved.</p>
    </div>
  </footer>
</body>
</html>`;
};

const renderPost = (post) => {
  const tocItems = post.items
    .map((item, idx) => `<li><a href="#pick-${idx + 1}">${esc(item.name)}</a></li>`)
    .join('\n');

  const pickCards = post.items
    .map((item, idx) => {
      const bullets = (item.highlights || []).map((b) => `<li>${esc(b)}</li>`).join('\n');
      const url = buildAmazonUrl(item);
      return `<section class="pick-card" id="pick-${idx + 1}">
        <div class="pick-top">
          <span class="pick-num">Pick #${idx + 1}</span>
          ${item.badge ? `<span class="pick-tag">${esc(item.badge)}</span>` : ''}
        </div>
        <h2>${esc(item.name)}</h2>
        <p class="pick-why">${esc(item.whyItWorks)}</p>
        <ul class="pick-bullets">${bullets}</ul>
        <a class="cta-btn" href="${esc(url)}" target="_blank" rel="nofollow sponsored noopener">Check Current Price on Amazon &rarr;</a>
      </section>`;
    })
    .join('\n');

  const faqHtml = (post.faqs || []).length
    ? `<section class="faq-section">
        <h2>Frequently Asked Questions</h2>
        ${post.faqs
          .map(
            (f) => `<div class="faq-item">
            <h3>${esc(f.q)}</h3>
            <p>${esc(f.a)}</p>
          </div>`
          )
          .join('\n')}
      </section>`
    : '';

  const body = `<article class="article-wrap">
    <div class="post-header">
      <span class="badge">${esc(post.categoryLabel || post.category)}</span>
      <h1>${esc(post.title)}</h1>
      <div class="post-meta">Updated ${esc(post.updatedAt)} &middot; ${post.items.length} Practical Picks</div>
    </div>
    <div class="disclosure-bar">${esc(config.disclosureShort)}</div>
    <p>${esc(post.intro)}</p>
    <div class="toc">
      <h3>Quick Jump</h3>
      <ol>${tocItems}</ol>
    </div>
    ${pickCards}
    ${faqHtml}
  </article>`;

  return layout({
    title: post.title,
    description: post.metaDescription,
    canonicalPath: `/posts/${post.slug}/`,
    body,
    ogType: 'article'
  });
};

const renderHome = (posts) => {
  const palettes = [
    'linear-gradient(135deg, #3f6154, #284138)',
    'linear-gradient(135deg, #b85d3b, #873e24)',
    'linear-gradient(135deg, #5f5b52, #383530)',
    'linear-gradient(135deg, #4b6584, #2e4259)'
  ];

  const cards = posts
    .map(
      (p, i) => `<article class="card">
        <div class="card-cover" style="background:${palettes[i % palettes.length]}">${esc(p.categoryLabel || p.category)}</div>
        <div class="card-body">
          <h2><a href="${esc(withBase(`/posts/${p.slug}/`))}">${esc(p.title)}</a></h2>
          <p>${esc(p.metaDescription)}</p>
          <div class="card-meta">${p.items.length} curated picks &middot; Updated ${esc(p.updatedAt)}</div>
        </div>
      </article>`
    )
    .join('\n');

  const body = `<section class="wrap hero">
    <h1>Clutter-Free Living for Small Spaces</h1>
    <p>${esc(config.description)}</p>
  </section>
  <section class="wrap">
    <div class="grid">${cards}</div>
  </section>`;

  return layout({
    title: config.siteName,
    description: config.description,
    canonicalPath: '/',
    body
  });
};

const renderStaticPage = (title, slug, paragraphs) => {
  const body = `<article class="article-wrap">
    <div class="post-header"><h1>${esc(title)}</h1></div>
    ${paragraphs.map((p) => `<p>${esc(p)}</p>`).join('\n')}
  </article>`;
  return layout({ title, description: `${title} — ${config.siteName}`, canonicalPath: `/${slug}/`, body });
};

// Clean & build
fs.rmSync(distDir, { recursive: true, force: true });
ensureDir(distDir);
fs.copyFileSync(path.join(__dirname, 'styles.css'), path.join(distDir, 'styles.css'));

const posts = fs.existsSync(postsDir)
  ? fs
      .readdirSync(postsDir)
      .filter((f) => f.endsWith('.json'))
      .map((f) => JSON.parse(fs.readFileSync(path.join(postsDir, f), 'utf8')))
      .sort((a, b) => (b.updatedAt || '').localeCompare(a.updatedAt || ''))
  : [];

fs.writeFileSync(path.join(distDir, 'index.html'), renderHome(posts), 'utf8');

for (const post of posts) {
  const dir = path.join(distDir, 'posts', post.slug);
  ensureDir(dir);
  fs.writeFileSync(path.join(dir, 'index.html'), renderPost(post), 'utf8');
}

const staticPages = [
  {
    slug: 'about',
    title: 'About NeatNook',
    paragraphs: [
      'NeatNook shares practical, renter-friendly storage and organization guides designed for small kitchens, compact home offices, and tiny apartments.',
      'Our focus is simple: zero fluff, real space-saving measurements, and affordable tools that solve everyday clutter without drilling holes or remodeling.',
      `Questions or suggestions? Reach us at ${config.contactEmail}.`
    ]
  },
  {
    slug: 'disclosure',
    title: 'Affiliate Disclosure',
    paragraphs: [
      config.disclosureShort,
      'When you click on product links on NeatNook and make a qualifying purchase on Amazon or partner retailers, we may receive a small commission. Prices and availability are subject to change on the retailer website.',
      'We do not accept paid placements to distort our recommendations.'
    ]
  },
  {
    slug: 'privacy',
    title: 'Privacy Policy',
    paragraphs: [
      'NeatNook is a lightweight static website. We do not sell your personal information or require account registration to browse our guides.',
      'Third-party partners (such as Amazon Associates or analytics/advertising providers) may use cookies when you click outbound links to track referrals in accordance with their own privacy policies.',
      `For privacy inquiries, contact ${config.contactEmail}.`
    ]
  }
];

for (const page of staticPages) {
  const dir = path.join(distDir, page.slug);
  ensureDir(dir);
  fs.writeFileSync(path.join(dir, 'index.html'), renderStaticPage(page.title, page.slug, page.paragraphs), 'utf8');
}

const base = config.baseUrl.replace(/\/$/, '');
const urls = ['/', '/about/', '/disclosure/', '/privacy/', ...posts.map((p) => `/posts/${p.slug}/`)];
const sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls
  .map((u) => `  <url><loc>${esc(base + u)}</loc></url>`)
  .join('\n')}\n</urlset>\n`;
fs.writeFileSync(path.join(distDir, 'sitemap.xml'), sitemap, 'utf8');
fs.writeFileSync(path.join(distDir, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${base}/sitemap.xml\n`, 'utf8');

console.log(`Built ${posts.length} posts and ${staticPages.length} static pages into ${distDir}`);
