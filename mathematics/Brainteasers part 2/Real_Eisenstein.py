import math
from decimal import *
getcontext().prec = int(100)

n = 23
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103]
PRIMES = [int(x) for x in PRIMES]

M = Matrix(ZZ, n + 1, n + 1)
for i in range(n):
    M[i, i] = 1
    M[i, n] = math.floor(Decimal(PRIMES[i]).sqrt() * int(16**64))
M[n, n] = 1350995397927355657956786955603012410260017344805998076702828160316695004588429433

res = M.BKZ()
flag = ""
for kk in range(n):
    flag += chr(abs(res[0][kk]))
print(flag)