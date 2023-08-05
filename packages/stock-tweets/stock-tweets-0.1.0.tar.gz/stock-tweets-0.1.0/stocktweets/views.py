from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import DatabaseError, connection, IntegrityError, transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import sys
from stocktweets.forms import AddSymbolForm
from stocktweets.models import Stock
from stocktweets.utils import getStockInfo, getTwitterMentions, sortStocks
from django.forms.util import ErrorList
from decimal import Decimal
import constants

def index(request, hours=1):
	errors = []
	# adding a symbol
	if request.method == 'POST':
		if 'symbol' in request.POST:
			symbolForm = AddSymbolForm(request.POST)
			if symbolForm.is_valid():
				newSymbol = symbolForm.cleaned_data['symbol'].upper().split()[0] # chop off after space
				with transaction.commit_on_success():
					try:
						newStock = Stock.objects.create(symbol=newSymbol)
						getStockInfo([newStock])
						newStock.save()
						# if no info found on stock don't add it
						if newStock.price == Decimal(0) and newStock.change == Decimal(0) and newStock.avgVol == 0:
							symbolErrors = symbolForm._errors.setdefault("symbol", ErrorList())
							symbolErrors.append(constants.ERR_NO_SYMBOL + newSymbol)
							newStock.delete()
					except IntegrityError: # trying to add duplicate
						transaction.rollback()
						symbolErrors = symbolForm._errors.setdefault("symbol", ErrorList())
						symbolErrors.append(constants.ERR_DUPLICATE + newSymbol)
				

				stockList = Stock.objects.all()
				hours = int(request.POST.get("hours", 1))
				error = getTwitterMentions(stockList, hours)
				errors.extend(error)
				stockList = sortStocks(stockList)
				return render_to_response('stocktweets/index.html', 
						{ 'stocks': stockList, 'symbolForm': symbolForm, 'hours': hours, 'errors': errors},
						context_instance = RequestContext(request))
	else:
		symbolForm = AddSymbolForm()	

	stockList = Stock.objects.all()
	getStockInfo(stockList)
	error = getTwitterMentions(stockList, hours)
	errors.extend(error)
	stockList = sortStocks(stockList)

	return render_to_response('stocktweets/index.html', 
			{ 'stocks': stockList, 'symbolForm': symbolForm, 'hours': hours, 'errors':errors},
			context_instance = RequestContext(request))

def deleteStock(request, id, hours=1):
	errors = []
	try:
		Stock.objects.get(pk=id).delete()
	except Stock.DoesNotExist:
		errors = [constants.ERR_NO_STOCK]

	stockList = sortStocks(Stock.objects.all())
	symbolForm = AddSymbolForm()	

	return render_to_response('stocktweets/index.html', 
			{ 'stocks': stockList, 'symbolForm': symbolForm, 'hours': hours, 'errors': errors}, 
			context_instance = RequestContext(request))
