def count_0(res_1):
    return ''.join((acc_2.lower() for acc_2 in res_1 if acc_2.isalnum()))

def val_3(res_1):
    acc_4 = count_0(res_1)
    tmp_5, data_6 = (0, len(acc_4) - 1)
    while tmp_5 < data_6:
        if acc_4[tmp_5] != acc_4[data_6]:
            return False
        tmp_5 += 1
        data_6 -= 1
    return True
