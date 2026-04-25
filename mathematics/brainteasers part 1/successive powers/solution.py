#!/usr/bin/env python3
"""
Giải challenge Successive Powers - CryptoHack.

Ý tưởng:
- Dãy số là các lũy thừa liên tiếp của x modulo p.
- Suy ra: x ≡ a[i+1] * inverse(a[i]) (mod p).
- Duyệt các số nguyên tố p có 3 chữ số để tìm p và x thỏa mãn.
"""

from sympy import primerange

# Dãy số đề bài cho
a = [588, 665, 216, 113, 642, 4, 836, 114, 851, 492, 819, 237]

def find_p_x(sequence):
    # Duyệt tất cả số nguyên tố 3 chữ số
    for p in primerange(100, 1000):
        x_candidate = None
        valid = True

        for i in range(len(sequence) - 1):
            ai = sequence[i] % p
            ai_next = sequence[i + 1] % p

            # Nếu ai không khả nghịch modulo p thì bỏ
            if ai == 0:
                valid = False
                break

            inv_ai = pow(ai, -1, p)
            x_i = (ai_next * inv_ai) % p

            if x_candidate is None:
                x_candidate = x_i
            elif x_candidate != x_i:
                valid = False
                break

        if valid:
            return p, x_candidate

    return None, None


def main():
    p, x = find_p_x(a)
    print(f"crypto{{{p},{x}}}")


if __name__ == "__main__":
    main()
