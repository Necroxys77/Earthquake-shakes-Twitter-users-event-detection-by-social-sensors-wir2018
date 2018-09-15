import csv, os
import preprocessing
p = '/Users/riccardochiaretti/Desktop/noise_file/'
pall = '/Users/riccardochiaretti/Desktop/noise_file/all' 
pdiff = '/Users/riccardochiaretti/Desktop/noise_file/diff'
header = ['tweet_id', 'date', 'time','tweet_text', 'tweet_stemmed', 'tweet_lemmatized', 'tweet_lon', 'tweet_lat', 'author_position','label_10']

csv_files = os.listdir(p) #List of all csv files
csv_files.remove('.DS_Store')
csv_files.remove('diff')
csv_files.remove('all')
csv_filesall = os.listdir(pall)
csv_filesall.remove('.DS_Store')
csv_filesdiff = os.listdir(pdiff)
csv_filesdiff.remove('.DS_Store')

'''
Here, we use several files for collecting some tweets which will be the noise for our classifier. Those files are related to other type of crisis like flooding, typhoons or hurricanes.
Since those files differ from the point of view of the structure of the information, we need to perform different actions according to the files we are considering: either 
those from volunteers or not.
'''
def create_noise(): 
    f_write = open('/Users/riccardochiaretti/Desktop/noisy_tweets.csv' , 'w')
    writer = csv.DictWriter(f_write, fieldnames = header)
    writer.writeheader()

    for file in csv_files:  
        f_read = open(p + '/' + file, 'r', encoding='latin-1')
        reader = csv.reader(f_read, delimiter = ',')
        i = 0
        for row in reader:
            i = i + 1
            stemmed_tweet = preprocessing.doPreprocessing(row[7], "s")
            lemma_tweet = preprocessing.doPreprocessing(row[7], "l")
            if ( ( len(stemmed_tweet.replace(" ", "").split()) != 0 ) and ( len(stemmed_tweet.replace(" ", "").split()) != 0 ) ):
                writer.writerow({header[0]:'None',header[1]:'None',header[2]:'None',header[3]:'None',header[4]:stemmed_tweet,header[5]:lemma_tweet,header[6]:'None',header[7]:'None',header[8]:'None',header[9]:0})
            if i == 1500:
                break

    for file in csv_filesall:
        f_read = open(pall + '/' + file, 'r', encoding='latin-1')
        reader = csv.reader(f_read, delimiter = ',')
        for row in reader:
            stemmed_tweet = preprocessing.doPreprocessing(row[7], "s")
            lemma_tweet = preprocessing.doPreprocessing(row[7], "l")
            if ( ( len(stemmed_tweet.replace(" ", "").split()) != 0 ) and ( len(stemmed_tweet.replace(" ", "").split()) != 0 ) ):
                writer.writerow({header[0]:'None',header[1]:'None',header[2]:'None',header[3]:'None',header[4]:stemmed_tweet,header[5]:lemma_tweet,header[6]:'None',header[7]:'None',header[8]:'None',header[9]:0})

    for file in csv_filesdiff:
        f_read = open(pdiff + '/' + file, 'r', encoding='latin-1')
        reader = csv.reader(f_read, delimiter = ',')
        for row in reader:
            stemmed_tweet = preprocessing.doPreprocessing(row[9], "s")
            lemma_tweet = preprocessing.doPreprocessing(row[9], "l")
            if ( ( len(stemmed_tweet.replace(" ", "").split()) != 0 ) and ( len(stemmed_tweet.replace(" ", "").split()) != 0 ) ):
                writer.writerow({header[0]:'None',header[1]:'None',header[2]:'None',header[3]:'None',header[4]:stemmed_tweet,header[5]:lemma_tweet,header[6]:'None',header[7]:'None',header[8]:'None',header[9]:0})

'''
Specifically crafted function for creating a noise file for each earthquake.
'''
def noiseCsv(path_to_final_csv):
	l = []
	lines = 0
	opened_file = open(path_to_final_csv, 'r', encoding = 'latin-1')
	reader = csv.reader(opened_file, delimiter=',')
	next(reader)
	for row in reader: #start[1] = month-day-year, start[2] = hour:minutes:seconds
		lines += 1
		l.append(row1)
	start = l[0] #Oldest tweet related to the earthquake under consideration
	startdate = start[1].split('-')
	starttime = start[2].split(':')
	end = l[-1] #last tweet related to the earthquake under consideration
	enddate = end[1].split('-')
	endtime = end[2].split(':')

	#Noise file related to the earthquake under consideration	
	noise_filew = open(path_to_final_csv_noise + 'noise_pakistan.csv', 'w')
	writer = csv.DictWriter(noise_filew, fieldnames = header)
	writer.writeheader()

	#File containing noisy tweets from which we are going to take the noise
	noise_file = open(path_to_final_csv_noise + 'noisy_tweets.csv')
	noise_reader = csv.reader(noise_file, delimiter = ',')
	next(noise_reader)
	noise_list = []
	for row in noise_reader:
		noise_list.append(row)
	
	#We are going to put 30% of noise w.r.t. the number of tweets for each earthquake
	noise_fraction = int(lines * 0.3)
	for x in range(0, noise_fraction):
		randomMonth = 9
		randomDay = 25

		row = noise_list[random.randint(0, len(noise_list)-1)]
		randomHour = random.randint(0, 23)
		randomMinute = random.randint(0, 59)
		randomSeconds = random.randint(0, 59)
		writer.writerow({header[0]: x, #Write row[0] 'id'
            			header[1]: '-'.join([str(randomMonth), str(randomDay), str(startdate[2])]), #Writing the date
						header[2]: ':'.join([str(randomHour), str(randomMinute), str(randomSeconds)]), #Writing the time
						header[3]: row[3], #Text not preprocessed
						header[4]: row[4], #Stemmed text
						header[5]: row[5], #Lemmatized text
						header[6]: row[6], #Longitude
						header[7]: row[7], #Latitude 
						header[8]: row[8], #Author position
						header[9]: row[9]}) # 1: if relevant, 0 otherwise
	noise_filew.close()

	#We have written an intermediate file, then sorting is needed
	fi = open(path_to_final_csv_noise + 'noise_pakistan.csv', 'r', encoding = 'latin-1')
	fi.seek(0)
	readerf = csv.reader(fi, delimiter = ',')
	next(readerf)
	sortedlist = sorted(readerf, key=lambda row: (datetime.strptime(row[1], "%m-%d-%Y"), datetime.strptime(row[2], '%H:%M:%S')))
	noise_fw = open(path_to_final_csv_noise + 'sorted_pakistan_noise.csv', 'w')
	writerf = csv.DictWriter(noise_fw, fieldnames = header)
	writerf.writeheader()
	for row in sortedlist:
		writerf.writerow({header[0]: (row[0])[1:-1], #Write row[0] 'id'
            			header[1]: row[1], #Writing the date
						header[2]: row[2], #Writing the time
						header[3]: row[3], #Text not preprocesssed
						header[4]: row[4], #Stemmed text
						header[5]: row[5], #Lemmatized text
						header[6]: row[6], #Longitude
						header[7]: row[7], #Latitude 
						header[8]: row[8], #Author position
						header[9]: row[9]}) # 1: if relevant, 0 otherwise

noiseCsv(path_to_final_csv)
create_noise()