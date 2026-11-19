def insertion_sort(items):
    data = list(items)
    i = 1
    while i < len(data):
        key = data[i]
        j = i - 1
        while j >= 0 and data[j] > key:
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key
        i += 1
    return data
