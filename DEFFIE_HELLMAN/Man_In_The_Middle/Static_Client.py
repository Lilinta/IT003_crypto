import socket
import json
import hashlib
from Crypto.Cipher import AES

def decrypt_flag(shared_secret, iv_hex, ciphertext_hex):
    key = hashlib.sha1(str(shared_secret).encode('ascii')).digest()[:16]
    iv = bytes.fromhex(iv_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(ciphertext)

print("[*] Đang kết nối tới server...")
s = socket.create_connection(('socket.cryptohack.org', 13373))
f = s.makefile('r', encoding='utf-8') 

def send_json(data):
    s.sendall((json.dumps(data) + '\n').encode('utf-8'))

def get_json():
    # Tự động tìm và bóc tách JSON, bất chấp server hiển thị prompt gì
    while True:
        line = f.readline()
        if not line:
            raise ConnectionError("Server ngắt kết nối!")
        if "{" in line:
            return json.loads(line[line.find("{"):])

print("[*] Đang thu thập dữ liệu...")
p_str = A_str = iv_hex = ciphertext_hex = None

# Đọc 3 gói tin trao đổi đầu tiên của Alice và Bob
for _ in range(3):
    data = get_json()
    if "p" in data and "A" in data:
        p_str = data["p"]
        A_str = data["A"]
    elif "iv" in data:
        iv_hex = data["iv"]
        # Bắt lỗi đổi tên key của CryptoHack (có thể là 'encrypted_flag' hoặc 'encrypted')
        ciphertext_hex = data.get("encrypted_flag", data.get("encrypted"))

print("[*] Đang lừa Bob để lấy Shared Secret...")
# 4. Tiêm tham số giả cho Bob (g = A)
send_json({
    "p": p_str,
    "g": A_str,  # Mấu chốt: Thay generator bằng Public Key A của Alice
    "A": "0x2"   # Key của mình để là gì cũng được
})

# 5. Bob trả về B' (chính là Shared Secret)
bob_reply = get_json()
shared_secret = int(bob_reply['B'], 16)

print("[*] Đang giải mã...")
flag = decrypt_flag(shared_secret, iv_hex, ciphertext_hex)
print(f"\n[+] Flag tìm được: {flag.decode(errors='ignore').strip()}")

s.close()