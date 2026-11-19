def is_palindrome(text):
    filtered = [c.lower() for c in text if c.isalnum()]
    return filtered == filtered[::-1]
