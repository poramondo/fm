#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# 1) продлить сертификаты, если подходит срок
docker compose run --rm certbot renew --webroot -w /var/www/certbot --quiet

# 2) мягко перечитать сертификаты в nginx
docker compose exec -T nginx nginx -s reload
