p = 29
ints = [14, 6, 11]

# Tạo danh sách các số dư chính phương (squares mod p)
qr_found = {}
for a in range(1, p):
    square = (a * a) % p
    if square in ints:
        if square not in qr_found:
            qr_found[square] = []
        qr_found[square].append(a)

# Xuất kết quả
for val in ints:
    if val in qr_found:
        roots = qr_found[val]
        print(f"Số {val} là Quadratic Residue.")
        print(f"Các căn bậc hai của {val} là: {roots}")
        print(f"Căn bậc hai nhỏ hơn (Flag): {min(roots)}")
    else:
        print(f"Số {val} là Quadratic Non-Residue.")