def reverse_words(sentence):
    words = sentence.split()
    result = []
    for i in range(len(words) - 1, -1, -1):
        result.append(words[i])
    return ' '.join(result)

def reverse_text(text):
    out = ''
    for ch in text:
        out = ch + out
    return out
