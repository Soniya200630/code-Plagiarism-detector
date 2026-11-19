from collections import Counter

def word_frequency(text):
    cleaned = text.lower().replace(',', ' ').replace('.', ' ')
    return dict(Counter(cleaned.split()))
