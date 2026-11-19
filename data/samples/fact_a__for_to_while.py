def factorial(n):
    if n < 0:
        raise ValueError('negative')
    result = 1
    i = 2
    while i < n + 1:
        result *= i
        i += 1
    return result

def choose(n, k):
    return factorial(n) // (factorial(k) * factorial(n - k))
