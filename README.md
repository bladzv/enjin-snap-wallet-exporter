# Enjin Snap Wallet Exporter

Export [Enjin Snap](https://snaps.metamask.io/snap/npm/enjin-io/snap/) (MetaMask Snap) wallet keypairs as a hex private key or encrypted JSON keystore for importing into the **Enjin Wallet** or compatible wallets.

## ⚠️ Security Warning

This tool handles **mnemonics and private keys**. For maximum security:

- **Run offline** — disconnect from the internet before entering your recovery phrase
- Never share your mnemonic or private key with anyone
- Verify the source code before running — it's a single script / single HTML file

## Features

- **Three address derivations** from one BIP-39 mnemonic:
  - Ethereum (BIP-44 `m/44'/60'/0'/0/0`)
  - Enjin Matrixchain sr25519 (blank derivation path, SS58 format 1110)
  - Enjin Snap ed25519 (non-standard SLIP-10 derivation matching the snap's `account.ts`)
- **Private key export** — hex seed for direct wallet import
- **Keystore export** — encrypted JSON in Web3 (Ethereum v3) or Polkadot-compatible formats for importing into Enjin Wallet or other wallets
- **Two interfaces** — Python CLI script and standalone browser HTML

## Quick Start

### Python Script

```sh
# Install dependencies
pip install -r requirements.txt
# or pip3 install -r requirements.txt

# Create .env with your recovery phrase
cp .env.example .env
# Edit .env and replace the placeholder with your actual 12 or 24 word BIP-39 mnemonic
# Example: MNEMONIC="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

# Run
python generate_addresses.py
# or python3 generate_addresses.py
```

> **Note:** The script checks for required dependencies at startup and offers to install them automatically if missing.

### Browser (HTML)

#### Online Use
Open `index.html` in any modern browser with internet access. The page loads cryptographic libraries from CDN and runs entirely client-side.

To serve via local server (recommended):
```sh
python3 scripts/serve_offline.py
```
Open `http://localhost:8000/index.html` in your browser.

#### Offline Use
For guaranteed offline operation, first run the vendoring script on a machine with internet access:
```sh
./scripts/vendor_and_serve_polkadot_libs.sh
```

This downloads and vendors the required libraries into `./libs/`. Then run the server:
```sh
python3 scripts/serve_offline.py
```
Open `http://localhost:8000/index.html` in your browser (do not use `file://`).

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
    → SS58 encode with prefix 1110
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
| `eth-account` | Ethereum BIP-44 derivation |
| `bip-utils` | BIP-39 seed generation, SLIP-10 secp256k1 |
| `PyNaCl` | xsalsa20-poly1305 authenticated encryption |

### Browser (index.html)

All loaded from CDN via ES modules — no build step required:

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
├── generate_addresses.py  # Python CLI — full offline support
├── index.html             # Browser version — single static file
├── requirements.txt       # Python dependencies
├── .env.example           # Template for mnemonic configuration
├── .gitignore             # Ignores .env, keystores, logs
├── .github/               # GitHub-specific configuration and templates
├── libs/                  # Vendored JS/WASM libraries for offline HTML use
├── npm/                   # Temporary npm package storage for vendoring
├── scripts/               # Vendoring and utility scripts
└── README.md
```
