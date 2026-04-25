import socket
import json
from Crypto.Util.number import bytes_to_long, long_to_bytes

def solve_modular_cube_root(target, bits):
    """Giải phương trình x^3 = target (mod 2^bits) bằng Hensel's Lifting"""
    res = 1
    for i in range(bits):
        if (res**3) & (1 << i) != (target & (1 << i)):
            res |= (1 << i)
    return res

# Thông số đề bài
N = 22266616657574989868109324252160663470925207690694094953312891282341426880506924648525181014287214350136557941201445475540830225059514652125310445352175047408966028497316806142156338927162621004774769949534239479839334209147097793526879762417526445739552772039876568156469224491682030314994880247983332964121759307658270083947005466578077153185206199759569902810832114058818478518470715726064960617482910172035743003538122402440142861494899725720505181663738931151677884218457824676140190841393217857683627886497104915390385283364971133316672332846071665082777884028170668140862010444247560019193505999704028222347577
e = 3
target_str = b"\x00VOTE FOR PEDRO"
target_int = bytes_to_long(target_str)

print("[*] Đang tính toán căn bậc ba modulo để giả mạo chữ ký...")
# Giải x sao cho x^3 ends with target_str
# Chúng ta cần x^3 = target (mod 2^120) vì 15 bytes = 120 bits
x = solve_modular_cube_root(target_int, 120)

# Kiểm tra lại
check = pow(x, e, N)
if long_to_bytes(check).endswith(target_str):
    print("[+] Tìm thấy số vote hợp lệ!")
else:
    print("[-] Thất bại, đang thử lại với bit cao hơn...")
    x = solve_modular_cube_root(target_int, 256)

print("[*] Đang kết nối tới server...")
s = socket.create_connection(('socket.cryptohack.org', 13375))
f = s.makefile('r', encoding='utf-8')

def send_json(data):
    s.sendall((json.dumps(data) + '\n').encode())

def get_json():
    while True:
        line = f.readline()
        if not line: return None
        if '{' in line: return json.loads(line[line.find('{'):])

f.readline() # Skip chào mừng
send_json({"option": "vote", "vote": hex(x)})

result = get_json()
print(f"\n[+] Kết quả: {result.get('flag', result)}")
s.close()