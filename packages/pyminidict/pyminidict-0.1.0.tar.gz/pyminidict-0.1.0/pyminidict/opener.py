# encoding=utf-8

import cookielib
import urllib2
import os.path
import md5
import time
from os import system

from urllib import urlencode

def warpGmTime(fun):
    '''修正time模块bug'''
    def _warpGmTime(*args):
        args = list(args)
        if args[0] > 1899962739: args[0] = 1899962739
        return fun(*args)
    if hasattr(fun, '_is_hook'): return fun
    _warpGmTime._is_hook = 1
    return _warpGmTime
time.gmtime = warpGmTime(time.gmtime)
        
class Opener(object):
    '''连接服务器'''

    def __init__(self, url):
        url = url.strip(' \n/\\')
        if not url.startswith('http://') and not url.startswith('https://'):
            self.url = 'http://' + url +'/'
        else:
            self.url = url

        self.data = None
        self.headers = {'User-agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:11.0) Gecko/20100101 Firefox/11.0'}
        self.cj = cookielib.LWPCookieJar()
        

        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(self.opener)
        try:
            req = urllib2.Request(url=self.url, data=self.data, headers=self.headers)
            handle = urllib2.urlopen(req)
        except IOError, e:
            print 'Failed to open "%s".' % self.url
            if hasattr(e, 'code'):
                print 'Error code: %s.' % e.code
            raise IOError, e
        else:
            self.recv_headers = handle.info()

        cookies = ''
        self.headers['Cookie'] = cookies


    def request(self, url='', data=None, method='GET'):
        url = url.strip(' /')
        url = self.url + '/' + url
        method = method.upper()
        _data = ''
        for a in data.keys():
            _data += a + '=' + data[a] + '&'
        _data.strip('&')
        
        req = urllib2.Request(url=url, data=_data, headers=self.headers)
        return urllib2.urlopen(req)

def main():
    url = "http://dict.youdao.com"
    opener = Opener(url)
    data = {'q': 'test', 'keyfrom': 'dict.index'}
    fp = opener.request(url='/search', data=data)
    print fp.read()

if __name__ == '__main__':
    main()

