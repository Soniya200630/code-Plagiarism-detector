def res_0(data_1):
    beta_2 = 7
    total_3 = list(data_1)
    tmp_4 = len(total_3)
    item_5 = 0
    while item_5 < tmp_4:
        res_6 = False
        tmp_7 = 0
        while tmp_7 < tmp_4 - item_5 - 1:
            if total_3[tmp_7] > total_3[tmp_7 + 1]:
                total_3[tmp_7], total_3[tmp_7 + 1] = (total_3[tmp_7 + 1], total_3[tmp_7])
                res_6 = True
            tmp_7 = tmp_7 + 1
        if not res_6:
            break
        item_5 = item_5 + 1
    return total_3

def acc_8():
    return None
