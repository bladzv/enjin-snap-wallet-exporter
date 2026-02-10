# Enjin Snap Wallet Exporter

Export [Enjin Snap](https://snaps.metamask.io/snap/npm/enjin-io/snap/) (MetaMask Snap) wallet keypairs as a hex private key or encrypted JSON keystore for importing into the **Enjin Wallet** or compatible wallets.

## ⚠️ Security Warning

This tool handles **mnemonics and private keys**. For maximum security:

- **Run offline** — disconnect from the internet before entering your recovery phrase
- Never share your mnemonic or private key with anyone
- Verify the source code before running — it's a single script / single HTML file

## Features

- **Five address derivations** from one BIP-39 mnemonic:
  - Ethereum (BIP-44 `m/44'/60'/0'/0/0`)
  - Enjin Matrixchain sr25519 (blank derivation path, SS58 prefix 1110)
  - Enjin Relaychain sr25519 (blank derivation path, SS58 prefix 2135)
  - Enjin Snap ed25519 — Matrixchain (non-standard SLIP-10 derivation, SS58 prefix 1110)
  - Enjin Snap ed25519 — Relaychain (non-standard SLIP-10 derivation, SS58 prefix 2135)
- **Private key export** — hex seed for direct wallet import
- **Keystore export** — encrypted JSON in Web3 (Ethereum v3) or Polkadot-compatible formats for importing into Enjin Wallet or other wallets
- **Two interfaces** — Python CLI script and standalone browser HTML

## Quick Start

### Standalone Executable (Recommended)

Download pre-built standalone executables for your platform from the [GitHub releases](../../releases) page (no Python installation required). Supports macOS, Linux, and Windows.

```sh
# Run the executable (it will prompt for .env setup)
./enjin-snap-exporter        # macOS / Linux
.\enjin-snap-exporter.exe    # Windows
```

Keystores and private keys will be saved in the current working directory.

### Python Script

For users who have Python installed and prefer running the CLI directly (alternative to the standalone executable):

```sh
# Install dependencies
pip install -r requirements.txt

# Create .env with your recovery phrase
cp .env.example .env
# Edit .env and replace the placeholder with your actual 12 or 24 word BIP-39 mnemonic
# Example: MNEMONIC="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

# Run
python release/tools/enjin_snap_exporter.py
```

The script will automatically detect and offer to install missing dependencies. Keystores and private keys will be saved in the current working directory.

### Browser (HTML)

#### Online Use
Open `release/web/index.html` in any modern browser with internet access. The page loads cryptographic libraries from CDN (jsDelivr) and runs entirely client-side.

#### Offline Use
For guaranteed offline operation, run the setup script:
```sh
python3 release/tools/browser_setup.py
```

Select "offline" mode. It will download ESM bundles from jsDelivr CDN into `release/web/libs/` and `release/web/npm/`, then start a local HTTP server. Open `http://localhost:8000/index.html` in your browser.

## How It Works

### Enjin Snap Derivation (the non-obvious part)

The Enjin Snap uses a non-standard key derivation that this project replicates:

```
BIP-39 mnemonic
    → BIP-39 seed (64 bytes)
    → SLIP-10 secp256k1 derive at m/44'/1155'
    → private key → prepend "0x" → hex string (66 chars)
    → .slice(0, 32) → first 32 characters
    → UTF-8 encode → 32 bytes
    → ed25519 keypair from seed
    → SS58 encode with prefix 1110 (Matrixchain) or 2135 (Relaychain)
```

This replicates the logic from the snap's `account.ts` — the `.slice(0, 32)` on the hex string (not the bytes) is intentional and critical for compatibility.

### Keystore Format

The tool exports encrypted JSON keystores in two formats:

#### Web3 (Ethereum v3) Format — Recommended for Enjin Wallet
- **Encryption**: scrypt (N=262144, r=8, p=1) + aes-128-ctr
- **Key encoding**: Raw private key bytes
- **Schema version**: `"3"`
- **Import into Enjin Wallet**:
  1. Go to **Settings → Wallets → Add Wallet → Import Wallet → Import Keystore**
  2. Paste the keystore content into the "Import Keystore" field
  3. Enter the password in the "Encryption Password" field

#### Polkadot-Style Format
- **Encryption**: scrypt (N=32768, r=8, p=1) + xsalsa20-poly1305
- **Key encoding**: PKCS8 with ed25519 OID header
- **Schema version**: `"3"`
- **Compatibility**: Polkadot.js and other Substrate-based wallets
- **Note**: Enjin Wallet currently does not support importing Polkadot-style keystore files

## Dependencies

### Python

| Package | Purpose |
|---------|---------|
| `python-dotenv` | Load mnemonic from `.env` file |
| `substrate-interface` | sr25519/ed25519 keypairs, SS58 encoding |
| `eth-account` | Ethereum BIP-44 derivation, Web3 v3 keystore |
| `bip-utils` | BIP-39 seed generation, SLIP-10 secp256k1 |
| `PyNaCl` | xsalsa20-poly1305 authenticated encryption |
| `pycryptodome` | scrypt KDF for keystore encryption |

### Browser (index.html)

Loaded from vendored ESM bundles (offline) or jsDelivr CDN (online) — no build step required:

| Package | Purpose |
|---------|---------|
| `@scure/bip39` | BIP-39 mnemonic validation and seed generation |
| `@scure/bip32` | SLIP-10 / BIP-32 HD key derivation |
| `@noble/curves` | secp256k1 public key derivation (Ethereum) |
| `@noble/hashes` | keccak256, blake2b, scrypt |
| `@scure/base` | Base58 encoding (SS58 addresses) |
| `tweetnacl` | ed25519 keypairs, xsalsa20-poly1305 encryption |
| `@polkadot/util-crypto` | sr25519 via WASM (optional, graceful fallback) |

## Project Structure

```
├── .github/
│   └── workflows/
│       └── build.yml          # GitHub Actions CI — builds PyInstaller executables
├── release/
│   ├── tools/
│   │   ├── enjin_snap_exporter.py  # Main CLI script (built into executable)
│   │   └── browser_setup.py        # Browser setup, vendoring, and HTTP server
│   └── web/
│       ├── index.html         # Browser UI (single-file, self-contained)
│       ├── libs/              # Vendored ESM bundles (loaded via importmap)
│       └── npm/               # Sub-module ESM bundles (for absolute /npm/ imports)
├── .env.example               # Template for mnemonic storage
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT license
└── README.md                  # This file
```

## Building

### Automated (GitHub Actions)

Executables are built automatically via GitHub Actions for macOS, Linux, and Windows using PyInstaller.

- **Every push / PR** to `main` — builds and uploads artifacts (for CI validation)
- **Version tags** (`v*`) — builds, creates a GitHub Release, and attaches all platform binaries

To create a release:
```sh
git tag v1.0.0
git push origin v1.0.0
```

Download pre-built binaries from:
- **[Releases](../../releases)** — tagged releases with all platform binaries attached
- **[Actions artifacts](../../actions)** — CI build artifacts from every push/PR

### Manual Build

```sh
pip install -r requirements.txt pyinstaller
cd release
python -m PyInstaller --onefile --name enjin-snap-exporter \
  --hidden-import=coincurve._cffi_backend \
  --hidden-import=_cffi_backend \
  --hidden-import=coincurve \
  --collect-all=bip_utils \
  --collect-all=sr25519 \
  tools/enjin_snap_exporter.py
# Output: release/dist/enjin-snap-exporter
```

## Security

- **Content Security Policy (CSP)**: The HTML page uses a strict CSP that only allows `self` and `cdn.jsdelivr.net` as script sources
- **No network calls**: The Python CLI makes zero network requests — all derivation is offline
- **Memory cleanup**: The browser clears mnemonics, passwords, and key material from DOM and memory on page unload
- **Input protection**: Mnemonic textarea disables autocomplete, autocorrect, and spellcheck
- **Mnemonic source**: Always loaded from `.env` file, never accepted as a CLI argument
