import string
from spiral import ronin
from math import log
words_by_frequency = 'words-by-frequency.txt'
words = open(words_by_frequency).read().split() # 有特殊字符的话直接在其中添加
wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
maxword = max(len(x) for x in words)

def is_number(s):
    try: 
        float(s)
        return True
    except ValueError: 
        pass 
    try:
        import unicodedata 
        for i in s:
            unicodedata.numeric(i)
        return True
    except (TypeError, ValueError):
        pass
    return False

def infer_spaces(s, wordcost, maxword):
    '''Uses dynamic programming to infer the location of spaces in a string without spaces.
    .使用动态编程来推断不带空格的字符串中空格的位置。'''
    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
        return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)

    # Build the cost array.
    cost = [0]
    for i in range(1,len(s)+1):
        c,k = best_match(i)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i>0:
        c,k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))

def split_string(sentence):
    strings = ronin.split(sentence)
    tmp_string = []
    for i, s in enumerate(strings):
        if is_number(s):
            strings[i]=''
        else:
            split_result = infer_spaces(s.lower(), wordcost, maxword)
            if len(split_result.split()) > 3:
                tmp_string.append(s)
            else:
                tmp_string += split_result.split()
    strings = ' '.join(tmp_string).strip()
    if not strings:
        return ''
    text = strings.translate(str.maketrans('', '', string.punctuation)).lower()
    return text