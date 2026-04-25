import os
import re
import hashlib
from pwn import remote
import json
from Crypto.Util.number import long_to_bytes, bytes_to_long
from pkcs1 import emsa_pkcs1_v15

from sympy import factorint

from sympy import nextprime as next_prime, isprime as is_prime, discrete_log
from sympy.ntheory.modular import crt as sympy_crt
from math import gcd

# Giả lập lại hàm crt của SageMath
def crt(remainders, moduli):
    return int(sympy_crt(moduli, remainders)[0])

# Giả lập lại Zmod của SageMath
def Zmod(n):
    return lambda x: x % n

# --- Hàm hỗ trợ tạo địa chỉ BTC hợp lệ ---
def make_btc(prefix=b"1"):
    alpha = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    raw = b"\0" + os.urandom(20)
    checksum = hashlib.sha256(hashlib.sha256(raw).digest()).digest()[:4]
    raw += checksum
    res = bytes_to_long(raw)
    addr = b""
    while res > 0:
        res, mod = divmod(res, 58)
        addr = bytes([alpha[mod]]) + addr
    for c in raw:
        if c == 0: addr = b"1" + addr
        else: break
    return addr.decode()

# --- Kết nối và lấy thông tin ---
io = remote('socket.cryptohack.org', 13394)
io.recvline()

io.sendline(json.dumps({"option": "get_signature"}).encode())
data = json.loads(io.recvline())
S = int(data['signature'], 16)

# --- Sinh 2 số nguyên tố mượt ---
print("[+] Generating smooth primes p and q...")

def gen_smooth_prime(S, start_prime):
    base = 2
    pr = start_prime
    # Rút ngắn độ dài xuống 384 bit để N đạt 768 bit
    while base.bit_length() < 384:
        base *= pr
        pr = next_prime(pr)
        
    k = 1
    while True:
        p = k * base + 1
        if is_prime(p):
            # KIỂM TRA CĂN NGUYÊN THỦY: Đảm bảo S có thể sinh ra mọi D
            factors = list(factorint(p - 1).keys())
            is_primitive = True
            for f in factors:
                if pow(S, (p - 1) // f, p) == 1:
                    is_primitive = False
                    break
            
            if is_primitive:
                return p, pr
        k += 1

print("[+] Generating optimal smooth primes p and q...")
p, next_pr = gen_smooth_prime(S, 3)
q, _ = gen_smooth_prime(S, next_pr)

n = p * q
print(f"[+] Sending pubkey n = p * q")
io.sendline(json.dumps({"option": "set_pubkey", "pubkey": hex(n)}).encode())
suffix = json.loads(io.recvline())['suffix']

# --- Khởi tạo và xử lý từng Pattern ---
shares = []
patterns_templates = [
    lambda i: f"This is a test {i} for a fake signature.",
    # Lặp chữ 'a' thay vì dùng số nguyên i để khớp regex chữ cái
    lambda i: f"My name is Jack {'a' * i} and I own CryptoHack.org",
    # Thêm đúng tiền tố regex yêu cầu
    lambda i: f"Please send all my money to {make_btc()}"
]

Zp, Zq = Zmod(p), Zmod(q)
Sp, Sq = Zp(S), Zq(S)

for idx in range(3):
    print(f"\n[+] Processing index {idx}")
    attempt = 0
    while True:
        msg_base = patterns_templates[idx](attempt)
        msg = msg_base + suffix
        D = bytes_to_long(emsa_pkcs1_v15.encode(msg.encode(), 96))
        
        Dp, Dq = D % p, D % q
        
        try:
            ep = discrete_log(p, Dp, Sp)
            eq = discrete_log(q, Dq, Sq)
            
            res = sympy_crt([p - 1, q - 1], [ep, eq])
            if res is not None:
                e = int(res[0])
                print(f"[+] Found valid e for index {idx} on attempt {attempt}!")
                
                io.sendline(json.dumps({
                    "option": "claim",
                    "msg": msg,
                    "e": hex(e),
                    "index": idx
                }).encode())
                
                server_res = json.loads(io.recvline())
                if 'secret' in server_res:
                    shares.append(bytes.fromhex(server_res['secret']))
                    print(f"[+] Got secret for index {idx}!")
                    break
                else:
                    # Ném ra log nếu server báo lỗi hoặc chối từ
                    print(f"[-] Server rejected msg (Regex fail): {server_res}")
                    break # Break luôn để khỏi lặp vô tận, sửa lại template rồi chạy
        except ValueError:
            # Chỉ bỏ qua lỗi tính Logarit (ValueError)
            pass
        
        attempt += 1
# --- Khôi phục Flag ---
def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

flag = shares[0]
for s in shares[1:]:
    flag = xor(flag, s)

print(f"\n[!] FLAG: {flag.decode()}")