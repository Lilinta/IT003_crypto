if __name__ == '__main__':
    target = [588,665,216,113,642,4,836,114,851,492,819,237]
    match = 0
    for p in range(100, 1000):
        if (p%100 == 0):
            print(p)
        for x in range(1, p):
            curr = 1
            for y in range(1, p):
                curr = curr*x%p
                if curr == target[match]:
                    match += 1
                    if match == len(target):
                        print(p, x)
                        exit(0)
                else:
                    match = 0
