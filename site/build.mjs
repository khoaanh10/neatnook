import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'site.config.json'), 'utf8'));
const postsDir = path.join(__dirname, 'content', 'posts');
const bgDir = path.join(__dirname, '..', 'pin-factory', 'backgrounds');
const pinOutDir = path.join(__dirname, '..', 'pin-factory', 'output');
const distDir = path.join(__dirname, 'dist');
const distImgDir = path.join(distDir, 'images');
const distPinDir = path.join(distDir, 'pins');

const esc = (str = '') =>
  String(str)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');

const ensureDir = (dir) => fs.mkdirSync(dir, { recursive: true });
const cssContent = fs.readFileSync(path.join(__dirname, 'styles.css'), 'utf8');
const cssVersion = cssContent.length;

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

const findPostImages = (slug) => {
  if (!fs.existsSync(bgDir)) return [];
  const list = [];
  for (const suffix of ['', '-2', '-3']) {
    for (const ext of ['.jpg', '.jpeg', '.png', '.webp']) {
      const p = path.join(bgDir, `${slug}${suffix}${ext}`);
      if (fs.existsSync(p)) {
        list.push({ src: p, filename: `${slug}${suffix}${ext}` });
        break;
      }
    }
  }
  return list;
};

const layout = ({ title, description, canonicalPath = '/', body, ogType = 'website', ogImage = '' }) => {
  const fullTitle = title === config.siteName ? `${config.siteName} — ${config.tagline}` : `${title} | ${config.siteName}`;
  const canonical = `${config.baseUrl.replace(/\/$/, '')}${canonicalPath}`;
  const pinterestMeta = config.pinterestVerifyMeta
    ? `\n  <meta name="p:domain_verify" content="${esc(config.pinterestVerifyMeta)}">`
    : '';
  const googleMeta = config.googleVerifyMeta
    ? `\n  <meta name="google-site-verification" content="${esc(config.googleVerifyMeta)}">`
    : '';
  const ogImgMeta = ogImage
    ? `\n  <meta property="og:image" content="${esc(ogImage)}">`
    : '';
  const ga4Script = config.ga4MeasurementId
    ? `\n  <script async src="https://www.googletagmanager.com/gtag/js?id=${esc(config.ga4MeasurementId)}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${esc(config.ga4MeasurementId)}');document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a');if(!a||!a.href)return;if(a.href.indexOf('amazon.com')!==-1){gtag('event','amazon_click',{link_url:a.href,page_path:location.pathname});}else if(a.href.indexOf('gumroad.com')!==-1){gtag('event','gumroad_click',{link_url:a.href,page_path:location.pathname});}});</script>`
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
  <meta property="og:site_name" content="${esc(config.siteName)}">${ogImgMeta}${pinterestMeta}${googleMeta}${ga4Script}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400..700;1,9..40,400&family=Newsreader:ital,opsz,wght@0,6..72,400..600;1,6..72,400..500&display=swap" rel="stylesheet">
  <link rel="alternate" type="application/rss+xml" title="${esc(config.siteName)} RSS Feed" href="${esc(withBase('/rss.xml'))}">
  <link rel="stylesheet" href="${esc(withBase(`/styles.css?v=${cssVersion}`))}">
</head>
<body>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="${esc(withBase('/'))}">Neat<span>Nook</span></a>
      <nav class="main-nav">
        <a href="${esc(withBase('/'))}">All Guides</a>
        <a href="${esc(withBase('/about/'))}">About</a>
        <a href="${esc(withBase('/disclosure/'))}">Disclosure</a>
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
        <a href="${esc(withBase('/about/'))}">About NeatNook</a>
        <a href="${esc(withBase('/disclosure/'))}">Affiliate Disclosure</a>
        <a href="${esc(withBase('/privacy/'))}">Privacy Policy</a>
      </div>
      <p>${esc(config.disclosureShort)}</p>
      <p>&copy; ${new Date().getFullYear()} ${esc(config.siteName)}. Small-space living &amp; practical home organization.</p>
    </div>
  </footer>
</body>
</html>`;
};

const renderPost = (post, allPosts) => {
  const tocItems = post.items
    .map((item, idx) => `<li><a href="#pick-${idx + 1}">${esc(item.name)}</a></li>`)
    .join('\n');

  const extraImgs = post._extraImages || [];

  const pickSections = post.items
    .map((item, idx) => {
      const num = String(idx + 1).padStart(2, '0');
      const bullets = (item.highlights || []).map((b) => `<li>${esc(b)}</li>`).join('\n');
      const url = buildAmazonUrl(item);

      let inlineBreak = '';
      if (idx === 2 && extraImgs[0]) {
        inlineBreak = `<figure class="inline-photo"><img src="${esc(withBase(`/images/${extraImgs[0]}`))}" alt="${esc(post.title)} inspiration" loading="lazy"><figcaption>Clean, vertical storage keeps compact spaces calm and easy to reset daily.</figcaption></figure>`;
      } else if (idx === 5 && extraImgs[1]) {
        inlineBreak = `<figure class="inline-photo"><img src="${esc(withBase(`/images/${extraImgs[1]}`))}" alt="${esc(post.categoryLabel)} styling" loading="lazy"><figcaption>Stick to warm neutrals and hidden zones so small rooms feel open.</figcaption></figure>`;
      }

      const skipHtml = item.skipIf
        ? `<p class="pick-skip"><strong>Skip if:</strong> ${esc(item.skipIf)}</p>`
        : '';

      return `<section class="pick-item" id="pick-${idx + 1}">
        <div class="pick-head">
          <span class="pick-num">No. ${num}</span>
          ${item.badge ? `<span class="pick-label">${esc(item.badge)}</span>` : ''}
        </div>
        <h2>${esc(item.name)}</h2>
        <p class="pick-why">${esc(item.whyItWorks)}</p>
        <ul class="pick-bullets">${bullets}</ul>
        ${skipHtml}
        <a class="cta-link" href="${esc(url)}" target="_blank" rel="nofollow sponsored noopener">Shop on Amazon &#8599;</a>
      </section>${inlineBreak}`;
    })
    .join('\n');

  const faqHtml = (post.faqs || []).length
    ? `<section class="faq-section">
        <h2>Common Questions</h2>
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

  const related = allPosts.filter((p) => p.slug !== post.slug).slice(0, 3);
  const relatedHtml = related.length
    ? `<section class="related-section">
        <h2>More Small-Space Guides</h2>
        <div class="related-grid">
          ${related
            .map(
              (r) => `<article class="card">
              ${r._imageFile ? `<a class="card-photo-link" href="${esc(withBase(`/posts/${r.slug}/`))}"><img src="${esc(withBase(`/images/${r._imageFile}`))}" alt="${esc(r.title)}" loading="lazy"></a>` : ''}
              <div class="card-body">
                <span class="card-cat">${esc(r.categoryLabel || r.category)}</span>
                <h2 style="font-size:1.12rem;"><a href="${esc(withBase(`/posts/${r.slug}/`))}">${esc(r.title)}</a></h2>
              </div>
            </article>`
            )
            .join('\n')}
        </div>
      </section>`
    : '';

  const heroImg = post._imageFile
    ? `<figure class="post-hero"><img src="${esc(withBase(`/images/${post._imageFile}`))}" alt="${esc(post.title)}" loading="eager"><figcaption>${esc(post.categoryLabel || 'Small-Space Living')} — curated practical picks for everyday rentals.</figcaption></figure>`
    : '';

  const kitBox = config.gumroadKitUrl
    ? `<aside class="kit-callout">
        <div class="kit-kicker">NeatNook Printable Edition &middot; $5 Instant Download</div>
        <h3>The January Apartment Reset Kit + 72 Minimalist Labels</h3>
        <p>Want a step-by-step printable plan? Grab our 12-page US Letter PDF with a 30-day 15-minute declutter calendar, room checklists, cabinet measuring card, and 72 minimalist pantry &amp; fridge labels.</p>
        <a class="cta-link" href="${esc(config.gumroadKitUrl)}" target="_blank" rel="noopener">Get the Printable Kit ($5) &#8599;</a>
      </aside>`
    : '';

  const quickTableHtml = (post.quickTable || []).length
    ? `<div class="quick-table-wrap"><table class="quick-table">
        <thead><tr><th>Option</th><th>Best For</th><th>Watch Out</th></tr></thead>
        <tbody>${post.quickTable
          .map((r) => `<tr><td><strong>${esc(r.name)}</strong></td><td>${esc(r.bestFor)}</td><td>${esc(r.watchOut || '—')}</td></tr>`)
          .join('')}</tbody>
      </table></div>`
    : '';

  const stepsHtml = (post.steps || []).length
    ? `<section class="howto-steps">
        <h2>${esc(post.stepsTitle || 'Step-by-Step Setup')}</h2>
        <ol>${post.steps.map((s) => `<li><strong>${esc(s.title)}:</strong> ${esc(s.detail)}</li>`).join('')}</ol>
      </section>`
    : '';

  const body = `<article class="article-wrap">
    <div class="post-header">
      <div class="kicker">${esc(post.categoryLabel || post.category)}</div>
      <h1>${esc(post.title)}</h1>
      <div class="byline"><span>By <strong>NeatNook Editorial</strong></span> &middot; <span>Updated ${esc(post.updatedAt)}</span> &middot; <span>${post.items.length} curated picks</span></div>
    </div>
    ${heroImg}
    <p class="disclosure-note">${esc(config.disclosureShort)}</p>
    <p class="lead-intro">${esc(post.intro)}</p>
    <div class="toc">
      <h3>In This Guide</h3>
      <ol>${tocItems}</ol>
    </div>
    ${quickTableHtml}
    ${stepsHtml}
    ${pickSections}
    ${kitBox}
    ${faqHtml}
    ${relatedHtml}
  </article>`;

  return layout({
    title: post.title,
    description: post.metaDescription,
    canonicalPath: `/posts/${post.slug}/`,
    body,
    ogType: 'article',
    ogImage: post._imageFile ? `${config.baseUrl.replace(/\/$/, '')}/images/${post._imageFile}` : ''
  });
};

const renderHome = (posts) => {
  const cards = posts
    .map(
      (p) => `<article class="card">
        ${
          p._imageFile
            ? `<a class="card-photo-link" href="${esc(withBase(`/posts/${p.slug}/`))}"><img src="${esc(withBase(`/images/${p._imageFile}`))}" alt="${esc(p.title)}" loading="lazy"></a>`
            : ''
        }
        <div class="card-body">
          <span class="card-cat">${esc(p.categoryLabel || p.category)}</span>
          <h2><a href="${esc(withBase(`/posts/${p.slug}/`))}">${esc(p.title)}</a></h2>
          <p>${esc(p.metaDescription)}</p>
          <div class="card-meta">${p.items.length} picks &middot; ${esc(p.updatedAt)}</div>
        </div>
      </article>`
    )
    .join('\n');

  const body = `<section class="wrap hero">
    <div class="hero-kicker">Small-Space Living &amp; Organization</div>
    <h1>Practical storage ideas for calm, clutter-free apartments.</h1>
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
ensureDir(distImgDir);
ensureDir(distPinDir);
fs.copyFileSync(path.join(__dirname, 'styles.css'), path.join(distDir, 'styles.css'));

const posts = fs.existsSync(postsDir)
  ? fs
      .readdirSync(postsDir)
      .filter((f) => f.endsWith('.json'))
      .map((f) => {
        const post = JSON.parse(fs.readFileSync(path.join(postsDir, f), 'utf8'));
        const imgs = findPostImages(post.slug);
        if (imgs.length) {
          for (const im of imgs) {
            fs.copyFileSync(im.src, path.join(distImgDir, im.filename));
          }
          post._imageFile = imgs[0].filename;
          post._extraImages = imgs.slice(1).map((im) => im.filename);
        }
        post._pinImages = {};
        for (let n = 1; n <= 5; n++) {
          const pinSrc = path.join(pinOutDir, post.slug, `pin-${n}.png`);
          if (fs.existsSync(pinSrc)) {
            const fname = `${post.slug}-pin-${n}.png`;
            fs.copyFileSync(pinSrc, path.join(distPinDir, fname));
            post._pinImages[n] = fname;
          }
        }
        post._pinImageFile = post._pinImages[1] || null;
        return post;
      })
      .sort((a, b) => (b.updatedAt || '').localeCompare(a.updatedAt || ''))
  : [];

fs.writeFileSync(path.join(distDir, 'index.html'), renderHome(posts), 'utf8');

for (const post of posts) {
  const dir = path.join(distDir, 'posts', post.slug);
  ensureDir(dir);
  fs.writeFileSync(path.join(dir, 'index.html'), renderPost(post, posts), 'utf8');
}

// Redirect alias for scheduled Pin 4 slug
const aliasDir = path.join(distDir, 'posts', 'bathroom-vanity-organizer-aesthetic-ideas');
ensureDir(aliasDir);
const targetUrl = withBase('/posts/small-bathroom-vanity-counter-organizers/');
fs.writeFileSync(
  path.join(aliasDir, 'index.html'),
  `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=${esc(targetUrl)}"><link rel="canonical" href="${esc(config.baseUrl.replace(/\/$/, '') + '/posts/small-bathroom-vanity-counter-organizers/')}"></head><body><a href="${esc(targetUrl)}">Redirecting...</a></body></html>`,
  'utf8'
);

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
if (config.customDomain) {
  fs.writeFileSync(path.join(distDir, 'CNAME'), `${config.customDomain.trim()}\n`, 'utf8');
}

// Deterministic Daily RSS Drip (3 fresh Pins/day starting 2026-11-27, zero duplicates)
const DRIP_START = '2026-11-27';
const PINS_PER_DAY = 3;
const todayStr = process.env.DRIP_DATE || new Date().toISOString().slice(0, 10);
const msPerDay = 86400000;
const daysElapsed = Math.floor((Date.parse(todayStr + 'T00:00:00Z') - Date.parse(DRIP_START + 'T00:00:00Z')) / msPerDay) + 1;
const dripCount = Math.max(0, daysElapsed) * PINS_PER_DAY;

// Build all RSS entries: Wave 0 (pin-1, already live Nov 26) + Drip Queue (pin-2..pin-5)
const postsBySlug = [...posts].sort((a, b) => a.slug.localeCompare(b.slug));
const allRssEntries = [];

for (const p of postsBySlug) {
  const imgUrl = p._pinImages?.[1]
    ? `${base}/pins/${p._pinImages[1]}`
    : p._imageFile
    ? `${base}/images/${p._imageFile}`
    : '';
  allRssEntries.push({
    category: p.category,
    title: p.title,
    link: `${base}/posts/${p.slug}/`,
    guid: `${base}/posts/${p.slug}/`,
    pubDate: new Date(`${p.updatedAt || '2026-11-25'}T09:00:00Z`).toUTCString(),
    sortTs: Date.parse(`${p.updatedAt || '2026-11-25'}T09:00:00Z`),
    description: p.metaDescription,
    imgUrl
  });
}

const dripQueue = [];
for (let pinNum = 2; pinNum <= 5; pinNum++) {
  for (const p of postsBySlug) {
    if (!p._pinImages?.[pinNum]) continue;
    const hooks = p.pinHooks || [p.title];
    dripQueue.push({
      category: p.category,
      slug: p.slug,
      pinNum,
      title: hooks[(pinNum - 1) % hooks.length],
      description: p.metaDescription,
      imgUrl: `${base}/pins/${p._pinImages[pinNum]}`
    });
  }
}

const releasedDrip = dripQueue.slice(0, dripCount);
releasedDrip.forEach((item, idx) => {
  const dayOffset = Math.floor(idx / PINS_PER_DAY);
  const slotHour = [9, 14, 20][idx % PINS_PER_DAY];
  const pubTs = Date.parse(DRIP_START + 'T00:00:00Z') + dayOffset * msPerDay + slotHour * 3600000;
  allRssEntries.push({
    category: item.category,
    title: item.title,
    link: `${base}/posts/${item.slug}/?pin=${item.pinNum}`,
    guid: `${base}/posts/${item.slug}/#pin-${item.pinNum}`,
    pubDate: new Date(pubTs).toUTCString(),
    sortTs: pubTs,
    description: item.description,
    imgUrl: item.imgUrl
  });
});

const buildRssXml = (entries, titleSuffix = '') => {
  const sorted = [...entries].sort((a, b) => b.sortTs - a.sortTs);
  const itemsXml = sorted
    .map((e) => {
      const imgType = e.imgUrl.endsWith('.png') ? 'image/png' : 'image/jpeg';
      return `  <item>
    <title>${esc(e.title)}</title>
    <link>${esc(e.link)}</link>
    <guid isPermaLink="false">${esc(e.guid)}</guid>
    <pubDate>${e.pubDate}</pubDate>
    <description>${esc(e.description)}</description>${
        e.imgUrl
          ? `\n    <enclosure url="${esc(e.imgUrl)}" type="${imgType}" length="0"/>\n    <media:content url="${esc(e.imgUrl)}" medium="image" type="${imgType}"/>`
          : ''
      }
  </item>`;
    })
    .join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
<channel>
  <title>${esc(config.siteName)}${titleSuffix ? ' — ' + esc(titleSuffix) : ' — ' + esc(config.tagline)}</title>
  <link>${esc(base)}/</link>
  <description>${esc(config.description)}</description>
  <language>en-us</language>
${itemsXml}
</channel>
</rss>
`;
};

fs.writeFileSync(path.join(distDir, 'rss.xml'), buildRssXml(allRssEntries), 'utf8');

for (const cat of config.categories || []) {
  const catEntries = allRssEntries.filter((e) => e.category === cat.id);
  fs.writeFileSync(path.join(distDir, `rss-${cat.id}.xml`), buildRssXml(catEntries, cat.label), 'utf8');
}

console.log(
  `Built ${posts.length} editorial posts, ${allRssEntries.length} RSS entries (drip=${releasedDrip.length}/${dripQueue.length} as of ${todayStr}), and ${staticPages.length} static pages into ${distDir}`
);
