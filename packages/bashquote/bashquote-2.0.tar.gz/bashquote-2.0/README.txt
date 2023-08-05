bashquote v2.0 - A Python interface to bash.org
By Ben Rosser
Released under MIT License (see LICENSE.txt)

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

-------------------------------------------------------------------------------

Documentation:

I will eventually get around to generating some proper HTML docs for the module,
but in the mean time here's the output of "pydoc bashquote":

-------------------------------------------------------------------------------

Help on module bashquote:

NAME
    bashquote - Python library for accessing bash.org quotes

FILE
    /usr/lib/python2.7/site-packages/obashquote.py

DESCRIPTION
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

CLASSES
    BashQuote
    
    class BashQuote
     |  Methods defined here:
     |  
     |  __init__(self, quoteNum)
     |  
     |  __repr__(self)
     |      String representation of a BashQuote object
     |  
     |  __str__(self)
     |      String representation of a BashQuote object
     |  
     |  doHTMLFormatting(self, quoteText)
     |      Perform formatting to clean up the quote text and make it human-readable
     |  
     |  getHeaderSize(self, bashQuote)
     |      Utility function, returns size of a bash.org page's header (the page text is in bashQuote)
     |  
     |  getLine(self, lineNum)
     |      Returns a specific line from a quote
     |  
     |  getLink(self)
     |      Returns a link to the quote on bash.org
     |  
     |  getNumLines(self)
     |      Returns the number of lines
     |  
     |  getNumber(self)
     |      Returns the quote number
     |  
     |  getText(self)
     |      Returns the quote text with lines separated by
     |  
     |  isExists(self)
     |      Returns true if a quote exists (is publically visible), false if it is not for whatever reason
     |  
     |  isPending(self)
     |      Returns true if a quote is not publically visible but is pending moderation
     |  
     |  setBlankQuote(self)
     |      'Blanks' a quote by wiping out the content of the quote array, quote text, sets number of lines to -1, and flags it as not existing

FUNCTIONS
    getLatestQuote()
        Function that returns
    
    getLatestQuoteNum()
        Function that returns the number of the last-approved bash.org quote
    
    getQuote(num)
        Function to return a BashQuote object for a given quote number-- note, does not check for valid quote numbers
    
    getQuoteSafe(num)
        Function to return a BashQuote object for a given quote number, returns BashQuote(-1) if the quote does not exist
    
    getRandomQuote()
        Function that returns a BashQuote object for a random quote number, is (almost) guaranteed to be valid
    
    getRandomQuoteNum()
        Function that returns a random quote number


