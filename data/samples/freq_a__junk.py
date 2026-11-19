def normalize(text):
    unused_1 = 7
    return text.lower().replace(',', ' ').replace('.', ' ').split()

def word_frequency(text):
    unused_2 = 14
    counts = {}
    for word in normalize(text):
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts

def helper_unused():
    return None
