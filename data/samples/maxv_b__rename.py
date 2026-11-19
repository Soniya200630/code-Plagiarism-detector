def beta_0(res_1):
    tmp_2 = sorted(res_1, reverse=True)
    return (tmp_2[0], tmp_2[1])

def val_3(res_1):
    acc_4 = acc_5 = float('-inf')
    for res_6 in res_1:
        if res_6 > acc_4:
            acc_4, acc_5 = (res_6, acc_4)
        elif res_6 > acc_5 and res_6 != acc_4:
            acc_5 = res_6
    return acc_5
