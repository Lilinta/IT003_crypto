import socket
import json
import hashlib
from Crypto.Cipher import AES
from sympy.ntheory import discrete_log

def decrypt_flag(shared_secret, iv_hex, ciphertext_hex):
    key = hashlib.sha1(str(shared_secret).encode('ascii')).digest()[:16]
    iv = bytes.fromhex(iv_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(ciphertext)

print("[*] Đang kết nối tới server...")
# Dùng socket thuần kết hợp makefile để tạo buffer cực kỳ ổn định trên Windows
s = socket.create_connection(('socket.cryptohack.org', 13379))
f = s.makefile('r', encoding='utf-8') 

def send_json(data):
    # Gửi thẳng dữ liệu, không cần chờ server hỏi
    s.sendall((json.dumps(data) + '\n').encode('utf-8'))

def get_json(prefix):
    # Chỉ lùng sục dòng nào có chứa dữ liệu JSON (bỏ qua các dòng rác)
    while True:
        line = f.readline()
        if not line:
            raise ConnectionError("Server ngắt kết nối đột ngột! Hãy chạy lại script.")
        if prefix in line:
            return json.loads(line.split(prefix)[1].strip())

print("[*] Đang đánh chặn và hạ cấp tham số xuống DH64...")

# 1. Chặn Alice -> Ép Bob dùng cấu hình yếu nhất
get_json("Intercepted from Alice: ")
send_json({"supported": ["DH64"]})

# 2. Chặn Bob -> Phản hồi lại Alice
msg_bob = get_json("Intercepted from Bob: ")
send_json(msg_bob)

# 3. Lấy p, g, A của Alice
alice_dh = get_json("Intercepted from Alice: ")
p = int(alice_dh['p'], 16)
g = int(alice_dh['g'], 16)
A = int(alice_dh['A'], 16)
send_json(alice_dh)

# 4. Lấy B của Bob
bob_dh = get_json("Intercepted from Bob: ")
B = int(bob_dh['B'], 16)
send_json(bob_dh)

# 5. Lấy Flag bị mã hóa
flag_msg = get_json("Intercepted from Alice: ")

print("[*] Đã thu thập đủ dữ liệu!")
print("[*] Đang giải mã Logarit rời rạc (chờ khoảng 2-5 giây)...")
a = discrete_log(p, A, g)
shared_secret = pow(B, a, p)

print("[*] Đang giải mã AES...")
flag = decrypt_flag(shared_secret, flag_msg['iv'], flag_msg['encrypted_flag'])
print(f"\n[+] Flag tìm được: {flag.decode(errors='ignore').strip()}")

s.close()