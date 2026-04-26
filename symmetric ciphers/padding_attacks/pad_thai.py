import socket
import json

def solve():
    # Kết nối tới server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("socket.cryptohack.org", 13421))
    
    def readline():
        buf = b""
        while not buf.endswith(b"\n"):
            buf += s.recv(1)
        return buf.decode()
    
    def send_cmd(cmd):
        s.sendall((json.dumps(cmd) + "\n").encode())
        return json.loads(readline())

    print("[*] Đang kết nối...")
    readline() # Bỏ qua dòng banner
    
    # Lấy Ciphertext (IV + CT)
    res = send_cmd({"option": "encrypt"})
    ct_bytes = bytes.fromhex(res["ct"])
    blocks = [ct_bytes[i:i+16] for i in range(0, len(ct_bytes), 16)]
    
    plaintext = b""
    print("[*] Bắt đầu chạy Padding Oracle Attack (có thể mất 1-2 phút)...")
    
    # Giải mã từng block
    for block_idx in range(1, len(blocks)):
        prev_block = blocks[block_idx - 1]
        curr_block = blocks[block_idx]
        
        decrypted_block = bytearray(16)
        inter_state = bytearray(16)
        
        for i in range(15, -1, -1):
            pad_val = 16 - i
            for byte_guess in range(256):
                forged_prev = bytearray(16)
                
                # Cài đặt các byte đã biết phía sau
                for j in range(15, i, -1):
                    forged_prev[j] = inter_state[j] ^ pad_val
                
                # Thử nghiệm byte hiện tại
                forged_prev[i] = byte_guess
                test_ct = bytes(forged_prev) + curr_block
                
                pad_res = send_cmd({"option": "unpad", "ct": test_ct.hex()})
                
                if pad_res.get("result"):
                    # Xử lý trường hợp false positive ở byte cuối cùng
                    if i == 15:
                        forged_prev[14] ^= 1
                        check_res = send_cmd({"option": "unpad", "ct": (bytes(forged_prev) + curr_block).hex()})
                        if not check_res.get("result"):
                            continue
                    
                    inter_state[i] = byte_guess ^ pad_val
                    decrypted_block[i] = inter_state[i] ^ prev_block[i]
                    break
        
        plaintext += decrypted_block
        print(f"[*] Block {block_idx} đã giải mã: {decrypted_block}")

    # Loại bỏ padding theo chuẩn PKCS#7
    msg = plaintext.decode('ascii')
    print(f"\n[*] Thông điệp khôi phục được: {msg}")
    
    # Gửi thông điệp để nhận Flag
    print("[*] Đang lấy Flag...")
    flag_res = send_cmd({"option": "check", "message": msg})
    print(f"[+] Kết quả: {flag_res.get('flag', flag_res)}")

if __name__ == "__main__":
    solve()