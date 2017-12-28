import collections

import blbl_time, json, time, MySQLdb, requests
from bs4 import BeautifulSoup


def animate_json(title, rate, people_num, rating, imdb_url, tag, look1, look2, look3, duanping1, juping1):
    animate = collections.OrderedDict()
    animate['标题'] = title
    if rate != '':
        animate['分数'] = rate
    if people_num != '':
        animate['评价人数'] = people_num
    if rating != '':
        animate['评分占比'] = rating
    if imdb_url != '':
        animate['imdb_url'] = imdb_url
    animate['标签'] = tag
    if look3 != '':
        animate['在看'] = look1
        animate['看过'] = look2
        animate['想看'] = look3
    elif look2 == '' and look3 == '':
        animate['看过'] = look1
    else:
        animate['看过'] = look1
        animate['想看'] = look2
    animate['短评人数'] = duanping1
    animate['剧评人数'] = juping1
    data = json.dumps(animate, ensure_ascii=False)
    return data


def get_html(url):
    headers = {
        'User-agent': 'Mozilla/5.0'
    }
    response = requests.request("GET", url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def in_mysql(title, data):
    db = MySQLdb.connect("localhost", "root", "root", "blbl_new", use_unicode=True, charset="utf8")
    cursor = db.cursor()
    tsql = "select * from douban_animate where title = \'" + title.replace('\'', r'\'') + "\'"
    sql = "INSERT INTO douban_animate(title,detail) VALUES (\'" + title.replace('\'', r'\'') + "\',\'" + data.replace(
        '\'', r'\'') + "\')"
    try:
        cursor.execute(tsql)
        find_data = cursor.fetchall()
        if len(find_data) == 0:
            cursor.execute(sql)
            db.commit()
    except Exception as e:
        print('error:' + title + ',' + str(start) + ',' + str(e))
        db.rollback()
    db.close()


start = 0
go = True
while go:
    try:
        time.sleep(60)
        html = blbl_time.gethtml(
            'https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=%E5%8A%A8%E7%94%BB,%E6%97%A5%E6%9C%AC&start=' + str(
                start))
        rehtml = json.loads(str(html))
        if len(rehtml['data']) != 0:
            i = 0
            while len(rehtml['data']) > i:
                try:
                    imdb_url, rate, look2, look3, title = '', '', '', '', ''
                    time.sleep(30)
                    title = rehtml['data'][i]['title']
                    rate = rehtml['data'][i]['rate']
                    html_web = get_html(rehtml['data'][i]['url'])
                    if html_web.find('title').get_text().find('页面不存在') == -1:
                        if rate != '':
                            if len(html_web.find('a', class_='rating_people')) != 0:
                                people_num = html_web.find('a', class_='rating_people').get_text().replace('人评价', '')
                                rating = ''
                                for span in html_web.find_all('span', class_='rating_per'):
                                    rating += span.get_text() + ','
                                rating = rating[:-1]
                        if html_web.find('div', attrs={'id': 'info'}).find_all('span')[
                                    len(html_web.find('div', attrs={'id': 'info'}).find_all(
                                        'span')) - 1].get_text().find(
                            '链接') != -1:
                            if html_web.find('div', attrs={'id': 'info'}).find_all('a')[
                                        len(html_web.find('div', attrs={'id': 'info'}).find_all(
                                            'a')) - 1].get_text().find(
                                'tt') != -1:
                                imdb_url = 'http://www.imdb.com/title/' + \
                                           html_web.find('div', attrs={'id': 'info'}).find_all('a')[
                                               len(html_web.find('div', attrs={'id': 'info'}).find_all(
                                                   'a')) - 1].get_text()
                        tags = html_web.find('div', attrs={'class': 'tags-body'})
                        tag = ''
                        for a in tags.find_all('a'):
                            tag += a.get_text() + ','
                        tag = tag[:-1]
                        look = html_web.find('div', attrs={'class': 'subject-others-interests-ft'})
                        if len(look.find_all('a')) == 3:
                            look1 = look.find_all('a')[0].get_text()[:-3]
                            look2 = look.find_all('a')[1].get_text()[:-3]
                            look3 = look.find_all('a')[2].get_text()[:-3]
                        elif len(look.find_all('a')) == 2 and look.find_all('a')[0].get_text().find('看过') != -1 and \
                                        look.find_all('a')[1].get_text().find('想看') != -1:
                            look1 = look.find_all('a')[0].get_text()[:-3]
                            look2 = look.find_all('a')[1].get_text()[:-3]
                        elif len(look.find_all('a')) == 1 and look.find_all('a')[0].get_text().find('看过') != -1:
                            print('in')
                            look1 = look.find_all('a')[0].get_text()[:-3]
                        duanping1 = html_web.find('div', attrs={'id': 'comments-section'}).find_all('a')[1].get_text()[
                                    :-1].replace(
                            '全部', '').replace(' ', '')
                        juping1 = html_web.find(attrs={'class': 'reviews mod movie-content'}).find_all('a')[
                                      1].get_text()[
                                  :-1].replace(
                            '全部', '').replace(' ', '')
                        data = animate_json(title, rate, people_num, rating, imdb_url, tag, look1, look2, look3,
                                            duanping1,
                                            juping1)
                        print(title, data)
                        in_mysql(title, data)
                        i += 1
                    else:
                        i += 1
                except Exception as e:
                    print('error:' + title + ',' + str(start) + ',' + str(e))
        else:
            if start < 5100:
                continue
            else:
                go = False
        start += 20
    except Exception as e:
        print('error:' + title + ',' + str(start) + ',' + str(e))
