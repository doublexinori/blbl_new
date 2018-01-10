from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
import json
import collections


def in_mongo(data):
    client = MongoClient('localhost', 27017)
    db = client.suzhoumeng
    posts = db.posts
    result = posts.insert_one(data)
    print('One post: {0}'.format(result.inserted_id))


year = 2017
month = 1
go = True
while go:
    dr = webdriver.PhantomJS()
    dr.get('http://newhouse.suzhou.fang.com/top/cjdetail-%d-%d' % (year, month))
    html = dr.page_source
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('ul', attrs={'id': 'cjDetail'}) is not None:
        divs = soup.find('ul', attrs={'id': 'cjDetail'}).find_all('li')
        for div in divs:
            data = collections.OrderedDict()
            data['date'] = '%d-%d' % (year, month)
            data['location'] = div.find('div', attrs={'class': 'text'}).find('span').get_text()
            data['name'] = div.find('div', attrs={'class': 'text'}).find('a').get_text()
            data['price'] = div.find('div', attrs={'class': 'price'}).find('span').get_text()
            in_mongo(data)
    else:
        dr.close()
        dr = webdriver.PhantomJS()
        dr.get('http://newhouse.suzhou.fang.com/top/cjdetail')
        html = dr.page_source
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find('ul', attrs={'id': 'cjDetail'}).find_all('li')
        for div in divs:
            data = collections.OrderedDict()
            data['date'] = '%d-%d' % (year, month)
            data['location'] = div.find('div', attrs={'class': 'text'}).find('span').get_text()
            data['name'] = div.find('div', attrs={'class': 'text'}).find('a').get_text()
            data['price'] = div.find('div', attrs={'class': 'price'}).find('span').get_text()
            in_mongo(data)
        go = False
    month += 1
    dr.close()
