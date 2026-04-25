import requests
import hashlib
from Crypto.Cipher import AES

# 1. Dữ liệu đầu vào
ciphertext_hex = "c92b7734070205bdf6c0087a751466ec13ae15e6f1bcdd3f3a535ec0f4bbae66"
ciphertext = bytes.fromhex(ciphertext_hex)
url = "https://gist.githubusercontent.com/wchargin/8927565/raw/d9783627c731268fb2935a731a618aa8e95cf465/words"

# 2. Tải danh sách từ điển
print("Đang tải danh sách từ điển...")
words = requests.get(url).text.splitlines()

# 3. Brute-force giải mã
print("Đang dò tìm Flag...")
for word in words:
    # Tạo key bằng cách băm MD5 từng từ
    key = hashlib.md5(word.encode()).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    
    # Giải mã
    decrypted = cipher.decrypt(ciphertext)
    
    # Kiểm tra nếu chuỗi bắt đầu bằng "crypto{"
    if b"crypto{" in decrypted:
        print(f"[*] Từ khóa tìm thấy: {word}")
        print(f"[*] Kết quả Flag: {decrypted.decode('utf-8', errors='ignore').strip()}")
        break