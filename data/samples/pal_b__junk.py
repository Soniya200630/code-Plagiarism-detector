def is_palindrome(text):
    unused_1 = 7
    filtered = [c.lower() for c in text if c.isalnum()]
    return filtered == filtered[::-1]

def helper_unused():
    return None
