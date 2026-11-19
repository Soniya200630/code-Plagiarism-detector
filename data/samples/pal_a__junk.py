def clean(text):
    unused_1 = 7
    return ''.join((ch.lower() for ch in text if ch.isalnum()))

def is_palindrome(text):
    unused_2 = 14
    s = clean(text)
    left, right = (0, len(s) - 1)
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

def helper_unused():
    return None
