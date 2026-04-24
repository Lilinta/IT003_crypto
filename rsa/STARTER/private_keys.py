# Các thông số từ đề bài
p = 857504083339712752489993810777
q = 1029224947942998075080348647219
e = 65537

# Bước 1: Tính Euler's Totient phi(N)
phi = (p - 1) * (q - 1)

# Bước 2: Tính khóa bí mật d (nghịch đảo của e mod phi)
# Sử dụng pow(e, -1, phi) là cách nhanh nhất trong Python hiện đại
d = pow(e, -1, phi)

print(f"Khóa bí mật d (Flag) là: {d}")