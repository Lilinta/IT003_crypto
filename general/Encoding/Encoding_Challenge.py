from pwn import * # pip install pwntools
import json
import base64
import codecs
from Crypto.Util.number import long_to_bytes

# Connection details
r = remote('socket.cryptohack.org', 13377)

def json_recv():
    line = r.recvline()
    return json.loads(line.decode())

def json_send(hsh):
    request = json.dumps(hsh).encode()
    r.sendline(request)

# Loop through the 100 levels
for i in range(101):
    received = json_recv()
    
    # If we get the flag, it's usually in the last response
    if "flag" in received:
        print(f"\n[!] FLAG: {received['flag']}")
        break

    print(f"Level {i+1}: {received['type']}")
    
    encoding = received["type"]
    encoded_val = received["encoded"]
    decoded_val = ""

    # Decode based on type
    if encoding == "base64":
        decoded_val = base64.b64decode(encoded_val).decode()
    elif encoding == "hex":
        decoded_val = bytes.fromhex(encoded_val).decode()
    elif encoding == "rot13":
        decoded_val = codecs.decode(encoded_val, 'rot_13')
    elif encoding == "bigint":
        # Convert hex string (starting with 0x) to bytes
        decoded_val = long_to_bytes(int(encoded_val, 16)).decode()
    elif encoding == "utf-8":
        # Convert list of integers to characters
        decoded_val = "".join(chr(b) for b in encoded_val)

    # Send the answer back
    to_send = {"decoded": decoded_val}
    json_send(to_send)

#crypto{3nc0d3_d3c0d3_3nc0d3}