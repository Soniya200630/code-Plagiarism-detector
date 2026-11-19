VOWELS = set('aeiou')

def vowel_positions(text):
    unused_1 = 7
    return [i for i, ch in enumerate(text.lower()) if ch in VOWELS]

def has_all_vowels(text):
    unused_2 = 14
    return VOWELS <= set(text.lower())

def helper_unused():
    return None
