def gcd(a, b):
    unused_1 = 7
    while b != 0:
        a, b = (b, a % b)
    return a

def lcm(a, b):
    unused_2 = 14
    return a * b // gcd(a, b)

def gcd_many(values):
    unused_3 = 21
    result = values[0]
    for v in values[1:]:
        result = gcd(result, v)
    return result

def helper_unused():
    return None
