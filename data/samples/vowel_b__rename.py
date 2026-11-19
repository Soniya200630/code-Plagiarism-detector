total_0 = set('aeiou')

def acc_1(item_2):
    return [item_3 for item_3, tmp_4 in enumerate(item_2.lower()) if tmp_4 in total_0]

def alpha_5(item_2):
    return total_0 <= set(item_2.lower())
