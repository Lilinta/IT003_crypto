import requests


BASE_URL = "https://aes.cryptohack.org/ecbcbcwtf/"

def get_flag_enc():
    r = requests.get(f"{BASE_URL}/encrypt_flag/")
    return r.json()['ciphertext']

def decrypt_block(hex_block):
    r = requests.get(f"{BASE_URL}/decrypt/{hex_block}/")
    return r.json()['plaintext']

def xor(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

# 1. Lấy dữ liệu
ct_hex = get_flag_enc()
ct_bytes = bytes.fromhex(ct_hex)

# 2. Chia khối (16 bytes mỗi khối)
blocks = [ct_bytes[i:i+16] for i in range(0, len(ct_bytes), 16)]
iv = blocks[0]
cipher_blocks = blocks[1:]

# 3. Giải mã và XOR
flag = b""
prev_block = iv

for block in cipher_blocks:
    # Gửi khối hiện tại lên server để giải mã ECB
    decrypted_block = bytes.fromhex(decrypt_block(block.hex()))
    # XOR với khối cipher đứng trước nó
    flag += xor(decrypted_block, prev_block)
    prev_block = block

print(f"Flag của bạn là: {flag.decode()}")