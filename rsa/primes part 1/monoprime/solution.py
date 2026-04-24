#!/usr/bin/env python3
"""
Giải challenge Monoprime của CryptoHack.

Ý tưởng:
1) Nhận thấy n là số nguyên tố.
2) Suy ra phi(n) = n - 1.
3) Tính d = e^{-1} mod (n - 1).
4) Giải mã ciphertext bằng RSA chuẩn.
5) Chuyển plaintext từ số nguyên sang bytes để lấy flag.
"""

def long_to_bytes(n: int) -> bytes:
    """Chuyển số nguyên lớn sang bytes."""
    if n == 0:
        return b"\x00"
    out = bytearray()
    while n > 0:
        out.append(n & 0xFF)
        n >>= 8
    return bytes(reversed(out))


def main():
    # Dữ liệu từ output.txt
    n = 171731371218065444125482536302245915415603318380280392385291836472299752747934607246477508507827284075763910264995326010251268493630501989810855418416643352631102434317900028697993224868629935657273062472544675693365930943308086634291936846505861203914449338007760990051788980485462592823446469606824421932591
    e = 65537
    ct = 161367550346730604451454756189028938964941280347662098798775466019463375610700074840105776873791605070092554650190486030367121011578171525759600774739890458414593857709994072516290998135846956596662071379067305011746842247628316996977338024343628757374524136260758515864509435302781735938531030576289086798942

    # Vì n là số nguyên tố, phi(n) = n - 1
    phi = n - 1

    # Tính khóa bí mật d
    d = pow(e, -1, phi)

    # Giải mã
    pt = pow(ct, d, n)

    # Đổi sang bytes và in flag
    flag = long_to_bytes(pt).decode()
    print(flag)


if __name__ == "__main__":
    main()