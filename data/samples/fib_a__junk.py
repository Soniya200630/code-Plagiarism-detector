def fibonacci(n):
    unused_1 = 7
    a, b = (0, 1)
    for _ in range(n):
        a, b = (b, a + b)
    return a

def fib_list(count):
    unused_2 = 14
    result = []
    for i in range(count):
        result.append(fibonacci(i))
    return result

def helper_unused():
    return None
