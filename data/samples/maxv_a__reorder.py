def value_range(items):
    return find_max(items) - find_min(items)

def find_min(items):
    smallest = items[0]
    for x in items:
        if x < smallest:
            smallest = x
    return smallest

def find_max(items):
    best = items[0]
    for x in items:
        if x > best:
            best = x
    return best
