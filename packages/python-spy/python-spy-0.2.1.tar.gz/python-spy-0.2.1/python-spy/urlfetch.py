from os import path
import os
from hashlib import md5
import  time
import urllib2
import urlparse,urllib
import cookielib
from random import choice

_cook = cookielib.CookieJar()

def post_form_fetch(url, data, char = ''):
    host = urlparse.urlparse(url).hostname
    content = urllib.urlencode(data)
    get_num = 0
    
    while(1):
            try:
                opener = urllib2.build_opener(urllib2.HTTPHandler,urllib2.HTTPCookieProcessor(_cook))
                opener.addheaders = [('Host', host)]
                opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3')]
                opener.addheaders = [('Content-Type','application/x-www-form-urlencoded')]
            
                urllib2.install_opener(opener)
                f = urllib2.urlopen(url,content)
                s = f.read()
                f.close()
                if char:
                    return s.decode(char).encode('utf-8')
                else:
                    return s
                    
            except Exception, e:
	            if 'time out' in str(e):
		            time.sleep(1)
		            get_num += 1
		            if get_num >= 3:
			            break
	            elif '404' in str(e):
		            break
	            else:
		            get_num += 1
		            if get_num >= 3:
			            break
    return


class DownOpener(urllib.FancyURLopener):
    user_agents = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
    ]
    version = choice(user_agents)
        
def download_file(url,save):
    host = urlparse.urlparse(url).hostname
    
    trycnt = 3
    for i in xrange(trycnt):
        try:
            opener = urllib2.build_opener(urllib2.HTTPHandler,urllib2.HTTPCookieProcessor(_cook))
            opener.addheaders = [('Host', host)]
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3')]
            opener.addheaders = [('Referer',"http://%s/"%host)]
            urllib2.install_opener(opener)
            f = DownOpener()
            return f.retrieve(url, save)
        except urllib2.URLError, e:
            if i == trycnt - 1:
                raise e

def retryOnURLError(self, trycnt=3):
    def funcwrapper(fn):
        def wrapper( *args, **kwargs):
            for i in range(trycnt):
                try:
                    return fn( *args, **kwargs)
                except urllib2.URLError, e:
                    if i == trycnt - 1:
                        raise e
        return wrapper
    return funcwrapper

class Fetch(object):
    def __init__(self, cache, headers = [], char = '', cook = None):
        self.cache = cache
        self.headers = headers
        self.char = char
        
        if cook:
            self.cook = cook
        else:
            self.cook = cookielib.CookieJar()
            

    def cache_get(self, url):
        cache_dir = path.join(
            self.cache, urlparse.urlparse(url).hostname
        )
        if not path.exists(cache_dir):
            os.mkdir(cache_dir)

        if not path.exists(cache_dir):
            os.mkdir(cache_dir)
        file_name = md5(url).hexdigest()
        file_path = path.join(cache_dir, file_name)

        if path.exists(file_path):
            print "Using cache"
            with open(file_path) as f:
                data = f.read()
                return data

    def read(self, url):
        
        opener = urllib2.build_opener(urllib2.HTTPHandler,urllib2.HTTPCookieProcessor(self.cook))
        opener.addheaders = [('Host', urlparse.urlparse(url).hostname)]
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3')]
        
        for i in self.headers:
            opener.addheaders = [i]
            
        urllib2.install_opener(opener)
        
        _req = urllib2.urlopen(url ,timeout=30)
        _data = _req.read()
        _req.close()
        if self.char:
            return _data.decode(self.char).encode('utf-8')
        else:
            return _data

    @retryOnURLError(3)
    def __call__(self, url):
        data = self.cache_get(url)
        if data is None:
            cache_dir = path.join(
                    self.cache, urlparse.urlparse(url).hostname
                    )
            file_name = md5(url).hexdigest()
            file_path = path.join(cache_dir, file_name)
            with open(file_path, 'w') as f:
                data = self.read(url)
                f.write(data)

        return data

class NoCacheFetch(object):
    def __init__(self,sleep = 0, headers=[], char = '', cook = None):
        self.headers = headers
        self.sleep = sleep
        self.char = char
        
        if cook:
            self.cook = cook
        else:
            self.cook = cookielib.CookieJar()

    def read(self, url):
        print "read %s\n"%url
        
        opener = urllib2.build_opener(urllib2.HTTPHandler,urllib2.HTTPCookieProcessor(self.cook))
        opener.addheaders = [('Host', urlparse.urlparse(url).hostname)]
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3')]
        
        for i in self.headers:
            opener.addheaders = [i]
            
        urllib2.install_opener(opener)
        
        _req = urllib2.urlopen(url ,timeout=30)
        _data = _req.read()
        _req.close()
        if self.sleep:
            time.sleep(self.sleep)
            
        if self.char:
            return _data.decode(self.char).encode('utf-8')
        else:
            return _data

    @retryOnURLError(3)
    def __call__(self, url):
        data  = self.read(url)
        return data

from os import path
CURRENT_PATH = path.dirname(path.abspath(__file__))
fetch=Fetch(path.join(CURRENT_PATH, "cache"))
