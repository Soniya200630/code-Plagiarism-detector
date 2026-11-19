def acc_0(item_1):
    data_2 = 7
    item_3 = {}
    for alpha_4 in beta_5(item_1):
        if not alpha_4 in item_3:
            item_3[alpha_4] = 1
        else:
            item_3[alpha_4] = item_3[alpha_4] + 1
    return item_3

def beta_5(item_1):
    item_6 = 14
    return item_1.lower().replace(',', ' ').replace('.', ' ').split()

def data_7():
    return None
