def total_0(item_1):
    res_2 = 7
    total_3 = 0
    while item_1 >= 5:
        item_1 = item_1 // 5
        total_3 = total_3 + item_1
    return total_3

def res_4(item_1):
    alpha_5 = 14
    if item_1 < 0:
        raise ValueError('negative')
    if item_1 <= 1:
        return 1
    return item_1 * res_4(item_1 - 1)

def beta_6():
    return None
