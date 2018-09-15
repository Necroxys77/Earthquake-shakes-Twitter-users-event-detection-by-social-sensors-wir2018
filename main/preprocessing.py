import nltk
import csv
import string
import re
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import sent_tokenize

'''
the prepocessing is composed by:
	- URLs elimination
	- punctuaction elimination
	- slang/acronyms/misspelling replacing by using CrisisNLP's OOV
	- stop words elimination
	- stemming or lemmatization
	- digits elimination
	- extra spaces elimination
'''
def doPreprocessing(tweet_message, sl):
	print("Original tweet: " + tweet_message)
	tweet_message = removeUrls(tweet_message)
	print("Removed URL: " + tweet_message)
	tweet_message = removePunct(tweet_message)
	print("Removed punctuaction: " + str(tweet_message))
	tweet_message = oovTransf(tweet_message)
	print("Misspelling replacement: " + str(tweet_message))
	tweet_message = removeStopWords(tweet_message)
	print("Removed stopwords (1): " + str(tweet_message))
	if sl=="s":
		#do stemming
		tweet_message = doStemming(tweet_message)
		print("Stemming: " + str(tweet_message))
	else:
		#do lemmatization
		tweet_message = doLemmatization(tweet_message)
		print("Lemmatization: " + str(tweet_message))
	tweet_message = removeDigits(tweet_message)
	print("Removed Digits: " + tweet_message)
	#remove double spaces and unwanted spaces
	return re.sub(' +',' ',tweet_message).strip()

'''given a string it returns a message without any digits'''
def removeDigits(tweet_message):
	remove_digits = str.maketrans('', '', string.digits)
	clean_message = tweet_message.translate(remove_digits)
	return clean_message

'''given a string it returns a string in which there aren't any http/https link'''
def removeUrls(tweet_message):
	return re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', tweet_message)

'''
given an array of words, it replace any slang/acronym with the correspondent
correct word foudn in the OOV of the CrisisNLP dataset
'''
def oovTransf(tokens):
	slangs = []
	correct_words = []

	with open('/home/mmariani/Desktop/wir_project/datasets/OOV_Dict/OOV_Dictionary_V1.0.tsv', 'r', encoding = 'latin-1') as oov:
		oov = csv.reader(oov, delimiter='\t')
		for row in oov:
			slangs.append(row[0])
			correct_words.append(row[1])
	j=0
	slang_found = False

	for token in tokens:
		if token in slangs:
			for i in range(0,len(slangs)):
				if token==slangs[i]:
					tokens[j] = correct_words[i]
					slang_found = True
					break
		j=j+1

	#tokenization is applied again in order to split the slang
	if slang_found:
		tokens = " ".join(tokens)
		tokens = word_tokenize(tokens)
	return tokens

'''given a string, it tokenizes the input (array) and removes punctuaction'''
def removePunct(tweet_message):
	tokenizer = RegexpTokenizer(r'\w+')
	return tokenizer.tokenize(tweet_message.lower())

'''given an array of words, it removes any stop words in it'''
def removeStopWords(tokens):
	stop_words = set(stopwords.words('english'))
	filtered_sentence = []
	for token in tokens:
		if token not in stop_words:
			filtered_sentence.append(token)
	return filtered_sentence

'''given an array of words, it applies stemming and returns a string'''
def doStemming(tokens):
	ps = PorterStemmer()
	for i in range(0, len(tokens)):
		tokens[i] = ps.stem(tokens[i])
	tweet_message = " ".join(str(x) for x in tokens)
	return tweet_message

'''given an array of words, it applies lemmatization and returns a string'''
def doLemmatization(tokens):
	wordnet_lemmatizer = WordNetLemmatizer()
	tokens_pos = pos_tag(tokens)
	i=0
	tweet_message = ''

	for token in tokens:
		tag = tokens_pos[i][1][0].lower()
		i=i+1
		if tag in ['a','r','n','v']:
			tweet_message = tweet_message + " " + wordnet_lemmatizer.lemmatize(token, pos=tag).lower()
		else:
			tweet_message = tweet_message + " " + wordnet_lemmatizer.lemmatize(token).lower()
	return tweet_message
