# Khai báo các giá trị đề bài cho
p = 17
q = 23
e = 65537
message = 12

# Tính N
n = p * q

# Tính Ciphertext bằng hàm pow(base, exp, mod)
ciphertext = pow(message, e, n)

print(f"Bản mã (Flag) thu được là: {ciphertext}")