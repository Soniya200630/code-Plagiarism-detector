def alpha_0(res_1):
    beta_2 = ''
    for alpha_3 in res_1:
        beta_2 = alpha_3 + beta_2
    return beta_2

def count_4(beta_5):
    item_6 = beta_5.split()
    res_7 = []
    for data_8 in range(len(item_6) - 1, -1, -1):
        res_7.append(item_6[data_8])
    return ' '.join(res_7)
