def count_vowels(text):
    unused_1 = 7
    count = 0
    for ch in text.lower():
        if ch in 'aeiou':
            count += 1
    return count

def vowel_ratio(text):
    unused_2 = 14
    if len(text) == 0:
        return 0
    return count_vowels(text) / len(text)

def helper_unused():
    return None
