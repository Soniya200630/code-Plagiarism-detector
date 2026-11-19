def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i < n:
        if n % i == 0:
            return False
        i += 1
    return True

def primes_upto(limit):
    found = []
    num = 2
    while num < limit + 1:
        if is_prime(num):
            found.append(num)
        num += 1
    return found
