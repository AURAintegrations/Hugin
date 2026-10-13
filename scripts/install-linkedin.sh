#!/usr/bin/env bash
set -euo pipefail
cd /workspace/Hugin
linkedin_dir=/workspace/.hugin-setup/linkedin
python -m venv "$linkedin_dir"
"$linkedin_dir/bin/pip" install --cache-dir /workspace/.hugin-setup/cache/pip -r backend/linkedin.lock.txt
"$linkedin_dir/bin/pip" check
test -x /usr/bin/chromium
# No login, cookies, live LinkedIn requests or paid sources during installation.
