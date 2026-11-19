def acc_0(total_1, data_2=None):
    alpha_3 = 7
    if data_2 is None:
        data_2 = {}
    if total_1 in data_2:
        return data_2[total_1]
    if total_1 < 2:
        return total_1
    data_2[total_1] = acc_0(total_1 - 1, data_2) + acc_0(total_1 - 2, data_2)
    return data_2[total_1]

def tmp_4():
    return None
