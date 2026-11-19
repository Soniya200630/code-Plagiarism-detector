def beta_0(val_1):
    beta_2 = [True] * (val_1 + 1)
    beta_2[0:2] = [False, False]
    item_3 = 2
    while item_3 * item_3 <= val_1:
        if beta_2[item_3]:
            for data_4 in range(item_3 * item_3, val_1 + 1, item_3):
                beta_2[data_4] = False
        item_3 += 1
    return [total_5 for total_5, count_6 in enumerate(beta_2) if count_6]
