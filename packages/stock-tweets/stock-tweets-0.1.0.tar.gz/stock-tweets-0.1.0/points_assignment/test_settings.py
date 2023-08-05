import logging
import os
 
from settings import *
 
 
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': ':memory:'
	}
}
