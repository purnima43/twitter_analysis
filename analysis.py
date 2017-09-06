import json
import pandas as pd
import matplotlib.pyplot as plt
import re
from pandas.io.json import json_normalize 
from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')

#Next we will read the data in into an array that we call tweets.

tweets_data_path = '/home/my/Desktop/eating.txt'

tweets_data = []
tweets_file = open(tweets_data_path, "r")
for line in tweets_file:
    try:
        tweet = json.loads(line)
        tweets_data.append(tweet)
    except:
        continue
  
tweets = pd.DataFrame()
tweets['text'] = map(lambda tweet: tweet['text'], tweets_data)
tweets['lang'] = map(lambda tweet: tweet['lang'], tweets_data)
tweets['country'] = map(lambda tweet: tweet['place']['country'] if tweet['place'] != None else None, tweets_data)


#preprocess the text
def processTweet(tweet):
    # process the tweets

    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet
tweets['prepro'] = tweets['text'].apply(lambda tweet: processTweet(tweet))

#to match for keywords or name of restaurants in whole text
def word_in_text(word, text):
    word = word.lower()
    sentences = re.split(r' *[\.\?!][\'"\)\]]* *', text)
    
    #text = text.lower()
    #pre=tokenize()
    arr=[]
    for stuff in sentences:
         match = re.search(word,stuff)#if we are able to find the word in sentence 
         if match:
             arr.append(stuff)
    list(set(arr))
    return arr
tweets['dominos'] = tweets['prepro'].apply(lambda tweet: word_in_text('dominos', tweet))
tweets['pizza hut'] = tweets['prepro'].apply(lambda tweet: word_in_text('pizza hut', tweet))
len1=len(tweets['dominos'])
#i=0 
strhut=[]
strdomi=[]
##conerting to list the non empty values of dataframes
def division(word):
    i=0
    str4=[]
    while i<len1:
        if len(tweets[word][i])!=0: 
            str4.append(tweets[word][i])
        i=i+1
    return str4
strhut=division('pizza hut')
strdomi=division('dominos')
###the core function to perform sentiment analysis on data
def sentiment_anal(list1):
    newlist=[]
    for i in list1:
        if i not in newlist:
            newlist.append(i)

    i=0
    k=len(newlist)
    pos=0
    neg=0
    while i<k:
    #i=i+1
        s1=str(newlist[i]).strip('[]')
        s1.strip('u ')
        res = nlp.annotate(s1,
                            properties={
                               'annotators': 'sentiment',
                               'outputFormat': 'json',
                               'timeout': 50000,
                           })

        for s in res["sentences"]:
            print "%d: '%s': %s %s" % (
                s["index"],
                " ".join([t["word"] for t in s["tokens"]]),
                s["sentimentValue"], s["sentiment"])
            if s["sentiment"]=='Positive':
                pos=pos+1
            if s["sentiment"]=='Negative':
                neg=neg+1
        i=i+1
    print 'positive reviews are ',pos
    print 'negative reviews are ',neg
    print 'total reviews are',i
sentiment_anal(strhut)#calling the function for each one of dominos and pizzahut
sentiment_anal(strdomi)

