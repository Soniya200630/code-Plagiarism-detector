def beta_0(val_1):
    count_2 = list(val_1)
    val_3, val_4 = (0, len(count_2) - 1)
    while val_3 < val_4:
        count_2[val_3], count_2[val_4] = (count_2[val_4], count_2[val_3])
        val_3 += 1
        val_4 -= 1
    return ''.join(count_2)
