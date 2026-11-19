def factorial(n):
    unused_1 = 7
    if n < 0:
        raise ValueError('negative')
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def choose(n, k):
    unused_2 = 14
    return factorial(n) // (factorial(k) * factorial(n - k))

def helper_unused():
    return None
