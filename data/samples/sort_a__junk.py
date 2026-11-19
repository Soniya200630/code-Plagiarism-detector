def bubble_sort(items):
    unused_1 = 7
    data = list(items)
    n = len(data)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = (data[j + 1], data[j])
                swapped = True
        if not swapped:
            break
    return data

def helper_unused():
    return None
