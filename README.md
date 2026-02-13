<div align="center">

# ![Enjin Snap Wallet Exporter](assets/favicon-32x32.png) Enjin Snap Wallet Exporter

</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python 3.8+"></a>
  <img src="https://img.shields.io/badge/Security-Offline%20First-green" alt="Security">
</p>

Export [Enjin Snap](https://snaps.metamask.io/snap/npm/enjin-io/snap/) (MetaMask Snap) wallet keypairs as hex private keys or encrypted JSON keystores for importing into the **Enjin Wallet** or compatible wallets.

### ⚠️ Security Warning

This tool handles **mnemonics and private keys**. For maximum security:
- **Run offline** — disconnect from the internet before entering your recovery phrase
- **Never share** your mnemonic or private key with anyone
- **Verify the source** before running — it's a single script / single HTML file

## ✨ Features

- **Five address derivations** from one BIP-39 mnemonic:
  - Ethereum — standard BIP-44 (`m/44'/60'/0'/0/0`)
  - Enjin Matrixchain sr25519 — blank derivation, SS58 prefix `1110`
  - Enjin Relaychain sr25519 — blank derivation, SS58 prefix `2135`
  - Enjin Snap ed25519 — Matrixchain — non-standard SLIP-10, SS58 prefix `1110`
  - Enjin Snap ed25519 — Relaychain — non-standard SLIP-10, SS58 prefix `2135`

- **Private key export** — hex seed for direct wallet import
- **Keystore export** — encrypted JSON in Web3 (Ethereum v3) or Polkadot-compatible formats
- **Two interfaces** — Python CLI script and standalone browser HTML
- **Standalone executables** — no Python installation needed (macOS, Linux, Windows)

## 🚀 Quick Start

### Option 1: Browser Interface

**🌐 Live Demo**

Try the browser interface online: **[Live Demo](https://bladzv.github.io/enjin-snap-wallet-exporter)**

> **Note**: This demo runs online to load cryptographic libraries from CDN. Once all libraries are loaded (you'll see "Libraries Loaded"), you can disconnect from the internet for secure offline operation.

**Online** (instant, uses CDN):
- Open `release/web/index.html` in any modern browser

**Offline** (guaranteed offline operation):
```bash
python3 release/tools/browser_setup.py
# Select "offline" mode
# Opens http://localhost:8000/index.html in your browser
```

### Option 2: Standalone Executable (Recommended)

No Python installation required. Download pre-built binaries from the [releases](../../releases) page:

```bash
# macOS / Linux
./enjin-snap-exporter

# Windows
.\enjin-snap-exporter.exe
```

Keystores and private keys are saved in your current working directory.

### Option 3: Python Script

For users with Python installed:

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env with your mnemonic
cp .env.example .env
# Edit .env and add your 12 or 24 word BIP-39 mnemonic
# MNEMONIC="your recovery phrase here"

# Run
python release/tools/enjin_snap_exporter.py
```

The script auto-detects missing dependencies and offers to install them.

## � How It Works

### Enjin Snap Derivation (The Non-Standard Part)

The Enjin Snap uses a custom key derivation path that differs from standard wallets:

```
BIP-39 mnemonic
  → BIP-39 seed (64 bytes)
  → SLIP-10 secp256k1 derive at m/44'/1155'
  → Private key → prepend "0x" → hex string (66 chars)
  → .slice(0, 32) → take first 32 characters (not bytes!)
  → UTF-8 encode → 32 bytes
  → ed25519 keypair from seed
  → SS58 encode
      ├─ Matrixchain: prefix 1110
      └─ Relaychain: prefix 2135
```

**⚠️ Important**: The `.slice(0, 32)` on the hex string (not bytes) is intentional and critical for compatibility with existing Enjin Snap wallets. This replicates the snap's `account.ts` logic.

### Keystore Formats

The tool exports encrypted JSON keystores in two formats:

#### Web3 (Ethereum v3) — Recommended for Enjin Wallet
| Property | Value |
|----------|-------|
| Encryption | scrypt (N=262144, r=8, p=1) + aes-128-ctr |
| Key Encoding | Raw private key bytes |
| Schema Version | `"3"` |

**Import steps**:
1. Go to **Settings → Wallets → Add Wallet → Import Wallet → Import Keystore**
2. Paste keystore content
3. Enter encryption password

#### Polkadot-Style Format
| Property | Value |
|----------|-------|
| Encryption | scrypt (N=32768, r=8, p=1) + xsalsa20-poly1305 |
| Key Encoding | PKCS8 with ed25519 OID header |
| Schema Version | `"3"` |
| Compatibility | Polkadot.js, other Substrate wallets |

⚠️ **Note**: Enjin Wallet currently doesn't support Polkadot-style keystore files.

## 📦 Dependencies

### Python Runtime

| Package | Purpose |
|---------|---------|
| `python-dotenv` | Load mnemonic from `.env` file |
| `substrate-interface` | sr25519/ed25519 keypairs, SS58 encoding |
| `eth-account` | Ethereum BIP-44 derivation, Web3 v3 keystore |
| `bip-utils` | BIP-39 seed, SLIP-10 secp256k1 |
| `PyNaCl` | xsalsa20-poly1305 authenticated encryption |
| `pycryptodome` | scrypt KDF for keystore encryption |

### Browser Runtime

Loaded from vendored ESM bundles (offline) or jsDelivr CDN (online) — no build step required:

| Package | Purpose |
|---------|---------|
| `@scure/bip39` | BIP-39 mnemonic & seed generation |
| `@scure/bip32` | SLIP-10 / BIP-32 HD key derivation |
| `@noble/curves` | secp256k1 key derivation (Ethereum) |
| `@noble/hashes` | keccak256, blake2b, scrypt |
| `@scure/base` | Base58 encoding (SS58 addresses) |
| `tweetnacl` | ed25519 keypairs, xsalsa20-poly1305 |
| `@polkadot/util-crypto` | sr25519 via WASM (optional, graceful fallback) |

## 📁 Project Structure

```
enjin-snap-wallet-exporter/
├── .github/
│   ├── workflows/
│   │   └── build.yml                  # GitHub Actions CI — PyInstaller builds
│   ├── copilot-instructions.md        # Copilot development guidelines
│   ├── actions.md                     # Session action tracking
│   └── pr_description.md              # PR template
│
├── release/
│   ├── tools/
│   │   ├── enjin_snap_exporter.py     # Main CLI script (built into executable)
│   │   └── browser_setup.py           # Browser vendoring & HTTP server
│   └── web/
│       ├── index.html                 # Browser UI (single-file, self-contained)
│       ├── assets/                    # Favicons & PWA manifest
│       ├── libs/                      # Vendored ESM bundles (offline support)
│       └── npm/                       # Sub-module imports (for absolute paths)
│
├── assets/                            # Project branding (favicons, manifest)
├── .env.example                       # Mnemonic template (local config)
├── requirements.txt                   # Python dependencies
├── LICENSE                            # MIT license
└── README.md                          # This file
```

### Key Directories Explained

- **`.github/`** — GitHub workflows, documentation, and session tracking
- **`release/tools/`** — CLI script and browser setup utilities
- **`release/web/`** — Browser UI with vendored cryptographic libraries
- **`assets/`** — Branding assets (favicons, web manifest for PWA support)

## 🔨 Building

### Automated via GitHub Actions (Recommended)

Pre-built executables are created automatically for macOS, Linux, and Windows via GitHub Actions.

- **Every push/PR** to `main` — builds and uploads artifacts (CI testing)
- **Version tags** (`v*`) — creates release and attaches all platform binaries

To create a release:
```bash
git tag v1.0.0
git push origin v1.0.0
```

**Download** pre-built binaries from:
- [**Releases**](../../releases) — tagged releases with all platform binaries
- [**Actions**](../../actions) — CI build artifacts from every push/PR

### Manual Build

For local builds, you'll need Python and PyInstaller:

```bash
pip install -r requirements.txt pyinstaller

cd release
python -m PyInstaller --onefile \
  --name enjin-snap-exporter \
  --hidden-import=coincurve._cffi_backend \
  --hidden-import=_cffi_backend \
  --hidden-import=coincurve \
  --collect-all=bip_utils \
  --collect-all=sr25519 \
  tools/enjin_snap_exporter.py

# Output: release/dist/enjin-snap-exporter
```

## 🛡️ Security

### Core Principles

**Offline-First Operation**
- Python CLI makes zero network requests — all derivation is local
- Browser mode works fully offline with vendored libraries
- No telemetry, no tracking, no external dependencies at runtime

**Cryptographic Security**
- Content Security Policy (CSP) — strict policies allowing only `self` and `cdn.jsdelivr.net`
- Scrypt KDF — industry-standard key derivation (N=262144, r=8, p=1)
- Authenticated Encryption — xsalsa20-poly1305 for keystore files
- Memory Cleanup — browser clears mnemonics, passwords, and keys on page unload

**Input Protection**
- Mnemonic textarea disables autocomplete, autocorrect, and spellcheck
- All inputs validated against BIP-39 standards
- No sensitive data logged or persisted

**Keystore Compatibility**
- Encrypted JSON output is password-protected and user-initiated
- Keystores written with pattern `enjin-snap-keystore-{addr[:8]}.json`
- Default location: script's working directory (user controls where files are stored)
