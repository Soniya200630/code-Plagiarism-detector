def vowel_ratio(text):
    if len(text) == 0:
        return 0
    return count_vowels(text) / len(text)

def count_vowels(text):
    count = 0
    for ch in text.lower():
        if ch in 'aeiou':
            count += 1
    return count
