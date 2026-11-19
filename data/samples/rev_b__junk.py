def reverse_text(text):
    unused_1 = 7
    chars = list(text)
    left, right = (0, len(chars) - 1)
    while left < right:
        chars[left], chars[right] = (chars[right], chars[left])
        left += 1
        right -= 1
    return ''.join(chars)

def helper_unused():
    return None
