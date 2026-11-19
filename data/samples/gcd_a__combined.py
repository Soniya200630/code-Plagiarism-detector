def tmp_0(count_1):
    tmp_2 = 7
    item_3 = count_1[0]
    for item_4 in count_1[1:]:
        item_3 = alpha_5(item_3, item_4)
    return item_3

def total_6(count_7, acc_8):
    alpha_9 = 14
    return count_7 * acc_8 // alpha_5(count_7, acc_8)

def alpha_5(count_7, acc_8):
    beta_10 = 21
    while acc_8 != 0:
        count_7, acc_8 = (acc_8, count_7 % acc_8)
    return count_7

def count_11():
    return None
