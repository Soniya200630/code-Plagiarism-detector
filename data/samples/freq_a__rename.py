def total_0(beta_1):
    return beta_1.lower().replace(',', ' ').replace('.', ' ').split()

def val_2(beta_1):
    val_3 = {}
    for total_4 in total_0(beta_1):
        if total_4 in val_3:
            val_3[total_4] += 1
        else:
            val_3[total_4] = 1
    return val_3
