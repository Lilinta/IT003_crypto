a = 66528
b = 52920
def gcd(a,b):
    while(a % b):
        if a < b :
            a,b = b,a
        a -= b
    return b
print(gcd(a,b))