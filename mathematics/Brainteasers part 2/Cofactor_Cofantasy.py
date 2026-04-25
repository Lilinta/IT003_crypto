import time
import json
from pwn import remote

def solve():
    conn = remote('socket.cryptohack.org', 13398)
    conn.recvline()

    def get_execution_time(index):
        payload = json.dumps({"option": "get_bit", "i": index})
        start = time.time()
        conn.sendline(payload)
        conn.recvline()
        return time.time() - start

    # Bước 1: Lấy chuẩn từ bit đã biết (crypto{...)
    # 'c' = 01100011 -> bit 0 (index 0) là 1, bit 7 (index 7) là 0
    t_ones = [get_execution_time(0) for _ in range(5)]
    t_zeros = [get_execution_time(7) for _ in range(5)]
    
    threshold = (min(t_ones) + min(t_zeros)) / 2
    print(f"[*] Threshold: {threshold:.4f}s")

    flag_bits = ""
    # Giả sử flag dài khoảng 40-50 ký tự
    for i in range(8 * 50): 
        times = [get_execution_time(i) for _ in range(3)]
        best_time = min(times)
        
        if best_time > threshold:
            flag_bits += "1"
        else:
            flag_bits += "0"
            
        if len(flag_bits) % 8 == 0:
            byte = flag_bits[-8:][::-1] # Đảo ngược vì get_bit dùng (1 << (i % 8))
            char = chr(int(byte, 2))
            print(f"{char}", end='', flush=True)
            if char == '}': break

    conn.close()

solve()
#crypto{0ver3ng1neering_ch4lleng3_s0lution$}