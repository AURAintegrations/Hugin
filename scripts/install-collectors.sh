#!/usr/bin/env bash
set -euo pipefail
collector_dir=/workspace/.hugin-setup/maigret
python -m venv "$collector_dir"
cd /workspace/Hugin
"$collector_dir/bin/pip" install --cache-dir /workspace/.hugin-setup/cache/pip -r backend/collectors.lock.txt
"$collector_dir/bin/pip" check
