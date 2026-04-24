#!/usr/bin/env python3
"""
Giải challenge Inferius Prime của CryptoHack.

Ý tưởng:
1) Dùng p, q đã factor được từ n.
2) Tính phi(n) = (p - 1)(q - 1)
3) Tính d = e^{-1} mod phi(n)
4) Giải mã ct bằng m = ct^d mod n
5) Đổi số nguyên sang bytes để lấy flag
"""

from math import gcd


def long_to_bytes(n: int) -> bytes:
    """Chuyển số nguyên lớn thành chuỗi bytes."""
    if n == 0:
        return b"\x00"
    out = []
    while n > 0:
        out.append(n & 0xFF)
        n >>= 8
    return bytes(reversed(out))


def main():
    # Public values từ đề bài
    n = 984994081290620368062168960884976209711107645166770780785733
    e = 65537
    ct = 948553474947320504624302879933619818331484350431616834086273

    # p, q thu được sau khi factor n
    p = 848445505077945374527983649411
    q = 1160939713152385063689030212503

    # Kiểm tra lại n = p*q
    assert n == p * q

    # Tính phi(n)
    phi = (p - 1) * (q - 1)

    # Tính khóa bí mật d
    assert gcd(e, phi) == 1
    d = pow(e, -1, phi)

    # Giải mã ciphertext
    pt = pow(ct, d, n)

    # Đổi về bytes và in ra
    flag = long_to_bytes(pt).decode()
    print(flag)


if __name__ == "__main__":
    main()