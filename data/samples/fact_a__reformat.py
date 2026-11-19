def factorial(n):
    if n < 0:
        raise ValueError('negative')
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def choose(n, k):
    return factorial(n) // (factorial(k) * factorial(n - k))
