Python files in this folder have been used for gathering all the missing information needed to have a complete dataset for our purpose.
In particular:
- retrieve_tweets_info.py is the module which it has been used to retrieve missing information we needed like: tweet coordinates, author position and so on;
- noise_data.py creates, for each earthquake event, a set of noisy tweets for our classifier;
- retrieve_latlong.py is the one in which, starting from the position registered in the user profile and using geopy library, we were able to retireve the correspondent coordinates;
- timedata_processing.py is the module in which is implemented the processing of time/date in order to sort them later.