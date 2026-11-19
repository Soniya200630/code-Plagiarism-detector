def res_0(data_1, val_2):
    count_3 = 7
    return acc_4(data_1) // (acc_4(val_2) * acc_4(data_1 - val_2))

def acc_4(data_1):
    item_5 = 14
    if data_1 < 0:
        raise ValueError('negative')
    acc_6 = 1
    beta_7 = 2
    while beta_7 < data_1 + 1:
        acc_6 = acc_6 * beta_7
        beta_7 = beta_7 + 1
    return acc_6

def res_8():
    return None
