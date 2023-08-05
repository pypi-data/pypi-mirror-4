from django.test import TestCase
from stocktweets.models import Stock
from stocktweets.forms import AddSymbolForm
from django import forms
import constants

class StockTweetsViewsTestCase(TestCase):
	def test_about_page(self):
		#test it exists
		resp = self.client.get('/stocktweets/about/')
		self.assertEqual(resp.status_code, 200)

	def test_index(self):
		resp = self.client.get('/stocktweets/')
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('stocks' in resp.context)
		self.assertTrue('symbolForm' in resp.context)
		self.assertTrue('hours' in resp.context)
		self.assertTrue('errors' in resp.context)

	def test_add_stock(self):
		# ensure stock was added
		resp = self.client.post('/stocktweets/', {'symbol': 'RIMM'})
		self.assertEqual(resp.status_code, 200)
		numStocks = Stock.objects.all().count()
		self.assertEqual(numStocks, 1)

		# send blank symbol
		resp = self.client.post('/stocktweets/', {'symbol': ''})
		self.assertEqual(resp.status_code, 200)
		self.assertTrue(u'This field is required.' in resp.context['symbolForm'].errors['symbol']) 

		# send junk symbol
		symbol = 'ERPIWJEPR'
		resp = self.client.post('/stocktweets/', {'symbol': symbol})
		self.assertEqual(resp.status_code, 200)
		self.assertIn(constants.ERR_NO_SYMBOL + symbol, resp.context['symbolForm'].errors['symbol']) 

		# send duplicate symbol
		#resp = self.client.post('/stocktweets/', {'symbol': 'RIMM'})
		#self.assertEqual(resp.status_code, 200)

	def test_change_time(self):
		# add the stock
		resp = self.client.post('/stocktweets/', {'symbol': 'GOOG'})
		self.assertEqual(resp.status_code, 200)
		hour1Mentions =  Stock.objects.get(pk=1).mentions

		# change hours for mentioned tweets
		resp = self.client.get('/stocktweets/5/')
		self.assertEqual(resp.status_code, 200)
		hour2Mentions =  Stock.objects.get(pk=1).mentions

		# could be false if stock hasn't been mentioned more in the past 5 hours, but should usually..
		self.assertTrue(hour2Mentions > hour1Mentions)

		# decrease hours again
		resp = self.client.get('/stocktweets/2/')
		self.assertEqual(resp.status_code, 200)
		hour3Mentions =  Stock.objects.get(pk=1).mentions

		# could be false if stock hasn't been mentioned more in the past 5 hours, but should usually..
		self.assertTrue(hour3Mentions < hour2Mentions)

