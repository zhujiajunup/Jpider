import json
from dao.redis_cookies import RedisCookies
from headers import get_header
import requests
from tasks.workers import app
from bs4 import BeautifulSoup
import re
from model.models import Weibo
from dao.sqlalchemy_session import db_session

@app.task
def home_page():
    home_url = 'http://weibo.com/u/{}?is_ori=1&is_tag=0&profile_ftype=1&page=1'

    cookies_json = RedisCookies.fetch_cookies()


    cookies = cookies_json['cookies']

    unique_id = cookies_json['unique_id']

    resp = requests.get(url=home_url.format(unique_id), headers=get_header(), cookies=cookies, verify=False).text

    home_html = BeautifulSoup(resp, 'html.parser')

    scripts = home_html.find_all('script')
    scripts.reverse()

    view = re.compile('FM.view\((.*)\)')
    weibo_html_content = ''
    for script in scripts:
        result = view.findall(script.string)
        if len(result):

            r_json = json.loads(result[0])
            if 'pl.content.homeFeed.index' == r_json['ns']:
                weibo_html_content = r_json['html']
                break
    weibo_info = []

    if weibo_html_content != '':
        weibo_html = BeautifulSoup(weibo_html_content, 'html.parser')
        weibos = weibo_html.find_all('div', 'WB_detail')

        for weibo in weibos:

            source = ''
            date = ''
            weibo_url = ''
            all_a = weibo.find_all('a', attrs={'class': 'S_txt2'})
            weibo_text = weibo.find('div', attrs={'class': 'WB_text'})
            content = weibo_text.text


            for _a in all_a:


                if _a.has_attr('date') and _a.has_attr('href'):

                    date = _a.get('date')
                    weibo_url = _a.get('href')
                if _a.has_attr('action-type'):
                    source = _a.text
            weibo = Weibo(source=source, url=weibo_url, date_time=date, content=content)
            db_session.add(weibo)
            db_session.commit()
            weibo_info.append('date:%s\tsource:%s\turl:%s' % (date, source, weibo_url))
    return weibo_info

