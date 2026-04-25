import requests
import string

BASE_URL = "https://aes.cryptohack.org/ecb_oracle/encrypt/"

def encrypt(payload_hex):
    r = requests.get(f"{BASE_URL}{payload_hex}/")
    return r.json()['ciphertext']

alphabet = string.ascii_letters + string.digits + "{}_!"
flag = ""

# Giả sử flag dài không quá 32 byte (2 khối)
for i in range(32):
    # Tạo padding để đẩy ký tự cần tìm vào cuối khối 16 byte
    padding = "aa" * (31 - len(flag)) 
    target_all = encrypt(padding)
    
    # Lấy khối chứa ký tự đang tìm (khối 1 hoặc khối 2 tùy vào độ dài flag)
    # Ở đây chúng ta xét 2 khối đầu (64 ký tự hex)
    target_block = target_all[32:64] 

    for char in alphabet:
        # Thử từng ký tự: padding + flag_đã_biết + ký tự_thử
        test_payload = padding + flag.encode().hex() + char.encode().hex()
        test_res = encrypt(test_payload)
        
        if test_res[32:64] == target_block:
            flag += char
            print(f"Flag hiện tại: {flag}")
            break