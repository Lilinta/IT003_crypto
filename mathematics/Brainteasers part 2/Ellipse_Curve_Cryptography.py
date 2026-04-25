from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import sha1
from sympy.ntheory.residue_ntheory import discrete_log

# --- Thông số từ thử thách ---
p = 173754216895752892448109692432341061254596347285717132408796456167143559
w = 23  # Vì D = 529 = 23^2

# Điểm gốc G
G_x = 29394812077144852405795385333766317269085018265469771684226884125940148
G_y = 94108086667844986046802106544375316173742538919949485639896613738390948

# Khóa công khai của Alice (A)
A_x = 155781055760279718382374741001148850818103179141959728567110540865590463
A_y = 73794785561346677848810778233901832813072697504335306937799336126503714

# Khóa công khai của Bob (B)
B_x = 171226959585314864221294077932510094779925634276949970785138593200069419
B_y = 54353971839516652938533335476115503436865545966356461292708042305317630

# Dữ liệu mã hóa
enc_data = {
    'iv': '64bc75c8b38017e1397c46f85d4e332b',
    'encrypted_flag': '13e4d200708b786d8f7c3bd2dc5de0201f0d7879192e6603d7c5d6b963e1df2943e3ff75f7fda9c30a92171bbbc5acbf'
}

# --- BƯỚC 1: Đưa về bài toán DLP trên số nguyên ---
g = (G_x + w * G_y) % p
target = (A_x + w * A_y) % p

print("[*] Đang giải Discrete Logarithm bằng SymPy (có thể mất vài giây)...")
# Tìm n_a sao cho g^n_a = target (mod p)
n_a = discrete_log(p, target, g)
print(f"[+] Đã tìm thấy Private Key n_a: {n_a}")

# --- BƯỚC 2: Tính Shared Secret ---
# Tính (B_x + w*B_y)^n_a mod p
s_val = pow(B_x + w * B_y, n_a, p)

# Lấy lại phần thực x_shared = (s + s^-1) / 2 mod p
s_inv = pow(s_val, -1, p)
shared_secret = ((s_val + s_inv) * pow(2, -1, p)) % p
print(f"[*] Shared Secret: {shared_secret}")

# --- BƯỚC 3: Giải mã AES ---
key = sha1(str(shared_secret).encode('ascii')).digest()[:16]
iv = bytes.fromhex(enc_data['iv'])
ciphertext = bytes.fromhex(enc_data['encrypted_flag'])

cipher = AES.new(key, AES.MODE_CBC, iv)
flag = unpad(cipher.decrypt(ciphertext), 16)

print(f"\n[!] FLAG CỦA BẠN: {flag.decode()}")