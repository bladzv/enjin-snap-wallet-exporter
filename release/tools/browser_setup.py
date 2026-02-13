#!/usr/bin/env python3
"""
Browser Setup and Server for Enjin Snap Wallet Exporter.

This script prepares the browser interface for offline use by downloading
ESM bundles from jsDelivr CDN, then starts a local HTTP server.

Run this on a machine with internet access (for vendoring) and Python installed.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def download_file(url, dest):
    """Download a file from a URL to a local path."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urlopen(req, timeout=30) as resp:
            with open(dest, 'wb') as f:
                f.write(resp.read())
        return True
    except (URLError, HTTPError) as e:
        print(f"  ✗ Failed to download {url}: {e}")
        return False


def check_libs_exist(libs_dir, web_dir):
    """Check if all required vendored libs exist."""
    expected_files = [
        # Polkadot bundles (directory-based packages)
        libs_dir / "@polkadot_util@13.4.4" / "bundle-polkadot-util.js",
        libs_dir / "@polkadot_util-crypto@13.4.4" / "bundle-polkadot-util-crypto.js",
        libs_dir / "@polkadot_util-crypto@13.4.4" / "index.js",
        libs_dir / "@polkadot_util@13.4.4" / "index.js",
        libs_dir / "@polkadot_wasm-crypto@7.4.1" / "index.js",
        libs_dir / "@polkadot_wasm-bridge@7.4.1" / "index.js",
        libs_dir / "@polkadot_wasm-util@7.4.1" / "index.js",
        # Single-file ESM bundles (from jsDelivr CDN)
        libs_dir / "@noble_hashes_utils@1.7.1.js",
        libs_dir / "@noble_hashes_sha3.js",
        libs_dir / "@noble_hashes_blake2b.js",
        libs_dir / "@noble_hashes_scrypt.js",
        libs_dir / "@noble_curves_secp256k1.js",
        libs_dir / "@scure_base@1.2.4.js",
        libs_dir / "@scure_bip32@1.6.2.js",
        libs_dir / "@scure_bip39@1.5.4.js",
        libs_dir / "@scure_bip39_wordlist_english.js",
        libs_dir / "tweetnacl@1.0.3.js",
        # Sub-module ESM bundles referenced by the CDN bundles via absolute /npm/ paths
        web_dir / "npm" / "@noble" / "hashes@1.7.1" / "crypto" / "+esm.js",
        web_dir / "npm" / "@noble" / "hashes@1.7.1" / "sha256" / "+esm.js",
        web_dir / "npm" / "@noble" / "hashes@1.7.1" / "sha512" / "+esm.js",
        web_dir / "npm" / "@noble" / "hashes@1.7.1" / "hmac" / "+esm.js",
        web_dir / "npm" / "@noble" / "hashes@1.7.1" / "utils" / "+esm.js",
        web_dir / "npm" / "@noble" / "hashes@1.7.1" / "_assert" / "+esm.js",
        web_dir / "npm" / "@noble" / "hashes@1.7.1" / "ripemd160" / "+esm.js",
        web_dir / "npm" / "@noble" / "curves@1.8.1" / "secp256k1" / "+esm.js",
        web_dir / "npm" / "@noble" / "curves@1.8.1" / "abstract" / "modular" / "+esm.js",
        web_dir / "npm" / "@scure" / "base@1.2.2" / "+esm.js",
        # @polkadot ESM bundles referenced by the importmap
        web_dir / "npm" / "@polkadot" / "networks@13.4.4" / "+esm.js",
        web_dir / "npm" / "@polkadot" / "x-bigint@13.4.4" / "+esm.js",
    ]
    return all(f.exists() for f in expected_files)


def vendor_libs(libs_dir, web_dir):
    """
    Download ESM bundles from jsDelivr CDN for offline browser use.

    The jsDelivr CDN provides pre-built ESM bundles that work directly in browsers.
    These bundles use relative import paths like './npm/@noble/hashes@1.7.1/crypto/+esm.js'
    for their internal dependencies. Since the bundles live in libs/, we rewrite those
    to '../npm/' so they resolve to the web root's /npm/ directory.
    """
    CDN = "https://cdn.jsdelivr.net"

    # ─── 1. Single-file ESM bundles loaded by the importmap / tryImport ───
    # These go into libs/ and are referenced by index.html directly.
    esm_bundles = {
        # Noble hashes sub-modules used directly by index.html
        f"{CDN}/npm/@noble/hashes@1.7.1/utils/+esm":       libs_dir / "@noble_hashes_utils@1.7.1.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/sha3/+esm":        libs_dir / "@noble_hashes_sha3.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/blake2b/+esm":     libs_dir / "@noble_hashes_blake2b.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/scrypt/+esm":      libs_dir / "@noble_hashes_scrypt.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/sha256/+esm":      libs_dir / "@noble_hashes_sha256@1.7.1.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/sha512/+esm":      libs_dir / "@noble_hashes_sha512@1.7.1.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/hmac/+esm":        libs_dir / "@noble_hashes_hmac@1.7.1.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/ripemd160/+esm":   libs_dir / "@noble_hashes_ripemd160@1.7.1.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/_assert/+esm":     libs_dir / "@noble_hashes__assert@1.7.1.js",
        # Noble curves
        f"{CDN}/npm/@noble/curves@1.8.1/secp256k1/+esm":   libs_dir / "@noble_curves_secp256k1.js",
        f"{CDN}/npm/@noble/curves@1.8.1/abstract/modular/+esm": libs_dir / "@noble_curves_abstract_modular@1.8.1.js",
        # Scure
        f"{CDN}/npm/@scure/base@1.2.4/+esm":               libs_dir / "@scure_base@1.2.4.js",
        f"{CDN}/npm/@scure/bip32@1.6.2/+esm":              libs_dir / "@scure_bip32@1.6.2.js",
        f"{CDN}/npm/@scure/bip39@1.5.4/+esm":              libs_dir / "@scure_bip39@1.5.4.js",
        f"{CDN}/npm/@scure/bip39@1.5.4/wordlists/english/+esm": libs_dir / "@scure_bip39_wordlist_english.js",
        # TweetNaCl
        f"{CDN}/npm/tweetnacl@1.0.3/+esm":                 libs_dir / "tweetnacl@1.0.3.js",
    }

    # ─── 2. Sub-module ESM bundles referenced by internal imports ───────
    # The jsDelivr ESM bundles use relative imports like:
    #   import "./npm/@noble/hashes@1.7.1/crypto/+esm.js"
    # After downloading, we rewrite './npm/' to '../npm/' so they resolve
    # from libs/ to the web root's npm/ directory.
    npm_submodules = {
        # @noble/hashes sub-modules
        f"{CDN}/npm/@noble/hashes@1.7.1/crypto/+esm":              "npm/@noble/hashes@1.7.1/crypto/+esm.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/sha256/+esm":              "npm/@noble/hashes@1.7.1/sha256/+esm.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/sha512/+esm":              "npm/@noble/hashes@1.7.1/sha512/+esm.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/hmac/+esm":                "npm/@noble/hashes@1.7.1/hmac/+esm.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/utils/+esm":               "npm/@noble/hashes@1.7.1/utils/+esm.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/_assert/+esm":             "npm/@noble/hashes@1.7.1/_assert/+esm.js",
        f"{CDN}/npm/@noble/hashes@1.7.1/ripemd160/+esm":           "npm/@noble/hashes@1.7.1/ripemd160/+esm.js",
        # @noble/curves sub-modules
        f"{CDN}/npm/@noble/curves@1.8.1/secp256k1/+esm":           "npm/@noble/curves@1.8.1/secp256k1/+esm.js",
        f"{CDN}/npm/@noble/curves@1.8.1/abstract/modular/+esm":    "npm/@noble/curves@1.8.1/abstract/modular/+esm.js",
        # @scure/base (referenced by bip32 bundle as @scure/base@1.2.2)
        f"{CDN}/npm/@scure/base@1.2.2/+esm":                       "npm/@scure/base@1.2.2/+esm.js",
        # @polkadot ESM bundles (referenced by importmap)
        f"{CDN}/npm/@polkadot/networks@13.4.4/+esm":               "npm/@polkadot/networks@13.4.4/+esm.js",
        f"{CDN}/npm/@polkadot/x-bigint@13.4.4/+esm":               "npm/@polkadot/x-bigint@13.4.4/+esm.js",
    }

    print(f"Downloading ESM bundles from jsDelivr CDN...")
    print()

    # Download single-file ESM bundles
    ok_count = 0
    fail_count = 0
    for url, dest in esm_bundles.items():
        if dest.exists():
            print(f"  ✓ {dest.name} (already exists)")
            ok_count += 1
            continue
        print(f"  ↓ {dest.name}")
        if download_file(url, dest):
            ok_count += 1
        else:
            fail_count += 1

    print()

    # Download sub-module ESM bundles to web root /npm/ directory
    print("Downloading sub-module ESM bundles (for internal imports)...")
    for url, rel_path in npm_submodules.items():
        dest = web_dir / rel_path
        if dest.exists():
            print(f"  ✓ {rel_path} (already exists)")
            ok_count += 1
            continue
        print(f"  ↓ {rel_path}")
        if download_file(url, dest):
            ok_count += 1
        else:
            fail_count += 1

    # ─── 3. Post-process: rewrite relative imports in libs/ bundles ─────
    # jsDelivr bundles use './npm/' relative paths for sub-module imports.
    # Since the bundles live in libs/, './npm/' resolves to libs/npm/ which
    # doesn't exist. Rewrite to '../npm/' so they resolve to <web_root>/npm/.
    print("Rewriting relative import paths in vendored bundles...")
    rewrite_count = 0
    for dest in esm_bundles.values():
        if dest.exists():
            content = dest.read_text(encoding='utf-8')
            if '"./npm/' in content:
                content = content.replace('"./npm/', '"../npm/')
                dest.write_text(content, encoding='utf-8')
                rewrite_count += 1
                print(f"  ✓ Rewrote imports in {dest.name}")
    if rewrite_count:
        print(f"  Rewrote {rewrite_count} file(s).")
    else:
        print("  No files needed rewriting.")

    print()
    if fail_count:
        print(f"⚠ Vendoring finished with {fail_count} failures ({ok_count} succeeded).")
        print("  Re-run with internet access to retry failed downloads.")
    else:
        print(f"✅ All {ok_count} ESM bundles downloaded successfully.")

    print()
    print("Note: Polkadot UMD bundles (@polkadot/util, @polkadot/util-crypto,")
    print("@polkadot/wasm-crypto, etc.) must be pre-bundled in libs/. These are")
    print("large WASM-based packages that cannot be vendored via simple downloads.")
    print("They are included in the release distribution by default.")

def find_python_command():
    """Find a suitable Python 3 command."""
    for cmd in ['python3', 'python']:
        if shutil.which(cmd):
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'Python 3' in result.stdout:
                    return cmd
            except:
                continue
    return None

def start_server(web_dir):
    """Start the local HTTP server."""
    python_cmd = find_python_command()
    if not python_cmd:
        print("Error: Could not find Python 3 command.")
        return

    print("Starting simple HTTP server on port 8000 (CTRL-C to stop)")
    print()
    print("  → Open in browser: http://localhost:8000/index.html")
    print()
    os.chdir(web_dir)
    try:
        subprocess.run([python_cmd, '-m', 'http.server', '8000', '--bind', '127.0.0.1'])
    except KeyboardInterrupt:
        print("\nServer stopped.")

def main():
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    web_dir = root_dir / "web"
    libs_dir = web_dir / "libs"

    print("Enjin Snap Wallet Exporter - Browser Setup")
    print("=" * 50)

    try:
        mode = input("Online or offline use? (online/offline): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        return

    if mode == "online":
        index_path = web_dir / "index.html"
        if not index_path.exists():
            print("Error: index.html not found.")
            return
        print("Opening index.html in default browser (online mode - loads from CDN)...")
        import webbrowser
        webbrowser.open(f"file://{index_path.absolute()}")
        print("Done.")
        return

    if mode != "offline":
        print("Invalid choice. Please enter 'online' or 'offline'.")
        return

    # Offline mode
    print("Offline mode selected.")
    if not (web_dir / "index.html").exists():
        print("Error: index.html not found in web directory.")
        sys.exit(1)

    # Check if libs are vendored
    if not check_libs_exist(libs_dir, web_dir):
        print("Vendored libraries not found or incomplete.")
        try:
            response = input("Download ESM bundles for offline use? (y/N): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            return
        if response in ('y', 'yes'):
            libs_dir.mkdir(parents=True, exist_ok=True)
            vendor_libs(libs_dir, web_dir)
        else:
            print("Skipping vendoring. Note: browser may not work offline.")
    else:
        print("Vendored libraries found.")

    print()
    print("Next steps: start a local HTTP server for offline use.")

    try:
        response = input("Start local HTTP server now? (y/N): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        return

    if response in ('y', 'yes'):
        start_server(web_dir)
    else:
        print("Skipped starting server. To start later:")
        print(f"  cd {web_dir} && python3 -m http.server 8000")

    print("Done.")

if __name__ == '__main__':
    main()