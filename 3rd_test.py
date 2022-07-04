from behavior_extraction.get_suspicious_behavior import get_widget_string
from textblob import TextBlob
from nltk import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from tools import basic_tool, nlp_tool
# keywordSet = {"don't","never", "nothing", "nowhere", "noone", "none", "not",
#                   "hasn't","hadn't","can't","couldn't","shouldn't","won't",
#                   "wouldn't","don't","doesn't","didn't","isn't","aren't","ain't", 'no'}
keywordSet = ["n't", 'not', 'nothing', 'none', 'nowhere', 'no', 'noone', 'never', 'non', 'un', 'never', 'without']


sid = SentimentIntensityAnalyzer()

def word_polarity2(test_subset):
    pos_word_list=[]
    neu_word_list=[]
    neg_word_list=[]
    for word in test_subset:
        if (sid.polarity_scores(word)['compound']) >= 0.5:
            pos_word_list.append(word)
        elif (sid.polarity_scores(word)['compound']) <= -0.5:
            neg_word_list.append(word)
        else:
            neu_word_list.append(word)       
    return neg_word_list

def word_polarity(test_subset):
    pos_word_list=[]
    neu_word_list=[]
    neg_word_list=[]

    for word in test_subset:               
        testimonial = TextBlob(word)
        if testimonial.sentiment.polarity >= 0.5:
            pos_word_list.append(word)
        elif testimonial.sentiment.polarity <= -0.2:
            neg_word_list.append(word)
        else:
            neu_word_list.append(word)

    # print('Positive :',pos_word_list)        
    # print('Neutral :',neu_word_list)    
    # print('Negative :',neg_word_list)      
    return neg_word_list

def print_negative_sentences(contents, text_dic):
    for line in contents:
        if '/' in line or '_' in line:
            continue
        new_line = nlp_tool.split_string_del_some_marks(line)
        new_words = word_tokenize(new_line)
        if len(new_words) > 20:
            continue
        neg_word_list = word_polarity(new_words)
        neg_word_list2 = word_polarity2(new_words)
        neg_word_list3 = []
        for word in new_words:
            if word in keywordSet:
                neg_word_list3.append(word)
        
        # if len(neg_word_list) >= 1:
        #     print(line)
        # if len(neg_word_list2) >= 1:
        #     print(line)
        # if len(neg_word_list3) >= 1:
        #     print(line)
        if (len(neg_word_list) + len(neg_word_list3))>=2 or (len(neg_word_list2) + len(neg_word_list3))>= 2:
            # print(line)
            if line not in text_dic:
                text_dic[line] = ''

if __name__ == '__main__':
    text_dir = 'data/strings'
    files = basic_tool.getAllFiles(text_dir, [], '')
    text_dic = {}
    for f in files:
        if f.endswith('.txt'):
            contents = list(basic_tool.read_json(basic_tool.readContentText(f)).keys())
        else:
            contents = list(basic_tool.read_json(basic_tool.readContentText(f)).keys())
        print_negative_sentences(contents, text_dic)
    for key in text_dic:
        print(key)



 