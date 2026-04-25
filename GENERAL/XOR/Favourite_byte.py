hex_data = "73626960647f6b206821204f21254f7d694f7624662065622127234f726927756d"
cipher_bytes = bytes.fromhex(hex_data)

# Tìm Key bằng cách lấy byte đầu tiên XOR với 'c'
key = cipher_bytes[0] ^ ord('c')
print(f"Chìa khóa bí mật là: {key}")

# Giải mã toàn bộ chuỗi với Key vừa tìm được
flag=""
for b in cipher_bytes:
	char= chr(b^key)
	flag+= char
print(f"Flag: {flag}")