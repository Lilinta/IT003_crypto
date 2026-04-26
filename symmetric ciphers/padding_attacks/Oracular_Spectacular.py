import socket
import json

def solve():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.connect(("socket.cryptohack.org", 13423))
    
    f = s.makefile("rw")
    f.readline()
    
    def query(msg):
        f.write(json.dumps(msg) + "\n")
        f.flush()
        return json.loads(f.readline().strip())
    
    ct_hex = query({"option": "encrypt"})["ct"]
    ct_bytes = bytes.fromhex(ct_hex)
    blocks = [ct_bytes[i:i+16] for i in range(0, len(ct_bytes), 16)]
    
    hex_chars = list(b"0123456789abcdef")
    message = b""
    total_queries = 0
    
    for b_idx in range(1, 3):

        Case = False

        while Case == False:
            B_prev, B_curr = blocks[b_idx - 1], blocks[b_idx]
            I_curr = bytearray(16)
            
            for idx in range(15, -1, -1):
                pad_val = 16 - idx
                # Khởi tạo xác suất chia đều cho 16 ký tự
                probs = {c: 1.0 / 16 for c in hex_chars}
                
                tests = 0
                while tests < 360: # Chặn an toàn, không vượt quá 360 requests
                    # Chỉ lôi ký tự có xác suất cao nhất ra test
                    best_c = max(hex_chars, key=lambda c: probs[c])
                    
                    if probs[best_c] > 0.999: # Nếu độ tin cậy chạm 99.9% thì chốt luôn
                        break
                        
                    B_prev_prime = bytearray(B_prev)
                    for k in range(15, idx, -1): B_prev_prime[k] = I_curr[k] ^ pad_val
                    B_prev_prime[idx] = best_c ^ B_prev[idx] ^ pad_val
                    ct_test = B_prev_prime.hex() + B_curr.hex()
                    
                    is_true = query({"option": "unpad", "ct": ct_test}).get("result")
                    total_queries += 1
                    tests += 1
                    
                    # Cập nhật xác suất Bayes
                    lik_correct = 0.4 if is_true else 0.6
                    lik_incorrect = 0.6 if is_true else 0.4
                    
                    for c in hex_chars:
                        if c == best_c:
                            probs[c] *= lik_correct
                        else:
                            probs[c] *= lik_incorrect
                            
                    # Chuẩn hóa lại tổng xác suất về 100%
                    total_p = sum(probs.values())
                    for c in hex_chars: probs[c] /= total_p
                        
                best_guess = max(hex_chars, key=lambda c: probs[c])
                if probs[best_guess]*100 > 90:
                    Case = True
                    
            I_curr[idx] = best_guess ^ B_prev[idx]
            print(f"Block {b_idx}, Byte {idx}: {chr(best_guess)} ({tests} tests, tự tin: {probs[best_guess]*100:.1f}%)")
            
        message += bytes([I_curr[i] ^ B_prev[i] for i in range(16)])
        
    print(f"\nMessage gốc: {message.decode()}")
    print(f"Tổng số queries: {total_queries}/12000")
    print("Kết quả:", query({"option": "check", "message": message.decode()}))

if __name__ == "__main__":
    solve()