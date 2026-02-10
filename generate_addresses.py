#!/usr/bin/env python3
"""
Generate addresses matching the Enjin Snap derivation logic, and export
the Enjin Snap keypair as a private key (hex) and a JSON keystore file
for importing into the Enjin Wallet.

Derivations:
  1. Ethereum — standard BIP-44 (m/44'/60'/0'/0/0)
  2. Matrixchain sr25519 — blank derivation path, SS58 format 1110
  3. Enjin Snap ed25519 — non-standard SLIP-10 derivation replicating the snap

Security:
  - Mnemonic is loaded from MNEMONIC in .env (never hardcoded or passed as CLI arg)
  - All operations run fully offline — no network calls
  - Keystore files use scrypt + xsalsa20-poly1305 matching Polkadot.js defaults
"""

import os
import sys
import json
import struct
import time
import hashlib
import warnings
import getpass
import base64
from dotenv import load_dotenv


def ask_yes_no(prompt, default='y', max_retries=3):
    """Ask a yes/no question, validate input, return True/False.

    default: 'y' or 'n' or None (no default)
    """
    for _ in range(max_retries):
        try:
            ans = input(prompt).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print('\nAborted by user.')
            sys.exit(1)
        if ans == '' and default is not None:
            ans = default
        if ans in ('y', 'yes'):
            return True
        if ans in ('n', 'no'):
            return False
        print("Please answer 'y' or 'n'.")
    print('Too many invalid responses. Aborting.')
    sys.exit(1)


def ask_choice(prompt, choices, default=None, max_retries=3):
    """Ask for a choice from `choices` (iterable of strings). Returns chosen string."""
    choices_set = set(choices)
    for _ in range(max_retries):
        try:
            ans = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print('\nAborted by user.')
            sys.exit(1)
        if ans == '' and default is not None:
            ans = default
        if ans in choices_set:
            return ans
        print(f"Invalid selection; choose one of: {', '.join(choices)}")
    print('Too many invalid responses. Aborting.')
    sys.exit(1)


def get_password_confirm(prompt1="Enter password for keystore", prompt2="Confirm password", max_retries=3):
    for _ in range(max_retries):
        try:
            pw = getpass.getpass(f"  {prompt1}: ")
        except (KeyboardInterrupt, EOFError):
            print('\nAborted by user.')
            sys.exit(1)
        if not pw:
            print('  Error: Password cannot be empty.')
            continue
        try:
            confirm = getpass.getpass(f"  {prompt2}: ")
        except (KeyboardInterrupt, EOFError):
            print('\nAborted by user.')
            sys.exit(1)
        if pw != confirm:
            print('  Error: Passwords do not match.')
            continue
        return pw
    print('Too many invalid password attempts. Aborting.')
    sys.exit(1)

# Check for required dependencies before importing them
required_modules = [
    'substrateinterface',
    'eth_account',
    'bip_utils',
    'nacl.secret'
]

missing_modules = []
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print("Error: Missing required Python modules:")
    for module in missing_modules:
        print(f"  - {module}")
    print()

    install = ask_yes_no("Would you like to install the missing dependencies automatically? (y/n): ", default='n')
    if install:
        print("Installing dependencies...")
        import subprocess
        try:
            # Try different pip commands in order of preference
            pip_commands = [
                ['pip', 'install', '-r', 'requirements.txt'],
                ['pip3', 'install', '-r', 'requirements.txt'],
                ['python3', '-m', 'pip', 'install', '-r', 'requirements.txt'],
                ['python', '-m', 'pip', 'install', '-r', 'requirements.txt']
            ]

            success = False
            for cmd in pip_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
                    if result.returncode == 0:
                        success = True
                        break
                    else:
                        print(f"Command {' '.join(cmd)} failed, trying next option...")
                except FileNotFoundError:
                    continue

            if not success:
                print("Failed to install with pip/pip3/python -m pip. Error output:")
                print(result.stderr if 'result' in locals() else "No pip command found")
                raise Exception("Installation failed")

            print("Dependencies installed successfully!")
            print("Please run the script again.")
            sys.exit(0)

        except FileNotFoundError:
            print("pip not found. Please install pip or run the manual installation commands below.")
        except Exception as e:
            print(f"Installation failed: {e}")
            print("Please try the manual installation commands below.")
    else:
        print("Installation cancelled by user.")

    # Show manual installation instructions
    print("\nManual installation:")
    print("pip install -r requirements.txt")
    print("or pip3 install -r requirements.txt")
    print("or manually: pip install python-dotenv substrate-interface eth-account bip-utils PyNaCl")
    print("or manually: pip3 install python-dotenv substrate-interface eth-account bip-utils PyNaCl")
    sys.exit(1)

# Now safe to import
from substrateinterface import Keypair, KeypairType
from eth_account import Account
from bip_utils import Bip39SeedGenerator, Bip32Slip10Secp256k1
from nacl.secret import SecretBox

# SS58 format for Enjin Matrixchain
SS58_FORMAT = 1110



def load_mnemonic():
    """Ensure .env exists and contains MNEMONIC, then return it.

    Behavior:
    - If `.env` does not exist and `.env.example` exists, copy `.env.example` to `.env`.
    - If `.env` does not exist and no example exists, create a minimal `.env` template.
    - If `.env` exists but `MNEMONIC` is not set or empty, prompt the user to edit the file
      and confirm when ready.
    - Never print or log the mnemonic value.
    """
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    example_path = os.path.join(os.path.dirname(__file__), '.env.example')

    # If .env missing, try to create it from .env.example or a minimal template
    if not os.path.exists(env_path):
        if os.path.exists(example_path):
            try:
                import shutil
                shutil.copyfile(example_path, env_path)
                print('Created .env from .env.example. Please edit .env and add your MNEMONIC.')
            except Exception as e:
                print(f'Error creating .env from example: {e}')
                print('Please create a .env file with: MNEMONIC="your twelve word phrase here ..."')
        else:
            try:
                with open(env_path, 'w') as f:
                    f.write('MNEMONIC=""\n')
                print('Created .env template. Please edit .env and add your MNEMONIC.')
            except Exception as e:
                print(f'Error creating .env: {e}')
                print('Please create a .env file with: MNEMONIC="your twelve word phrase here ..."')

    # Loop until we have a non-empty MNEMONIC or the user aborts
    while True:
        load_dotenv(dotenv_path=env_path)
        mnemonic = os.getenv('MNEMONIC')
        if mnemonic and mnemonic.strip() != '':
            # Reminder: always ask user to confirm they want to proceed
            print('\nReminder: Your recovery phrase should be placed in the .env file as:')
            print('  MNEMONIC="your twelve word phrase here ..."')
            print('For maximum security, enter this on an offline machine and avoid sharing the file.')
            try:
                proceed = input('\nDo you want to continue and use the mnemonic from .env? (y/n): ').strip().lower()
            except KeyboardInterrupt:
                print('\nAborted by user.')
                sys.exit(1)

            if proceed == 'y':
                return mnemonic.strip()
            else:
                print('Aborting. Edit or remove .env as needed and run the script again when ready.')
                sys.exit(1)

        # .env exists but MNEMONIC empty
        print('\nMNEMONIC not found or empty in .env file.')
        print('  Please open .env and add your recovery phrase in the following form:')
        print('    MNEMONIC="your twelve word phrase here ..."')
        if ask_yes_no('\nHave you added your MNEMONIC to .env and want to continue? (y/n): ', default='n'):
            # reload and validate one more time; loop will re-check
            continue
        else:
            print('Aborting. Add your MNEMONIC to .env and run the script again when ready.')
            sys.exit(1)


def derive_ethereum(mnemonic):
    """Derive Ethereum address using standard BIP-44 path m/44'/60'/0'/0/0."""
    Account.enable_unaudited_hdwallet_features()
    return Account.from_mnemonic(mnemonic, account_path="m/44'/60'/0'/0/0")


def derive_matrixchain_sr25519(mnemonic):
    """Derive sr25519 Matrixchain keypair with blank derivation path."""
    return Keypair.create_from_uri(
        mnemonic,
        ss58_format=SS58_FORMAT,
        crypto_type=KeypairType.SR25519
    )


def derive_enjin_snap_ed25519(mnemonic):
    """
    Derive Enjin Snap ed25519 keypair replicating the snap's account.ts logic:

      BIP-39 seed → SLIP-10 secp256k1 at m/44'/1155' → 0x-prefixed hex →
      first 32 chars → UTF-8 encode → ed25519 seed

    Returns (keypair, seed_bytes) tuple.
    """
    # Step 1: Generate BIP-39 seed from mnemonic
    bip39_seed = Bip39SeedGenerator(mnemonic).Generate()

    # Step 2: Derive SLIP-10 secp256k1 key at m/44'/1155'
    bip32_node = Bip32Slip10Secp256k1.FromSeedAndPath(bip39_seed, "m/44'/1155'")

    # Step 3: Get 0x-prefixed hex private key (like MetaMask's key-tree)
    priv_key_hex = "0x" + bip32_node.PrivateKey().Raw().ToHex()

    # Step 4: .slice(0, 32) — first 32 characters of the hex string
    seed_str = priv_key_hex[:32]

    # Step 5: stringToU8a — convert to UTF-8 bytes (each ASCII char = 1 byte)
    seed_bytes = seed_str.encode('utf-8')

    # Step 6: Create ed25519 keypair from seed
    keypair = Keypair.create_from_seed(
        seed_bytes,
        ss58_format=SS58_FORMAT,
        crypto_type=KeypairType.ED25519
    )
    return keypair, seed_bytes


def build_keystore(keypair, seed_bytes, password):
    """
    Build a Polkadot-compatible encrypted JSON keystore.

    Uses scrypt (N=32768, p=1, r=8) + xsalsa20-poly1305, matching
    Polkadot.js defaults. The PKCS8 byte layout and JSON schema must
    stay compatible with Enjin Wallet's import parser.

    Returns keystore dict.
    """
    # PKCS8 encoding of ed25519 keypair
    # Header: SEQUENCE, INTEGER(version=1), AlgorithmIdentifier(ed25519 OID),
    #         OCTET STRING wrapping the secret key
    pkcs8_header = bytes([
        0x30, 0x53, 0x02, 0x01, 0x01, 0x30, 0x05, 0x06,
        0x03, 0x2b, 0x65, 0x70, 0x04, 0x22, 0x04, 0x20
    ])
    pkcs8_divider = bytes([0xa1, 0x23, 0x03, 0x21, 0x00])
    plaintext = pkcs8_header + seed_bytes + pkcs8_divider + keypair.public_key

    # Scrypt parameters (matching Polkadot.js defaults — do not change)
    scrypt_n = 1 << 15  # 32768
    scrypt_p = 1
    scrypt_r = 8
    salt = os.urandom(32)

    # Derive encryption key via scrypt
    # Uses hashlib.scrypt (stdlib) if available, otherwise PyNaCl's scrypt
    password_bytes = password.encode('utf-8')
    try:
        key = hashlib.scrypt(
            password_bytes, salt=salt, n=scrypt_n, r=scrypt_r, p=scrypt_p, dklen=32
        )
    except AttributeError:
        # Fallback to PyNaCl's scrypt implementation
        from nacl.pwhash import scrypt
        # Calculate memlimit: 128 * N * r bytes
        memlimit = 128 * scrypt_n * scrypt_r
        key = scrypt.kdf(32, password_bytes, salt, opslimit=scrypt_n, memlimit=memlimit)

    # Encrypt with xsalsa20-poly1305
    nonce = os.urandom(24)
    box = SecretBox(key)
    encrypted = box.encrypt(plaintext, nonce)[24:]  # strip prepended nonce

    # Build the encoded blob: salt + N(LE) + p(LE) + r(LE) + nonce + ciphertext
    encoded_bytes = (
        salt
        + struct.pack('<I', scrypt_n)
        + struct.pack('<I', scrypt_p)
        + struct.pack('<I', scrypt_r)
        + nonce
        + encrypted
    )
    encoded_b64 = base64.b64encode(encoded_bytes).decode('ascii')

    return {
        "encoded": encoded_b64,
        "encoding": {
            "content": ["pkcs8", "ed25519"],
            "type": ["scrypt", "xsalsa20-poly1305"],
            "version": "3"
        },
        "address": keypair.ss58_address,
        "meta": {
            "name": "Enjin Snap",
            "whenCreated": int(time.time() * 1000)
        }
    }


def build_web3_keystore(private_key_hex, password):
    """
    Build a Web3 / Ethereum v3 keystore JSON using eth-account's helper.

    Returns a dict conforming to the Web3 Secret Storage Definition (version 3).
    """
    # eth_account.Account.encrypt will produce the correct v3 JSON structure
    # using the default KDF (scrypt/pbkdf2 depending on implementation). It
    # preserves the expected fields: address, id, version, crypto { cipher,... }.
    return Account.encrypt(private_key_hex, password)


def export_keystore(keypair, seed_bytes):
    """Prompt user and export encrypted keystore JSON file."""
    print("Generate JSON keystore file for Enjin Wallet import?")
    if not ask_yes_no("  Export keystore? (y/n): ", default='n'):
        return

    password = get_password_confirm()

    # Which keystore format to produce — numeric menu (1 = Ethereum v3 default, 2 = Polkadot-style)
    print("  Keystore format:")
    print("    1) Ethereum v3 (Web3) — supported by Enjin Wallet and compatible with Ethereum wallets (default)")
    print("    2) Polkadot-style (scrypt + xsalsa20-poly1305)")
    choice = ask_choice("  Select format [1]: ", ['1', '2'], default='1')

    fmt = 'web3' if choice == '1' else 'polkadot'

    if fmt == 'web3':
        # Build Ethereum v3 keystore from the seed bytes (private key hex)
        private_key_hex = '0x' + seed_bytes.hex()
        try:
            keystore = build_web3_keystore(private_key_hex, password)
        except Exception as e:
            print(f"  Error building Web3 keystore: {e}")
            return
        ts = int(time.time())
        filename = f"enjin-snap-keystore-web3-{keystore.get('address','unknown')[:8]}-{ts}.json"
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

        with open(filepath, 'w') as f:
            json.dump(keystore, f, indent=2)

        print(f"\n  Web3 keystore saved to: {filename}")
        print(f"  Address: {keystore.get('address')}")
        print(f"  Format: Web3 secret storage (v3)")
        print("\n  Import this into Enjin Wallet via:")
        print("    Settings > Wallets > Add Wallet > Import Wallet > Import Keystore")
        print("    Copy the content of the exported file and paste in the 'Import Keystore' field.")
        print("    Input the password in the 'Encryption Password' field.")
        return

    # Default: Polkadot-style keystore for Enjin Wallet
    keystore = build_keystore(keypair, seed_bytes, password)
    ts = int(time.time())
    filename = f"enjin-snap-keystore-{keypair.ss58_address[:8]}-{ts}.json"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(filepath, 'w') as f:
        json.dump(keystore, f, indent=2)

    print(f"\n  Keystore saved to: {filename}")
    print(f"  Address: {keypair.ss58_address}")
    print(f"  Encoding: scrypt + xsalsa20-poly1305 (ed25519)")
    print("\n  Note: Enjin Wallet currently does not support importing Polkadot-style keystore files.")
    print("  You may try importing this file into Ethereum-compatible wallets, but compatibility is not guaranteed.")


def main():
    """Main entry point — derive addresses and optionally export keystore."""
    # Suppress urllib3 OpenSSL warnings
    warnings.filterwarnings("ignore", category=UserWarning)

    mnemonic = load_mnemonic()

    print("=" * 60)

    # 1. Ethereum address
    try:
        eth_account = derive_ethereum(mnemonic)
        print(f"Ethereum (m/44'/60'/0'/0/0):\n  {eth_account.address}")
    except Exception as e:
        print(f"Error generating Ethereum address: {e}")

    print("-" * 60)

    # 2. sr25519 Matrixchain address
    try:
        sr25519_kp = derive_matrixchain_sr25519(mnemonic)
        print(f"Matrixchain sr25519 (blank derivation):\n  {sr25519_kp.ss58_address}")
    except Exception as e:
        print(f"Error generating sr25519 address: {e}")

    print("-" * 60)

    # 3. Enjin Snap ed25519 address + exports
    try:
        snap_keypair, seed_bytes = derive_enjin_snap_ed25519(mnemonic)
        print(f"Enjin Snap ed25519 (m/44'/1155' seed logic):\n  {snap_keypair.ss58_address}")
        print(f"  Public key: 0x{snap_keypair.public_key.hex()}")

        print("-" * 60)

        # Private key (hex)
        private_key_hex = "0x" + seed_bytes.hex()
        print(f"Private key (hex seed) for wallet import:\n  {private_key_hex}")

        print("-" * 60)

        # Keystore export
        export_keystore(snap_keypair, seed_bytes)
    except Exception as e:
        print(f"Error generating Enjin Snap address: {e}")

    print("=" * 60)


if __name__ == "__main__":
    main()
