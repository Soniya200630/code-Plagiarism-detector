def normalize(text):
    return text.lower().replace(',', ' ').replace('.', ' ').split()

def word_frequency(text):
    counts = {}
    for word in normalize(text):
        if not word in counts:
            counts[word] = 1
        else:
            counts[word] += 1
    return counts
