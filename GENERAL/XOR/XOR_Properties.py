# Các dữ liệu đề bài cho (dạng Hexadecimal)
key1 = "a6c8b6733c9b22de7bc0253266a3867df55acde8635e19c73313"
key2_xor_key3 = "c1545756687e7573db23aa1c3452a098b71a7fbf0fddddde5fc1"
encrypted_flag = "04ee9855208a2cd59091d04767ae47963170d1660df7f56f5faf"

# Chuyển đổi từ Hex string sang Integer để thực hiện phép XOR
k1_int = int(key1, 16)
k23_int = int(key2_xor_key3, 16)
enc_int = int(encrypted_flag, 16)

# Thực hiện XOR: FLAG = (FLAG ^ K1 ^ K2 ^ K3) ^ (K1) ^ (K2 ^ K3)
flag_int = enc_int ^ k1_int ^ k23_int

# Chuyển kết quả từ số nguyên ngược lại thành chuỗi bytes, sau đó decode sang text
# Lưu ý: Mỗi byte là 2 ký tự hex, nên ta chia độ dài chuỗi hex cho 2
flag_hex = hex(flag_int)[2:] # Bỏ tiền tố '0x'
flag = bytes.fromhex(flag_hex)
print(f"Flag của bạn là: {flag}")