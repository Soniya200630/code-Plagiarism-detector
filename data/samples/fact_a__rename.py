def data_0(item_1):
    if item_1 < 0:
        raise ValueError('negative')
    total_2 = 1
    for val_3 in range(2, item_1 + 1):
        total_2 *= val_3
    return total_2

def res_4(item_1, item_5):
    return data_0(item_1) // (data_0(item_5) * data_0(item_1 - item_5))
