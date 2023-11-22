from io import open
from conllu import parse_incr
import re
import warnings
from sklearn_crfsuite import CRF
import pickle

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


#Ater defining the extract_features, we define a simple function to transform our data in a more 'datasetish' format.
#This function returns the data as two lists, one of Dicts of features and the other with the labels.
def transform_to_dataset(tagged_sentences):
    X, y = [], []
    for sentence, tags in tagged_sentences:
        sent_word_features, sent_tags = [],[]
        for index in range(len(sentence)):
            sent_word_features.append(extract_features(sentence, index)),
            sent_tags.append(tags[index])
        X.append(sent_word_features)
        y.append(sent_tags)
    return X, y

data_file = open("dataset/en_ewt-ud-train.conllu", "r", encoding="utf-8")
ud_files = []
for tokenlist in parse_incr(data_file):
    ud_files.append(tokenlist)

print('Dataset count:' , len(ud_files))

#Now we iterate over all samples from the corpus 
#retrieve the word and the pre-labeled PoS tag (upostag). 
#This will be added as a list of tuples with a list of words 
#and a list of their respective PoS tags.
ud_treebank = []
for sentence in ud_files:
    tokens = []
    tags = []
    for token in sentence:
        tokens.append(token['form'])
        tags.append(token['upostag'])
    ud_treebank.append((tokens, tags))

print('Treebank count:', len(ud_treebank))

#Then, for UD Treebank.
ud_train_size = int(0.8*len(ud_treebank))
ud_training = ud_treebank[:ud_train_size]
ud_testing = ud_treebank[ud_train_size:]
X_ud_train, y_ud_train = transform_to_dataset(ud_training)
X_ud_test, y_ud_test = transform_to_dataset(ud_testing)


print('Training set:', len(X_ud_train))
print('Testing set:',len(X_ud_test))


#This loads the model. Specifics are: 
#algorithm: methodology used to check if results are improving.
#Default is lbfgs (gradient descent).
#c1 and c2:  coefficients used for regularization.
#max_iterations: max number of iterations.
#all_possible_transitions: since crf creates a "network"
#, of probability transition states,
#this option allows it to map even "connections" not present in the data.
ud_crf = CRF(
    algorithm='lbfgs',
    c1=0.01,
    c2=0.1,
    max_iterations=100,
    all_possible_transitions=True
)
print("Started training on UD corpus!")
ud_crf.fit(X_ud_train, y_ud_train)
print("Finished training on UD corpus!")


#Simply dump! Use 'wb' in open to write bytes.
ud_filename = 'ud_crf_postagger.sav'
pickle.dump(ud_crf, open(ud_filename,'wb'))
print("The trained model is saved successfully!!!")

def bnc_to_ud(tag):
    if "AJ" in tag:
        return "ADJ"
    if tag == "AT0":
        return "DET"
    if "AV" in tag:
        return "ADV"
    if tag == "CJC":
        return "CCONJ"
    if tag in ["CJS", "CJT"]:
        return "SCONJ"
    if tag in ["CRD", "ORD"]:
        return "NUM"
    if tag == "DPS":
        return "PRON"
    if tag in ["DT0", "DTQ"]:
        return "DET"
    if tag == "EX0":
        return "PRON"
    if tag == "ITJ":
        return "INTJ"
    if tag in ["NN0","NN1","NN2"]:
        return "NOUN"
    if tag == "NPO":
        return "PROPN"
    if "PN" in tag:
        return "PRON"
    if tag in ["POS","TO0","XX0","ZZ0"]:
        return "PART"
    if "PR" in tag:
        return "ADP"
    if "PU" in tag:
        return "PUNCT"
    if tag == "UNC":
        return "NOUN"
    if tag.startswith("V"):
        if tag[1] != "V":
            return "AUX"
        else:
            return "VERB"

word_lemma_dict = {}
# Open the file and load the sentences to a list.

files_list = ["dataset/en_ewt-ud-train.conllu", "dataset/en_ewt-ud-test.conllu", "dataset/en_ewt-ud-dev.conllu"]
ud_files = []
for file in files_list:
  data_file = open(file, "r", encoding="utf-8")
  for tokenlist in parse_incr(data_file):
    ud_files.append(tokenlist)
data_file.close()

#For each sentence loaded, let us extract all tokens, their form, 
#the pos_tag and the lemma. We keep the lemma intact because there are proper names.
for sentence in ud_files:
    for token in sentence:
        form = token['form'].lower()
        ud_postag = token['upostag']
        lemma = token['lemma']
        #There are also numbers that are annotated weirdly, let us just skip them:
        if ud_postag == "NUM":
            continue
        #Now, we check if the form is in the dictionary, then we check if the POS is set for the form. 
        #Only then we add the lemma related to the word.
        if form in word_lemma_dict:
            if ud_postag not in word_lemma_dict[form]:
                word_lemma_dict[form][ud_postag] = lemma
        #If the word is not in the dict, we add it.
        else:
            word_lemma_dict[form] = {ud_postag:lemma}

print(len(ud_files))

with open("dataset/BNClemma10_3_with_c5.txt", 'r', encoding='utf-8') as file:
    lines = file.read()
lines = lines.replace('\ufeff','').split("\n")

for line in lines:
    parts = line.split("->")
    if len(parts) <2:
        continue
    lemma = parts[0].strip().lower()
    forms = parts[1].split(",")
    for form in forms:
        data = form.split(">")
        tag = bnc_to_ud(data[0].replace('<','').strip())
        word = data[1].strip().lower()
        if word in word_lemma_dict:
            word_lemma_dict[word][tag]=lemma
        else:
            word_lemma_dict[word]={tag:lemma}

print(len(word_lemma_dict.keys()))

lemma_filename = 'lemma_dictionary.sav'
pickle.dump(word_lemma_dict, open(lemma_filename,'wb'))