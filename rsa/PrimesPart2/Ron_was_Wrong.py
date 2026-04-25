
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util import number
import math
import os

# =============================================================================
# CRYPTOHACK CHALLENGE: "Ron was Wrong, Whit is Right"
# Attack: Common-factor RSA attack (based on the famous 2012 paper)
# =============================================================================

# Folder containing the 50 public keys and ciphertexts (extract keys_and_messages.zip)
DATA_DIR = "keys_and_messages"

# Store all moduli, ciphertexts (as integers), and public exponents
moduli = []
ciphertexts = []
exponents = []

print("[+] Loading 50 RSA public keys and ciphertexts...")

for i in range(1, 51):
    # Load public key from .pem
    with open(f"{DATA_DIR}/{i}.pem", "r") as f:
        key = RSA.import_key(f.read())
    
    # Load ciphertext (hex string) and convert to integer
    with open(f"{DATA_DIR}/{i}.ciphertext", "r") as f:
        ct_hex = f.read().strip()
        ct_int = number.bytes_to_long(bytes.fromhex(ct_hex))
    
    moduli.append(key.n)
    ciphertexts.append(ct_int)
    exponents.append(key.e)
    
    print(f"    Loaded key {i:2d} | n-bits: {key.n.bit_length():4d} | e = {key.e}")

print(f"[+] Loaded {len(moduli)} keys successfully.\n")

# =============================================================================
# MAIN ATTACK: Pairwise GCD to find shared prime factors
# Theory (from "Ron was Wrong, Whit is Right" paper):
#   Many real-world RSA keys were generated with poor randomness.
#   This causes different public keys to share the exact same prime factor p.
#   If GCD(n_i, n_j) = p > 1, then we instantly factor both n_i and n_j.
# =============================================================================

print("[+] Searching for shared prime factors via pairwise GCD...")

found = False
for i in range(len(moduli)):
    for j in range(i + 1, len(moduli)):
        g = math.gcd(moduli[i], moduli[j])
        if g > 1:
            print(f"\n[!] Shared factor found between key {i+1} and key {j+1}!")
            print(f"    GCD = {g} (bit length: {g.bit_length()})")
            
            # We can decrypt using either key (here we use key i)
            n = moduli[i]
            p = g
            q = n // p
            e = exponents[i]
            phi = (p - 1) * (q - 1)
            
            # Compute private exponent d = e^(-1) mod phi
            d = number.inverse(e, phi)
            
            # Reconstruct private RSA key
            priv_key = RSA.construct((n, e, d))
            
            # Decrypt using PKCS#1 OAEP
            cipher = PKCS1_OAEP.new(priv_key)
            plaintext = cipher.decrypt(number.long_to_bytes(ciphertexts[i]))
            
            print(f"\n[+] DECRYPTED MESSAGE (key {i+1}):")
            print(plaintext)
            print(f"\n[+] FLAG FOUND: {plaintext.decode(errors='ignore')}")
            
            found = True
            break
    if found:
        break

if not found:
    print("[-] No shared factors found. All keys appear strong.")