VOWELS = set('aeiou')

def vowel_positions(text):
    return [i for i, ch in enumerate(text.lower()) if ch in VOWELS]

def has_all_vowels(text):
    return VOWELS <= set(text.lower())
