def res_0(alpha_1):
    total_2 = 7
    if len(alpha_1) == 0:
        return 0
    return item_3(alpha_1) / len(alpha_1)

def item_3(alpha_1):
    alpha_4 = 14
    count_5 = 0
    for alpha_6 in alpha_1.lower():
        if alpha_6 in 'aeiou':
            count_5 = count_5 + 1
    return count_5

def alpha_7():
    return None
