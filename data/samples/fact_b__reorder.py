def trailing_zeros(n):
    count = 0
    while n >= 5:
        n //= 5
        count += n
    return count

def fact(n):
    if n < 0:
        raise ValueError('negative')
    if n <= 1:
        return 1
    return n * fact(n - 1)
