# -*-coding:utf-8-*-
import threading
from urllib import parse
import time, os, MySQLdb
import urllib.request as request
import datetime
from bs4 import BeautifulSoup
import json, logging, random
import collections

DIR = os.path.dirname(__file__)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='animate.log',
                    filemode='w')


def in_mysql(data, av_id):
    db = MySQLdb.connect("localhost", "root", "root", "blbl_new", use_unicode=True, charset="utf8")
    cursor = db.cursor()
    tsql = "select rejson from new_animate"
    sql = "INSERT INTO new_animate(rejson) VALUES (\'" + data + "\')"
    try:
        cursor.execute(tsql)
        find_data = cursor.fetchall()
        animatelist = []
        for strD in find_data:
            animatelist.append(strD)
        for i in range(len(animatelist)):
            animatelist[i] = str(animatelist[i])
        if ''.join(animatelist).find(av_id) == -1:
            cursor.execute(sql)
            db.commit()
            logging.info('save in sql')
            # data = cursor.fetchall()
    except Exception as e:
        logging.error(str(e))
        db.rollback()
    db.close()


def posthtml(url, season_id):
    try:
        login_data = parse.urlencode([
            ('episode_id', season_id),
        ]).encode(encoding='UTF8')
        opener = request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        page = opener.open(url, data=login_data, timeout=15).read()
        soup = BeautifulSoup(page.decode('utf-8'), 'html.parser')
        opener.close()
        return soup
    except Exception as e:
        logging.error(str(e))
        opener.close()


def gethtml(url):
    try:
        opener = request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        page = opener.open(url, timeout=15).read()
        soup = BeautifulSoup(page.decode('utf-8'), 'html.parser')
        opener.close()
        return soup
    except Exception as e:
        logging.error(str(e))
        opener.close()
        # continue


def get_av(ep_id, title, num):
    get = True
    now = 1
    logging.info('th')
    while get:
        try:
            date = time.strftime('%m%d', time.localtime())
            end = datetime.datetime.now().second
            av_html = posthtml('https://bangumi.bilibili.com/web_api/get_source', ep_id)
            av_json = json.loads(str(av_html))
            if str(av_json['message']).find('地球上找不到该内容哦') == -1 and str(av_json['message']).find('根据版权方要求') == -1:
                av_id = av_json['result']['aid']
                animate = collections.OrderedDict()
                animate['date'] = date
                animate['title'] = title
                animate['num'] = num
                animate['av_id'] = av_id
                data = json.dumps(animate, ensure_ascii=False)
                time.sleep(random.randint(5, 20))
                in_mysql(data, str(av_id))
                get = False
            elif str(av_json['message']).find('根据版权方要求') != -1:
                logging.info((title + 'do not watch'))
                get = False
            if end - now > 36000:
                logging.info(title + ' is not update')
                get = False
            time.sleep(30)
        except Exception as e:
            logging.error(str(e))
            time.sleep(30)


def japan_animate():
    jp_th = ''
    determine = True
    while True:
        try:
            now = time.strftime('%H:%M', time.localtime())
            if now.find('00:00') != -1 and determine:
                jp_th = ''
                determine = False
            if now.find('00:01') != -1:
                determine = True
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
            # logging.info('not update')
            time.sleep(30)
        except Exception as e:
            logging.error(str(e))
            time.sleep(30)


def china_animate():
    cn_th = ''
    determine = True
    while True:
        try:
            now = time.strftime('%H:%M', time.localtime())
            if now.find('00:00') != -1 and determine:
                cn_th = ''
                determine = False
            if now.find('00:01') != -1:
                determine = True
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
            # logging.info('not update')
            time.sleep(30)
        except Exception as e:
            logging.error(str(e))
            time.sleep(30)


threads = []
t1 = threading.Thread(target=japan_animate)
threads.append(t1)
t2 = threading.Thread(target=china_animate)
threads.append(t2)

if __name__ == '__main__':
    for t in threads:
        t.start()
        # t.join()
