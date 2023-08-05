"""Python library for accessing bash.org quotes

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
processed for approval, and so on."""

import HTMLParser
import random
import urllib

class BashQuote:

	def __init__(self, quoteNum):
		self.quoteNum = quoteNum
		self.numLines = -1
		self.quoteText = ""
		self.quoteLink = "http://www.bash.org/?" + str(quoteNum)
		self.exists = True
		self.pending = False
		self.quoteArray = []
		
		#The zeroth (and, obviously, some negative number) quote does not exist, ignore
		if quoteNum <= 0:
			self.quoteText = "Quote #" + str(quoteNum) + " does not exist."
			self.exists = False
			return

		#Retrieve quote text, format it, and process it into an array of strings
		bashSite = self.quoteLink
		rawBash = urllib.urlopen(bashSite).read()
		headerlen = self.getHeaderSize(rawBash)
		quoteText = rawBash[headerlen:]
		self.quoteText = self.doHTMLFormatting(quoteText)
		self.quoteArray = quoteText.partition("/n")
		self.numLines = len(self.quoteArray)
		
		#Check existance and pending status
		if "does not exist" in self.quoteText:
			self.setBlankQuote()
			self.quoteText = "Quote #" + str(quoteNum) + " does not exist."
		elif "was rejected" in self.quoteText:
			self.setBlankQuote()
			self.quoteText = "Quote #" + str(quoteNum) +  " was rejected."
		elif "pending moderation" in self.quoteText:
			self.pending = True
			self.setBlankQuote()
			self.quoteText = "Quote #" + str(quoteNum) + " is pending moderation."
			
	def __str__(self):
		"""String representation of a BashQuote object"""
		return "bash.org quote number " + str(self.quoteNum) + " at " + self.quoteLink

	def __repr__(self):
		"""String representation of a BashQuote object"""
		return "bash.org quote number " + str(self.quoteNum) + " at " + self.quoteLink

	def getLine(self, lineNum):
		"""Returns a specific line from a quote"""
		if 1 <= lineNum < self.numLines - 1:
			return self.quoteArray[lineNum - 1]
		return ""

	def getNumber(self):
		"""Returns the quote number"""
		return self.quoteNum

	def getText(self):
		"""Returns the quote text with lines separated by \n"""
		return self.quoteText

	def getNumLines(self):
		"""Returns the number of lines"""
		return self.numLines

	def getLink(self):
		"""Returns a link to the quote on bash.org"""
		return self.quoteLink

	def isExists(self):
		"""Returns true if a quote exists (is publically visible), false if it is not for whatever reason"""
		return self.exists
		
	def isPending(self):
		"""Returns true if a quote is not publically visible but is pending moderation"""
		return self.pending

	#Utility functions meant for internal usage only
	
	def getHeaderSize(self, bashQuote):
		"""Utility function, returns size of a bash.org page's header (the page text is in bashQuote)"""
		quotestart = '<p class="qt">'
		headerlen = bashQuote.find(quotestart)
		headerlen += len(quotestart)
		return headerlen
		
	def doHTMLFormatting(self, quoteText):
		"""Perform formatting to clean up the quote text and make it human-readable"""
		quoteText = quoteText[:quoteText.find('</p>')]
		quoteText = quoteText.replace('\r', '')
		quoteText = quoteText.replace('<br />', '')
		quoteText += "\n"
		parser = HTMLParser.HTMLParser()
		try:
			quoteText = parser.unescape(quoteText)
		except:
			pass
		return quoteText

	def setBlankQuote(self):
		"""'Blanks' a quote by wiping out the content of the quote array, quote text, sets number of lines to -1, and flags it as not existing"""
		self.exists = False
		self.numLines = -1
		self.quoteArray = []
		self.quoteText = ""
		
def getRandomQuoteNum():
	"""Function that returns a random quote number"""
	#Open the Latest page on bash.org and get a random one
	bashRand = "http://www.bash.org/?random"
	rawRand = urllib.urlopen(bashRand).read()
	numQuotes = rawRand.count('<p class="quote">')
	random.seed()
	randQuote = random.randint(0, numQuotes - 1)
	quotes = []
	start = 0
	while numQuotes >= 0:
		start = rawRand.find('<p class="quote">', start) + 1
		quotes.append(start + 26)
		numQuotes -= 1

	#Remove last quote, it's screwy and shouldn't be there
	quotes.remove(quotes[-1])
	
	#Grab the random quote number and manipulate it
	randQuote = quotes[randQuote]
	numString = rawRand[randQuote:]
	numString = numString[:numString.find('"')]
	try:
		numBash = int(numString)
	except:
		return 0

	return numBash

def getLatestQuoteNum():
	"""Function that returns the number of the last-approved bash.org quote"""
	#Open the Latest page on bash.org
	bashRand = "http://www.bash.org/?latest"
	rawRand = urllib.urlopen(bashRand).read()

	#Grab the first quote number and manipulate it
	numString = rawRand[2767:]
	numString = numString[:numString.find('"')]
	try:
		numBash = int(numString)
	except:
		return 0

	return numBash

def getLatestQuote():
	"""Function that returns """
	numBash = getLatestQuoteNum()
	return BashQuote(numBash)

def getRandomQuote():
	"""Function that returns a BashQuote object for a random quote number, is (almost) guaranteed to be valid"""
	numBash = getRandomQuoteNum()
	return BashQuote(numBash)

def getQuoteSafe(num):
	"""Function to return a BashQuote object for a given quote number, returns BashQuote(-1) if the quote does not exist"""
	quote = getQuote(num)
	if not quote.isExists():
		print "Error: You have requested a quote object that is either pending, was rejected, or does not exist."
		return BashQuote(-1)
	return quote
	
def getQuote(num):
	"""Function to return a BashQuote object for a given quote number-- note, does not check for valid quote numbers"""
	return BashQuote(num)
