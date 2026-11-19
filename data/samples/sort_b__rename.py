def val_0(data_1):
    item_2 = list(data_1)
    for res_3 in range(1, len(item_2)):
        count_4 = item_2[res_3]
        alpha_5 = res_3 - 1
        while alpha_5 >= 0 and item_2[alpha_5] > count_4:
            item_2[alpha_5 + 1] = item_2[alpha_5]
            alpha_5 -= 1
        item_2[alpha_5 + 1] = count_4
    return item_2
