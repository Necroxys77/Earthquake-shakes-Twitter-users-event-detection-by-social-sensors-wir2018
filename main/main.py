import argparse
import controller


'''
Argument parsing.
'''

ap = argparse.ArgumentParser()
ap.add_argument("-dp","--directory_path_csv", required=True, help="Path to the directory containing the csv to scan.")
ap.add_argument("-f", "--feature", required=True, help="Type of feature to extract: \"A\", \"B\" or \"C\". By deafult is A.")
ap.add_argument("-pm", "--preprocessing_mode", required=True, help="Preprocessing mode: \"s\" for stemming, \"l\" for lemmatization.")
ap.add_argument("-c","--classification_algorithm", required=True, help="Type of the classification algorithm: \"svm\" or \"knn\".")
ap.add_argument("-stm", "--spatio_temporal_model", required=False, type=bool, help="Spatio temporal event detection is applied after classification." )
ap.add_argument("-stm_f","--stm_namefile", required=False, nargs='?', default='pakistan', help="Name of the .csv to consider for the spatio-temporal model.")
ap.add_argument("-k","--k_fold", required=False, nargs='?', default=5, type=int, help="Number of k-cross validation used in the classification (5 by default).")
ap.add_argument("-t","--test_size", required=False, nargs='?', default=0.4, type=float, help="Number of k-cross validation used in the classification (0.4 by default).")
ap.add_argument("-o","--online_retrieve", required=False, nargs='?', default=False, type=bool, help="Use geopy to retrieve position of tweets for the spatio-temporal model (False by default).")
ap.add_argument("-v","--visual", required=False, nargs='?', default=False, type=bool, help="Plot some result performance metrics - confusion matrix and report (False by default).")



args = vars(ap.parse_args())

directory_path_csv = args["directory_path_csv"]
feature = args["feature"]
preprocessing_mode = args["preprocessing_mode"]
classification_algorithm = args["classification_algorithm"]
k_fold = args["k_fold"]
test_size = args["test_size"]
spatio_temporal_model =  args["spatio_temporal_model"]
stm_namefile = args["stm_namefile"]
online_retrieve = args["online_retrieve"]
visual = args["visual"]


controller.core(directory_path_csv,
                feature,
                preprocessing_mode,
                classification_algorithm,
                k_fold,
                test_size,
                spatio_temporal_model,
                stm_namefile,
                online_retrieve,
                visual)