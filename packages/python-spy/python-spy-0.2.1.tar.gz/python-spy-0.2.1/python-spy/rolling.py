#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from gspider import GSpider 
from collections import  defaultdict
import os
from gevent import monkey, queue
import Queue
from urlfetch import Fetch, fetch

class Rolling(object):
    def __init__(self, fetch , url_iter=()):
        self.subitems = queue.Queue(-1)
        self.url_iter = iter(url_iter)
        self.fetch = fetch

    def scheduler(self):
        subitems = self.subitems

        for item in self.url_iter:
            self.push(*item)
            yield subitems.get(timeout=60)

        while True:
            try:
                item = subitems.get(timeout=60)
            except Queue.Empty:
                return
            else:
                yield item

    def push(self, callback, url, *args, **kwds):
        self.subitems.put((callback, url, args, kwds))

    def worker(self, item):
        callback , url, args, kwds = item
        r = self.fetch(url)
        if r != None:
            new_items = callback(r, url, *args, **kwds)
        if new_items is not None:
            for item in new_items:
                self.push(*item)
        return r



def main():
    def callback(html, url):
        print  url

    spider = Rolling(
        fetch,
        (
            (callback, 'http://www.baidu.com'),
        )
    )
    spider = GSpider(spider, workers_count=10)
    spider.start()

if __name__ == '__main__':
    #main()
    pass
