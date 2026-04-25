import requests

BASE_URL = "https://aes.cryptohack.org/triple_des"

# Kết hợp 2 Weak Keys khác nhau để tránh lỗi "degenerates to single DES"
# Khóa này gồm: K1 (01x8) + K2 (FEx8) + K3 (01x8)
MIXED_WEAK_KEY = "0101010101010101FEFEFEFEFEFEFEFE0101010101010101"

def solve():
    # Bước 1: Lấy flag đã mã hóa
    url_flag = f"{BASE_URL}/encrypt_flag/{MIXED_WEAK_KEY}/"
    print(f"[*] Đang thử với Mixed Weak Key...")
    
    r1 = requests.get(url_flag).json()
    
    if 'error' in r1:
        print(f"[-] Vẫn lỗi: {r1['error']}")
        # Nếu vẫn lỗi, thử đổi chỗ: K1 (FE) + K2 (01) + K3 (FE)
        return

    ct_flag = r1['ciphertext']
    print(f"[+] Lấy ciphertext thành công!")

    # Bước 2: Giải mã
    # Trong 3DES, mã hóa là: E_K3(D_K2(E_K1(P)))
    # Vì cả 3 là Weak Keys, hàm E và D giống hệt nhau. 
    # Việc chạy lại quy trình này lần thứ 2 sẽ trả về P.
    url_encrypt = f"{BASE_URL}/encrypt/{MIXED_WEAK_KEY}/{ct_flag}/"
    r2 = requests.get(url_encrypt).json()
    
    if 'ciphertext' in r2:
        res_hex = r2['ciphertext']
        flag = bytes.fromhex(res_hex)
        print(f"\n[!] FLAG CỦA BẠN: {flag}")
    else:
        print(f"[-] Lỗi bước 2: {r2}")

if __name__ == "__main__":
    solve()