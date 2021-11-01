# NLP analysis of RiPS transcripts using NLTK
# requirements: python3 -m pip install nltk[all], wordcloud
# read in the csv file and print sentiment scores per sentence

import pandas as pd
import csv

import nltk
#nltk.download('punkt')
#nltk.download('vader_lexicon')
#nltk.download('stopwords')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from wordcloud import WordCloud
from PIL import Image


transd = 'transcript/'
sentd = 'sentimentAgg10/'
wcd = 'wordcloud/'
fqd = 'top100/'
trans = ['comment']

transf_list = ['2020-11-16fetch_AWS','2020-11-17fetch_AWS_v1','2020-11-18fetch_AWS_v1','2020-11-23fetch_AWS_v1',
               'pepper_1','pepper_2','pepper_3','pepper_4','WS3_Fetch','WS3_Pepper','WS3_all',
               '2020-11-16fetch_AWS_simu','2020-11-17fetch_AWS_v1_simu','2020-11-18fetch_AWS_v1_simu',
               '2020-11-23fetch_AWS_v1_simu','pepper_1_simu','pepper_2_simu','pepper_3_simu','pepper_4_simu',
               'WS3_Fetch_simu','WS3_Pepper_simu','WS3_all_simu','2020-11-16fetch_AWS_robo','2020-11-17fetch_AWS_v1_robo',
               '2020-11-18fetch_AWS_v1_robo','2020-11-23fetch_AWS_v1_robo','pepper_1_robo','pepper_2_robo','pepper_3_robo',
               'pepper_4_robo','WS3_Fetch_robo','WS3_Pepper_robo','WS3_all_robo']

for transf in transf_list:
	# read in transcripts
	df = pd.read_csv((transd+transf+'.csv'),usecols=trans)
	df_agg = df[trans].groupby(np.repeat(np.arange(len(df)), 10)[:len(df)]).agg(' '.join) # concatenate every 10 sentences
	
	# apply VADER pretrained sentiment analysis tools
	# https://ojs.aaai.org/index.php/ICWSM/article/view/14550
	sid = SentimentIntensityAnalyzer()
	sentscores = []
	for sentence in df_agg.comment:#df.comment
		score = sid.polarity_scores(sentence)
		sentscores.append(score)

	# print to file
	with open((sentd+transf+'_sentscore.csv'),'w') as outf:
		wr = csv.writer(outf,delimiter='\n')
		wr.writerow(sentscores)


	
	# generate word cloud
	# remove stop words and other less meaningful words
	stop = set(stopwords.words('english'))
	stop.update(['yeah','really','one','okay','maybe','uh','could','thio','sort','right','probably','e',
                     'gonna','z','kind','mhm','would','um','something','going','mean','like','well','actually',
                     'also','oh','mm','know','think','might','bit','way','thing','guess','much','eso'])

	# print top 100 most frequent words
	series = df['comment']
	text = series.str.cat(sep = ' ')
	list_of_words = [i.lower() for i in wordpunct_tokenize(text) if i.lower() not in stop and i.isalpha()]
	wordfreqdist = nltk.FreqDist(list_of_words)
	mostcommon = []
	mostcommon = wordfreqdist.most_common(100)
	#print('top 100 most frequent words:',mostcommon)
	with open((fqd+transf+'_top100.csv'),'w') as outf:
		wr = csv.writer(outf,delimiter='\n')
		wr.writerow(mostcommon)

	# generate a square wordcloud
	wordcloud1 = WordCloud(width=1800,height=1400).generate(' '.join(list_of_words))
	wordcloud1.to_file(wcd+transf+'_wc_square.png')

	# generate a android shaped wordcloud
	mask = np.array(Image.open('android.png'))
	wordcloud2 = WordCloud(background_color="white", max_words=200, mask=mask, stopwords=stop,
						   contour_width=3, contour_color='steelblue').generate(' '.join(list_of_words))
	wordcloud2.to_file(wcd+transf+'_wc_andriod.png')
	
	print('Completed:',transf)

print('All files processed!')
