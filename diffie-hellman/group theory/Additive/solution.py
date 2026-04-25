#!/usr/bin/env python3
"""
CryptoHack - Diffie-Hellman / Group Theory / Additive

Ý tưởng:
1) Đọc p, g, A, B, iv, encrypted_flag từ server.
2) Vì DH nằm trong nhóm cộng:
      A = g * a mod p
      B = g * b mod p
   nên shared secret là:
      s = A * B * inverse(g, p) mod p
3) Dẫn xuất AES key bằng SHA1(str(s))[:16]
4) Giải mã AES-CBC để lấy flag.
"""

import json
import hashlib

from pwn import remote
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.number import inverse

HOST = "socket.cryptohack.org"
PORT = 13380


def decrypt_flag(shared_secret: int, iv_hex: str, ciphertext_hex: str) -> str:
    """
    Dẫn xuất key AES-128 từ shared_secret và giải mã ciphertext CBC.
    """
    sha1 = hashlib.sha1()
    sha1.update(str(shared_secret).encode("ascii"))
    key = sha1.digest()[:16]

    iv = bytes.fromhex(iv_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext_padded = cipher.decrypt(ciphertext)
    plaintext = unpad(plaintext_padded, AES.block_size)
    return plaintext.decode("ascii")


def recv_json_line(r) -> dict:
    """
    Đọc một dòng JSON từ socket và chuyển thành dict.
    Hàm này đủ linh hoạt cho các thông điệp dạng '... {json} ...'.
    """
    line = r.recvline().decode().strip()
    start = line.find("{")
    end = line.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Không tìm thấy JSON hợp lệ trong dòng: {line}")
    return json.loads(line[start:end + 1])


def main():
    r = remote(HOST, PORT)

    # Nhận thông số từ Alice
    # Tùy server, chuỗi nhắc có thể hơi khác nhau, nhưng nội dung JSON là đủ.
    r.recvuntil(b"Intercepted from Alice: ")
    alice_msg = recv_json_line(r)
    p = int(alice_msg["p"], 16)
    g = int(alice_msg["g"], 16)
    A = int(alice_msg["A"], 16)

    # Nhận thông số từ Bob
    r.recvuntil(b"Intercepted from Bob: ")
    bob_msg = recv_json_line(r)
    B = int(bob_msg["B"], 16)

    # Nhận ciphertext từ Alice
    r.recvuntil(b"Intercepted from Alice: ")
    flag_msg = recv_json_line(r)
    iv_hex = flag_msg["iv"]
    ciphertext_hex = flag_msg["encrypted"]

    # Shared secret trong nhóm cộng:
    # s = A * B * g^{-1} mod p
    shared_secret = (A * B * inverse(g, p)) % p

    flag = decrypt_flag(shared_secret, iv_hex, ciphertext_hex)
    print(flag)


if __name__ == "__main__":
    main()
