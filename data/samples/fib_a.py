def fibonacci(n):
    # returns the nth fibonacci number iteratively
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fib_list(count):
    result = []
    for i in range(count):
        result.append(fibonacci(i))
    return result
