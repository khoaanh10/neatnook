#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_ROOT="/var/www/neatnook"
DOMAIN="${DOMAIN:-}"

echo "==> [1/4] Updating repository in ${APP_DIR}"
cd "${APP_DIR}"
if [ -d ".git" ] && git remote | grep -q .; then
  git pull --ff-only
fi

echo "==> [2/4] Building static site"
if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: Node.js not found. Install Node.js 20+ first."
  exit 1
fi
node site/build.mjs

echo "==> [3/4] Syncing site/dist/ -> ${WEB_ROOT}"
sudo mkdir -p "${WEB_ROOT}"
sudo rsync -a --delete "${APP_DIR}/site/dist/" "${WEB_ROOT}/"

echo "==> [4/4] Configuring web server"
if [ -n "${DOMAIN}" ]; then
  if command -v nginx >/dev/null 2>&1; then
    CONF_TARGET="/etc/nginx/sites-available/neatnook"
    sed "s/__DOMAIN__/${DOMAIN}/g" "${APP_DIR}/deploy/nginx.conf" | sudo tee "${CONF_TARGET}" >/dev/null
    sudo ln -sf "${CONF_TARGET}" /etc/nginx/sites-enabled/neatnook
    sudo nginx -t && sudo systemctl reload nginx
    echo "Nginx configured for ${DOMAIN}."
    echo "To enable free HTTPS, run: sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
  elif command -v caddy >/dev/null 2>&1; then
    sed "s/__DOMAIN__/${DOMAIN}/g" "${APP_DIR}/deploy/Caddyfile" | sudo tee /etc/caddy/Caddyfile.neatnook >/dev/null
    echo "Caddy snippet written to /etc/caddy/Caddyfile.neatnook (import it in /etc/caddy/Caddyfile and reload caddy)."
  else
    echo "Files synced to ${WEB_ROOT}. Install nginx or caddy to serve them."
  fi
else
  echo "Sync complete (${WEB_ROOT}). Pass DOMAIN=yourdomain.com on first run to auto-configure Nginx/Caddy."
fi

echo "Done!"
