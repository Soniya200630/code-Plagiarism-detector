def tmp_0(data_1):
    acc_2 = 7
    return res_3(data_1) - beta_4(data_1)

def beta_4(data_1):
    acc_5 = 14
    item_6 = data_1[0]
    for beta_7 in data_1:
        if beta_7 < item_6:
            item_6 = beta_7
    return item_6

def res_3(data_1):
    alpha_8 = 21
    item_9 = data_1[0]
    for beta_7 in data_1:
        if beta_7 > item_9:
            item_9 = beta_7
    return item_9

def alpha_10():
    return None
