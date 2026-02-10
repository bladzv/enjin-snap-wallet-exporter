#!/usr/bin/env bash
# Vendor Polkadot WASM and ESM bundles for offline use and optionally run a local HTTP server.
# Run this on a machine with internet access. It downloads npm packages via `npm pack`,
# extracts them, copies necessary ESM and WASM artifacts into `./libs`, and attempts to
# place primary ESM bundles at the filenames `index.html` expects (e.g. ./libs/@polkadot_util_crypto@13.4.4.js).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/libs"
TMP_DIR=$(mktemp -d)

PKGS=(
  "@polkadot/util@13.4.4"
  "@polkadot/util-crypto@13.4.4"
  "@polkadot/wasm-crypto@7.4.1"
  "@polkadot/wasm-bridge@7.4.1"
  "@polkadot/wasm-util@7.4.1"
)

# Map package to an expected top-level filename used by index.html
declare -A EXPECTED
EXPECTED["@polkadot/util-crypto@13.4.4"]="@polkadot_util_crypto@13.4.4.js"
EXPECTED["@polkadot/util@13.4.4"]="@polkadot_util@13.4.4.js"

echo "Vendor + Serve script started. Output: $OUT_DIR"
mkdir -p "$OUT_DIR"

cd "$TMP_DIR"

find_candidate_js() {
  local root="$1"
  # Preferred patterns (in order)
  local f
  f=$(find "$root" -maxdepth 1 -type f -name 'index.js' -print -quit 2>/dev/null || true)
  [ -n "$f" ] && { printf '%s' "$f"; return 0; }
  f=$(find "$root" -type f -name '*+esm*.js' -print -quit 2>/dev/null || true)
  [ -n "$f" ] && { printf '%s' "$f"; return 0; }
  f=$(find "$root" -type f -name '*.esm.js' -print -quit 2>/dev/null || true)
  [ -n "$f" ] && { printf '%s' "$f"; return 0; }
  f=$(find "$root" -type f -name 'dist/*.js' -print -quit 2>/dev/null || true)
  [ -n "$f" ] && { printf '%s' "$f"; return 0; }
  f=$(find "$root" -maxdepth 3 -type f -name '*.js' -print -quit 2>/dev/null || true)
  [ -n "$f" ] && { printf '%s' "$f"; return 0; }
  return 1
}

for pkg in "${PKGS[@]}"; do
  echo "Packing $pkg..."
  TAR=$(npm pack "$pkg")
  echo "Downloaded $TAR"
  mkdir -p "extract"
  tar -xzf "$TAR" -C extract
  PKG_ROOT="extract/package"

  # normalize a safe directory name for output, replace / with _
  safe_name=$(echo "$pkg" | sed 's#/#_#g')
  tgt="$OUT_DIR/$safe_name"
  mkdir -p "$tgt"

  # Copy JS and WASM assets while preserving relative paths (portable)
  echo "Copying JS and WASM assets for $pkg to $tgt"
  while IFS= read -r -d '' file; do
    rel_path="${file#$PKG_ROOT/}"
    dest_dir="$tgt/$(dirname "$rel_path")"
    mkdir -p "$dest_dir"
    cp "$file" "$tgt/$rel_path" || true
  done < <(find "$PKG_ROOT" -type f \( -name '*.js' -o -name '*+esm*' -o -name '*.wasm' \) -print0)

  # Copy package.json if present
  if [ -f "$PKG_ROOT/package.json" ]; then
    cp "$PKG_ROOT/package.json" "$tgt/"
  fi

  # If there's an expected top-level filename defined, try to locate an entry ESM and copy it
  if [ -n "${EXPECTED["$pkg"]+set}" ]; then
    expected_name="${EXPECTED["$pkg"]}"
    candidate=$(find_candidate_js "$PKG_ROOT" || true)
    if [ -n "$candidate" ]; then
      echo "Found candidate ESM for $pkg: $candidate"
      echo "Copying to $OUT_DIR/$expected_name"
      cp "$candidate" "$OUT_DIR/$expected_name" || true
    else
      echo "Warning: no candidate ESM found for $pkg; expected to create $expected_name"
    fi
  fi

  # Cleanup before next package
  rm -rf extract "$TAR"
done

echo "Vendor complete. Files placed under $OUT_DIR"
echo
echo "Next steps: open http://localhost:8000/index.html via a local HTTP server (do not use file://)."

read -r -p "Do you want to start a local HTTP server now? (y/N): " runserver
runserver=${runserver:-n}
if [ "$runserver" = "y" ] || [ "$runserver" = "Y" ]; then
  echo "Starting simple HTTP server on port 8000 (CTRL-C to stop)"
  echo ""
  echo "  → Open in browser: http://localhost:8000/index.html"
  echo ""
  cd "$ROOT_DIR"
  python3 -m http.server 8000 --bind 127.0.0.1
else
  echo "Skipped starting server. To start later run:"
  echo "  cd $ROOT_DIR && python3 -m http.server 8000"
fi

echo "Cleaning up tmp dir $TMP_DIR"
rm -rf "$TMP_DIR"

echo "Done."
