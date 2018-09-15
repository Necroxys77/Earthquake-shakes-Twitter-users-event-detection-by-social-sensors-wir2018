import os, io
import csv, random, time
from datetime import datetime
import preprocessing

path_to_csv = '/Users/riccardochiaretti/Desktop/Engineering in Computer Science/First Year/Second Semester/Web Information & Retrieval/Project/csv Files/Unprocessed_tweets/'
inter_path = '/Users/riccardochiaretti/Desktop/Engineering in Computer Science/First Year/Second Semester/Web Information & Retrieval/Project/csv Files/Preprocessed_tweets/'
path_to_final_csv = '/Users/riccardochiaretti/Desktop/Engineering in Computer Science/First Year/Second Semester/Web Information & Retrieval/Project/csv Files/Preprocessed_tweets/sorted/sorted_pakistan_preprocessed.csv'
path_to_final_csv_noise = '/Users/riccardochiaretti/Desktop/Engineering in Computer Science/First Year/Second Semester/Web Information & Retrieval/Project/csv Files/Preprocessed_tweets/sorted/'
header = ['tweet_id', 'date', 'time','tweet_text', 'tweet_stemmed', 'tweet_lemmatized', 'tweet_lon', 'tweet_lat', 'author_position','label_10']

def main():
	csv_files = os.listdir(path_to_csv) #List of all csv files
	csv_files.remove('.DS_Store') #MacOS directory
	for file in csv_files:
		opened_file = open(path_to_csv + file, 'r', encoding = 'latin-1')
		reader_file = csv.reader(opened_file, delimiter=',')
		next(reader_file) #Skipping the header of the .csv file

		preprocessed_file = open(inter_path + file + 'inter.csv', 'w') #File in which writing the intermediate set of tweets, still unsorted 
		writer = csv.DictWriter(preprocessed_file, fieldnames = header)
		writer.writeheader()

		for row in reader_file:
			if ( (row[7] == 'Other relevant information') or (row[7] == 'Not related or irrelevant') ): #Here, we are collapsing 9 classes into 2: crisis-related (1) or not (0)
				label = 0
			else:
				label = 1
			
			#Here we are going to split date and time into two different columns and removing useless info 
			time_date = []
			time_date = row[1].split()
			time_date.remove(time_date[0]) #Removing day
			time_date.remove(time_date[3]) #Removing +0000
			time_date[2], time_date[3] = time_date[3], time_date[2] #Swappping time and year. At the end spl[2] = year
			time = time_date[3]
			time_date.remove(time_date[3]) #Removing time
			#Mapping month to its number which is needed for sorting tweets
			if time_date[0] == 'Aug':
				time_date[0] = '8'
			elif time_date[0] == 'Apr':
				time_date[0] = '4'
			elif time_date[0] == 'Sep':
				time_date[0] = '9'
			elif time_date[0] == 'Jan':
				time_date[0] = '1'
			elif time_date[0] == 'Feb':
				time_date[0] = '2'
			elif time_date[0] == 'Mar':
				time_date[0] = '3'
			elif time_date[0] == 'May':
				time_date[0] = '5'
			elif time_date[0] == 'Jun':
				time_date[0] = '6'
			elif time_date[0] == 'Jul':
				time_date[0] = '7'
			elif time_date[0] == 'Oct':
				time_date[0] = '10'
			elif time_date[0] == 'Nov':
				time_date[0] = '11'
			elif time_date[0] == 'Dec':
				time_date[0] = '12'
			row[1] = '-'.join(time_date)
			stemmed_tweet = preprocessing.doPreprocessing(row[4], "s") #Stemmed tweet
			lemma_tweet = preprocessing.doPreprocessing(row[4], "l") #Lemmatized tweet
			if ( ( len(stemmed_tweet.replace(" ", "").split()) != 0 ) and ( len(stemmed_tweet.replace(" ", "").split()) != 0 ) ):
				writer.writerow({header[0]: (row[0])[1:-1], #Write row[0] 'id'
            				header[1]: row[1], #Writing the date
							header[2]: time, #Writing the time
							header[3]: row[4], #Text not preprocessed
							header[4]: stemmed_tweet, #Stemmed text
							header[5]: lemma_tweet, #Lemmatized text
							header[6]: row[2], #Longitude
							header[7]: row[3], #Latitude 
							header[8]: row[6], #Author position
							header[9]: label}) # 1: if relevant, 0 otherwise

'''
This function is responsible of reading all intermediate files previously created, sorting them and writing the final .csv file
'''
def sort(inter_path, path_to_final_csv, header):
	preprocessing.sortByDate(inter_path, path_to_final_csv, header)

main()
sort(inter_path, path_to_final_csv, header)
