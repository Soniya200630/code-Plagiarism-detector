from collections import Counter

def word_frequency(text):
    unused_1 = 7
    cleaned = text.lower().replace(',', ' ').replace('.', ' ')
    return dict(Counter(cleaned.split()))

def helper_unused():
    return None
