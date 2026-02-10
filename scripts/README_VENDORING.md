Offline vendor guide — Polkadot WASM & ESM
========================================

Purpose
-------
This document explains how to vendor the real @polkadot JavaScript bundles and WASM artifacts
into the repository so the `index.html` UI works fully offline (including sr25519 via WASM).

Overview
--------
- Run the `scripts/vendor_and_serve_polkadot_libs.sh` script on a machine with an internet connection.
- The script uses `npm pack` to download the packages, extracts them, and copies JS/WASM files
  into `./libs/`.
- After vendoring, run a local HTTP server from the repo root (do not use `file://`):

```bash
python3 -m http.server 8000
```

Packages to vendor
------------------
- @polkadot/util@13.4.4
- @polkadot/util-crypto@13.4.4
- @polkadot/wasm-crypto@7.4.1
- @polkadot/wasm-bridge@7.4.1
- @polkadot/wasm-util@7.4.1

Notes and troubleshooting
-------------------------
- The script copies matching `*.js`, `*+esm*` and `*.wasm` files into `./libs/<pkg>@<ver>/...`.
- Some upstream packages use nested `npm/` import specifiers; you may need to move or
  rename extracted files so that the paths expected by `index.html` exist (e.g.,
  `./libs/@polkadot_util_crypto@13.4.4/+esm.js`).
- If `cryptoWaitReady()` still fails in the browser:
  - Verify `.wasm` files are present and referenced by the local ESM bundle.
  - Check browser DevTools for 404s and adjust file locations accordingly.

Advanced: manual steps
----------------------
If you prefer manual steps instead of running the script, here is an example sequence for one package:

```bash
npm pack @polkadot/util-crypto@13.4.4
tar -xzf @polkadot-util-crypto-13.4.4.tgz
mkdir -p libs/@polkadot_util_crypto@13.4.4
cp -r package/* libs/@polkadot_util_crypto@13.4.4/
```

Repeat for `@polkadot/wasm-crypto@7.4.1` and ensure the `.wasm` files are copied into a folder
where the ESM bundle expects to find them.

Security
--------
- Download and vendor these packages only from a trusted network. Verify signatures/hashes where
  possible if this is a high-security environment.
