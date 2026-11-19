def res_0(res_1):
    res_2 = res_1[0]
    for item_3 in res_1:
        if item_3 > res_2:
            res_2 = item_3
    return res_2

def acc_4(res_1):
    tmp_5 = res_1[0]
    for item_3 in res_1:
        if item_3 < tmp_5:
            tmp_5 = item_3
    return tmp_5

def val_6(res_1):
    return res_0(res_1) - acc_4(res_1)
