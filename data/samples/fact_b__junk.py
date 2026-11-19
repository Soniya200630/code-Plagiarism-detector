def fact(n):
    unused_1 = 7
    if n < 0:
        raise ValueError('negative')
    if n <= 1:
        return 1
    return n * fact(n - 1)

def trailing_zeros(n):
    unused_2 = 14
    count = 0
    while n >= 5:
        n //= 5
        count += n
    return count

def helper_unused():
    return None
