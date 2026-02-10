# Copilot Instructions — enjinsnap_exporter

## Project Purpose

Offline CLI tool to export Enjin Snap (MetaMask Snap) wallet keypairs as a hex private key or Polkadot-compatible JSON keystore for importing into the Enjin Wallet. Security-critical — handles mnemonics and private keys, must always run offline.

## Architecture

Two interfaces — a Python CLI script ([enjin_snap_exporter.py](../release/tools/enjin_snap_exporter.py)) and a static browser page ([index.html](../release/web/index.html)) — performing five derivations from one BIP-39 mnemonic:

1. **Ethereum** — standard BIP-44 (`m/44'/60'/0'/0/0`) via `eth-account`
2. **Matrixchain sr25519** — blank derivation path, SS58 prefix `1110`, via `substrate-interface`
3. **Relaychain sr25519** — blank derivation path, SS58 prefix `2135`, via `substrate-interface`
4. **Enjin Snap ed25519 — Matrixchain** — non-standard derivation replicating the snap's `account.ts`, SS58 prefix `1110`
5. **Enjin Snap ed25519 — Relaychain** — same derivation, SS58 prefix `2135`

The snap derivation:
   BIP-39 seed → SLIP-10 secp256k1 at `m/44'/1155'` → hex private key → take first 32 chars of `0x`-prefixed hex → UTF-8 encode → use as ed25519 seed

The snap derivation is the core value of this project — it cannot be changed without breaking compatibility with existing Enjin Snap wallets.

## Key Dependencies

**Python:** `python-dotenv`, `substrate-interface` (Keypair, KeypairType), `eth-account`, `bip-utils` (Bip39SeedGenerator, Bip32Slip10Secp256k1), `PyNaCl` (SecretBox), `pycryptodome` (scrypt KDF). Scrypt KDF uses `hashlib.scrypt` (stdlib) with `pycryptodome` fallback.

**Browser (release/web/index.html):** `@scure/bip39`, `@scure/bip32`, `@noble/curves`, `@noble/hashes`, `tweetnacl`, `@polkadot/util-crypto` (sr25519 via WASM — optional, graceful fallback). Loaded from vendored ESM bundles or jsDelivr CDN.

## Critical Conventions

- **Mnemonic source**: always loaded from `MNEMONIC` in a `.env` file via `python-dotenv`; never hardcoded or accepted as a CLI argument
- **SS58 prefixes**: `1110` for Enjin Matrixchain, `2135` for Enjin Relaychain
- **Keystore encryption**: scrypt (N=32768, p=1, r=8) + xsalsa20-poly1305, matching Polkadot.js defaults — do not change these parameters
- **PKCS8 ed25519 encoding**: uses a fixed header (`0x30 0x53 0x02 0x01 ...`) and divider — byte layout must match Polkadot.js for wallet import compatibility
- **Keystore JSON schema**: fields `encoded`, `encoding` (with `content`, `type`, `version: "3"`), `address`, `meta` — must stay compatible with Enjin Wallet's import parser

## Security Rules

- Never log, print, or persist the mnemonic or raw private key to any file (keystore export is password-protected and user-initiated)
- All operations must work fully offline — no network calls
- Keystore files are written to the script's directory with pattern `enjin-snap-keystore-{addr[:8]}.json`

## Development Setup

```sh
# Python
pip install -r requirements.txt
cp .env.example .env   # edit with your actual mnemonic
python release/tools/enjin_snap_exporter.py

# Note: The Python script automatically detects and offers to install missing dependencies
# Browser — open release/web/index.html (needs internet for CDN modules)
# For offline operation, run: python3 release/tools/browser_setup.py
```

## Core Development Principles

### Code Quality
- Write clean, well-commented code explaining complex logic and business decisions
- Follow Python best practices and conventions
- Prioritize readability and maintainability

### Security Requirements (CRITICAL)
- **Input Sanitization**: Sanitize and validate ALL user inputs to prevent injection attacks
- **Output Encoding**: Properly encode data before rendering
- **Authentication/Authorization**: Implement proper access controls
- **Dependency Security**: Use up-to-date, secure dependencies

### Error Handling & Logging
- Log all **runtime errors and exceptions** to `logs.txt` with ISO 8601 timestamps
- Build/compilation errors should be fixed immediately, not logged
- Never expose sensitive information in error messages
- Implement graceful error handling with user-friendly messages

### Communication Style
**For every code change you make, provide:**
- **High-level explanation**: What changed and why
- **Implementation details**: Technical approach and key decisions
- **Important considerations**: Edge cases, dependencies, or follow-up items

## Session Workflow

This project uses a session-based workflow with commands `START`, `LOG`/`SUCCESS`, and `END` that manage `.github/actions.md` and `.github/pr_description.md`.

### START
Resets `.github/actions.md` and `.github/pr_description.md` to empty files.

### LOG → SUCCESS
- `LOG`: Begin tracking all actions, changes, and decisions
- `SUCCESS`: Stop tracking and append a new entry to `.github/actions.md` with:
  - Short descriptive title
  - Timestamp (YYYY-MM-DD HH:MM:SS UTC)
  - Detailed description of changes
  - Files modified
  - Rationale
  - Technical notes

### END
- Reads `.github/actions.md`
- Generates semantic git branch name (e.g., `feature/add-blockchain-wallet-integration`)
- Creates concise git commit message (imperative mood, <72 chars)
- Checks existing GitHub Issues
- Creates comprehensive PR description in `.github/pr_description.md`

**Important rules for action logging:**
- Use the **actual current timestamp** fetched programmatically at runtime (never use placeholders)
- Always **append new entries after all existing content** (add to end of file)
- Do not modify existing entries during normal operation (only START resets the file)
- The separator line (`---`) is part of the entry template and must be included

**DO log in actions.md:**
- Feature additions or modifications
- Bug fixes
- Security improvements
- Architecture changes
- API changes
- Configuration changes that affect functionality
- New dependencies added

**Do NOT log:**
- Minor formatting changes (whitespace, indentation)
- Typo fixes in comments
- Routine dependency updates without functional changes
- Auto-generated code from tools
- Simple variable renaming without logic changes

### Git Integration
After the `END` command completes:
- Copilot will provide the suggested branch name and commit message
- **Do NOT automatically create branches, commits, or push code**
- Present all suggestions to the user for review
- Wait for explicit user confirmation before executing any git operations

**Suggested workflow for user:**
1. Review the generated PR description in `.github/pr_description.md`
2. Create branch: `git checkout -b [suggested-branch-name]`
3. Stage changes: `git add .`
4. Commit: `git commit -m "[suggested-commit-message]"`
5. Push: `git push origin [branch-name]`
6. Create PR on GitHub using the description from `.github/pr_description.md`
