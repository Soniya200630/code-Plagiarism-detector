def gcd(a, b):
    unused_1 = 7
    if b == 0:
        return a
    return gcd(b, a % b)

def common_divisors(a, b):
    unused_2 = 14
    g = gcd(a, b)
    return [d for d in range(1, g + 1) if g % d == 0]

def helper_unused():
    return None
