from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Step 1: Read and import the public key from the provided PEM file
# This gives us access to the public modulus (n) and public exponent (e)
f = open('key_pem.pem', 'rb')
key = RSA.import_key(f.read())

# Step 2: Define the prime factors p and q
# These were likely obtained by factoring the weak modulus 'n' (e.g., via FactorDB)
p = 51894141255108267693828471848483688186015845988173648228318286999011443419469
q = 77342270837753916396402614215980760127245056504361515489809293852222206596161

# Step 3: Calculate Euler's totient function phi(n)
phi = (p - 1) * (q - 1)

# Step 4: Load and decode the ciphertext from hex to raw bytes
c = "249d72cd1d287b1a15a3881f2bff5788bc4bf62c789f2df44d88aae805b54c9a94b8944c0ba798f70062b66160fee312b98879f1dd5d17b33095feb3c5830d28"
c = bytes.fromhex(c)

# Step 5: Calculate the private exponent d (modular multiplicative inverse)
d = pow(key.e, -1, phi)

# Step 6: Reconstruct the full RSA private key using (n, e, d)
key = RSA.construct((key.n, key.e, d))
print(key)

# Step 7: Initialize the cipher with PKCS1_OAEP padding scheme
cipher = PKCS1_OAEP.new(key)
print(cipher)

# Step 8: Decrypt the ciphertext to retrieve the original plaintext/flag
plaintext = cipher.decrypt(c)
print(plaintext)