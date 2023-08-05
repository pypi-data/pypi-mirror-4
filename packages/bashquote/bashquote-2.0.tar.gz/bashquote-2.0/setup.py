#!/usr/bin/env python

from distutils.core import setup

long_description = """
This is a Python library for accessing and printing quotes from bash.org, a
quote database on the Internet from various chat sources. It is NOT made by
bash.org, or endorsed by them in any way. Note that it merely uses HTML 
parsing to filter through the site's content

The BashQuote object can be created directly (BashQuote(8)) or it can be
created using various functions. getQuoteSafe and getQuote take a quote 
number and return a quote object- getQuoteSafe checks to verify the quote
exists. Then, getLatestQuote and getRandomQuote will both do HTML parsing to
find the quote numbers. 

These BashQuote objects then have various helper functions which can return
various data about a quote. So, for instance, to get the text of a random 
quote, BashQuote.getText() will print out all the text. Or to check if a
quote is pending, isPending() will return true if the quote has yet to be
processed for approval, and so on.
"""

setup(name='bashquote',
	version='2.0',
	description='Library to access and retrieve quotes from bash.org',
	long_description=long_description,
	author='Ben Rosser',
	license="MIT",
	author_email='rosser.bjr@gmail.com',
	url='http://venus.arosser.com/projects/bashquote.html',
	py_modules=['bashquote'],
	)
