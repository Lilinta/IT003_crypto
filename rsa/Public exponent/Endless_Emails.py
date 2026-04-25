from Crypto.Util.number import long_to_bytes, inverse
from math import prod
from gmpy2 import iroot
from itertools import combinations

with open("output_0ef6d6343784e59e2f44f61d2d29896f.txt", "r") as f:
    n_list = []
    c_list = []

    for _ in range(7):
        n = int(f.readline().split()[-1])
        e = int(f.readline().split()[-1]) 
        c = int(f.readline().split()[-1])
        n_list.append(n)
        c_list.append(c)
        f.readline()
        f.readline()

def cbrt(x):
    m, valid = iroot(x, 3)
    if valid:
        print("Cleartext:", long_to_bytes(m))

def crt(C, N): # Chinese Remainder Theorem
    total = 0
    modulo = prod(N)

    for n_i, c_i in zip(N, C):
        p = modulo // n_i
        total += c_i * inverse(p, n_i) * p
    return total % modulo

# Generate all possible combinations of at least 3 elements
for r in range(3, len(c_list) + 1):
    for c_subset, n_subset in zip(combinations(c_list, r), combinations(n_list, r)):
        result = crt(c_subset, n_subset)
        cbrt(result)