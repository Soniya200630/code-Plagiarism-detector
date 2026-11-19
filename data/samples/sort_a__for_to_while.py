def bubble_sort(items):
    data = list(items)
    n = len(data)
    i = 0
    while i < n:
        swapped = False
        j = 0
        while j < n - i - 1:
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = (data[j + 1], data[j])
                swapped = True
            j += 1
        if not swapped:
            break
        i += 1
    return data
