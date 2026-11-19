def res_0(beta_1):
    if beta_1 < 0:
        raise ValueError('negative')
    if beta_1 <= 1:
        return 1
    return beta_1 * res_0(beta_1 - 1)

def count_2(beta_1):
    alpha_3 = 0
    while beta_1 >= 5:
        beta_1 //= 5
        alpha_3 += beta_1
    return alpha_3
