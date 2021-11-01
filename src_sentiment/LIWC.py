# NLP analysis of RiPS transcripts using LIWC disctionary
# read in the csv file and print sentiment scores per sentence 
# sentiment scores calculated as [C(PosWords) - C(NegWords)] / Len(Utterance), value [-1,+1]
# classification: pos if sent score > 0, neg if sent score < 0, neutral if sent score = 0
# dictionary from https://github.com/abhilash-shrivastava/LIWC-Dictionary

import pandas as pd
import csv

import nltk
#nltk.download('punkt')
#nltk.download('vader_lexicon')
#nltk.download('stopwords')

import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize


transd = 'transcript/'
sentd = 'LIWCsentAgg10/'
trans = ['comment']

transf_list = ['2020-11-16fetch_AWS','2020-11-17fetch_AWS_v1','2020-11-18fetch_AWS_v1','2020-11-23fetch_AWS_v1',
               'pepper_1','pepper_2','pepper_3','pepper_4','WS3_Fetch','WS3_Pepper','WS3_all',
               '2020-11-16fetch_AWS_simu','2020-11-17fetch_AWS_v1_simu','2020-11-18fetch_AWS_v1_simu',
               '2020-11-23fetch_AWS_v1_simu','pepper_1_simu','pepper_2_simu','pepper_3_simu','pepper_4_simu',
               'WS3_Fetch_simu','WS3_Pepper_simu','WS3_all_simu','2020-11-16fetch_AWS_robo','2020-11-17fetch_AWS_v1_robo',
               '2020-11-18fetch_AWS_v1_robo','2020-11-23fetch_AWS_v1_robo','pepper_1_robo','pepper_2_robo','pepper_3_robo',
               'pepper_4_robo','WS3_Fetch_robo','WS3_Pepper_robo','WS3_all_robo']

stop = set(stopwords.words('english'))

# loading all the positive words in the the variable array posWords
with open('PosWords.txt') as f_pos:
    posContent = f_pos.readlines()
    posWords = []
    for num in range(0, len(posContent)):
        posContent[num] = posContent[num].split("\n")
        posWords.append(posContent[num][0].lower());

# loading all the negative words in the variable array negWords
with open('NegWords.txt') as f_neg:
    negContent = f_neg.readlines()
    negWords = []
    for num in range(0, len(negContent)):
        negContent[num] = negContent[num].split("\n")
        negWords.append(negContent[num][0].lower());

# compute sentiment scores
for transf in transf_list:
	# read in transcripts
	df = pd.read_csv((transd+transf+'.csv'),usecols=trans)
	df_agg = df[trans].groupby(np.repeat(np.arange(len(df)), 10)[:len(df)]).agg(' '.join) # concatenate every 10 sentences
	
	sentscores = []
	for sentence in df_agg.comment:#df.comment
		# remove stop words
		words = [i.lower() for i in wordpunct_tokenize(sentence) if i.lower() not in stop and i.isalpha()]
		
		# initialize counters
		UttSize = 0
		PosCount = 0
		NegCount = 0
		sentlabel = ''
		
		# count positive and negative words
		for word in words:
			if word in posWords:
				PosCount = PosCount + 1
			elif word in negWords:
				NegCount = NegCount + 1
		
		# compute sentiment score and label
		if len(words) == 0:
			UttSize = 1
		else:
			UttSize = len(words)
		score = (PosCount - NegCount) / UttSize
		if score > 0:
			sentlabel = 'Positive'
		elif score < 0:
			sentlabel = 'Negative'
		else:
			sentlabel = 'Neutral'
		sentscores.append([score,sentlabel])

	# print to file
	with open((sentd+transf+'_sentscore.csv'),'w') as outf:
		wr = csv.writer(outf,delimiter='\n')
		wr.writerow(sentscores)

	print('Completed:',transf)

print('All files processed!')



