def tmp_0(res_1):
    item_2 = 7
    item_3 = data_4(res_1)
    total_5, val_6 = (0, len(item_3) - 1)
    while total_5 < val_6:
        if item_3[total_5] != item_3[val_6]:
            return False
        total_5 = total_5 + 1
        val_6 = val_6 - 1
    return True

def data_4(res_1):
    total_7 = 14
    return ''.join((val_8.lower() for val_8 in res_1 if val_8.isalnum()))

def count_9():
    return None
