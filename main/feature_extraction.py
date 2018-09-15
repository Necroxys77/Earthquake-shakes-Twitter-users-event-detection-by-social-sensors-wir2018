import csv
import numpy as np
import random
import sklearn
from gensim.models import KeyedVectors
import scipy.sparse
from sklearn.feature_extraction.text import CountVectorizer

'''
given (1) the path of the word2vector .bin model,
(2) a list of iterators of the .csv files,
(3) the mode of preprocessing ("s" for stemmed, lemmatization otherwise),
(4) and the features that we want to use (A, B or C)
it returns (1) a matrix with the vectors associated to all tweets' messages and
(2) a vector of labels in which each entry is associated to a tweet where:
0 means that the tweet is not_crisis_related and 1 otherwise.
Note that the matrix's semantic changes with respect to the type of feature that
we consider
'''
def doFeatureExtraction(path_w2v, paths, mode_preprocessing, feature):
	#number of rows in all the csv (so the total number of tweets)
	rowLength = sum(row for (_,row) in paths)
	#it contains rowLength number of 0s or 1s to understand if the i-th tweet
	#is crisis related or not according to the ground truth
	labelVector = []

	if feature=='C':
		#support is the model of the w2v, loaded
		support = retrieveModel_w2v(path_w2v)
		featureMatrix = np.zeros(shape=(rowLength,600))
		(featureMatrix,labelVector) = extractFeatureC(featureMatrix, support, paths, mode_preprocessing)
	#feature B:
	elif feature=='B':
		#support is the vectorizer
		(featureMatrix,labelVector,support) = extractFeatureB(paths, mode_preprocessing)
	#feature A:
	elif feature=='A':
		support = None #it's not used in feature A
		featureMatrix = np.zeros(shape=(rowLength,2)) 
		(featureMatrix,labelVector) = extractFeatureA(featureMatrix ,paths, mode_preprocessing)
		
	return (featureMatrix,labelVector,support)



'''
Feature A: statistical feature. The number of words in a tweet message and the position of the (first) query words within a tweet
The feature matrix is MxN where (1) M is the number of tweets and (2) N is 2, in which we have (1) tweet's length and (2) position of a query word, if any
'''
def extractFeatureA(featureMatrix, paths, mode_preprocessing):
	#query words detection (static)
	if mode_preprocessing=='s':
		#column in the csv to consider
		tweetColumn = 4
		#most important words to consider (descreasing order of importance), according to the preprocessing mode that we're considering
		queryWords = ["earthquak","shake","magnitud","quak","strike","tsunami"]
	else:
		tweetColumn = 5
		queryWords = ["earthquake","shaking","shake","magnitude","quake","strike","tsunami"]

	labelVector = []
	index = 0
	#scan all the .csv files
	for (reader,_) in paths:
		#scan tweetmessages
		for row in reader:
			#populate the labelVector with the label of the current row
			labelVector.append(row[9])
			#list of words from the current tweet
			words = row[tweetColumn].split()
			position = -1
			for queryword in queryWords:
				#as soon as we encounter the first query word, we exit 
				if position > -1:
					break
				for word in words:
					word = word.lower()
					if queryword == word:
						position = words.index(word)
						break

			featureMatrix[index:] = np.array([len(words),position])
			index+=1

	return (featureMatrix,labelVector)



'''
Feature B: keyword features. The words in a tweet.
The feature matrix is MxN where (1) M is the number of tweets and (2) N is the number of distinct words in the vocabulary, in the whole corpus
'''
def extractFeatureB(paths, mode_preprocessing):
	vectorizer = CountVectorizer()
	
	corpus = []
	labelVector = []
	if mode_preprocessing == 's':
		tweetColumn = 4
	else:
		tweetColumn = 5
	
	for (reader,_) in paths:
		for row in reader:
			corpus.append(row[tweetColumn]) #row[5] is the lemmatized text, row[4] is the stemmed one
			labelVector.append(row[9]) #row[9] is the label of each tweet
	
	featureMatrix = vectorizer.fit_transform(corpus) #tokenize and count the word occurrences
	
	return (featureMatrix, labelVector, vectorizer)


'''
Feature C: word context features. The words before and after the (first) query word in a tweet. Bonus: word2vector utilization exposed by CrisisNLP.
The feature matrix is MxN where (1) M is the number of tweets and (2) N is 600, because we have a vector of 600 integers representing each tweet.
The 600-sized vector is obtained by the concatenation of two 300-sized vectors representing the left context and right context of a query word
'''
def extractFeatureC(featureMatrix, model, paths, mode_preprocessing):
	if mode_preprocessing=='s':
		#column in the csv to consider
		tweetColumn = 4
		#most important words to consider, in descreasing order of importance
		queryWords = ["earthquak","shake","magnitud","quak","strike","tsunami"]
	else:
		tweetColumn = 5
		queryWords = ["earthquake","shaking","shake","magnitude","quake","strike","tsunami"]

	index = 0
	labelVector = []
	#leftContext is the vector associated to the words on the left wrt a query word
	leftContext = []
	#rightContext is the vector associated to the words on the left wrt a query word
	rightContext = []

	#scan all the .csv files
	for (reader,_) in paths:
		#scan tweetmessages
		for row in reader:
			labelVector.append(row[9])
			(leftContext, rightContext) = createContexts(row, queryWords, tweetColumn)
			#list of 300 elements each
			leftW2v = avgEmbedding(leftContext, model)
			rightW2v =  avgEmbedding(rightContext, model)

			#concatenate lists of 300 elements. The result is a vector of 600 elements
			w2v = np.append(leftW2v,rightW2v)

			featureMatrix[index:] = np.array(w2v)
			index = index +1

			#reset
			leftContext = []
			rightContext = []
	
	return (featureMatrix,labelVector)


'''
given the path of the w2v model .bin, it loads and returns the model
'''
def retrieveModel_w2v(path_w2v):
	print("Loading model w2v... ")
	model = KeyedVectors.load_word2vec_format(path_w2v, binary=True)
	print("w2v model loaded!")
	return model

'''
given a string and a loaded model, it returns a 300-sized vector
associated to the string (word) in the model if it exists, 
otherwise it returns a vector of 1 element
'''
def find_w2v(word,model):
	try:
		word_vector = model[word]
	except:
		#print(word + " not in the vocabulary!")
		word_vector = [-1]
	return word_vector


'''
given (1) a string, (2) an array of query words and (3) a number; it returns a tuple
of words representing the left and the right context either of the first found query words
or of a random word in the tweet message
'''
def createContexts(row, queryWords, tweetColumn):
	tweet_message = row[tweetColumn].split()

	leftContext= []
	rightContext = []
	for word in queryWords:
		if word in tweet_message:
			pos = tweet_message.index(word)
			return splittingContext(tweet_message,word,pos)

	#if there aren't query words then sample randomly
	if  (not leftContext) and (not rightContext):
		pos = random.randint(0,len(tweet_message)-1)
		return splittingContext(tweet_message,tweet_message[pos],pos)

	return (leftContext,rightContext)

'''
given a (1) tweet message (string), (2) a word and (3) the position of that word
in the tweet message it returns the left context and the right context of that word
'''
def splittingContext(tweet_message,word,pos):
	if pos==0:
		rightContext = tweet_message[1:]
		leftContext = [tweet_message[0]]
	elif pos==len(tweet_message)-1:
		leftContext = tweet_message[:pos]
		rightContext = [tweet_message[pos]]
	else:
		leftContext = tweet_message[:pos]
		rightContext = tweet_message[pos+1:]

	return (leftContext,rightContext)

'''
given (1) a vector of tokens and (2) a model, it computes the w2v of each token
and returns the mean vector of all w2v vectors
'''
def avgEmbedding(vectorContext, model):
	#matrix initialization
	if len(vectorContext)==0:
		tmpMatrix = np.zeros(shape=(1,300))
	else:
		tmpMatrix = np.zeros(shape=(len(vectorContext),300))

	index = 0
	for w in vectorContext:
		w2v = find_w2v(w, model)
		#if the word exists in the vocabulary, then the entry is replaced by
		#the w2v associated to that word
		if len(w2v)!=1:
			tmpMatrix[index:] = np.array(w2v)
		#otherwise, the entry is replace by an entry of 300 zeros
		else:
			tmpMatrix[index:] = np.zeros(300)
		index = index + 1

	#average between each i-th column element. The result is a vector of 300 floats
	return tmpMatrix.mean(axis=0)


'''
When all features are needed, we create a *huge* feature matrix composed by all the vectors from all the features
'''
def combineAllFeatureMatrices(featureMatrixA,featureMatrixB,featureMatrixC):
	(rowLength,columnLengthA) = featureMatrixA.shape
	#since the extraction of featureB returns a matrix that is sparse (but we have to concatenate vectors)
	#we transform it into a dense matrix
	denseFeatureB = featureMatrixB.todense()
	(_,columnLengthB) = denseFeatureB.shape
	(_,columnLengthC) = featureMatrixC.shape
	featureMatrixAll = np.zeros(shape=(rowLength,columnLengthA+columnLengthB+columnLengthC))

	counter = 0
	tmp = 0
	for row in range(0,rowLength):
		if row%100==0:
			tmp+=counter
			print("Progress: " + str(tmp) + "/" + str(rowLength))
			counter=0
		reshapedVectorB = np.array(denseFeatureB)[row].tolist()
		combinedVector = np.append(reshapedVectorB,featureMatrixA[row])
		combinedVector2 = np.append(combinedVector,featureMatrixC[row])
		featureMatrixAll[row:] = combinedVector2
		counter+=1

	return featureMatrixAll

