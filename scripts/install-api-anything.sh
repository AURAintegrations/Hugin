#!/usr/bin/env bash
set -euo pipefail
umask 077
cd /workspace/Hugin
api_runtime_lock=/workspace/Hugin/backend/api-anything.runtime-lock.json
setup=/workspace/.hugin-setup
api_src="$setup/api-anything-src"
api_revision=0b556c36932b111ee8840c412008261abe717725
mkdir -p "$setup/cache/npm" "$setup/logs" "$setup/bin" "$setup/api-anything-state"
chmod 700 "$setup/api-anything-state"
if [ ! -d "$api_src/.git" ]; then
  git clone --no-checkout https://github.com/goodnight000/api-anything.git "$api_src"
  git -C "$api_src" checkout --detach "$api_revision"
fi
[ "$(git -C "$api_src" rev-parse HEAD)" = "$api_revision" ]
[ -z "$(git -C "$api_src" status --porcelain --untracked-files=no)" ]
cd "$api_src"
npm ci --cache "$setup/cache/npm" --no-audit --no-fund
npm run check
npm pack --cache "$setup/cache/npm" --silent
npm install --prefix "$setup/api-anything" --cache "$setup/cache/npm" --global --no-audit --no-fund "$api_src/api-anything-0.1.0.tgz"
# Local installed-artifact security override; upstream source/lockfile remain unchanged.
npm install --prefix "$setup/api-anything/lib/node_modules/api-anything" --cache "$setup/cache/npm" --save-exact --ignore-scripts --omit=dev --no-audit --no-fund @modelcontextprotocol/sdk@1.31.0
cp "$api_runtime_lock" "$setup/api-anything/lib/node_modules/api-anything/package-lock.json"
npm ci --prefix "$setup/api-anything/lib/node_modules/api-anything" --cache "$setup/cache/npm" --ignore-scripts --omit=dev --no-audit --no-fund
npm audit --prefix "$setup/api-anything/lib/node_modules/api-anything" --cache "$setup/cache/npm" --omit=dev
cat > "$setup/bin/api-anything" <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail
umask 077
export API_ANYTHING_HOME=/workspace/.hugin-setup/api-anything-state
export NODE_USE_ENV_PROXY=1
if [ -n "${SSL_CERT_FILE:-}" ]; then export NODE_EXTRA_CA_CERTS="$SSL_CERT_FILE"; fi
exec /workspace/.hugin-setup/api-anything/bin/api-anything "$@"
WRAPPER
chmod 755 "$setup/bin/api-anything"

cd /workspace/Hugin
.venv/bin/python - <<'VERIFY'
from hugin.api_anything import ApiAnythingSource
from hugin.config import Settings
from hugin.sources import Budget
source = ApiAnythingSource(Settings(), None, None)
source.worker('build', 'openalex', Budget(1, 10, 0), args={'query': 'Example Person'})
print('Pinned offline API Anything worker verified')
VERIFY
