from pwn import *
import requests
import concurrent.futures

# Cấu hình log
context.log_level = 'info'

BASE_URL = "http://aes.cryptohack.org/paper_plane/"
session = requests.Session()

def check_padding(c_hex, m0_hex, c0_hex):
    try:
        url = f"{BASE_URL}/send_msg/{c_hex}/{m0_hex}/{c0_hex}/"
        r = session.get(url, timeout=5)
        # Server trả về {"msg": "Message received"} nếu padding đúng
        return "error" not in r.json()
    except:
        return False

def solve_block(block_idx, target_block, prev_m, prev_c):
    current_block_pt = bytearray(16)
    prog = log.progress(f"Block {block_idx}")
    
    for byte_pos in range(15, -1, -1):
        expected_padding = 16 - byte_pos
        found = False
        
        # Thứ tự ưu tiên: Printable ASCII -> Padding bytes -> Others
        guesses = list(range(32, 127)) + list(range(1, 32)) + list(range(127, 256))

        def try_val(guess):
            test_c0 = bytearray(prev_c)
            # Thiết lập các byte đã tìm được để tạo padding đúng
            for j in range(byte_pos + 1, 16):
                test_c0[j] = current_block_pt[j] ^ prev_c[j] ^ expected_padding
            
            # Thử giá trị guess
            test_c0[byte_pos] = guess ^ prev_c[byte_pos] ^ expected_padding
            
            if check_padding(target_block.hex(), prev_m.hex(), test_c0.hex()):
                # CHỐNG FALSE POSITIVE (Chỉ áp dụng cho byte cuối cùng của block)
                if byte_pos == 15:
                    # Thay đổi byte kế tiếp (vị trí 14) để xác nhận đây là 0x01 thật
                    test_c0[14] ^= 0xff
                    if not check_padding(target_block.hex(), prev_m.hex(), test_c0.hex()):
                        return None # Nếu đổi byte 14 mà padding hỏng -> đây là 0x02 0x02 (sai)
                return guess
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_guess = {executor.submit(try_val, g): g for g in guesses}
            for future in concurrent.futures.as_completed(future_to_guess):
                res = future.result()
                if res is not None:
                    current_block_pt[byte_pos] = res
                    prog.status(f"Byte {byte_pos}: '{chr(res) if 32 <= res <= 126 else hex(res)}' | PT hex: {current_block_pt[byte_pos:].hex()}")
                    found = True
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
        
        if not found:
            prog.failure(f"Kẹt tại byte {byte_pos}. Hãy thử chạy lại script!")
            return None

    decoded = "".join(chr(b) if 32 <= b <= 126 else f"\\x{b:02x}" for b in current_block_pt)
    prog.success(f"Dịch xong: {decoded}")
    return bytes(current_block_pt)

def main():
    log.info("Đang lấy ciphertext từ server...")
    try:
        resp = session.get(f"{BASE_URL}/encrypt_flag/").json()
        full_ct = bytes.fromhex(resp['ciphertext'])
        pm = bytes.fromhex(resp['m0'])
        pc = bytes.fromhex(resp['c0'])
    except Exception as e:
        log.error(f"Không thể kết nối server: {e}")
        return

    # Chia ciphertext thành các block 16 bytes
    blocks = [full_ct[i:i+16] for i in range(0, len(full_ct), 16)]
    log.info(f"Số lượng blocks cần giải mã: {len(blocks)}")
    
    final_flag = b""

    for i, target_block in enumerate(blocks):
        decrypted_block = solve_block(i, target_block, pm, pc)
        
        if decrypted_block is None:
            log.error("Tiến trình bị gián đoạn.")
            break
            
        final_flag += decrypted_block
        
        # LOGIC IGE CỰC KỲ QUAN TRỌNG:
        # m_{i-1} mới = plaintext vừa tìm được
        # c_{i-1} mới = ciphertext block vừa giải xong
        pm = decrypted_block
        pc = target_block
        
        print(f"\n[+] Flag (tạm thời): {final_flag.decode(errors='ignore')}\n")

    log.success(f"FLAG CUỐI CÙNG: {final_flag}")

if __name__ == "__main__":
    main()