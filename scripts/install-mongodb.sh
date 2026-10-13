#!/usr/bin/env bash
set -euo pipefail
# Optional local MongoDB. Use an existing authorized service instead when available.
setup="${HUGIN_SETUP_DIR:-/workspace/.hugin-setup}"
version=8.0.16
archive="mongodb-linux-x86_64-debian12-${version}.tgz"
mkdir -p "$setup"
cd "$setup"
curl --fail --location --max-time 30 "https://fastdl.mongodb.org/linux/$archive.sha256" -o "$archive.sha256"
if [ ! -f "$archive" ]; then
  curl --fail --location --max-time 120 "https://fastdl.mongodb.org/linux/$archive" -o "$archive"
fi
# Official checksum downloaded with normal TLS verification. Never extract on failure.
sha256sum -c "$archive.sha256"
tar -xzf "$archive"
"$setup/mongodb-linux-x86_64-debian12-${version}/bin/mongod" --version
