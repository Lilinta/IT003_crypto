#!/usr/bin/env python3
"""
CryptoHack - Diffie-Hellman / Group Theory / Static Client 2

Ý tưởng:
1) Đọc thông số DH gốc từ server: p, g, A, B, iv, ciphertext.
2) Tạo một mô-đun p' sao cho p' - 1 là smooth để discrete log dễ giải.
3) Gửi cho Bob (p', g'=2, A'=A) để Bob trả về B' = 2^b mod p'.
4) Dùng discrete_log để tìm b.
5) Tính shared secret thật: s = A^b mod p.
6) Dẫn xuất AES key bằng SHA1(str(s))[:16] và giải mã CBC.
"""

import json
import hashlib

from pwn import remote
from sympy import isprime
from sympy.ntheory.residue_ntheory import discrete_log
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


HOST = "socket.cryptohack.org"
PORT = 13378


def recv_json(r) -> dict:
    """
    Đọc một dòng JSON từ socket và chuyển thành dict.
    """
    line = r.recvline().decode().strip()
    return json.loads(line)


def send_json(r, obj: dict) -> None:
    """
    Gửi JSON qua socket.
    """
    r.sendline(json.dumps(obj).encode())


def derive_aes_key(shared_secret: int) -> bytes:
    """
    Dẫn xuất key AES-128 từ shared secret:
    key = SHA1(str(shared_secret))[:16]
    """
    sha1 = hashlib.sha1()
    sha1.update(str(shared_secret).encode("ascii"))
    return sha1.digest()[:16]


def decrypt_flag(shared_secret: int, iv_hex: str, ciphertext_hex: str) -> str:
    """
    Giải mã AES-CBC và bỏ padding PKCS#7.
    """
    key = derive_aes_key(shared_secret)
    iv = bytes.fromhex(iv_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext_padded = cipher.decrypt(ciphertext)
    plaintext = unpad(plaintext_padded, AES.block_size)
    return plaintext.decode("ascii")


def build_smooth_prime(min_bits: int) -> int:
    """
    Tạo một prime p' sao cho p' - 1 rất smooth.

    Cách làm:
    - Nhân dần các số tự nhiên 2, 3, 4, ...
    - Thử xem mul + 1 có phải prime không và đã đủ bit-length chưa.
    - Khi thỏa điều kiện thì trả về p' = mul + 1.

    Điều này làm cho nhóm modulo p' có bậc smooth, giúp discrete log
    có thể giải bằng Pohlig–Hellman.
    """
    smooth_part = 1
    i = 2

    while True:
        smooth_part *= i
        candidate = smooth_part + 1

        if candidate.bit_length() >= min_bits and isprime(candidate):
            return candidate

        i += 1


def main():
    r = remote(HOST, PORT)

    # Nhận dữ liệu từ Alice
    r.recvuntil(b"Intercepted from Alice: ")
    alice = recv_json(r)
    p = int(alice["p"], 16)
    g = int(alice["g"], 16)
    A = int(alice["A"], 16)

    # Nhận dữ liệu từ Bob
    r.recvuntil(b"Intercepted from Bob: ")
    bob = recv_json(r)
    _B = int(bob["B"], 16)  # không dùng trực tiếp

    # Nhận ciphertext từ Alice
    r.recvuntil(b"Intercepted from Alice: ")
    enc = recv_json(r)
    iv_hex = enc["iv"]
    ciphertext_hex = enc["encrypted"]

    # Tạo mô-đun mới p' sao cho p' - 1 smooth
    p_prime = build_smooth_prime(p.bit_length())

    # Gửi tham số cho Bob:
    # - p' : mô-đun mới có bậc smooth
    # - g  : chọn 2 để discrete log dễ giải
    # - A  : giữ nguyên A để cuối cùng tính shared secret thật trên p gốc
    r.recvuntil(b"send him some parameters: ")
    send_json(r, {
        "p": hex(p_prime),
        "g": hex(2),
        "A": hex(A),
    })

    # Bob trả về B' = 2^b mod p'
    r.recvuntil(b"Bob says to you: ")
    bob_reply = recv_json(r)
    B_prime = int(bob_reply["B"], 16)

    # Giải discrete log để lấy b
    b = discrete_log(p_prime, B_prime, 2)

    # Tính shared secret thật của phiên gốc
    shared_secret = pow(A, b, p)

    # Giải mã flag
    flag = decrypt_flag(shared_secret, iv_hex, ciphertext_hex)
    print(flag)


if __name__ == "__main__":
    main()
