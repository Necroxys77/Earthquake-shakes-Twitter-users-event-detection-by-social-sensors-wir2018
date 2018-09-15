import csv
import feature_extraction
import numpy as np
import math
import geopy
import datetime
import burst_detection as bd
import pandas
import time
from sklearn.feature_extraction.text import CountVectorizer
from math import sin, cos, atan2, sqrt, radians
from geopy.geocoders import Nominatim


#real date/time of earthquakes' strike
nepalDateTime = datetime.datetime(2015,4,25,6,11,25)
chileDateTime = datetime.datetime(2014,4,1,23,46,47)
pakistanDateTime = datetime.datetime(2013,9,24,11,29,47)
californiaDateTime = datetime.datetime(2014,8,24,10,20,44)

#real epicenters of earthquakes taken from wikipedia
pakistanEpicenter = [26.97, 65.52]
chileEpicenter = [-19.642, -70.817]
nepalEpicenter = [28.23, 84.731]
californiaEpicenter = [38.22, -122.31]

'''
spatial detection using the classifer previously trained on a .csv never used in the classification phase.
It predicts the class of new tweets and keeps track of longitude, latitude and position of crisis related ones.
Note: "support" parameter is overloaded: in case of feature B it's the vectorizer, in case of 
feature C it's the model, in case of feature A it's not used
'''
def doSpatioDetection(path,classifier,support,mode_processing,feature, online_retrieve):
    file_csv = open(path,'r',encoding='latin-1')
    reader = csv.reader(file_csv, delimiter=',')
    next(reader)

    if mode_processing=='s':
		#column in the csv to consider
	    tweetColumn = 4
		#most important words to consider
	    queryWords = ["earthquak","shake","magnitud","quak","strike","tsunami"]
    else:
	    tweetColumn = 5
	    queryWords = ["earthquake","shaking","shake","magnitude","quake","strike","tsunami"]

    #dictionary that has (1) the tweetIDs as keys and (2) a list as values.
    crisis_info = {}

    #exploiting the same feature used in the classification phase and the trained model (classifier)
    #we predict the new tweets and collect information about those tweets predicted as crisis related
    if feature=='C':
        leftContext = []
        rightContext = []
        for row in reader:
            (leftContext, rightContext) = feature_extraction.createContexts(row, queryWords, tweetColumn)
            leftW2v = feature_extraction.avgEmbedding(leftContext, support)
            rightW2v =  feature_extraction.avgEmbedding(rightContext, support)
            w2v_vec = np.append(leftW2v,rightW2v)
            #if the classifier recognize the tweet as crisis related, then...
            if classifier.predict([w2v_vec]):
                longitude = row[6]
                latitude = row[7]
                position = row[8]
                date = row[1]
                time = row[2]
                crisis_info[row[0]] = [date,time,longitude,latitude,position]

    elif feature=='B':
        corpus = []
        for row in reader:
            corpus.append(row[tweetColumn])
        file_csv.seek(0)
        reader = csv.reader(file_csv, delimiter=',')
        next(reader)
        for row in reader:
            w2v_vec = support.transform([row[tweetColumn]]).toarray()
            #if the classifier recognize the tweet as crisis related, then...
            if classifier.predict(w2v_vec):
                longitude = row[6] #None if not avalable
                latitude = row[7] #"None" if not available
                position = row[8] #"" (empty string) if not available
                date = row[1]
                time = row[2]
                crisis_info[row[0]] = [date,time,latitude,longitude,position]
    
    elif feature=='A':
        for row in reader:
            words = row[tweetColumn].split()
            position = -1
            for queryword in queryWords:
                if position > -1:
                    break
                for word in words: 
                    word = word.lower()
                    if queryword == word:
                        position = words.index(word)
                        break
            if classifier.predict([[len(words),position]]):
                longitude = row[6] #None if not avalable
                latitude = row[7] #"None" if not available
                position = row[8] #"" (empty string) if not available
                date = row[1]
                time = row[2]
                crisis_info[row[0]] = [date,time,latitude,longitude,position]

    #it returns the predicted values of latitude and longitute of the earthquake
    print("Retrieving data to calculate longitude and latitude...\n")
    (predictedMedLatitude,predictedMedLongtude) = spatioDetectionMedian(crisis_info, online_retrieve)
    (predictedMeanLatitude,predictedMeanLongtude) = spatioDetectionMean(crisis_info, online_retrieve)
        
    return (predictedMedLatitude,predictedMedLongtude,predictedMeanLatitude,predictedMeanLongtude)



'''
it performs the mean of a list of latitudes and longitudes.
'''
def spatioDetectionMean(crisis_info, online_retrieve):
    avgLat = 0.0
    avgLon = 0.0
    avgZ = 0.0
    counter = 0

    geolocator = Nominatim(timeout=5) #higher timeout, smaller risk of timeout

    length = len(crisis_info)
    scan = 0
    tmp = 0

    #if we don't want to query Google API through geopy - to speed up the process - then use the files, directly
    if not (online_retrieve):
        for tweet_id in crisis_info.values():
            if not (tweet_id[2]=="None" or tweet_id[3]=="None"):
                lat = float(tweet_id[2])
                lon = float(tweet_id[3])
                avgLat = avgLat + (cos(lat*(math.pi/180.0)) * cos(lon*(math.pi/180.0)))
                avgLon = avgLon + (cos(lat*(math.pi/180.0)) * sin(lon)*(math.pi/180.0))
                avgZ = avgZ + sin(lat*(math.pi/180.0))
                counter = counter +1
    else:
        for tweet_id in crisis_info.values():
            try:
                if scan%100==0:
                    tmp = tmp + scan
                    print("Progress: " + str(tmp)+ "/" + str(length))
                    scan = 0
                if (tweet_id[2]=="None" or tweet_id[3]=="None") and (tweet_id[4].replace(" ","")!=""):
                    location = geolocator.geocode(tweet_id[4])
                    if location is not None:
                        avgLat = avgLat + (cos(location.latitude*(math.pi/180.0)) * cos(location.longitude*(math.pi/180.0)))
                        avgLon = avgLon + (cos(location.latitude*(math.pi/180.0)) * sin(location.longitude)*(math.pi/180.0))
                        avgZ = avgZ + sin(location.latitude*(math.pi/180.0))
                        counter = counter +1
                    scan  = scan +1
                elif (tweet_id[2]=="None" or tweet_id[3]=="None") and (tweet_id[4].replace(" ","")==""):
                    scan = scan + 1
                    continue
                else:
                    avgLat = avgLat + (cos(float(tweet_id[2])*(math.pi/180.0)) * cos(float(tweet_id[3])*(math.pi/180.0)))
                    avgLon =  avgLon + (cos(float(tweet_id[2])*(math.pi/180.0)) * sin(float(tweet_id[3])*(math.pi/180.0)))
                    avgZ = avgZ + sin(float(tweet_id[2])*(math.pi/180.0))
                    counter = counter +1
                    scan = scan + 1
            #if the libraray raise an exception for too many requests, put the process in sleep
            except geopy.exc.GeopyError as e:
                print(e)
                print("Progess interrupted at " + str(tmp+scan) + "/"  + str(length) + "!")
                time.sleep(60*15)

    x = avgLat/counter
    y = avgLon/counter
    z = avgZ/counter

    centerLongitude = (atan2(y, x))*(180.0/math.pi)
    centerHyp = sqrt(x * x + y * y)
    centerLatitude = (atan2(z, centerHyp))*(180.0/math.pi)    

    return (centerLatitude,centerLongitude)


'''
it performs the median of a list of latitudes and longitudes
'''
def spatioDetectionMedian(crisis_info , online_retrieve):
    avgLat = []
    avgLon = []

    geolocator = Nominatim(timeout=5) #higher timeout, smaller risk of request timeout

    length = len(crisis_info)
    scan = 0
    tmp = 0

    #if we don't want to query Google API through geopy - to speed up the process - then use the files, directly
    if not (online_retrieve):
        for tweet_id in crisis_info.values():
            if not (tweet_id[2]=="None" or tweet_id[3]=="None"):
                avgLat.append(float(tweet_id[2]))
                avgLon.append(float(tweet_id[3]))
    else:
        for tweet_id in crisis_info.values():
            try:
                if scan%100==0:
                    tmp = tmp + scan
                    print("Progress: " + str(tmp)+ "/" + str(length))
                    scan = 0
                if (tweet_id[2]=="None" or tweet_id[3]=="None") and (tweet_id[4].replace(" ","")!=""):
                    location = geolocator.geocode(tweet_id[4])
                    if location is not None:
                        avgLat.append(location.latitude)
                        avgLon.append(location.longitude)
                    scan  = scan +1
                elif (tweet_id[2]=="None" or tweet_id[3]=="None") and (tweet_id[4].replace(" ","")==""):
                    scan = scan + 1
                    continue
                else:
                    avgLat.append(float(tweet_id[2]))
                    avgLon.append(float(tweet_id[3]))
                    scan = scan + 1
            #if the libraray raise an exception for too many requests, put the process in sleep
            except geopy.exc.GeopyError as e:
                print(e)
                print("Progess interrupted at " + str(tmp+scan) + "/" + str(length) + "!")
                time.sleep(60*15)

    centerLatitude = np.median(avgLat)
    centerLongitude = np.median(avgLon)

    return (centerLatitude,centerLongitude)


'''
It returns the distance between the estimated epicenter location and the true epicenter of the earthquake.
The true epicenter is hard coded and taken from wikipedia 
'''
def getEpicenterDistance(estimatedEpicenter,name_file):
    #earth radius
    R = 6371.0

    trueEpicenter = None
    if name_file=="pakistan":
        trueEpicenter = pakistanEpicenter
    elif name_file=="california":
        trueEpicenter = californiaEpicenter
    elif name_file=="chile":
        trueEpicenter = nepalEpicenter
    elif name_file=="nepal":
        trueEpicenter = nepalEpicenter

    estLat = radians(estimatedEpicenter[0])
    estLon = radians(estimatedEpicenter[1])
    trueLat = radians(trueEpicenter[0])
    trueLon = radians(trueEpicenter[1])

    dlon = trueLon - estLon
    dlat = trueLat - estLat

    a = sin(dlat / 2)**2 + cos(estLat) * cos(trueLat) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


'''
creates a dictionary containing tweets (rows of the csv) grouped by time slices. 
The time slice is hard coded (60s)
It returns a dictionary where:
- key is an integer representing the window
- value is a list of lists of two elements. Those two elements are (1) row of the csv file and (2) the temporal data of that row, manipulated properly
'''
def parsingTemporalInfo(reader,reader_noisy):
    windowsRows = {}
    window = 1
    startingTime=0
    
    mergedTweets = mergeNoise(reader,reader_noisy)

    for row in mergedTweets:
        dateToken = row[1].split("-")
        timeToken = row[2].split(":")
        temporalRow = datetime.datetime(int(dateToken[2]),int(dateToken[0]),int(dateToken[1]),int(timeToken[0]),int(timeToken[1]),int(timeToken[2])) 
        if startingTime==0:
            startingTime = temporalRow
            windowsRows[window] = [[row,temporalRow]]
            continue
        #time slice is 60 seconds
        if temporalRow < (startingTime + datetime.timedelta(seconds=60*window)):
            windowsRows[window].append([row,temporalRow])
        else:
            window+=1
            windowsRows[window] = [[row,temporalRow]]

    return windowsRows

'''
it returns a list of tweets (original/noisy) sorted by date/time
'''
def mergeNoise(reader,reader_noisy):
    mergedTweets = []

    for tweet in reader:
        mergedTweets.append(tweet)
    for tweetNoise in reader_noisy:
        mergedTweets.append(tweetNoise)

    return sorted(mergedTweets, key=lambda row: (datetime.datetime.strptime(row[1], "%m-%d-%Y"), datetime.datetime.strptime(row[2], '%H:%M:%S')))


'''
temporal detection using the classifier previously trained on a .csv never used in the classification phase
Note: "model" parameter is overloaded: in case of feature B it's the vectorizer, in case of 
feature C it's the model, in case of feature A it's not used
'''
def doTemporalDetection(path,path_noise,classifier,model,mode_processing,feature):
    file_csv = open(path,'r',encoding='latin-1')
    reader = csv.reader(file_csv, delimiter=',')
    next(reader)

    noise_csv = open(path_noise,'r',encoding='latin-1')
    reader_noisy = csv.reader(noise_csv, delimiter=',')
    next(reader_noisy)

    if mode_processing=='s':
		#column in the csv to consider
	    tweetColumn = 4
		#most important words to consider
	    queryWords = ["earthquak","shake","magnitud","quak","strike","tsunami"]
    else:
	    tweetColumn = 5
	    queryWords = ["earthquake","shaking","shake","magnitude","quake","strike","tsunami"]

    
    windowsRows = parsingTemporalInfo(reader,reader_noisy)

    #list of occurences that keep track of the number of target events (crisis related) in each time window
    targetEvents = []
    #list of occurences that keep track of the number of total events (crisis related or not) in each time window
    totalEvents = []

    if feature=='C':
        leftContext = []
        rightContext = []
        for el in windowsRows:
            targetCounter = 0
            totalCounter = len(windowsRows[el])
            for subel in windowsRows[el]:
                (leftContext, rightContext) = feature_extraction.createContexts(subel[0], queryWords, tweetColumn)
                leftW2v = feature_extraction.avgEmbedding(leftContext, model)
                rightW2v =  feature_extraction.avgEmbedding(rightContext, model)
                w2v_vec = np.append(leftW2v,rightW2v)
                #if the classifier recognize the tweet as crisis related, then...
                if classifier.predict([w2v_vec])=='1':
                    targetCounter+=1
            targetEvents.append(targetCounter)
            totalEvents.append(totalCounter)
    
    elif feature=='B':
        for el in windowsRows:
            targetCounter = 0
            totalCounter = len(windowsRows[el])
            for subel in windowsRows[el]:
                row = subel[0]
                w2v_vec = model.transform([row[tweetColumn]]).toarray()
                #if the classifier recognize the tweet as crisis related, then...
                if classifier.predict(w2v_vec)=='1':
                    targetCounter+=1
            targetEvents.append(targetCounter)
            totalEvents.append(totalCounter)

    elif feature=='A':
        for el in windowsRows:
            targetCounter = 0
            totalCounter = len(windowsRows[el])
            for subel in windowsRows[el]:
                row = subel[0]
                words = row[tweetColumn].split()
                position = -1
                for queryword in queryWords:
                    if position > -1:
                        break
                    for word in words: 
                        word = word.lower()
                        if queryword == word:
                            position = words.index(word)
                            break
                if classifier.predict([[len(words),position]])=='1':
                    targetCounter+=1
            targetEvents.append(targetCounter)
            totalEvents.append(totalCounter)
    

    targetEvents = np.array(targetEvents,dtype=float)
    totalEvents = np.array(totalEvents,dtype=float)
    q,totalEvents,targetEvents,p = bd.burst_detection(targetEvents,totalEvents,len(targetEvents),s=5,gamma=.01,smooth_win=1)

    optTweets = retrieveWindows(q.T[0],windowsRows)
    #if there is no burst - meaning that the whole sequence is a giant burst - then I force
    #the q.T to be composed by only 1s, considering al tweets
    if len(optTweets)==0:
        optTweets = retrieveWindows(np.ones(len(windowsRows)),windowsRows)

    d = {"one": pandas.Series(optTweets)}
    df = pandas.DataFrame(d)
    (predictedMeanTime, predictedMedianTime)=avg_datetime(df)

    return (predictedMeanTime, predictedMedianTime)



'''
given the optimal sequence an the dictionary con rows divided into windows/time slices, returns
a list of datetime objects related to those tweets belonging into a burst
'''
def retrieveWindows(optSequence,windowsRows):
    optList = list(optSequence)
    optTweets = []

    for i in range(0, len(optList)-1):
        if optList[i]==1:
            try:
                for (_,temporalRow) in windowsRows[i]:
                    optTweets.append(temporalRow)
            except KeyError as e:
                print('')
    return optTweets



'''
returns (1) the mean and (2) median date/time of a sequence of date time objects
'''
def avg_datetime(series):
    meanDateTime = (series.one-series.one.min()).mean()+series.one.min()
    medianDateTime = (series.one-series.one.min()).median()+series.one.min()
    return (meanDateTime,medianDateTime)


'''
it simply returns the true date/time of an earthquake strike, considering a given file
'''
def getTrueDateTime(name_file):
    trueDateTime = None
    
    if name_file=="pakistan":
        trueDateTime = pakistanDateTime
    elif name_file=="california":
        trueDateTime = californiaDateTime
    elif name_file=="chile":
        trueDateTime = chileDateTime
    elif name_file=="nepal":
        trueDateTime = nepalDateTime

    return trueDateTime