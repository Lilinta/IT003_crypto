import requests

BASE_URL = "https://aes.cryptohack.org/flipping_cookie/"

# 1. Lấy cookie ban đầu
resp = requests.get(f"{BASE_URL}/get_cookie/").json()
cookie_hex = resp['cookie']
iv_old = bytes.fromhex(cookie_hex[:32])
ciphertext = cookie_hex[32:]

# 2. Thiết lập chuỗi cũ và mới
old_plain = b"admin=False"
new_plain = b"admin=True;"

# 3. Tính IV mới bằng cách XOR
# IV_new = IV_old ^ P_old ^ P_new
iv_new = list(iv_old)
for i in range(len(old_plain)):
    iv_new[i] = iv_new[i] ^ old_plain[i] ^ new_plain[i]

iv_new_hex = bytes(iv_new).hex()

# 4. Gửi lên để lấy flag
final_resp = requests.get(f"{BASE_URL}/check_admin/{ciphertext}/{iv_new_hex}/").json()
print(final_resp)