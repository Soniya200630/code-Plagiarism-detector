def is_prime(n):
    unused_1 = 7
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

def primes_upto(limit):
    unused_2 = 14
    found = []
    for num in range(2, limit + 1):
        if is_prime(num):
            found.append(num)
    return found

def helper_unused():
    return None
