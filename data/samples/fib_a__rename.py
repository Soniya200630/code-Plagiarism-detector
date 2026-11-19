def beta_0(alpha_1):
    data_2, res_3 = (0, 1)
    for res_4 in range(alpha_1):
        data_2, res_3 = (res_3, data_2 + res_3)
    return data_2

def tmp_5(beta_6):
    item_7 = []
    for beta_8 in range(beta_6):
        item_7.append(beta_0(beta_8))
    return item_7
