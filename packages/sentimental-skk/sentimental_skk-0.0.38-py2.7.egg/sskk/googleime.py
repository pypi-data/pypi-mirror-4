#!/usr/lib/python
#vim:fileencoding=utf-8
 
 
 
class GoogleIME:
    '''
    http://www.google.com/intl/ja/ime/cgiapi.html
     
    >>> api = GoogleIME()
    >>> result = api.convert('こにｎａ ')
    >>> print result
    '''
    def __init__(self):
        pass
        
    def convert(self, text):
        import urllib, urllib2, json
        params = urllib.urlencode({ 'langpair' : 'ja-Hira|ja', 'text' : text })  
        result = urllib2.urlopen('http://www.google.com/transliterate?', params).read()
        lis = json.loads(result)
        return lis

def test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()

