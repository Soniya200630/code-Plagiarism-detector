def item_0(tmp_1, item_2):
    while item_2 != 0:
        tmp_1, item_2 = (item_2, tmp_1 % item_2)
    return tmp_1

def beta_3(tmp_1, item_2):
    return tmp_1 * item_2 // item_0(tmp_1, item_2)

def data_4(item_5):
    total_6 = item_5[0]
    for res_7 in item_5[1:]:
        total_6 = item_0(total_6, res_7)
    return total_6
