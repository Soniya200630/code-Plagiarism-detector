def is_palindrome(text):
    s = clean(text)
    left, right = (0, len(s) - 1)
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

def clean(text):
    return ''.join((ch.lower() for ch in text if ch.isalnum()))
