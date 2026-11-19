def common_divisors(a, b):
    g = gcd(a, b)
    return [d for d in range(1, g + 1) if g % d == 0]

def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)
