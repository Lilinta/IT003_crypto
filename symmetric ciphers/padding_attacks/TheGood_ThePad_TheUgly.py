import socket
import json

def solve():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("socket.cryptohack.org", 13422))
    f = s.makefile("rw")
    f.readline() # Bỏ qua dòng giới thiệu
    
    def query(msg):
        f.write(json.dumps(msg) + "\n")
        f.flush()
        return json.loads(f.readline().strip())
    
    ct_hex = query({"option": "encrypt"})["ct"]
    ct_bytes = bytes.fromhex(ct_hex)
    blocks = [ct_bytes[i:i+16] for i in range(0, len(ct_bytes), 16)]
    
    hex_chars = b"0123456789abcdef"
    message = b""
    
    for b_idx in range(1, len(blocks)):
        B_prev, B_curr = blocks[b_idx - 1], blocks[b_idx]
        I_curr = bytearray(16)
        
        for idx in range(15, -1, -1):
            pad_val = 16 - idx
            for p_guess in hex_chars:
                I_guess = p_guess ^ B_prev[idx]
                B_prev_prime = bytearray(B_prev)
                
                # Setup padding cho các byte đã biết
                for k in range(15, idx, -1):
                    B_prev_prime[k] = I_curr[k] ^ pad_val
                # Setup padding cho byte hiện tại
                B_prev_prime[idx] = I_guess ^ pad_val
                
                ct_test = B_prev_prime.hex() + B_curr.hex()
                
                # Xác nhận padding (25 lần để triệt tiêu xác suất nhiễu 0.6^25)
                is_valid = True
                for _ in range(25):
                    if not query({"option": "unpad", "ct": ct_test})["result"]:
                        is_valid = False
                        break
                
                if is_valid:
                    I_curr[idx] = I_guess
                    break
                    
        message += bytes([I_curr[i] ^ B_prev[i] for i in range(16)])
        print(f"Giải mã thành công block {b_idx}...")
        
    print("\nMessage gốc:", message.decode())
    print("Kết quả:", query({"option": "check", "message": message.decode()}))

if __name__ == "__main__":
    solve()