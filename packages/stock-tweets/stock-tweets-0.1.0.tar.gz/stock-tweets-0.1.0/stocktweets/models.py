from django.db import models
from django.contrib.auth.models import User 

class Stock(models.Model):
	symbol = models.CharField(max_length=48, unique=True)
	name = models.CharField(max_length=200)
	mentions = models.IntegerField(default=0)
	price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	pctChange = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	volume = models.IntegerField(default=0)
	avgVol = models.IntegerField(default=0)

class Tweet(models.Model):
	stock = models.ForeignKey(Stock)
	name = models.CharField(max_length=20)
	screenName = models.CharField(max_length=15)
	message = models.TextField()
	tweetId = models.CharField(max_length=200)
	date = models.DateTimeField()
