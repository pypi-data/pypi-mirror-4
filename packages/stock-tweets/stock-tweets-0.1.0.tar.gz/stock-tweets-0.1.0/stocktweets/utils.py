import urllib
import re
from decimal import Decimal
from twython import Twython, TwythonError
from datetime import datetime, timedelta
from stocktweets.models import Tweet
import constants

from django.utils import timezone
from django.db import transaction

def getStockInfo(stockList):
	symbols = ",".join([stock.symbol for stock in stockList]) # create comma separated string of symbols
	stat = "l1c1p2va2n" #l1 - price c1 - change p2 - pct change v - volume a2 - avg vol n-name
	url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbols, stat)
	stockData = urllib.urlopen(url).readlines()
	for i in range(len(stockList)):
		sd = re.sub('["%+]', '', stockData[i].strip())
		sd = str.replace(sd, 'N/A', '0')
		sd = sd.split(',')
		stockList[i].price = Decimal(sd[0])
		stockList[i].change = Decimal(sd[1])
		stockList[i].pctChange = Decimal(sd[2])
		stockList[i].volume = int(sd[3])
		stockList[i].avgVol = int(sd[4])
		stockList[i].name = sd[5]
		stockList[i].save

def getTwitterMentions(stockList, hours):
	twitter = Twython()
	timeNow = timezone.now()
	hour = 3600 * int(hours)
	Tweet.objects.all().delete()
	errors = []
	for stock in stockList:
		stock.mentions = 0
		stop = False
		for i in range(1,15): # max 15 pages
			if stop:
				break
			cashtag = "$" + stock.symbol
			try:
				searchResults = twitter.search(q=cashtag, rpp="100", page=i, result_type="recent")
			except TwythonError as te:
				errors.append(u"An error occured searching Twitter, please try again in a few moments.") 

			if not searchResults["results"]:
				break
			else:
				# Get some tweets
				if stock.tweet_set.all().count() < constants.NUM_TWEETS:
					for t in searchResults["results"]:
						if not(t["text"].startswith("RT")): #don't add retweets
							created = datetime.strptime(t["created_at"], "%a, %d %b %Y %H:%M:%S +0000")
							created = timezone.make_aware(created, timezone.utc)
							tweet = Tweet.objects.create(stock=stock, screenName=t["from_user"], message=t["text"], tweetId=t["id_str"], date=created)
						if stock.tweet_set.all().count() > constants.NUM_TWEETS:
							break
						 
				for j in reversed(searchResults["results"]):
					tweetCreated = datetime.strptime(j["created_at"], "%a, %d %b %Y %H:%M:%S +0000")
					tweetCreated = timezone.make_aware(tweetCreated, timezone.utc)
					secondsElapsed = (timeNow - tweetCreated).total_seconds()
					if secondsElapsed <= hour:
						stock.mentions += searchResults["results"].index(j)+1	
						stock.save()
						if j != searchResults["results"][-1]:
							stop = True
						break
					elif j == searchResults["results"][0] and secondsElapsed > hour:
						stop = True
						break

	return errors

def sortStocks(stockList):
	return sorted(stockList, key=lambda stock: stock.mentions, reverse=True)	
