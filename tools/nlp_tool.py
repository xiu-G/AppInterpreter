import string
from spiral import ronin
from math import log
import enchant
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk import pos_tag
porter_stemmer= PorterStemmer()
SPECIAL_WORD_LIST = ['gsm','sms','sim','dns','vpn','usb','gps','url', 'http','sd','mic','tel','mms', 'ad','gsm','dfcp','icc','ims', 'mmtel']
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


def get_lemmatize_data(words):
    values=[(words,tag_classes) for (words,tag_classes) in lemmatize_all(words)]
    words, tags=  [], []
    for k1, k2 in values:
        words.append(k1)
        tags.append(k2)
    return words, tags

def lemmatize_all(words):
    wnl = WordNetLemmatizer()
    for word, tag in pos_tag(words):
        if word in SPECIAL_WORD_LIST:
            yield (word, 'NN')
        elif word.endswith('ing') or word.endswith('ed'):
            yield (wnl.lemmatize(word, pos='v'), 'VB')
        elif tag.startswith('NN'):
            yield (wnl.lemmatize(word, pos='n'), 'NN')
        elif tag.startswith('VB'):
            yield (wnl.lemmatize(word, pos='v'), 'VB')
        elif tag.startswith('JJ'):
            yield (wnl.lemmatize(word, pos='a'), 'JJ')
        elif tag.startswith('R'):
            yield (wnl.lemmatize(word, pos='r'), 'R')
        else:
            yield (word, '')

def deal_words(strings, split_dict={}):
    strings = ' '.join(ronin.split(strings))
    string_items = strings.translate(str.maketrans('', '', string.punctuation)).lower().split()
    d = enchant.Dict("en_US")
    new_items = []
    for item in string_items:
        if item in SPECIAL_WORD_LIST:
            new_items.append(item)
            split_dict[item] = True
            continue
        if item in split_dict:
            if not split_dict[item]:
                continue
            new_items.append(item)
        else:
            if not d.check(item) or item.isdigit():
                split_dict[item] = False
                continue
            else:
                split_dict[item] = True
                new_items.append(item)
    return new_items