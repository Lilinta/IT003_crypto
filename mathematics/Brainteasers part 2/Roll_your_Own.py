from pwn import *
import json

# Kết nối tới server CryptoHack
r = remote('socket.cryptohack.org', 13403)

def get_clean_int(prompt_trigger):
    """Hàm phụ trợ để nhận dữ liệu, làm sạch dấu ngoặc kép và chuyển sang int"""
    r.recvuntil(prompt_trigger.encode() if isinstance(prompt_trigger, str) else prompt_trigger)
    # Nhận dòng, decode, loại bỏ khoảng trắng và dấu ngoặc kép dư thừa
    raw_data = r.recvline().decode().strip().strip('"').strip("'")
    return int(raw_data, 16)

# 1. Nhận giá trị q (Prime) từ server
try:
    q = get_clean_int("Prime generated: ")
    print(f"[+] Received q: {q}")

    # 2. Thiết lập thông số n và g theo trick n = q^2
    # Điều này biến bài toán Discrete Log thành phép chia đơn giản
    n = q * q
    g = q + 1

    # Gửi g và n dưới dạng JSON
    payload = {
        "g": hex(g),
        "n": hex(n)
    }
    print(f"[*] Sending g and n...")
    r.sendlineafter(b"Send integers (g,n) such that pow(g,q,n) = 1: ", json.dumps(payload).encode())

    # 3. Nhận Public Key h từ server
    h = get_clean_int("Generated my public key: ")
    print(f"[+] Received h: {h}")

    # 4. Tính toán secret x
    # Với g = q + 1 và n = q^2, ta có h = (q+1)^x = 1 + xq (mod q^2)
    # Do đó x = (h - 1) // q
    x = (h - 1) // q
    print(f"[+] Calculated secret x: {x}")

    # 5. Gửi x để lấy flag
    secret_payload = {"x": hex(x)}
    r.sendlineafter(b"What is my private key: ", json.dumps(secret_payload).encode())

    # Nhận và in flag
    print("\n[!] Result from server:")
    print(r.recvall().decode())

except Exception as e:
    print(f"[!] Error: {e}")
finally:
    r.close()