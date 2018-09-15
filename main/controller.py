import feature_extraction
import csv
import classification
import event_detection
import numpy as np


#path of the word2vector .bin file
path_w2v = '/home/mmariani/Desktop/web_information_retrieval/wir_project/datasets/crisisNLP_word2vec_model/crisisNLP_word_vector.bin'

'''
core function
'''
def core(directory_path_csv,
            feature,
            preprocessing_mode,
            classification_algorithm,
            k_fold,
            test_size,
            spatio_temporal_model,
            stm_namefile,
            online_retrieve,
            visual):
    
    #paths of the .csv files
    paths = [directory_path_csv+'sorted_california_preprocessed.csv',
            directory_path_csv+'sorted_nepal_preprocessed.csv',
            directory_path_csv+'sorted_chile_preprocessed.csv',
            directory_path_csv+'sorted_pakistan_preprocessed.csv',
            directory_path_csv+'noisy_tweets.csv']

    #paths of the files to exclude from the training phase
    stm_namefile = stm_namefile.lower()
    stm_file = directory_path_csv+'sorted_'+stm_namefile+'_preprocessed.csv'
    stm_noise = directory_path_csv+'sorted_'+stm_namefile+'_noise.csv'

    #remove from the files to consider for the training, the one that will be used for the spatio temporal model
    paths_iterators = []
    try:
        paths.remove(stm_file)
    except ValueError as valerr:
        print('Please insert one of the following countries: Pakistan, Chile, California or Nepal')
        exit(0)
    for path in paths:
        paths_iterators.append(readerCsv(path))
    if len(paths)==5:
        print("Please, write some .csv to exclude!")
        exit(0)

    print("Type of feature to extract: " + feature)
    if preprocessing_mode=='s':
        print("Type of preprocessing: stemming \n")
    else:
        print("Type of preprocessing: lemmatization \n")
    # support is something strongly related to the feature that we want to extract.
    # - for feature A, it's None - it's just some placeholder that will never be used
    # - for feature B, it's the vectorizer
    # - for feature C, it's the model of the w2v
    
    if not feature=="all":
        (featureMatrix, labelVector, support) = feature_extraction.doFeatureExtraction(path_w2v, paths_iterators, preprocessing_mode, feature)
    #if we want to consider all the features, we have to combine the three matrices
    else: 
        #if we want all the features, we're not interested in doing the spatio-temporal model - too costly
        spatio_temporal_model = False

        print("Extracting Feature A...\n")
        (featureMatrixA, labelVector, _) = feature_extraction.doFeatureExtraction(path_w2v,paths_iterators,preprocessing_mode,'A')
    
        #1 - restarting readers for feature B
        paths_iterators = []
        for path in paths:
            paths_iterators.append(readerCsv(path))

        print("Extracting Feature B...\n")
        (featureMatrixB, _, _) = feature_extraction.doFeatureExtraction(path_w2v,paths_iterators,preprocessing_mode,'B')
        
        #2 - restarting readers for feature C
        paths_iterators = []
        for path in paths:
            paths_iterators.append(readerCsv(path))
        
        print("Extracting Feature C...")
        (featureMatrixC, _, _) = feature_extraction.doFeatureExtraction(path_w2v,paths_iterators,preprocessing_mode,'C')
        
        print("\n")
        print("Combining all Feature matrices...\n")
        #combines all feature matrices into one huge matrix
        featureMatrix = feature_extraction.combineAllFeatureMatrices(featureMatrixA,featureMatrixB,featureMatrixC)

    #CLASSIFICATION
    print("Starting classification...\n")
    # Note that with feature A, svm linear kernel is not a good idea since it doesn't classify well with only two dimensions.
    # Solution: knn or svm with rbf suits well
    if classification_algorithm=="svm":
        classifier = classification.classify("svm",featureMatrix,labelVector,k_fold,test_size,visual)
    elif classification_algorithm=="knn":
        classifier = classification.classify("knn",featureMatrix,labelVector,k_fold,test_size,visual)
    print("Classification done!\n")


    #SPATIO TEMPORAL EVENT DETECTION
    #this is requested only for the single features, not for all
    if spatio_temporal_model:
        print("Spatio-temporal model on \"" + stm_namefile +".csv\" file ===>")
    
        #1) TEMPORAL
        print("1) Starting time event detection...")
        (predictedMeanTime, predictedMedianTime) = event_detection.doTemporalDetection(stm_file,
                                                                                        stm_noise,
                                                                                        classifier,
                                                                                        support,
                                                                                        preprocessing_mode,
                                                                                        feature)
        print("Event detected at mean time " + predictedMeanTime.strftime("%Y-%m-%d %H:%M:%S") + " and median time " + predictedMedianTime.strftime("%Y-%m-%d %H:%M:%S") + ".")
        
        trueDateTime = event_detection.getTrueDateTime(stm_namefile)
        print("True date/time strike: " + trueDateTime.strftime("%Y-%m-%d %H:%M:%S") + "\n")

        #2) SPATIO
        print("2) Starting spatio event detection...")
        (predictedMedLatitude, predictedMedLongitude,predictedMeanLatitude, predictedMeanLongitude) = event_detection.doSpatioDetection(stm_file,classifier,
                                                                                                                                        support,
                                                                                                                                        preprocessing_mode,
                                                                                                                                        feature, 
                                                                                                                                        online_retrieve)

        print("Event detected at *median* latitude (" + str(predictedMedLatitude) + "), *median* longitude (" +str(predictedMedLongitude) + ")")
        print("Event detected at *mean* latitude (" + str(predictedMeanLatitude) + "), *mean* longitude (" +str(predictedMeanLongitude) + ")")

        distanceMeanFromTrueEpicenter = event_detection.getEpicenterDistance([predictedMeanLatitude,predictedMeanLongitude],stm_namefile)
        distanceMedianFromTrueEpicenter = event_detection.getEpicenterDistance([predictedMedLatitude,predictedMedLongitude],stm_namefile)
        print("Distance from true epicenter (km): *median* " + str(distanceMedianFromTrueEpicenter)+ ", *mean* " +str(distanceMeanFromTrueEpicenter))


'''
given the path of a csv file, it returns a tuple composed by:
-	an iterator on the csv files
-	the number of (rows of the csv file - 1) -> (the header)
'''
def readerCsv(path_csv):
	file_csv = open(path_csv,'r',encoding='latin-1')
	reader = csv.reader(file_csv, delimiter=',')
	next(reader)
	lines = sum(1 for line in reader)
	file_csv.seek(0)
	reader = csv.reader(file_csv, delimiter=',')
	next(reader)
	return (reader,lines)
