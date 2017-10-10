# -*-coding:utf-8-*-
import threading
from urllib import parse
import time, os
import urllib.request as request
import MySQLdb
from bs4 import BeautifulSoup
import json
import random
import blbl_time

jp_title = ''
cn_title = ''


def in_mysql(data):
    db = MySQLdb.connect("localhost", "root", "root", "blbl_new", use_unicode=True, charset="utf8")
    cursor = db.cursor()
    tsql = "select * from new_animate"
    sql = "INSERT INTO new_animate(rejson) VALUES (\'" + data + "\')"
    try:
        cursor.execute(tsql)
        data = cursor.fetchall()


    except Exception as e:
        print(e)
        db.rollback()
    db.close()


def get_title():
    global jp_title, cn_title
    jp_title = ''
    cn_title = ''
    html = blbl_time.gethtml('https://bangumi.bilibili.com/web_api/timeline_global')
    html_cn = blbl_time.gethtml('https://bangumi.bilibili.com/web_api/timeline_cn')
    rehtml = json.loads(str(html))
    rehtml_cn = json.loads(str(html_cn))
    for i in range(len(rehtml['result'])):
        if rehtml['result'][i - 1]['is_today'] == 1:
            for j in range(len(rehtml['result'][i - 1]['seasons'])):
                s = str(rehtml['result'][i - 1]['seasons'][j - 1]['pub_index']).replace('第', '')
                num = s.replace('话', '')
                jp_title += rehtml['result'][i - 1]['seasons'][j - 1]['title'] + str(num) + ','
    for i in range(len(rehtml_cn['result'])):
        if rehtml_cn['result'][i - 1]['is_today'] == 1:
            for j in range(len(rehtml_cn['result'][i - 1]['seasons'])):
                s = str(rehtml_cn['result'][i - 1]['seasons'][j - 1]['pub_index']).replace('第', '')
                num_cn = s.replace('话', '')
                cn_title += rehtml_cn['result'][i - 1]['seasons'][j - 1]['title'] + str(num_cn) + ','


def get_av(ep_id, title, num):
    get = True
    while get:
        try:
            av_html = blbl_time.posthtml('https://bangumi.bilibili.com/web_api/get_source', ep_id)
            av_json = json.loads(str(av_html))
            if str(av_json['message']).find('地球上找不到该内容哦') == -1 and str(av_json['message']).find('根据版权方要求') == -1:
                av_id = av_json['result']['aid']
                get = False
            time.sleep(15)
        except Exception as e:
            print(e)
            time.sleep(15)


def japan_animate():
    jp_th = ''
    while True:
        try:
            global jp_title
            time.sleep(30)
            newtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            now = time.strftime('%H%M', time.localtime())
            date = time.strftime('%m%d', time.localtime())
            if now == '0000':
                get_title()
            html = blbl_time.gethtml('https://bangumi.bilibili.com/web_api/timeline_global')
            rehtml = json.loads(str(html))
            for i in range(len(rehtml['result'])):
                if rehtml['result'][i - 1]['is_today'] == 1:
                    for j in range(len(rehtml['result'][i - 1]['seasons'])):
                        title = rehtml['result'][i - 1]['seasons'][j - 1]['title']
                        if jp_title.find(str(title)) == -1:
                            ep_id = rehtml['result'][i - 1]['seasons'][j - 1]['ep_id']
                            s = str(rehtml['result'][i - 1]['seasons'][j - 1]['pub_index']).replace('第', '')
                            num = s.replace('话', '')
                            print(num)
                            jp_title += title + str(num) + ','
                            t = threading.Thread(target=get_av, args=(ep_id, title, num))
                            t.setName(title)
                            if jp_th.find(date + title) == -1:
                                jp_th += date + title
                                t.start()
            print(newtime + ',next')
        except Exception as e:
            print(e)
            time.sleep(15)


def china_animate():
    cn_th = ''
    while True:
        try:
            global cn_title
            time.sleep(30)
            newtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            now = time.strftime('%H%M', time.localtime())
            date = time.strftime('%m%d', time.localtime())
            if now == '0000':
                get_title()
            html_cn = blbl_time.gethtml('https://bangumi.bilibili.com/web_api/timeline_cn')
            rehtml_cn = json.loads(str(html_cn))
            for i in range(len(rehtml_cn['result'])):
                if rehtml_cn['result'][i - 1]['is_today'] == 1:
                    for j in range(len(rehtml_cn['result'][i - 1]['seasons'])):
                        title = rehtml_cn['result'][i - 1]['seasons'][j - 1]['title']
                        if cn_title.find(str(title)) == -1:
                            ep_id = rehtml_cn['result'][i - 1]['seasons'][j - 1]['ep_id']
                            s = str(rehtml_cn['result'][i - 1]['seasons'][j - 1]['pub_index']).replace('第', '')
                            num = s.replace('话', '')
                            print(num)
                            cn_title += title + str(num) + ','
                            t = threading.Thread(target=get_av, args=(ep_id, title, num))
                            t.setName(title)
                            if cn_th.find(date + title) == -1:
                                cn_th += date + title
                                t.start()
            print(newtime + ',next')
        except Exception as e:
            print(e)
            time.sleep(15)


threads = []
t1 = threading.Thread(target=japan_animate)
threads.append(t1)
t2 = threading.Thread(target=china_animate)
threads.append(t2)

if __name__ == '__main__':
    get_title()
    for t in threads:
        t.start()
