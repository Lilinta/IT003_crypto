# Open the file containing the 2048-bit numbers in read mode
with open("out_Modular_Square_Root.txt", "r") as file:
    # Read the first line and assign it to 'a'
    a = file.readline()
    # Read the second line and assign it to 'p'
    p = file.readline()

# Convert the string inputs (which may include newline characters) into integers
a = int(a)
p = int(p)

def legendre(a, p):
    """Calculates the Legendre symbol to check for quadratic residues."""
    # Returns a^((p-1)/2) mod p. The result is 1 if 'a' has a square root.
    return pow(a, (p - 1) // 2, p)

def tonelli_shanks(n, p):
    """Tonelli-Shanks algorithm to find r such that r^2 = n mod p"""
    
    # Handle base and edge cases

    # The square root of 0 is always 0
    if n == 0:
        return 0

    # Edge case for the only even prime number 
    if p == 2:
        return n % 2

    # If n is not a quadratic residue, it has no square root
    if legendre(n, p) != 1:
        return "NoSquareRoot"
    # If p = 3 mod 4, use the simple formula from the previous challenge
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)

    # Step 1: Factor out powers of 2 from p - 1. 
    # Find Q and S such that p - 1 = Q * 2^S (with Q being an odd number)
    Q = p - 1
    S = 0
    while Q % 2 == 0:
        Q //= 2
        S += 1

    # Step 2: Find a quadratic non-residue z (acts as a tuning gear)
    z = 2
    while legendre(z, p) != p - 1:
        z += 1

    # Step 3: Initialize variables for the main loop

    # M (Exponent Bound): Tracks the maximum power of 2 needed to make t == 1. 
    # It strictly decreases in each iteration, guaranteeing the loop will finish.
    M = S 
    
    # c (Correction Factor): The "tuning gear" derived from the non-residue z. 
    # It is used to systematically fix the error term 't' and update 'R'.
    c = pow(z, Q, p)
    
    # t (Error Term: Measures how far R is from the true root.)
    # The mathematical invariant R^2 == t * n (mod p) is always maintained.
    # The ultimate goal of the loop is to force t to become 1.
    t = pow(n, Q, p)
    
    # R (Current Root Guess): The working approximation of the square root. 
    # When the loop manages to make t == 1, R becomes the exact square root.
    R = pow(n, (Q + 1) // 2, p)
    
    # Main loop: iterate until t reaches 1
    while t != 0 and t != 1:
        t2i = t
        i = 0
        
        # Repeatedly square t to find the lowest i (0 < i < M) such that t^(2^i) = 1
        for i in range(1, M):
            t2i = (t2i * t2i) % p
            if t2i == 1:
                break

        # Update the variables (rotate the gear) to reduce M for the next iteration
        b = pow(c, 1 << (M - i - 1), p) # Note: 1 << x is a bitwise shift, equivalent to 2^x
        M = i
        c = (b * b) % p
        t = (t * c) % p
        R = (R * b) % p

    # Return the successfully calculated square root
    return R

# ==========================================
# EXECUTION AND FLAG GENERATION
# ==========================================

# Calculate one of the square roots using the algorithm
root1 = tonelli_shanks(a, p)

# Calculate the second possible root (since (-r)^2 = r^2 mod p)
root2 = p - root1

# Select the smaller root as requested by the challenge description
flag = min(root1, root2)

# Print the final flag format
print(flag)