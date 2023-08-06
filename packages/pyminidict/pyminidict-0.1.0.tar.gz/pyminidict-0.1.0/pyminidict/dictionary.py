# encoding=utf-8
import opener
from pyquery import PyQuery

class Dictionary(object):
    '''Dictionary class to connect to dict.youdao.com and look up the queried word.'''
    def __init__(self):
        self.dict_opener = opener.Opener("dict.youdao.com")
        self.data = {'q':'', 'keyfrom':'dict.index'}
        self.url = '/search'

    def lookUp(self, word): 
        self.data['q'] = word
        html = self.dict_opener.request(url=self.url, data=self.data)
        cont = html.read()
        d = PyQuery(cont)
        trans_cont= d('#phrsListTab .trans-container li')

        if trans_cont.html() is None: return []
        else: return [i.text for i in trans_cont]
