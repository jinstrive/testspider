import hashlib
import re
import urllib2
import redisoper
import gevent
from gevent import queue

from bs4 import BeautifulSoup

REDIS_UNIQUE_KEY = "url_unique"
pattern = re.compile("^\/page\d+$")

class Consumers(object):
    def __init__(self,queue,name,start_url):
        self._queue = queue
        self._name = name
        self._redisoper = redisoper.RedisOper()
        self._start_url = start_url
    
    def put_to_queue(self,url):
        if re.search(pattern,url):
            url = self._start_url[:-1] + url
        if self.check_url(url):
            self._queue.put_nowait(url)
            
    def check_url(self,url):
        return self._redisoper.sadd(REDIS_UNIQUE_KEY,url)
        
    def get_content(self):
        try:
            url = self._queue.get_nowait()
            response = urllib2.urlopen(self.wrap_request(url))
            print response.getcode()
            return response
        except urllib2.HTTPError,e:
            print e.code
        
    def wrap_request(self,url):
        req = urllib2.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:27.0) Gecko/20100101 Firefox/27.0")
        req.add_header("Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        return req
    
    def parse_html(self,response):
        htmlobj = BeautifulSoup(response.read())
        links = htmlobj.findAll(href=re.compile(r'^(http|/page)'))
        print response.geturl()
        for link in links:
            print link['href'],link.string
            self.put_to_queue(link['href'])
            
    def run_parse(self):
        try:
            self._queue.put(self._start_url)
            self.parse_html(self.get_content())
        except Exception,e:
            print e,self._start_url,self.get_content()
            
    def pack_url_md5(self,url):
        m = hashlib.md5(url)
        return m.hexdigest()[8:-8]

queue = queue.Queue()
queue.put_nowait("")
threads = []
threads.append(gevent.spawn(Consumers(queue,'thread1',"http://beijing.lashou.com/").run_parse))
threads.append(gevent.spawn(Consumers(queue,'thread2',"http://beijing.lashou.com/").run_parse))
threads.append(gevent.spawn(Consumers(queue,'thread3',"http://beijing.lashou.com/").run_parse))
gevent.joinall(threads)
# if __name__ == "__main__":
#     pass
#     parse_html(get_content("http://beijing.lashou.com/"))
#     print pack_url_md5("http://beijing.lashou.com/")
        
