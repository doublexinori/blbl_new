# -*-coding:utf-8-*-
import threading
from urllib import parse
import time, os, MySQLdb
import urllib.request as request
import datetime
from bs4 import BeautifulSoup
import json
import random

DIR = os.path.dirname(__file__)


def in_mysql(data):
    db = MySQLdb.connect("localhost", "root", "root", "blbl_new", use_unicode=True, charset="utf8")
    cursor = db.cursor()
    sql = "INSERT INTO new_animate(rejson) VALUES (\'" + data + "\')"
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
    db.close()


def posthtml(url, season_id):
    try:
        login_data = parse.urlencode([
            ('episode_id', season_id),
        ]).encode(encoding='UTF8')
        opener = request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        page = opener.open(url, data=login_data).read()
        soup = BeautifulSoup(page.decode('utf-8'), 'html.parser')
        return soup
    except Exception as err:
        print(err)
        time.sleep(random.randint(10, 20))


def gethtml(url):
    try:
        opener = request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        page = opener.open(url).read()
        soup = BeautifulSoup(page.decode('utf-8'), 'html.parser')
        return soup
    except Exception as err:
        print(err)
        time.sleep(random.randint(10, 20))
        # continue


def get_av(ep_id, title, num):
    get = True
    date = time.strftime('%m%d', time.localtime())
    now = 1
    while get:
        try:
            end = datetime.datetime.now().second
            av_html = posthtml('https://bangumi.bilibili.com/web_api/get_source', ep_id)
            av_json = json.loads(str(av_html))
            if str(av_json['message']).find('地球上找不到该内容哦') == -1 and str(av_json['message']).find('根据版权方要求') == -1:
                av_id = av_json['result']['aid']
                animate = {'date': date, 'title': title, 'num': num, 'av_id': av_id}
                data = json.dumps(animate, ensure_ascii=False)
                in_mysql(data)
                get = False
            if end - now > 36000:
                print(title + ' is not update')
                get = False
            time.sleep(15)
        except Exception as e:
            print(e)
            time.sleep(15)


def japan_animate():
    jp_th = ''
    s = True
    while True:
        try:
            newtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            now = time.strftime('%H:%M', time.localtime())
            if now.find('00:00') != -1 and s:
                jp_th = ''
                s = False
            if now.find('00:01') != -1:
                s = True
            html = gethtml('https://bangumi.bilibili.com/web_api/timeline_global')
            rehtml = json.loads(str(html))
            for i in range(len(rehtml['result'])):
                if rehtml['result'][i - 1]['is_today'] == 1:
                    # ex_num = ''
                    for j in range(len(rehtml['result'][i - 1]['seasons'])):
                        if str(rehtml['result'][i - 1]['seasons'][j - 1]['pub_time']).find(now) != -1:
                            season_id = rehtml['result'][i - 1]['seasons'][j - 1]['season_id']
                            ep_id = rehtml['result'][i - 1]['seasons'][j - 1]['ep_id']
                            s = str(rehtml['result'][i - 1]['seasons'][j - 1]['pub_index']).replace('第', '')
                            num = s.replace('话', '')
                            title = rehtml['result'][i - 1]['seasons'][j - 1]['title']
                            t = threading.Thread(target=get_av, args=(ep_id, title, num))
                            if jp_th.find(title + str(num)) == -1:
                                jp_th += title + str(num) + ','
                                t.start()
            print(newtime + ',next')
            time.sleep(15)
        except Exception as e:
            print(e)
            time.sleep(15)


def china_animate():
    cn_th = ''
    s = True
    while True:
        try:
            newtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            now = time.strftime('%H:%M', time.localtime())
            if now.find('00:00') != -1 and s:
                cn_th = ''
                s = False
            if now.find('00:01') != -1:
                s = True
            html_cn = gethtml('https://bangumi.bilibili.com/web_api/timeline_cn')
            rehtml_cn = json.loads(str(html_cn))
            for i in range(len(rehtml_cn['result'])):
                if rehtml_cn['result'][i - 1]['is_today'] == 1:
                    # ex_num = ''
                    for j in range(len(rehtml_cn['result'][i - 1]['seasons'])):
                        if str(rehtml_cn['result'][i - 1]['seasons'][j - 1]['pub_time']).find(now) != -1:
                            season_id = rehtml_cn['result'][i - 1]['seasons'][j - 1]['season_id']
                            ep_id = rehtml_cn['result'][i - 1]['seasons'][j - 1]['ep_id']
                            s = str(rehtml_cn['result'][i - 1]['seasons'][j - 1]['pub_index']).replace('第', '')
                            num = s.replace('话', '')
                            title = rehtml_cn['result'][i - 1]['seasons'][j - 1]['title']
                            t = threading.Thread(target=get_av, args=(ep_id, title, num))
                            if cn_th.find(title + str(num)) == -1:
                                cn_th += title + str(num) + ','
                                t.start()
            print(newtime + ',next')
            time.sleep(15)
        except Exception as e:
            print(e)
            time.sleep(15)


threads = []
t1 = threading.Thread(target=japan_animate)
threads.append(t1)
t2 = threading.Thread(target=china_animate)
threads.append(t2)

if __name__ == '__main__':
    for t in threads:
        t.start()
        # t.join()