import collections
import blbl_time
import json, MySQLdb


def in_mysql(title, season_id, data):
    db = MySQLdb.connect("localhost", "root", "root", "blbl_new", use_unicode=True, charset="utf8")
    cursor = db.cursor()
    tsql = "select * from old_animate where season_id = \'" + season_id + "\'"
    sql = "INSERT INTO old_animate(title,season_id,json) VALUES (\'" + title + "\',\'" + season_id + "\',\'" + data + "\')"
    try:
        cursor.execute(tsql)
        find_data = cursor.fetchall()
        if len(find_data) == 0:
            cursor.execute(sql)
            db.commit()
    except Exception as e:
        print(e)
        db.rollback()
    db.close()


html = blbl_time.gethtml(
    'https://bangumi.bilibili.com/web_api/season/index_global?page=1&page_size=20&version=0&is_finish=2&start_year=0&tag_id=&index_type=1&index_sort=0&area=2&quarter=0'
)
rehtml = json.loads(str(html))
all_page = rehtml['result']['pages']
for page in range(1, int(all_page) + 1):
    url = 'https://bangumi.bilibili.com/web_api/season/index_global?page=' + str(
        page) + '&page_size=20&version=0&is_finish=2&start_year=0&tag_id=&index_type=1&index_sort=0&area=2&quarter=0'
    html = blbl_time.gethtml(url)
    rehtml = json.loads(str(html))
    for i in range(len(rehtml['result']['list'])):
        season_id = rehtml['result']['list'][i]['season_id']
        title = rehtml['result']['list'][i]['title'].replace("'", "\\'")
        # true_title = rehtml['result']['list'][i]['title']
        animate_url = 'http://bangumi.bilibili.com/jsonp/seasoninfo/' + str(
            season_id) + '.ver?callback=seasonListCallback'
        animate_html = blbl_time.gethtml(animate_url)
        episodes = []
        try:
            if title == 'NO GAME NO LIFE 游戏人生':
                animate_rehtml = json.loads(
                    animate_html.text.replace('seasonListCallback', '').replace('(', '').replace(')', '').replace(';',
                                                                                                                  ''))
            elif title == 'ACCA13区监察课':
                animate_rehtml = json.loads(
                    animate_html.text.replace('seasonListCallback', '').replace('(', '').replace(')', '').replace(';',
                                                                                                                  '').replace(
                        '"禅"', '\\"禅\\"'))
            else:
                animate_rehtml = json.loads(
                    str(animate_html).replace('seasonListCallback', '').replace('(', '').replace(')', '').replace(';',
                                                                                                                  ''))
            date = animate_rehtml['result']['pub_time']
            s = ''
            t_date = s + date[:10]
            for j in range(len(animate_rehtml['result']['episodes'])):
                episode_id = animate_rehtml['result']['episodes'][len(animate_rehtml['result']['episodes']) - 1 - j][
                    'episode_id']
                num = animate_rehtml['result']['episodes'][len(animate_rehtml['result']['episodes']) - 1 - j]['index']
                index_title = animate_rehtml['result']['episodes'][len(animate_rehtml['result']['episodes']) - 1 - j][
                    'index_title']
                episodes.append({'title': index_title, 'num': num, 'episode_id': episode_id})
            animate = collections.OrderedDict()
            animate['date'] = t_date
            # animate['season_id'] = season_id
            animate['episodes'] = episodes
            # animate = {'date': date, 'season_id': season_id, 'episodes': episodes}
            data = json.dumps(animate, ensure_ascii=False).replace("'", "\\'")
            in_mysql(title, season_id, data)
        except Exception as e:
            print(title, e)
            continue
