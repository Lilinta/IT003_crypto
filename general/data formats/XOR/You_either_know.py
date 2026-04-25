hex_data = "0e0b213f26041e480b26217f27342e175d0e070a3c5b103e2526217f27342e175d0e077e263451150104"
cipher_bytes = bytes.fromhex(hex_data)

# Phần flag chúng ta đã biết chắc chắn
known_prefix = b"crypto{"

# Tìm các ký tự đầu tiên của Key
key_part = ""
for i in range(len(known_prefix)):
    # Lấy từng byte của cipher XOR với từng byte của "crypto{"
    key_char = chr(cipher_bytes[i] ^ known_prefix[i])
    key_part += key_char

print(f"Found Key: '{key_part}'")   # "myXORke"
key = b"myXORkey"
key_len = len(key)

# Giải mã bằng cách lặp lại key (Repeating Key XOR)
flag = ""
for i in range(len(cipher_bytes)):
    # cipher_bytes[i] XOR với ký tự tương ứng trong key (dùng % để quay vòng key)
    decrypted_char = chr(cipher_bytes[i] ^ key[i % key_len])
    flag += decrypted_char

print(f"Flag: {flag}")