def val_0(data_1):
    acc_2 = list(data_1)
    count_3 = len(acc_2)
    for tmp_4 in range(count_3):
        count_5 = False
        for count_6 in range(0, count_3 - tmp_4 - 1):
            if acc_2[count_6] > acc_2[count_6 + 1]:
                acc_2[count_6], acc_2[count_6 + 1] = (acc_2[count_6 + 1], acc_2[count_6])
                count_5 = True
        if not count_5:
            break
    return acc_2
