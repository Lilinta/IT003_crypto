data = "label"
key = 13

print(xor(key,data))
# Tạo một chuỗi mới từ kết quả XOR
new_string = ""
for char in data:
    # Bước 1 & 2 & 3: Lấy mã ASCII, XOR với 13, rồi chuyển lại thành ký tự
    new_char = chr(ord(char) ^ key)
    new_string += new_char

print(f"Flag: crypto{{{new_string}}}")