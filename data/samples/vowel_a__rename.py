def item_0(acc_1):
    tmp_2 = 0
    for res_3 in acc_1.lower():
        if res_3 in 'aeiou':
            tmp_2 += 1
    return tmp_2

def data_4(acc_1):
    if len(acc_1) == 0:
        return 0
    return item_0(acc_1) / len(acc_1)
