from pwn import *
import json

# --- Configuration ---
HOST = 'socket.cryptohack.org'
PORT = 13399

# Connect to the target server
# Kết nối đến máy chủ mục tiêu
r = connect(HOST, PORT)
r.recvline() # Consume the initial greeting

# Step 1: Prepare the all-zero token (28 bytes of 0x00)
# Bước 1: Chuẩn bị token gồm toàn các byte 0
zero_token = (b"\x00" * 28).hex()
reset_payload = json.dumps({"option": "reset_password", "token": zero_token}).encode()

# Step 2: Prepare the authentication payload (empty password)
# Bước 2: Chuẩn bị gói tin xác thực với mật khẩu rỗng
auth_payload = json.dumps({"option": "authenticate", "password": ""}).encode()

# Step 3: Prepare the connection reset payload
# Bước 3: Chuẩn bị gói tin đặt lại kết nối để lấy Key AES mới
reconnect_payload = json.dumps({"option": "reset_connection"}).encode()

print("[*] Starting Zerologon brute-force attack (CVE-2020-1472)...")
attempts = 0

# Step 4: Brute-force loop (1/256 probability of success)
# Bước 4: Vòng lặp tấn công vét cạn (Xác suất thành công là 1/256)
while True:
    attempts += 1
    
    # Send the all-zero token to attempt resetting the password
    # Gửi token toàn số 0 để thử reset mật khẩu
    r.sendline(reset_payload)
    r.recvline() # Clear the buffer response
    
    # Attempt to authenticate with the empty password
    # Thử đăng nhập bằng mật khẩu rỗng
    r.sendline(auth_payload)
    response = r.recvline().decode().strip()
    
    # Check if the attack was successful (Flag is returned)
    # Kiểm tra xem tấn công đã thành công chưa (Server trả về Flag)
    if "crypto{" in response:
        print(f"\n[+] SUCCESS! Condition met after {attempts} attempts.")
        print(f"[!] Target Response: {response}")
        break
        
    # If failed, reset the connection to force the server to generate a new AES key
    # Nếu thất bại, reset kết nối để ép server tạo Key AES mới
    r.sendline(reconnect_payload)
    r.recvline() 
    
    # Print progress to show the script is running
    # In tiến trình để biết script vẫn đang chạy
    if attempts % 50 == 0:
        print(f"[*] Attempt {attempts} failed. Generating new keys and retrying...")