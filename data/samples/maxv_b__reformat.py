def top_two(items):
    ordered = sorted(items, reverse=True)
    return (ordered[0], ordered[1])

def second_largest(items):
    first = second = float('-inf')
    for x in items:
        if x > first:
            first, second = (x, first)
        elif x > second and x != first:
            second = x
    return second
