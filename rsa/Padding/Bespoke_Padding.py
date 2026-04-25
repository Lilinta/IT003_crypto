import socket
import json

def get_flag_data():
    # Kết nối đến server CryptoHack
    s = socket.create_connection(("socket.cryptohack.org", 13386))
    
    # Nhận thông báo chào mừng ban đầu
    s.recv(1024)
    
    results = []
    for i in range(2):
        # Gửi yêu cầu lấy flag
        s.sendall(json.dumps({"option": "get_flag"}).encode() + b"\n")
        # Nhận dữ liệu (tăng buffer lên để tránh thiếu dữ liệu)
        resp = b""
        while True:
            chunk = s.recv(4096)
            resp += chunk
            if b"\n" in chunk: break
        
        data = json.loads(resp.decode())
        results.append(data)
        print(f"\n--- LẦN LẤY DỮ LIỆU {i+1} ---")
        print(f"c{i+1} = {data['encrypted_flag']}")
        print(f"a{i+1} = {data['padding'][0]}")
        print(f"b{i+1} = {data['padding'][1]}")
    
    print(f"\nn = {results[0]['modulus']}")
    s.close()

if __name__ == "__main__":
    get_flag_data()


