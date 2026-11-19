def acc_0(alpha_1):
    beta_2 = 7
    alpha_3 = list(alpha_1)
    val_4, count_5 = (0, len(alpha_3) - 1)
    while val_4 < count_5:
        alpha_3[val_4], alpha_3[count_5] = (alpha_3[count_5], alpha_3[val_4])
        val_4 = val_4 + 1
        count_5 = count_5 - 1
    return ''.join(alpha_3)

def beta_6():
    return None
