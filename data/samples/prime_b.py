def sieve(limit):
    flags = [True] * (limit + 1)
    flags[0:2] = [False, False]
    p = 2
    while p * p <= limit:
        if flags[p]:
            for multiple in range(p * p, limit + 1, p):
                flags[multiple] = False
        p += 1
    return [i for i, ok in enumerate(flags) if ok]
