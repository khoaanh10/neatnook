/**
 * Official Pinterest API v5 Publisher (Safe Rate-Limited Queue Runner)
 *
 * Requirements:
 * - Set PINTEREST_ACCESS_TOKEN in environment (from Pinterest Developers App)
 * - Set PINTEREST_BOARD_MAP_JSON='{"Small Kitchen Organization Ideas":"<board_id>"}'
 * - Default dry-run mode unless --publish is passed.
 * - Max 5 pins per run to respect anti-spam velocity limits for new accounts.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const queuePath = path.join(__dirname, 'output', 'schedule_queue.json');
const publishMode = process.argv.includes('--publish');
const maxPins = Number(process.env.MAX_PINS_PER_RUN || 5);

if (!fs.existsSync(queuePath)) {
  console.error('Queue file not found. Run generate_pins.py first.');
  process.exit(1);
}

const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
const pending = queue.filter((item) => item.status === 'ready').slice(0, maxPins);

if (!pending.length) {
  console.log('No pending pins in queue.');
  process.exit(0);
}

if (!publishMode) {
  console.log(`[DRY RUN] Would publish ${pending.length} pins (pass --publish with PINTEREST_ACCESS_TOKEN to send):`);
  for (const p of pending) {
    console.log(`- [${p.board}] ${p.pin_title} -> ${p.destination_url} (${path.basename(p.image_path)})`);
  }
  process.exit(0);
}

const token = process.env.PINTEREST_ACCESS_TOKEN;
const boardMap = JSON.parse(process.env.PINTEREST_BOARD_MAP_JSON || '{}');

if (!token) {
  console.error('Missing PINTEREST_ACCESS_TOKEN env var.');
  process.exit(1);
}

for (const pin of pending) {
  const boardId = boardMap[pin.board];
  if (!boardId) {
    console.warn(`Skipping "${pin.pin_title}": missing board_id for "${pin.board}" in PINTEREST_BOARD_MAP_JSON`);
    continue;
  }

  const imageBase64 = fs.readFileSync(pin.image_path).toString('base64');
  const res = await fetch('https://api.pinterest.com/v5/pins', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      board_id: boardId,
      title: pin.pin_title,
      description: pin.pin_description,
      alt_text: pin.alt_text,
      link: pin.destination_url,
      media_source: {
        source_type: 'image_base64',
        content_type: 'image/png',
        data: imageBase64
      }
    })
  });

  if (!res.ok) {
    const errText = await res.text();
    console.error(`Failed to publish "${pin.pin_title}": ${res.status} ${errText}`);
    continue;
  }

  const created = await res.json();
  pin.status = 'published';
  pin.pinterest_pin_id = created.id;
  pin.published_at = new Date().toISOString();
  console.log(`Published Pin ${created.id}: ${pin.pin_title}`);
}

fs.writeFileSync(queuePath, JSON.stringify(queue, null, 2), 'utf8');
