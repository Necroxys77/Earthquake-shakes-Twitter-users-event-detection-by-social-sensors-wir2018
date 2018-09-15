import geopy, csv, os
from geopy.geocoders import Nominatim
import time

path_csv = '/Users/riccardochiaretti/Desktop/Engineering in Computer Science/First Year/Second Semester/Web Information & Retrieval/Project/csv Files/Preprocessed_tweets/sorted/lat/'
header = ['tweet_id', 'date', 'time','tweet_text', 'tweet_stemmed', 'tweet_lemmatized', 'tweet_lon', 'tweet_lat', 'author_position','label_10']

'''
In this function, using geopy library, we will retrieve the latitude and longitude
of tweets. Given the position registered by the users, we use the geolocator for 
obtaining the respective latitude and longitude
'''
def retrieve_geopos():
    csv_files = os.listdir(path_csv) #List of all csv files
    csv_files.remove('.DS_Store')
    geolocator = Nominatim(timeout=5) 

    for f in csv_files:
        file_csv = open(path_csv + f,'r',encoding='latin-1')
        reader = csv.reader(file_csv, delimiter=',')
        next(reader)

        #File containing also information related to the latitude and longitude of each tweet
        latlon_file = open(path_csv + f + 'lat.csv', 'w')
        writer = csv.DictWriter(latlon_file, fieldnames = header)
        writer.writeheader()
        for tweet_id in reader:
            try:
                #In the case we already have the latitude and longitude, we do not use 
                #the position of the user
                if (tweet_id[6]=="None" or tweet_id[7]=="None") and (tweet_id[8].replace(" ","")!=""):
                    location = geolocator.geocode(tweet_id[8])
                    #The geolocator could fail when, for example, the user registers
                    #a dummy location
                    if location is not None:
                        print(location.latitude, location.longitude)
                        tweet_id[6] = location.longitude
                        tweet_id[7] = location.latitude

                writer.writerow({header[0]: tweet_id[0], #Write row[0] 'id'
                                    header[1]: tweet_id[1], #Writing the date
                                    header[2]: tweet_id[2], #Writing the time
                                    header[3]: tweet_id[3], #Text not preprocessed
                                    header[4]: tweet_id[4], #Stemmed text
                                    header[5]: tweet_id[5], #Lemmatized text
                                    header[6]: tweet_id[6], #Longitude
                                    header[7]: tweet_id[7], #Latitude 
                                    header[8]: tweet_id[8], #Author position
                                    header[9]: tweet_id[9]}) # 1: if relevant, 0 otherwise
            except geopy.exc.GeopyError as e:
                time.sleep(60*5) #Sleeping waiting to be able to continue retrieving
