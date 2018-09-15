#we eliminate warnings related to ill-defined value when sklearn determines Precision and Recall value
import warnings
warnings.filterwarnings("ignore")

import numpy as np
from sklearn.datasets import load_files #those are utilities to manage the dataset
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate, GridSearchCV #those are utilities to manage the training set
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn import metrics, svm, model_selection #in order to evaluate the performances on the test set
from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score, classification_report 
import plotter

'''
given a (1) classificationType string (as "svm", "knn"), (2) the featureMatrix, (3) the labelVector,
(4) the number of k-cross validation needed and (3) the size of the test set; it performs the
classification of the tweets and it calculates the performance metrics
'''
def classify(classifier, featureMatrix, labelVector, k_fold, test_size, visual):

    if classifier == "svm":
        
        C_values = [.1]
        kernels = ['rbf']
        gamma_values = [.1]
        dict_grid = dict(C=C_values, kernel=kernels, gamma=gamma_values)

        '''
        C_values = [.1, 1, 10]
        kernels = ['rbf','linear']
        gamma_values = [.01, .1,1,10]
        dict_grid = dict(C=C_values, kernel=kernels, gamma=gamma_values)
        '''

        print("SVM classification with " + str(k_fold) + "-cross validation ====>\n")
        print("Parameters to consider:")
        print("Kernels " + str(kernels))
        print("C values " + str(C_values))
        print("Gamma values " + str(gamma_values) + "\n")
        print("Test set size: %0.2f" % (test_size)+"\n")
        #gamma modifies the standard deviation of the gaussian rbf: large values of gamma reflects into small variance
        #so two points are considered similar if they are very close each other. Otherwise, the classification is more flexible
        #wrt the distance. Rbf is better with feature A since we have only two dimensions to consider.
        #gamma=10^1 is the optimal value of gamma: above this value we get the same results

        grid = GridSearchCV(svm.SVC(),param_grid= dict_grid,cv=k_fold)
    #knn is good in the case we have to consider a low dimensional case - like feature A (two dimensions)
    #curse of dimensionality
    elif classifier == "knn":
        neighbors_values = [5,11,20,50]
        dict_grid = dict(n_neighbors=neighbors_values)
        print("KNN classification with " + str(k_fold) + "-cross validation ====>\n")
        print("Parameters to consider:")
        print("Neighbors " + str(neighbors_values)+"\n")
        print("Test set size: %0.2f" % (test_size)+"\n")
        grid = GridSearchCV(KNeighborsClassifier(),param_grid= dict_grid,cv=k_fold)

    X_train, X_test, Y_train, Y_test = train_test_split(featureMatrix, labelVector, test_size=test_size, random_state=0)

    grid.fit(X_train, Y_train)

    if classifier=="svm":
        print("Best C: ", grid.best_estimator_.C)
        print("Best kernel: ", grid.best_estimator_.kernel)
        print("Best gamma: ", grid.best_estimator_.gamma)
    elif classifier=="knn":
        print("Best number of neighbors: ", grid.best_estimator_.n_neighbors)

    Y_predicted = grid.predict(X_test)
    target_names = ['not-crisis-related','crisis-related']
    #Thus in binary classification, the count of true negatives is C_{0,0}, false negatives is C_{1,0}, true positives is C_{1,1} and false positives is C_{0,1}.
    confusion_matrix = metrics.confusion_matrix(Y_test, Y_predicted)
    (tn, fp, fn, tp) = confusion_matrix.ravel()
    accuracy = (tn+tp)/(tp+tn+fp+fn)

    print("CLASSIFICATION REPORT ====>")
    print("Accuracy: %0.2f" % (accuracy))
    print(classification_report(Y_test,Y_predicted,target_names=target_names))

    print("Confusion Matrix:")
    print(confusion_matrix)

    #plots some results, if required
    if visual:
        #plotting confusion matrix
        plotter.plot_confusionmatrix(confusion_matrix) 

        #plotting classification report
        plotter.plot_classification_report(classification_report(Y_test,Y_predicted,target_names=target_names))
    
    return grid