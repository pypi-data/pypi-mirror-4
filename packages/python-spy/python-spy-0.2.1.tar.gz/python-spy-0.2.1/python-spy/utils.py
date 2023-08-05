#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Guang Feng on 2012-06-23.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import MySQLdb
import time

CONNECTOR = {}

def connect_db(h, u, p, d):
    """ 
     create a pool of connections to mysql
     CREATE TABLE `fetcher` (
       `id` int(11) unsigned NOT NULL auto_increment,
       `url` varchar(255) NOT NULL default '',
       `lastmodified` varchar(255) NOT NULL default '0',
       `updated` timestamp NOT NULL default '0000-00-00 00:00:00' on update CURRENT_TIMESTAMP,
       PRIMARY KEY  (`id`),
       UNIQUE KEY `url` (`url`),
     ) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
    """
    
    global CONNECTOR
    CONNECTOR[d] = MySQLdb.connect(host = h, user = u, passwd= p,
                                db= d, charset='utf8')
    cursor=CONNECTOR[d].cursor()
    return cursor

def get_existed_conn(db):
    return CONNECTOR[db]
    

def last_modified(timestr):
    import datetime
    t = datetime.strptime(timestr,"%a, %d %b %Y %H:%M:%S %Z")
    return time.mktime(t.timetuple())
    
def spy_will_active(url, h, u, p, d = "spy_data"):
    """
    CREATE TABLE `fetcher` (
       `id` int(11) unsigned NOT NULL auto_increment,
       `url` varchar(255) NOT NULL default '',
       `lastmodified` varchar(255) NOT NULL default '0',
       `updated` timestamp NOT NULL default '0000-00-00 00:00:00' on update CURRENT_TIMESTAMP,
       PRIMARY KEY  (`id`),
       UNIQUE KEY `url` (`url`),
     ) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
    """
    
    c = connect_db(h, u ,p ,d)
    c.execute("select * from fetcher where url = %s",(url))
    r = c.fetchall()
     
    last = r[0][2] if r else 0
    
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    opener.addheaders = [('Host', urlparse.urlparse(url).hostname)]
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3')]
    urllib2.install_opener(opener)
    f = urllib2.urlopen(url,timeout = 30)
    header = f.info()
    f.close()
    
    expire = header.getheader('Last-Modified')
    expire = last_modified(expire)

    will_start = 1 if int(expire) > int(last) else 0

    c.execute("""insert fetcher (url,lastmodified,`updated`) values (%s,%s,now()) """,(url,str(expire)))
    
    get_existed_conn[d].commit()
    return will_start

