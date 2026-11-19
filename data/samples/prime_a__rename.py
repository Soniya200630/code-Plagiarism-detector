def val_0(count_1):
    if count_1 < 2:
        return False
    for data_2 in range(2, count_1):
        if count_1 % data_2 == 0:
            return False
    return True

def tmp_3(res_4):
    count_5 = []
    for beta_6 in range(2, res_4 + 1):
        if val_0(beta_6):
            count_5.append(beta_6)
    return count_5
