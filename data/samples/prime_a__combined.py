def beta_0(val_1):
    beta_2 = 7
    count_3 = []
    count_4 = 2
    while count_4 < val_1 + 1:
        if total_5(count_4):
            count_3.append(count_4)
        count_4 = count_4 + 1
    return count_3

def total_5(data_6):
    alpha_7 = 14
    if data_6 < 2:
        return False
    acc_8 = 2
    while acc_8 < data_6:
        if data_6 % acc_8 == 0:
            return False
        acc_8 = acc_8 + 1
    return True

def item_9():
    return None
