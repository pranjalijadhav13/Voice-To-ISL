from io import open
from conllu import parse_incr
import re
import warnings
from sklearn_crfsuite import CRF
import pickle
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.fx.all import resize
import os.path
import googletrans 
from googletrans import Translator
import time


from flask import Flask, render_template, request
app = Flask(__name__, static_folder = 'static')


@app.route('/')
def index():
   return render_template('index.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        result2 = request.form['Name']
        print(result2)
        isl_text, video_result = processing(result2)
        items = {
        'Speech To Text Conversion' : result2,
        'Text to Indian Sign Language' : isl_text[0]
        }
        print(isl_text[0])    
        return render_template("result.html",result = items, result1 = video_result)

def processing(result):
    translator = Translator()
    trans_result = translator.translate(result, dest ='en')
    print(result)
    print(trans_result)
    pos_tag_result = pos_tagging(trans_result.text)
    filter_result = filter(pos_tag_result)
    sentence_reordering_result = sentence_reordering(filter_result)
    stop_word_eliminator_result = stop_word_eliminate(sentence_reordering_result)
    lemmatize_result = convert_lemma(stop_word_eliminator_result)
    video_result = video_conversion(lemmatize_result)
    return lemmatize_result, video_result

def extract_features(sentence, index):
    return {
        'word':sentence[index],
        'is_first':index==0,
        'is_last':index ==len(sentence)-1,
        'is_capitalized':sentence[index][0].upper() == sentence[index][0],
        'is_all_caps': sentence[index].upper() == sentence[index],
        'is_all_lower': sentence[index].lower() == sentence[index],
        'is_alphanumeric': int(bool((re.match('^(?=.*[0-9]$)(?=.*[a-zA-Z])',sentence[index])))),
        'prefix-1':sentence[index][0],
        'prefix-2':sentence[index][:2],
        'prefix-3':sentence[index][:3],
        'prefix-3':sentence[index][:4],
        'suffix-1':sentence[index][-1],
        'suffix-2':sentence[index][-2:],
        'suffix-3':sentence[index][-3:],
        'suffix-3':sentence[index][-4:],
        'prev_word':'' if index == 0 else sentence[index-1],
        'next_word':'' if index < len(sentence) else sentence[index+1],
        'has_hyphen': '-' in sentence[index],
        'is_numeric': sentence[index].isdigit(),
        'capitals_inside': sentence[index][1:].lower() != sentence[index][1:]
    }


def pos_tagging(result):
    ud_filename = 'ud_crf_postagger.sav'
    crf_from_pickle = pickle.load(open(ud_filename, 'rb'))



    #First, we pass the sentence and quickly tokenize it.
    #sentences = ['She sells seashells by the seashore.', 'We should cross the road using zebra crossing.']
    # sentences=["Love thy nation!","The waiter leaves the hotel.","The tree has many leaves?", 'India is my country.','Which is my side??', 'How is my dress??']

    sentences = []
    sentences.append(result)

    ud_sents = []
    for sent in sentences:
        #sent = "Playing is my hobby."
        features = [extract_features(sent.split(), idx) for idx in range(len(sent.split()))]
        ud_results = crf_from_pickle.predict_single(features)

        #These line magics are just there to make it a neaty print, making a (word, POS) style print;
        ud_tups = [(sent.split()[idx], ud_results[idx]) for idx in range(len(sent.split()))]

        #The results come out here! Notice the difference in tags.
        ud_sents.append(ud_tups)
    print('\n\tPOS Tagging Done\t\n')
    for ud_tups in ud_sents:
        print(ud_tups)

    return ud_sents


punctuations = [',', '?', '!', '.']
def removePunctuations(word):
    new_word = ""
    for ch in word:
        if ch in punctuations:
            continue
        else:
            new_word = new_word + ch
    return new_word

def filter(ud_sents):
    print('\n\tPunctations Removed\t\n')
    new_sents = []
    for ud_tups in ud_sents:
        new_tups = []
        for tup in ud_tups:
            word = tup[0]
            tag = tup[1]
            word = word.lower()
            word = removePunctuations(word)
            new_tups.append((word, tag))
        new_sents.append(new_tups)
        print(new_tups)
    return new_sents

#ud_sents = filter(ud_sents)

def sentence_reordering(ud_sents):
    print('\n\tSentence Reorodering\t\n')
    #List to store reordered sentences
    reordered_sent_list = []

    #Looping through each sentence and reordeing it
    for sent in ud_sents:
        reordered_sent = []
        verbs = []
        for tup in sent:
            if tup[1] == 'VERB':
                verbs.append(tup)
            else:
                reordered_sent.append(tup)
        reordered_sent = reordered_sent + verbs
        start_word_tup = reordered_sent[0]
        if len(reordered_sent) >= 2:
            second_word_tuple = reordered_sent[1]

        if len(start_word_tup[0]) > 2:
            if ((start_word_tup[0][0] == 'w' or start_word_tup[0][0] == 'W' and start_word_tup[0][1] == 'h' or start_word_tup[0][1] == 'H') or (start_word_tup[0] == 'how' or start_word_tup[0] == 'How') or (start_word_tup[0] == 'how' or start_word_tup[0] == 'How')):
                if(len(reordered_sent) >= 2 and (start_word_tup[0] == 'how' or start_word_tup[0] == 'How') and (second_word_tuple[0] == 'much')):
                    reordered_sent.remove(start_word_tup)
                    reordered_sent.append(start_word_tup)
                    reordered_sent.remove(second_word_tuple)
                    reordered_sent.append(second_word_tuple)
                else:        
                    reordered_sent.remove(start_word_tup)
                    reordered_sent.append(start_word_tup)
        reordered_sent_list.append(reordered_sent)
    
    for sent in reordered_sent_list:
        print(sent)    
    return reordered_sent_list


def stop_word_eliminate(reordered_sent_list):
    print('\n\tStop Word Eliminator\t\n')

    stop_words = ['to', 'm', 'mustn', 'myself', 'a', 'because', 'don', 'had', "don't", "doesn't", 'once', 'is', 'own', "you've", 'each', 'into', 'both', "weren't", "mightn't", 'nor', 'are', 'were', 'too', 've', 'has', 'hasn', 'very', 'against', 'did',  'other', 'haven', "that'll", 'being', 'll', 'or', "hasn't", 'an', 'the', 'so', "didn't", 'was', 'shouldn', 'aren', "couldn't", 'by', 'ma', 'been', 'having', 's', 'as', "needn't", 'weren', "wasn't", "you'd", 'for', 'doesn', 'couldn', 'while', 'didn', "shouldn't", 'wouldn', 'am', 'and', 'off', 'such', 'hadn', "you'll", 'mightn', 'wasn', "isn't", 'but', "she's", 'isn', 'have', 'o', "hadn't", "won't", 'further', "shan't", 'doing', 'just', "mustn't", 'd', "aren't", "should've", 'be', 'does', 'shan', "it's", 'than', 'most',  'y', 'needn', "haven't", 're', 'if', "you're", "wouldn't", 't', 'ain', 'wow','alas','hurray','bravo','congratulations','congrats','ahem','aha','eureka']
    isl_sent_list = []
    for reordered_sent in reordered_sent_list:
        isl_sent = []
        for tup in reordered_sent:
            if stop_words.count(tup[0]) == 0:
                isl_sent.append(tup)
        isl_sent_list.append(isl_sent)

    for isl_sent in isl_sent_list: 
        print(isl_sent)

    return isl_sent_list


def inflect_noun_singular(word):
    irregular_dict = pickle.load(open('lemma_dictionary.sav','rb'))
    consonants = "bcdfghjklmnpqrstwxyz"
    vowels = "aeiou"
    word = str(word).lower()
    if len(word) <= 3:
        return word
    if word.endswith('i'):
        return word.replace('i', 'us')
    if word.endswith('s'):
        if len(word) > 3:
            #Leaves, wives, thieves
            if word.endswith('ves'):
                if len(word[:-3]) > 2:
                    return word.replace('ves','f')
                else:
                    return word.replace('ves','fe')
            #Parties, stories
            if word.endswith('ies'):
                return word.replace('ies','y')
            #Tomatoes, echoes
            if word.endswith('es'):
                if word.endswith('ses') and word[-4] in vowels:
                    return word[:-1]
                if word.endswith('zzes'):
                    return word.replace('zzes','z')
                if word.endswith('ees'):
                	return word[:-1]
                return word[:-2]
            if word.endswith('ys'):
                return word.replace('ys','y')
            if word.endswith('ss'):
                return word
            if word.endswith('us'):
                return word
        return word[:-1]
        if word in irregular_dict:
            return irregular_dict[word]
    return word


def lemmatize2(word, pos, lemma_dict_from_pickle, lemmatize_plurals=True):
    if word is None:
        return ''
    if pos is None:
        pos = ''
    word = str(word).lower()
    pos = str(pos).upper()
    print(word)
    if pos == "NOUN" and lemmatize_plurals:
        return inflect_noun_singular(word)
    if word in lemma_dict_from_pickle:
        if pos in lemma_dict_from_pickle[word]:
            return lemma_dict_from_pickle[word][pos]
    return word


def convert_lemma(isl_sent_list):
    lemma_filename = 'lemma_dictionary.sav'
    lemma_dict_from_pickle = pickle.load(open(lemma_filename, 'rb'))

    print('\n\tLemmatization\t\n')
    lema_isl_sent_list = []
    for isl_sent in isl_sent_list:
        print(isl_sent)
        isl_sent_lem = []
        for word_tuple in isl_sent:
            isl_sent_lem.append(lemmatize2(word_tuple[0], word_tuple[1], lemma_dict_from_pickle))
        lema_isl_sent_list.append(isl_sent_lem)

    for sent in lema_isl_sent_list:
        print(sent)

    return lema_isl_sent_list


def video_conversion(lema_isl_sent_list):

    print('\n\tVideo Conversion Module\t\n')
    start_time = time.time()
    for isl_sent in lema_isl_sent_list:
        video_array = []
        print(isl_sent)
        if len(isl_sent) >= 2:
            if isl_sent[-2] == "how" and isl_sent[-1] == "much":
                isl_sent[-2] = "how much"
                isl_sent.pop(-1)
        for word_tuple in isl_sent:
            #video_array.append(VideoFileClip("video_files/" + word_tuple + ".mp4"))
            word_tuple = str(word_tuple).lower()
            if os.path.isfile("video_files/" + word_tuple + ".mp4") and len(word_tuple) != 1:
                print("Entry 1")
                video_array.append(VideoFileClip("video_files/" + word_tuple + ".mp4").resize( (500, 380) ))
                print("video_files/" + word_tuple + ".mp4")
            else:
                for ch in word_tuple:
                    video_array.append(VideoFileClip("video_files/" + str(ch).upper() + ".mp4").resize( (500, 380) ))
                    print("video_files/" + str(ch).upper() + ".mp4")   

        print(video_array[0])
        sent = "".join(isl_sent) + ".mp4" 
        final_clip = concatenate_videoclips(video_array, method='compose')
        final_clip.write_videofile("static/"+sent)
        print(time.time() - start_time)
        sent_list = []
        sent_list.append(sent)
    return sent


if __name__ == '__main__':
   app.run(debug = True, use_reloader=False,port=5001)
