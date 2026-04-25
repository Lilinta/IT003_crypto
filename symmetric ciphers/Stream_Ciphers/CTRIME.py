import requests
import sys

# --- Configuration / Cấu hình ---

# URL of the challenge oracle
# Đường dẫn API của bài Lab
BASE_URL = "https://aes.cryptohack.org/ctrime/encrypt/"

# Possible characters in the flag. Priority given to common flag characters.
# Các ký tự có thể có trong Flag. Ưu tiên các ký tự thường gặp trước.
ALPHABET = '_{}' + 'abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '0123456789'

# A character that definitely isn't in the flag to establish a baseline
# Một ký tự chắc chắn không nằm trong Flag để thiết lập mức độ dài cơ sở
INVALID_CHAR = ';'

# Use a session to reuse the TCP connection for faster requests
# Sử dụng Session để tái sử dụng kết nối TCP giúp tăng tốc độ truy vấn
session = requests.Session()

def get_ciphertext_len(plaintext_str):
    """
    Sends plaintext to the server and returns the length of the ciphertext.
    Gửi bản rõ lên server và trả về độ dài của bản mã tương ứng.
    """
    payload_hex = plaintext_str.encode('ascii').hex()
    response = session.get(f"{BASE_URL}{payload_hex}/").json()
    return len(response['ciphertext'])

# Starting point of the flag recovery
# Điểm bắt đầu của quá trình khôi phục Flag
solution = "crypto{"

print(f"[*] Recovery started. Initial prefix: {solution}")

while True:
    # Step 1: Establish a baseline length using the 'doubling' trick
    # Bước 1: Thiết lập độ dài mẫu bằng kỹ thuật "nhân đôi"
    baseline_payload = (solution + INVALID_CHAR) * 2
    sample_len = get_ciphertext_len(baseline_payload)
    
    found_next_char = False
    
    # Step 2: Test each character in our alphabet
    # Bước 2: Thử nghiệm từng ký tự trong bảng chữ cái
    for c in ALPHABET:
        # Doubling the guess (prefix + guess) * 2 forces zlib to react strongly
        # Nhân đôi chuỗi dự đoán giúp thuật toán nén phản ứng mạnh mẽ hơn
        test_payload = (solution + c) * 2
        current_len = get_ciphertext_len(test_payload)
        
        # Step 3: If length is shorter than baseline, we found a match
        # Bước 3: Nếu độ dài ngắn hơn mẫu, ta đã tìm thấy ký tự đúng
        if current_len < sample_len:
            solution += c
            print(f"[+] Found: {solution}")
            
            # Check if the flag is complete
            # Kiểm tra xem Flag đã kết thúc chưa
            if c == "}":
                print(f"\n[!] Success! Final Flag: {solution}")
                sys.exit()
                
            found_next_char = True
            break # Move to the next position / Chuyển sang vị trí tiếp theo
            
    if not found_next_char:
        print("[-] Error: Stalled at current prefix. Check alphabet or logic.")
        break