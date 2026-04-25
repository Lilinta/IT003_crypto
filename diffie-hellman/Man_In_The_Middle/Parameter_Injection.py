from pwn import remote
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# 1. Kết nối tới server
r = remote('socket.cryptohack.org', 13371)

def decrypt_flag(shared_secret, iv_hex, ciphertext_hex):
    # Hash shared secret thành key 16 bytes (chuẩn của CryptoHack)
    key = hashlib.sha1(str(shared_secret).encode('ascii')).digest()[:16]
    iv = bytes.fromhex(iv_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(ciphertext) # Thêm unpad nếu cần

# 2. Chặn tin nhắn từ Alice, lấy p
r.recvuntil(b"Intercepted from Alice: ")
alice_msg = json.loads(r.recvline().decode())
p = alice_msg['p']

# 3. Gửi public key giả (A = p) cho Bob
r.recvuntil(b"Send to Bob: ")
malicious_alice_msg = {"p": p, "g": alice_msg['g'], "A": p}
r.sendline(json.dumps(malicious_alice_msg).encode())

# 4. Chặn tin nhắn từ Bob (bỏ qua public key B thật)
r.recvuntil(b"Intercepted from Bob: ")
r.recvline() 

# 5. Gửi public key giả (B = p) cho Alice
r.recvuntil(b"Send to Alice: ")
malicious_bob_msg = {"B": p}
r.sendline(json.dumps(malicious_bob_msg).encode())

# 6. Chặn flag đã mã hóa từ Alice
r.recvuntil(b"Intercepted from Alice: ")
flag_msg = json.loads(r.recvline().decode())

# 7. Giải mã với shared_secret = 0
flag = decrypt_flag(0, flag_msg['iv'], flag_msg['encrypted_flag'])
print(f"\n[+] Flag: {flag.decode()}")