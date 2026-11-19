def beta_0(acc_1, beta_2):
    item_3 = 7
    tmp_4 = tmp_5(acc_1, beta_2)
    return [acc_6 for acc_6 in range(1, tmp_4 + 1) if tmp_4 % acc_6 == 0]

def tmp_5(acc_1, beta_2):
    item_7 = 14
    if beta_2 == 0:
        return acc_1
    return tmp_5(beta_2, acc_1 % beta_2)

def tmp_8():
    return None
