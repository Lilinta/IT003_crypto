#!/usr/bin/env python3
from binascii import unhexlify

# --- Challenge Data / Dữ liệu bài Lab ---
KNOWN_MSG = b'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula.'
MSG_ENC_HEX = 'f3afbada8237af6e94c7d2065ee0e221a1748b8c7b11105a8cc8a1c74253611c94fe7ea6fa8a9133505772ef619f04b05d2e2b0732cc483df72ccebb09a92c211ef5a52628094f09a30fc692cb25647f'

FLAG_ENC_HEX = 'b6327e9a2253034096344ad5694a2040b114753e24ea9c1af17c10263281fb0fe622b32732'
IV2_HEX = 'a99f9a7d097daabd2aa2a235'

# --- Utility Functions / Hàm tiện ích ---
def bytes_to_words(b):
    """Convert bytes to a list of 32-bit little-endian integers."""
    """Chuyển đổi mảng byte thành danh sách các số nguyên 32-bit little-endian."""
    return [int.from_bytes(b[i:i+4], 'little') for i in range(0, len(b), 4)]

def words_to_bytes(w):
    """Convert a list of 32-bit integers back to bytes."""
    """Chuyển mảng số nguyên 32-bit ngược lại thành mảng byte."""
    return b''.join([i.to_bytes(4, 'little') for i in w])

def xor(a, b):
    """XOR two byte arrays of equal length."""
    """Thực hiện phép XOR giữa hai mảng byte."""
    return bytes([x ^ y for x, y in zip(a, b)])

def word(x):
    """Keep integer within 32-bit bounds."""
    """Giới hạn số nguyên trong phạm vi 32-bit."""
    return x % (2 ** 32)

def rotate(x, n):
    """Left bitwise rotation for 32-bit integers."""
    """Phép xoay bit sang trái cho số nguyên 32-bit."""
    return ((x << n) & 0xffffffff) | ((x >> (32 - n)) & 0xffffffff)

def rotr(x, n):
    """Right bitwise rotation (Inverse of rotate)."""
    """Phép xoay bit sang phải (Nghịch đảo của phép xoay trái)."""
    return ((x >> n) | ((x << (32 - n)) & 0xffffffff)) & 0xffffffff

# --- Vulnerable ChaCha20 Implementation / Trình giả lập mã hóa lỗi ---
class BrokenChaCha20:
    def __init__(self):
        self._state = []

    def _quarter_round(self, x, a, b, c, d):
        x[a] = word(x[a] + x[b]); x[d] ^= x[a]; x[d] = rotate(x[d], 16)
        x[c] = word(x[c] + x[d]); x[b] ^= x[c]; x[b] = rotate(x[b], 12)
        x[a] = word(x[a] + x[b]); x[d] ^= x[a]; x[d] = rotate(x[d], 8)
        x[c] = word(x[c] + x[d]); x[b] ^= x[c]; x[b] = rotate(x[b], 7)

    def _inner_block(self, state):
        # Column rounds / Vòng trộn theo cột
        self._quarter_round(state, 0, 4, 8, 12)
        self._quarter_round(state, 1, 5, 9, 13)
        self._quarter_round(state, 2, 6, 10, 14)
        self._quarter_round(state, 3, 7, 11, 15)
        # Diagonal rounds / Vòng trộn theo đường chéo
        self._quarter_round(state, 0, 5, 10, 15)
        self._quarter_round(state, 1, 6, 11, 12)
        self._quarter_round(state, 2, 7, 8, 13)
        self._quarter_round(state, 3, 4, 9, 14)

    def _setup_state(self, key, iv):
        self._state = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574] # "expand 32-byte k"
        self._state.extend(bytes_to_words(key))
        self._state.append(self._counter)
        self._state.extend(bytes_to_words(iv))

    def decrypt(self, c, key, iv):
        # In CTR mode, encryption and decryption are the same
        # Chế độ CTR, mã hóa và giải mã dùng chung hàm
        return self.encrypt(c, key, iv)

    def encrypt(self, m, key, iv):
        c = b''
        self._counter = 1
        for i in range(0, len(m), 64):
            self._setup_state(key, iv)
            for _ in range(10): # 20 rounds (10 double rounds)
                self._inner_block(self._state)
            
            # VULNERABILITY: Missing addition of initial state to final state!
            # LỖ HỔNG: Thiếu phép cộng trạng thái ban đầu vào trạng thái cuối cùng!
            c += xor(m[i:i+64], words_to_bytes(self._state))
            self._counter += 1
        return c

# --- Inverse Functions for Attack / Các hàm nghịch đảo để tấn công ---
def inv_quarter_round(x, a, b, c, d):
    """Reverses the ChaCha20 quarter round exactly step-by-step backward."""
    """Đảo ngược hoàn toàn vòng trộn quarter round theo thứ tự từ dưới lên."""
    a2, b2, c2, d2 = x[a], x[b], x[c], x[d]
    
    # Undo step 4 / Đảo ngược bước 4
    b1 = rotr(b2, 7) ^ c2
    c1 = (c2 - d2) & 0xffffffff
    # Undo step 3 / Đảo ngược bước 3
    a1 = (a2 - b1) & 0xffffffff
    d1 = rotr(d2, 8) ^ a2
    # Undo step 2 / Đảo ngược bước 2
    b0 = rotr(b1, 12) ^ c1
    c0 = (c1 - d1) & 0xffffffff
    # Undo step 1 / Đảo ngược bước 1
    a0 = (a1 - b0) & 0xffffffff
    d0 = rotr(d1, 16) ^ a1
    
    x[a], x[b], x[c], x[d] = a0, b0, c0, d0

def inv_inner_block(state):
    """Reverses the column and diagonal rounds (must be in reverse order)."""
    """Đảo ngược các vòng trộn chéo và cột (phải thực hiện ngược thứ tự ban đầu)."""
    # Undo Diagonal rounds
    inv_quarter_round(state, 3, 4, 9, 14)
    inv_quarter_round(state, 2, 7, 8, 13)
    inv_quarter_round(state, 1, 6, 11, 12)
    inv_quarter_round(state, 0, 5, 10, 15)
    # Undo Column rounds
    inv_quarter_round(state, 3, 7, 11, 15)
    inv_quarter_round(state, 2, 6, 10, 14)
    inv_quarter_round(state, 1, 5, 9, 13)
    inv_quarter_round(state, 0, 4, 8, 12)

def recover_key(msg, msg_enc):
    """Extracts the keystream, reverses the rounds, and pulls the key from the matrix."""
    """Trích xuất keystream, đảo ngược các vòng trộn và lấy khóa từ ma trận."""
    # 1. Get Keystream: K = P ^ C
    ks = xor(msg_enc[:64], msg[:64])
    state = bytes_to_words(ks)
    
    # 2. Walk backward through the 20 rounds (10 inner blocks)
    for _ in range(10):
        inv_inner_block(state)
        
    # 3. State is now restored to initial. Key is located at indices 4 through 11.
    return words_to_bytes(state[4:12])

# --- Main Execution / Thực thi ---
def main():
    msg_enc = unhexlify(MSG_ENC_HEX)
    flag_enc = unhexlify(FLAG_ENC_HEX)
    iv2 = unhexlify(IV2_HEX)
    
    print("[*] Starting attack on broken ChaCha20...")
    key = recover_key(KNOWN_MSG, msg_enc)
    print(f"[+] Recovered 256-bit Key: {key.hex()}")
    
    cipher = BrokenChaCha20()
    flag = cipher.decrypt(flag_enc, key, iv2)
    print(f"[!] Flag Decrypted: {flag.decode('utf-8')}")

if __name__ == "__main__":
    main()