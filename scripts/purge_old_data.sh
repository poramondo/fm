#!/usr/bin/env bash
# Запускать по cron/systemd-timer раз в час
set -euo pipefail
cd /srv/mixlab2/infra
/usr/bin/docker compose exec -T backend python -m app.tasks.cleanup_ttl