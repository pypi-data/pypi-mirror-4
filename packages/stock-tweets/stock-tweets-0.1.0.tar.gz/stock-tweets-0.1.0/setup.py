from distutils.core import setup
from setuptools import find_packages

setup(
	name='stock-tweets',
	version='0.1.0',
	author='Harry Kim',
	author_email='hkim85@gmail.com',
	packages=find_packages(),
	scripts=[],
	url='http://pypi.python.org/pypi/stock-tweets/',
	license='LICENSE.txt',
	description='Display stock and Tweet information',
	long_description=open('README.txt').read(),
	install_requires=[
	"Django >= 1.1.1",
 	"psycopg2==2.4.5",
  "requests==0.14.1",
  "simplejson==2.6.2",
  "twython==2.4.0",
  "wsgiref==0.1.2",
	],
	include_package_data=True,
	zip_safe=False,
)
