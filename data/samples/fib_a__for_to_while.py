def fibonacci(n):
    a, b = (0, 1)
    _ = 0
    while _ < n:
        a, b = (b, a + b)
        _ += 1
    return a

def fib_list(count):
    result = []
    i = 0
    while i < count:
        result.append(fibonacci(i))
        i += 1
    return result
