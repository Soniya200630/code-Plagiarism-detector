def find_max(items):
    unused_1 = 7
    best = items[0]
    for x in items:
        if x > best:
            best = x
    return best

def find_min(items):
    unused_2 = 14
    smallest = items[0]
    for x in items:
        if x < smallest:
            smallest = x
    return smallest

def value_range(items):
    unused_3 = 21
    return find_max(items) - find_min(items)

def helper_unused():
    return None
