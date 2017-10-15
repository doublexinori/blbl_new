# -*-coding:utf-8-*-
import threading
import time, os
import json, logging
import blbl_time

jp_title = ''
cn_title = ''

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


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


def japan_animate():
    jp_th = ''
    determine = True
    while True:
        try:
            global jp_title
            time.sleep(30)
            newtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            now = time.strftime('%H%M', time.localtime())
            date = time.strftime('%m%d', time.localtime())
            if now == '0000' and determine:
                get_title()
                determine = False
            if now == '0001':
                determine = True
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
                            jp_title += title + str(num) + ','
                            t = threading.Thread(target=blbl_time.get_av, args=(ep_id, title, num))
                            t.setName(title)
                            if jp_th.find(date + title) == -1:
                                jp_th += date + title
                                t.start()
            logging.info('not update')
        except Exception as e:
            logging.error(e)
            time.sleep(15)


def china_animate():
    cn_th = ''
    determine = True
    while True:
        try:
            global cn_title
            time.sleep(30)
            newtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            now = time.strftime('%H%M', time.localtime())
            date = time.strftime('%m%d', time.localtime())
            if now == '0000' and determine:
                get_title()
                determine = False
            if now == '0001':
                determine = True
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
                            cn_title += title + str(num) + ','
                            t = threading.Thread(target=blbl_time.get_av, args=(ep_id, title, num))
                            t.setName(title)
                            if cn_th.find(date + title) == -1:
                                cn_th += date + title
                                t.start()
            logging.info('not update')
        except Exception as e:
            logging.error(e)
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
