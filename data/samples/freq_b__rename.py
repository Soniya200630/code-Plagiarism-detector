from collections import Counter

def count_0(beta_1):
    data_2 = beta_1.lower().replace(',', ' ').replace('.', ' ')
    return dict(Counter(data_2.split()))
