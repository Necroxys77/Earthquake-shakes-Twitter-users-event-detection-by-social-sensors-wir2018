import csv
import time
import tweepy

# tweet_id, tweet_time, tweet_lon, tweet_lat, tweet_text, tweet_author_id, author_position, label

file_payed = open('/home/mmariani/Desktop/wir_project/datasets/CrisisNLP_labeled_data_crowdflower/2014_California_Earthquake/2014_california_eq.csv', 'r', encoding = 'latin-1')
file_volunteers = open('/home/mmariani/Desktop/wir_project/datasets/CrisisNLP_volunteers_labeled_data/2014_California_Earthquake/2014_California_Earthquake.csv', 'r', encoding = 'latin-1')

reader_payed = csv.reader(file_payed, delimiter=',')
reader_volunteers = csv.reader(file_volunteers, delimiter=',')
next(reader_payed)
next(reader_volunteers)

'''
Function that given the id of a tweet, it uses Tweepy to retrieve thw whole status object. Then, from that we will keep only the information needed:
- creation time and creation date
- coordinates at which it has been posted
- author id
- author position
'''
def retrieve_tweet_info(tweet_id):

	consumer_token = 'ETFCxxqm4tjN7xd5TIhXg2RIX'
	consumer_secret = 'mNIUzH4FrsRJpIc2hiMKmRIhDnDIJfTBBbRtmIRPTPW2TkNnl8'

	auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
	auth.set_access_token('941832650-BHsUvRMpKh2f0e9OYCyjuGcgvZjt7j7HcCQZCsTR', 'oLrFrByYqUciVE7hFB9tffhtNQqrWhh0PxygFPD97ibbB')
  
	api = tweepy.API(auth)
	tweet_info = []
	# Trasforming the status object into a json representation
	tweet = api.get_status(tweet_id, tweet_mode='extended')._json

	tweet_info.append(tweet['id'])
	tweet_info.append(tweet['created_at'])
	if (tweet['coordinates'] == None):
		tweet_info.append('None')
		tweet_info.append('None')
	else:
		tweet_info.append(tweet['coordinates']['coordinates'][0])
		tweet_info.append(tweet['coordinates']['coordinates'][1])
	tweet_info.append(tweet['full_text'])
	tweet_info.append(tweet['user']['id'])	
	tweet_info.append(tweet['user']['location'])

	return tweet_info

'''
In the function below, we are going to scan all .csv files containing labeled tweets by volunteers and payed people. For each of them, we use APIs offered by Tweepy
to retrive all information related to those tweets keeping only those needed. At the end, we have a .csv file for each earthquake.
'''
def main():
	effect_written = 0
	analyzed = 0	
	#This will be the final file for country earthquake
	final_csv = open('california.csv', 'w')

	#The header of the .csv file
	header = ['tweet_id', 'tweet_time', 'tweet_lon', 'tweet_lat', 'tweet_text', 'tweet_author_id', 'author_position', 'label']
	writer = csv.DictWriter(final_csv, fieldnames = header)
	writer.writeheader()

	tmp_list = [] #Used checking for duplicates between volunteers and payed
	#Here we are going to scan the .csv file from volunteers
	for row in reader_volunteers:
		tmp_list.append(row[0])
		try:
			analyzed = analyzed + 1

			tweet_info = retrieve_tweet_info((row[0])[1:-1])
			writer.writerow({header[0]: (row[0])[1:-1], #Write row[0] 'id'
                        header[1]: tweet_info[1], #Retrieve tweet time and write it down
                        header[2]: tweet_info[2], #Retrieve tweet_lon and write it down
                        header[3]: tweet_info[3], #Retrieve tweet_lat and write it down
                        header[4]: tweet_info[4], #Write 'text'
                        header[5]: tweet_info[5], #Write user 'id' 
                        header[6]: tweet_info[6], #Write user 'location'
                        header[7]: row[9]}) #Write row[9] 'label'

			effect_written = effect_written + 1
		except tweepy.RateLimitError: #Triggered when reaching 900 retrieved tweets -> need to wait 15 minutes
			print("Sleeping for a while...")
			time.sleep(70 * 15) #Waiting more just to be sure
		except tweepy.TweepError as error:
			if error.api_code == 88: #Rate limit exceed
				print(error)
				print('When issuing: ' + str(row[0]) + '\n')
				print('Sleeping for a while..')
				time.sleep(70 * 15)
			else:
				print(error)

	#Here we are going to scan the .csv file from payed people
	for row in reader_payed:
		#If it has been already retrieve, we skip it
		if (row[8] not in tmp_list):
			try:
				analyzed = analyzed + 1
				
				tweet_info = retrieve_tweet_info((row[8])[1:-1])
				writer.writerow({header[0]: (row[8])[1:-1], #Write row[8]
                        header[1]: tweet_info[1], #Retrieve tweet time and write it down
                        header[2]: tweet_info[2], #Retrieve tweet_lon and write it down
                        header[3]: tweet_info[3], #Retrieve tweet_lat and write it down
                        header[4]: tweet_info[4], #Write 'text'
                        header[5]: tweet_info[5], #Write user 'id' 
                        header[6]: tweet_info[6], #Write user 'location'
                        header[7]: row[5]}) #Write row[5]

				effect_written = effect_written + 1
			except tweepy.RateLimitError:#Triggered when reaching 900 retrieved tweets -> need to wait 15 minutes
				print("Sleeping for a while...")
				time.sleep(70 * 15) #Waiting more just to be sure
			except tweepy.TweepError as error:
				if error.api_code == 88: #Rate limit exceed
					print(error)
					print('When issuing:' + str(row[8]) + '\n')
					print('Sleeping for a while..')
					time.sleep(70 * 15) #Sleeping for 15 minutes
				else:
					print(error)

main()

