#!/usr/bin/env bash
set -euo pipefail
cd /workspace/Hugin
setup=/workspace/.hugin-setup
mkdir -p "$setup/tools" "$setup/cache/npm" "$setup/cache/pip" "$setup/cache/yarn" "$setup/logs" "$setup/data/mongodb"
if [ ! -x .venv/bin/python ]; then python -m venv .venv; fi
.venv/bin/pip install --cache-dir "$setup/cache/pip" -e backend
.venv/bin/pip check
npm install --prefix "$setup/tools" --cache "$setup/cache/npm" --no-audit --no-fund yarn@1.22.22 playwright-core@1.56.1
cd frontend
"$setup/tools/node_modules/.bin/yarn" install --frozen-lockfile --non-interactive --cache-folder "$setup/cache/yarn"
BUILD_PATH="$setup/build" npm run build
cd ..
bash scripts/install-mongodb.sh
bash scripts/install-collectors.sh
bash scripts/install-linkedin.sh
bash scripts/install-api-anything.sh
# Startup is registered separately. Neither this script nor a fixture is a live Dex validation.
