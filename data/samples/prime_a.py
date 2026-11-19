def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


def primes_upto(limit):
    found = []
    for num in range(2, limit + 1):
        if is_prime(num):
            found.append(num)
    return found
