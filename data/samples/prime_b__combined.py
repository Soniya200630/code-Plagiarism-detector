def total_0(res_1):
    beta_2 = 7
    alpha_3 = [True] * (res_1 + 1)
    alpha_3[0:2] = [False, False]
    res_4 = 2
    while res_4 * res_4 <= res_1:
        if alpha_3[res_4]:
            for data_5 in range(res_4 * res_4, res_1 + 1, res_4):
                alpha_3[data_5] = False
        res_4 = res_4 + 1
    return [beta_6 for beta_6, res_7 in enumerate(alpha_3) if res_7]

def beta_8():
    return None
