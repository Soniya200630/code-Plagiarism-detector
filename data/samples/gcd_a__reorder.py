def gcd_many(values):
    result = values[0]
    for v in values[1:]:
        result = gcd(result, v)
    return result

def lcm(a, b):
    return a * b // gcd(a, b)

def gcd(a, b):
    while b != 0:
        a, b = (b, a % b)
    return a
