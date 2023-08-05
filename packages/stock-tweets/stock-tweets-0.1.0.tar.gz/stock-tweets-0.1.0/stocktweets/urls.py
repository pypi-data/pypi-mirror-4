from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('stocktweets.views',
	url(r'^$', 'index'),
	url(r'^(\d+)/$', 'index'),
	url(r'^deleteStock/(\d+)/$', 'deleteStock'),
	url(r'^deleteStock/(\d+)/(\d+)/$', 'deleteStock'),
	url(r'^about/$', direct_to_template, {'template': 'about.html'}),
)
