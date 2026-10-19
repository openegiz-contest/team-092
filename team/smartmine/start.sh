#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/../.."

echo "Starting OpenEgiz platform..."
make up

echo "Loading configuration..."
set -a
source deploy/compose/.env
set +a

echo "Creating SmartMine digital twin..."
DITTO_URL="http://localhost:${DITTO_PORT:-8080}" \
python3 team/smartmine/setup_twins.py

echo "Installing Grafana dashboard..."
GRAFANA_PASSWORD="$GRAFANA_ADMIN_PASSWORD" \
python3 team/smartmine/setup_dashboard.py

echo "Starting SmartMine simulator..."
docker compose -f team/smartmine/compose.yml up -d --build

echo "SmartMine AI started successfully!"
echo "Grafana: http://localhost:3000"
