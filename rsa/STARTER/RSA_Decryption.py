# p và q lấy từ bài tập Private Keys trước đó
p = 857504083339712752489993810777
q = 1029224947942998075080348647219
e = 65537
c = 77578995801157823671636298847186723593814843845525223303932

# Tính toán các thành phần RSA
n = p * q
phi = (p - 1) * (q - 1)

# Tìm khóa bí mật d
d = pow(e, -1, phi)

# Giải mã để tìm flag
flag = pow(c, d, n)
print("Flag Decryption:", flag)