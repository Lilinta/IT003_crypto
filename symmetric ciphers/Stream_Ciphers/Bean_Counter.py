import requests

# 1. Lấy dữ liệu mã hóa từ server
r = requests.get("https://aes.cryptohack.org/bean_counter/encrypt/")
enc_hex = r.json()['encrypted']
enc_bytes = bytes.fromhex(enc_hex)

# 2. Header PNG chuẩn 16 bytes
png_header = bytes.fromhex("89504e470d0a1a0a0000000d49484452")

# 3. Lấy 16 byte đầu của bản mã XOR với header PNG để tìm Keystream
keystream = bytes([enc_bytes[i] ^ png_header[i] for i in range(16)])

# 4. Giải mã toàn bộ bằng cách XOR mọi khối 16-byte với cùng keystream đó
decrypted = bytearray()
for i in range(len(enc_bytes)):
    decrypted.append(enc_bytes[i] ^ keystream[i % 16])

# 5. Xuất file
with open("recovered_bean.png", "wb") as f:
    f.write(decrypted)