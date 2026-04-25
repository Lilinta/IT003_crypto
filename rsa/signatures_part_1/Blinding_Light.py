import socket
import json
from Crypto.Util.number import bytes_to_long, inverse

def send_json(s, data):
    s.sendall((json.dumps(data) + '\n').encode())

def recv_json(f):
    while True:
        line = f.readline()
        if not line: return None
        if '{' in line:
            return json.loads(line[line.find('{'):])

print("[*] Đang kết nối tới server...")
s = socket.create_connection(('socket.cryptohack.org', 13376))
f = s.makefile('r', encoding='utf-8')

# 1. Lấy Public Key
print("[*] Đang lấy Public Key...")
send_json(s, {"option": "get_pubkey"})
pubkey = recv_json(f)
N = int(pubkey['N'], 16)
E = int(pubkey['e'], 16)

# 2. Chuẩn bị thông điệp Admin và "Làm mù" (Blinding)
ADMIN_TOKEN = b"admin=True"
m = bytes_to_long(ADMIN_TOKEN)
r = 2 # Số ngẫu nhiên để làm mù
# m_blind = (m * r^e) mod N
m_blind = (m * pow(r, E, N)) % N

print(f"[*] Đang yêu cầu ký thông điệp đã làm mù...")
send_json(s, {"option": "sign", "msg": hex(m_blind)[2:]})
res = recv_json(f)
s_prime = int(res['signature'], 16)

# 3. Loại bỏ lớp mù để lấy chữ ký thật
# s = (s_prime * r^-1) mod N
s_real = (s_prime * inverse(r, N)) % N

print("[*] Đang gửi chữ ký giả mạo để lấy Flag...")
send_json(s, {
    "option": "verify",
    "msg": ADMIN_TOKEN.hex(),
    "signature": hex(s_real)
})

result = recv_json(f)
print(f"\n[+] Kết quả: {result.get('response', result)}")

s.close()