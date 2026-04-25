#!/usr/bin/env python3
"""
Giải challenge The Matrix của CryptoHack.

Ý tưởng:
1) Đọc ma trận ciphertext 50x50 trên GF(2).
2) Nhận ra ciphertext = M^E với E = 31337.
3) Vì gcd(E, |GL(50,2)|) = 1, ta tính d = E^{-1} mod |GL(50,2)|.
4) Khôi phục M bằng cách tính C^d trên GF(2).
5) Đổi ma trận bit về chuỗi bit gốc theo đúng cách đề đã dựng ma trận.
6) Chuyển bit sang bytes để lấy flag.
"""

from math import prod


N = 50
E = 31337


FLAG_ENC = """
00000001111101100001101010010001001011000110001001
10111010010100110001011011111110011000001001000001
01011101000110110101010100100100111110110110011111
11101100011011010001111011011000100010110001001010
11111111101001010101001011111101010010011010101001
10010011101000000010000110100101111011110011101110
00011100010011010110000000001011000111010101001011
01001111000110100111110011000101011110010111111110
01111001110011000100000110010101011111010000000011
11001101010111111011110110101010001101001001111101
01100111000100010101000001011011001101001110101000
00010001001011101111100010101101011000101100010111
01101100101101011101101000110001011111111010000100
00001110111111000111111100011110000101100100000011
10001001111111011000111011111010110111111111000110
01111101100011110110111000011110000100111001110100
11111100110101111001111000110100011010111011110001
00100011011100101010111011111100000010000101111111
01111001110100011111011100100011011010010011111000
01011011101011111111101011011011000111110011111010
00010100110111110011111100111101100000001101110111
10011011011101110101100110110000011101000010101011
01111000001111011011111000100010010010010111101001
00100000010001110000001101111100011111110011011000
10010101101011011111101111101000111010010011111001
10011011000111000001010111011000000000100111100011
11001001010001111111000011011011101001101010001000
00100100000101110010001001011001111011001110100001
00000101000101100111010111101010001101111110011001
00101000011010100110100111111110000101011001011110
11011001001111111010000001100111011101101100110110
00111000011011011111111011110001001101001101101100
11110010101001100110000110110000100000101010101011
00101001000011001110110111100010010011100101001000
11000100010010111110110010100110110110101000110110
01101011000111001111011110000110001011111000011100
11010011001111111110100101100011000000000011110001
10000011000101100011000110111111011010110111101000
11000011000100010001001011010011010000001101100011
11011001111001010100010101001100001010101100010010
10110101010111111010110001111111100100110001001100
11101001100110001001001100000011100101001010011010
10000011100110001101010110010010100001010011011101
10001110111111100110011000010000011011011111011001
00011100011111110101011100111000110010100011000010
00111111010010111100100101100001001011110101111100
10000100101101000011011010100100011111100101101111
00011101110001001010111001111011111110110011011001
11111100110101111100110001011001000001111100110011
00110010110110011001001111110110000011001111010110
""".strip()


def parse_matrix(text: str):
    """Đổi chuỗi 50 dòng bit thành ma trận 50x50 các số 0/1."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            rows.append([int(c) for c in line])
    return rows


def rows_to_ints(rows):
    """
    Chuyển mỗi hàng 50 bit thành một số nguyên 50-bit.
    Bit j tương ứng với cột j.
    """
    return [sum(bit << j for j, bit in enumerate(row)) for row in rows]


def ints_to_rows(int_rows, n=N):
    """Chuyển danh sách số nguyên 50-bit về lại ma trận bit."""
    return [[(row >> j) & 1 for j in range(n)] for row in int_rows]


def mat_mul(A, B, n=N):
    """
    Nhân hai ma trận trên GF(2).

    Với biểu diễn theo hàng:
    - Mỗi hàng của A là một vector bit.
    - Hàng kết quả = XOR các hàng của B tương ứng với các bit 1 trong hàng của A.
    """
    result = []
    for a in A:
        r = 0
        x = a
        while x:
            lsb = x & -x
            idx = lsb.bit_length() - 1
            r ^= B[idx]
            x ^= lsb
        result.append(r)
    return result


def mat_pow(M, e, n=N):
    """Lũy thừa ma trận trên GF(2) bằng bình phương-nhân."""
    result = [1 << i for i in range(n)]  # ma trận đơn vị
    base = M[:]

    while e > 0:
        if e & 1:
            result = mat_mul(result, base, n)
        e >>= 1
        if e:
            base = mat_mul(base, base, n)

    return result


def bits_to_bytes(bits):
    """Chuyển danh sách bit (0/1) sang bytes, mỗi 8 bit thành một byte."""
    out = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8]
        b = 0
        for bit in chunk:
            b = (b << 1) | bit
        out.append(b)
    return bytes(out)


def recover_message_bits(matrix_rows):
    """
    Đề tạo ma trận bằng:
        rows = [msg[i::N] for i in range(N)]
    nên khi khôi phục lại msg, phải quét theo cột.
    """
    bits = []
    for col in range(N):
        for row in range(N):
            bits.append(matrix_rows[row][col])
    return bits


def main():
    # Parse ciphertext matrix
    cipher_rows = parse_matrix(FLAG_ENC)
    cipher = rows_to_ints(cipher_rows)

    # Tính |GL(50,2)| = Π (2^50 - 2^i), i = 0..49
    group_order = prod((2**N - 2**i) for i in range(N))

    # Tính nghịch đảo của E modulo group order
    d = pow(E, -1, group_order)

    # Khôi phục ma trận gốc
    plain = mat_pow(cipher, d, N)

    # Đổi lại thành bit theo đúng thứ tự ban đầu
    plain_rows = ints_to_rows(plain, N)
    msg_bits = recover_message_bits(plain_rows)

    # Chuyển bit sang bytes
    msg_bytes = bits_to_bytes(msg_bits)

    # Flag nằm ở phần đầu, trước các bit ngẫu nhiên đệm thêm
    text = msg_bytes.decode("ascii", errors="ignore")
    start = text.find("crypto{")
    end = text.find("}", start)
    flag = text[start:end + 1]

    print(flag)


if __name__ == "__main__":
    main()