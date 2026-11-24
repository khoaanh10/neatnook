# NeatNook — Pinterest + Static Affiliate Site

Static affiliate guide site (`site/`) + automated 1000×1500 Pinterest Pin Factory (`pin-factory/`) + VPS deploy kit (`deploy/`).

## Local Commands

```bash
# 1. Build static site into site/dist/
node site/build.mjs

# 2. Generate 1000x1500 Pinterest Pins + schedule queue
python pin-factory/generate_pins.py

# 3. Preview Pinterest API v5 publish queue (dry run)
node pin-factory/publish_pinterest_api.mjs
```

## Deploy to VPS (Ubuntu / Debian)

1. Push this repo to GitHub (e.g. `https://github.com/khoaanh10/neatnook.git`).
2. Point your domain's `A` record (`@` and `www`) to your VPS IP.
3. SSH into your VPS and run:

```bash
git clone https://github.com/khoaanh10/neatnook.git /opt/neatnook
cd /opt/neatnook
chmod +x deploy/deploy.sh
DOMAIN="your-domain.com" ./deploy/deploy.sh
```

Subsequent updates on the VPS are just:

```bash
cd /opt/neatnook && ./deploy/deploy.sh
```
