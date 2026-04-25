#!/usr/bin/env python3
import telnetlib
import json
from random import randint
from functools import reduce
from Cryptodome.Util.number import *
import itertools
from tqdm import tqdm

# =============================================================================
# NETWORK COMMUNICATION WITH CRYPTOHACK CHALLENGE SERVER
# =============================================================================
HOST = "socket.cryptohack.org"
PORT = 13385
tn = telnetlib.Telnet(HOST, PORT)

def readline():
    """Read one line from the Telnet connection (used to receive server messages)."""
    return tn.read_until(b"\n")

def json_recv():
    """Receive raw line from server, decode it and parse as JSON object."""
    line = readline()
    return json.loads(line.decode())

def json_send(hsh):
    """Convert Python dict to JSON and send it to the server."""
    request = json.dumps(hsh).encode()
    tn.write(request)

# =============================================================================
# MATHEMATICAL UTILITY FUNCTIONS
# =============================================================================
def generate_basis(n):
    """Generate list of all prime numbers < n using optimized Sieve of Eratosthenes (odd numbers only)."""
    basis = [True] * n
    for i in range(3, int(n**0.5)+1, 2):
        if basis[i]:
            basis[i*i::2*i] = [False]*((n-i*i-1)//(2*i)+1)
    return [2] + [i for i in range(3, n, 2) if basis[i]]

def gcd(number1, number2):
    """Euclidean algorithm to compute GCD(number1, number2)."""
    if(number1 == 0): return number2
    return gcd(number2%number1, number1)

def extended_gcd(a,b):
    """Extended Euclidean algorithm returning (s, t, gcd) where s*a + t*b = gcd(a,b)."""
    s = 0
    old_s = 1
    r = b
    old_r = a
    bezout_t = None
    q = None
    while r!= 0:
        q = int(old_r / r)
        old_r, r = r, old_r - q*r
        old_s, s = s, old_s - q*s
    if b!=0 :
        bezout_t = int((old_r - old_s*a) / b)
    else:
        bezout_t = 0
    return (old_s,bezout_t,old_r)

def inv(number1, number2):
    """Compute modular inverse of number1 modulo number2 (returns -1 if not invertible)."""
    (old_s,bezout_t,old_r) = extended_gcd(number1, number2)
    if old_r > 1: return -1
    if old_s < 0: old_s+=number2
    return old_s

def mulMod(number1,number2, number3):
    """Modular multiplication: (number1 * number2) % number3."""
    return (number1*number2)%number3

def powMod(number1,number2, number3):
    """Modular exponentiation using binary exponentiation (right-to-left)."""
    assert number2 >= 0
    res = 1
    while number2 > 0:
        if(number2 & 1 == 1): res = mulMod(res, number1, number3)
        number1 = mulMod(number1, number1, number3)
        number2 = number2 >> 1
    return res

def chinese_remainder(r, p):
    """Classic CRT: solve system x ≡ r_i (mod p_i) for pairwise coprime moduli."""
    res = 0
    p_prod = reduce(lambda a,b: a*b, p) # N = n1*n2*n3*...
    for r_i,p_i in zip(r,p):
        N = (p_prod//p_i)
        if inv(N, p_i):
            res += (r_i*N*inv(N, p_i))
    return res % p_prod, p_prod

def xgcd(a, b):
    """Another implementation of Extended GCD (used in crt1)."""
    s = 0
    t = 1
    r = b
    s1 = 1
    t1 = 0
    r1 = a
    while not (r == 0):
        q = r1//r
        r1, r = r, r1-q*r
        s1, s = s, s1-q*s
        t1, t = t, t1-q*t
    return (r1, s1, t1)

def crt1(residues, modulos):
    """Incremental CRT that handles non-coprime moduli (returns -1 if inconsistent)."""
    rm = list(zip(residues, modulos))
    cur_res, cur_mod = rm[0]
    for r, m in rm[1:]:
        g = gcd(cur_mod, m)   # Note: original code used GCD (undefined), corrected to gcd for clarity
        if not r % g == cur_res % g:
            return -1, -1
        r1, s, t = xgcd(m//g, cur_mod//g)
        cur_res = cur_res * m//g * s + r * cur_mod//g * t
        cur_mod *= m//g
        cur_res %= cur_mod
    return cur_res, cur_mod

def miller_rabin(n, b):
    """
    Miller-Rabin primality test using all prime bases < b.
    Returns True if n is a strong probable prime to all these bases.
    """
    basis = generate_basis(b)
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for b in basis:
        x = pow(b, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

# =============================================================================
# STRONG PSEUDOPRIME CONSTRUCTION (CORE OF THE SOLUTION)
# =============================================================================
LOWER = 2**600 + 1
UPPER = 2**900 - 1

def gen_prime(lower = LOWER, upper = UPPER):
    """Generate a random probable prime in the given bit-length range using Miller-Rabin."""
    found = False
    while not(found):
        res = randint(lower, upper)
        if res % 2 == 0: res += 1
        found = miller_rabin(res, 5)
    return res

def lengendre(a,p):
    """Compute Legendre symbol (a/p) using Euler's criterion."""
    return pow(a,(p-1)//2,p)

def tonelli_shanks(a, p):
    """Tonelli-Shanks algorithm to find square root of a modulo odd prime p (assumes quadratic residue)."""
    assert lengendre(a, p) == 1
    q = p- 1
    s = 0
    while q%2 == 0:
        s = s+1
        q//=2
    if s == 1: return pow(a,(p-1)//4,p)
    # find quadratic non-residue z
    for z in range(2,p):
        if p-1 == lengendre(z, p): break
    # assign variables
    m = s
    c = pow(z, q, p)
    t = pow(a, q, p)
    r = pow(a, (q+1)//2, p)
    while (t-1)%p != 0:
        t2 = (t*t)%p
        for i in range(1,m):
            if (t2-1)%p == 0:
                break
            t2 = (t2*t2)%p
        b = pow(c, 1 << (m-i-1), p)
        r = (r*b)%p
        c = (b*b)%p
        t = (t*c)%p
        m = i
    return r

def strong_pseudo_prime(base):
    """
    Construct a strong pseudoprime (composite number) that passes Miller-Rabin test
    for ALL prime bases < 'base'. This is the core cryptographic construction used
    to solve the challenge.
    
    Theory: By carefully choosing residues modulo 4*p for each small prime p (using
    Legendre symbol conditions) and additional moduli from fixed k values, we force
    the Miller-Rabin conditions to hold even though the final number is composite.
    The system is solved via CRT to obtain a large pseudoprime in the required range.
    """
    primes = generate_basis(base)
    S_a = []
    for prime in primes:
        f = set()
        for i in generate_basis(200*prime)[1:]:
            if lengendre(prime, i) == i - 1:
                f.add(i % (4*prime))
        S_a.append(list(f))
    
    # Fixed auxiliary moduli used in the construction
    k = [1, 998244353, 233]
    p_Set = []
    for i, s in enumerate(S_a):
        prime = primes[i]
        m = prime*4
        current_set = set(s)
        for k_item in range(1,3):
            new_set = set()
            for f_item in s:
                if (inv(k[k_item], m)*(f_item + k[k_item] - 1)) % 4 == 3:
                    new_set.add((inv(k[k_item], m)*(f_item + k[k_item] - 1)) % m)
            current_set = current_set.intersection(new_set)
        p_Set.append((current_set))
   
    # Try all combinations of residues via itertools.product
    for item in itertools.product(*p_Set):
        residues = []
        modulus = []
        for i, j in enumerate(item):
            residues.append(j)
            modulus.append(primes[i]*4)
        # Add extra congruences from fixed k values
        residues.append(k[1] - inv(k[2], k[1]))
        modulus.append(k[1])
        residues.append(k[2] - inv(k[1], k[2]))
        modulus.append(k[2])
       
        psu, mod = crt1(residues, modulus)
        found = False
        if not psu == -1:
            cur_t = 2**73*mod + psu
            # Search for a suitable starting point
            for i in tqdm(range(100000)):
                # Note: isPrime() is not defined in the original script.
                # In practice, replace with miller_rabin(cur_t, some_base) or a deterministic test.
                if isPrime(cur_t):   # Placeholder - replace with actual primality check if needed
                    fin = cur_t
                    facs = [cur_t]
                    for j in range(1, 3):
                        facs.append(k[j]*(cur_t-1)+1)
                        fin = fin * (k[j]*(cur_t-1)+1)
                    if miller_rabin(fin, base):
                        print(isPrime(fin))
                        print(fin)
                        print(facs)
                        if fin.bit_length() >= 600 and fin.bit_length() <= 900:
                            found = True
                            break
                cur_t += mod
        if found:
            break
    return fin, facs, primes

# =============================================================================
# MAIN EXECUTION - SEND SOLUTION TO SERVER
# =============================================================================
pseudoPrime, pseudoFac, base = strong_pseudo_prime(64)

print(readline())  # Read initial challenge description from server

request = {
    "prime": pseudoPrime,
    "base": pseudoFac[-1]   # Send one of the constructed factors as the base
}
json_send(request)
response = json_recv()
print(response)  # Expected: flag or success message from the server