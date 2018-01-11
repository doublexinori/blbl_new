from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
import collections


def in_mongo(data):
    client = MongoClient('localhost', 27017)
    db = client.suzhoumeng
    posts = db.posts
    result = posts.insert_one(data)
    print('One post: {0}'.format(result.inserted_id))


year = 2015
month = 8
go = True
while go:
    if month == 13:
        year += 1
        month = 1
    dr = webdriver.PhantomJS()
    dr.get('http://newhouse.suzhou.fang.com/top/xtdetail-%d-%d' % (year, month))
    html = dr.page_source
    soup = BeautifulSoup(html, 'html.parser')
    if '%d%d' % (year, month) == '20181':
        dr.close()
        dr = webdriver.PhantomJS()
        dr.get('http://newhouse.suzhou.fang.com/top/xtdetail')
        html = dr.page_source
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find('ul', attrs={'id': 'xtdetailbox'}).find_all('li')
        for div in divs:
            data = collections.OrderedDict()
            data['date'] = '%d-%d' % (year, month)
            data['location'] = div.find('div', attrs={'class': 'text'}).find('span').get_text()
            data['name'] = div.find('div', attrs={'class': 'text'}).find('a').get_text()
            if div.find('div', attrs={'class': 'price'}).find('span').get_text() == '价格待定':
                continue
            if len(div.find('div', attrs={'class': 'price'}).find('span').get_text()) <= 3:
                data['price'] = div.find('div', attrs={'class': 'price'}).find('span').get_text() + '万元起'
            else:
                data['price'] = div.find('div', attrs={'class': 'price'}).find('span').get_text() + '元/平方米'
            in_mongo(data)
        go = False
    if soup.find('ul', attrs={'id': 'xtdetailbox'}) is not None:
        divs = soup.find('ul', attrs={'id': 'xtdetailbox'}).find_all('li')
        for div in divs:
            data = collections.OrderedDict()
            data['date'] = '%d-%d' % (year, month)
            data['location'] = div.find('div', attrs={'class': 'text'}).find('span').get_text()
            data['name'] = div.find('div', attrs={'class': 'text'}).find('a').get_text()
            if div.find('div', attrs={'class': 'price'}).find('span').get_text() == '价格待定':
                continue
            if len(div.find('div', attrs={'class': 'price'}).find('span').get_text()) <= 3:
                data['price'] = div.find('div', attrs={'class': 'price'}).find('span').get_text() + '万元起'
            else:
                data['price'] = div.find('div', attrs={'class': 'price'}).find('span').get_text() + '元/平方米'
            in_mongo(data)
    month += 1
dr.close()
