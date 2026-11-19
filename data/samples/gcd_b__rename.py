def data_0(res_1, alpha_2):
    if alpha_2 == 0:
        return res_1
    return data_0(alpha_2, res_1 % alpha_2)

def res_3(res_1, alpha_2):
    total_4 = data_0(res_1, alpha_2)
    return [beta_5 for beta_5 in range(1, total_4 + 1) if total_4 % beta_5 == 0]
