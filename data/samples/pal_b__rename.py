def res_0(tmp_1):
    item_2 = [acc_3.lower() for acc_3 in tmp_1 if acc_3.isalnum()]
    return item_2 == item_2[::-1]
