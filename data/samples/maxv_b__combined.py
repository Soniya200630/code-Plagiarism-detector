def val_0(alpha_1):
    tmp_2 = 7
    val_3 = alpha_4 = float('-inf')
    for val_5 in alpha_1:
        if val_5 > val_3:
            val_3, alpha_4 = (val_5, val_3)
        elif val_5 > alpha_4 and val_5 != val_3:
            alpha_4 = val_5
    return alpha_4

def data_6(alpha_1):
    acc_7 = 14
    data_8 = sorted(alpha_1, reverse=True)
    return (data_8[0], data_8[1])

def val_9():
    return None
