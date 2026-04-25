import socket
import json
import hashlib
from Crypto.Util.number import bytes_to_long

print("[*] Đang kết nối tới server...")
s = socket.create_connection(('socket.cryptohack.org', 13391))
f = s.makefile('r', encoding='utf-8')

def send_json(data):
    # Nén file JSON (xóa khoảng trắng thừa) để đảm bảo dung lượng luôn < 1024 bytes
    payload = json.dumps(data, separators=(',', ':'))
    s.sendall((payload + '\n').encode('utf-8'))

def get_json():
    while True:
        line = f.readline()
        if not line:
            raise ConnectionError("Server ngắt kết nối!")
        if "{" in line:
            return json.loads(line[line.find("{"):])

# Đọc và bỏ qua dòng chào mừng
f.readline()

print("[*] 1. Xin chữ ký gốc của server...")
send_json({"option": "get_signature"})
data = get_json()
signature = int(data['signature'], 16)

# Tinh chỉnh lại chuỗi để khớp 100% với mẫu chuẩn của CryptoHack
target_msg = "I am Mallory and I own CryptoHack.org"
print(f"[*] 2. Bắt đầu giả mạo với thông điệp: '{target_msg}'")

# Danh sách toàn bộ các chuẩn Hash và ASN.1 Prefix để tự động thử
hash_configs = [
    ("SHA-256 (Chuẩn)", hashlib.sha256, b'\x30\x31\x30\x0d\x06\x09\x60\x86\x48\x01\x65\x03\x04\x02\x01\x05\x00\x04\x20'),
    ("SHA-256 (Không NULL)", hashlib.sha256, b'\x30\x2f\x30\x0b\x06\x09\x60\x86\x48\x01\x65\x03\x04\x02\x01\x04\x20'),
    ("SHA-512", hashlib.sha512, b'\x30\x51\x30\x0d\x06\x09\x60\x86\x48\x01\x65\x03\x04\x02\x03\x05\x00\x04\x40'),
    ("SHA-1", hashlib.sha1, b'\x30\x21\x30\x09\x06\x05\x2b\x0e\x03\x02\x1a\x05\x00\x04\x14'),
    ("MD5", hashlib.md5, b'\x30\x20\x30\x0c\x06\x08\x2a\x86\x48\x86\xf7\x0d\x02\x05\x05\x00\x04\x10'),
    ("Raw (Bỏ qua ASN.1)", hashlib.sha256, b'')
]

print("[*] 3. Đang tự động quét và thử các chuẩn đệm...")
for name, hash_func, prefix in hash_configs:
    print(f"    [*] Đang thử chuẩn: {name}...")
    
    # Tạo đệm PKCS#1 v1.5 tương ứng với thuật toán hiện tại
    h = hash_func(target_msg.encode()).digest()
    T = prefix + h
    em_len = 256
    ps = b'\xff' * (em_len - len(T) - 3)
    digest_bytes = b'\x00\x01' + ps + b'\x00' + T
    
    digest_int = bytes_to_long(digest_bytes)
    
    # Luôn dùng e = 1 để tránh lỗi vượt quá 1024 bytes của server
    fake_e = 1
    fake_n = signature - digest_int
    
    if fake_n <= 0:
        print("        -> Bỏ qua (N bị âm)")
        continue
        
    send_json({
        "option": "verify",
        "msg": target_msg,
        "N": hex(fake_n),
        "e": hex(fake_e)
    })
    
    result = get_json()
    if "error" not in result or result["error"] != "Invalid signature":
        print(f"\n[+] Flag tìm được (Khớp chuẩn {name}):\n{result.get('msg', result)}")
        break
    else:
        print("        -> Thất bại (Chữ ký không khớp)")

s.close()