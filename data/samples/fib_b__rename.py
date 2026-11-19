def item_0(val_1, res_2=None):
    if res_2 is None:
        res_2 = {}
    if val_1 in res_2:
        return res_2[val_1]
    if val_1 < 2:
        return val_1
    res_2[val_1] = item_0(val_1 - 1, res_2) + item_0(val_1 - 2, res_2)
    return res_2[val_1]
