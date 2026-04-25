import socket
import json
from Crypto.Util.number import long_to_bytes

def solve():
    s = socket.create_connection(("socket.cryptohack.org", 13374))
    f = s.makefile('rw')
    f.readline() # Bỏ qua banner

    def send_cmd(cmd):
        f.write(json.dumps(cmd) + '\n')
        f.flush()
        return json.loads(f.readline())

    # Bước 1: Lấy Flag bị mã hóa (secret)
    secret_hex = send_cmd({"option": "get_secret"})["secret"]

    # Bước 2: Nhờ server "ký" (thực chất là giải mã) chính cái secret đó
    signature_hex = send_cmd({"option": "sign", "msg": secret_hex})["signature"]

    # Bước 3: Đổi hex sang chuỗi ký tự
    flag = long_to_bytes(int(signature_hex, 16)).decode()
    print(f"[+] KẾT QUẢ FLAG: {flag}")

if __name__ == "__main__":
    solve()