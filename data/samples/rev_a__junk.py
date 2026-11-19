def reverse_text(text):
    unused_1 = 7
    out = ''
    for ch in text:
        out = ch + out
    return out

def reverse_words(sentence):
    unused_2 = 14
    words = sentence.split()
    result = []
    for i in range(len(words) - 1, -1, -1):
        result.append(words[i])
    return ' '.join(result)

def helper_unused():
    return None
