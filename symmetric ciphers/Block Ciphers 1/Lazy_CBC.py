import requests

# 1. Cấu hình URL bài tập
BASE_URL = "https://aes.cryptohack.org/lazy_cbc/"

def solve():
    # Bước 1: Gửi 3 khối ciphertext toàn số 0 (48 byte hex = 96 ký tự '0')
    # Chúng ta cần ít nhất 3 khối để server trả về lỗi chứa plaintext giải mã
    null_cipher = "0" * 96
    print("[+] Đang gửi ciphertext rác để lấy Plaintext từ lỗi...")
    
    r = requests.get(f"{BASE_URL}/receive/{null_cipher}/").json()
    
    if 'error' not in r:
        print("[-] Không lấy được lỗi. Kiểm tra lại kết nối!")
        return

    # Bước 2: Trích xuất Plaintext từ thông báo lỗi
    # Định dạng lỗi: "Invalid plaintext: <hex_string>"
    error_msg = r['error']
    hex_plaintext = error_msg.split(": ")[1]
    plaintext_bytes = bytes.fromhex(hex_plaintext)
    
    # Chia thành các khối 16 byte
    p1 = plaintext_bytes[0:16]
    p2 = plaintext_bytes[16:32]
    
    print(f"[+] P1: {p1.hex()}")
    print(f"[+] P2: {p2.hex()}")

    # Bước 3: Tính KEY = P1 XOR P2
    # Vì P1 = D(C1) ^ KEY và P2 = D(C2) ^ C1. Với C1=C2=0 => P2 = D(C1)
    # Suy ra P1 ^ P2 = (D(C1) ^ KEY) ^ D(C1) = KEY
    key = bytes([a ^ b for a, b in zip(p1, p2)])
    key_hex = key.hex()
    print(f"[+] KEY tìm được: {key_hex}")

    # Bước 4: Dùng KEY để lấy FLAG
    print("[+] Đang lấy FLAG...")
    flag_resp = requests.get(f"{BASE_URL}/get_flag/{key_hex}/").json()
    
    if 'plaintext' in flag_resp:
        # Flag trả về thường ở dạng hex, cần decode sang ASCII
        flag = bytes.fromhex(flag_resp['plaintext']).decode()
        print(f"\n[*] FLAG CỦA BẠN: {flag}")
    else:
        print(f"[-] Có lỗi khi lấy flag: {flag_resp}")

if __name__ == "__main__":
    solve()