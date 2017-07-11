import json
from dao.redis_cookies import RedisCookies
from headers import headers
import requests
from tasks.workers import app
from bs4 import BeautifulSoup
import re

@app.task
def home_page():
    home_url = 'http://weibo.com/u/{}?is_ori=1&is_tag=0&profile_ftype=1&page=1'

    user_cookies = RedisCookies.fetch_cookies()
    cookies_json = json.loads(user_cookies)

    cookies = cookies_json['cookies']
    print(cookies)
    unique_id = cookies_json['unique_id']
    print(home_url.format(unique_id))
    resp = requests.get(url=home_url.format(unique_id), headers=headers, cookies=cookies, verify=False).text

    home_html = BeautifulSoup(resp, 'html.parser')

    scripts = home_html.find_all('script')
    scripts.reverse()

    view = re.compile('FM.view\((.*)\)')
    weibo_content = ''
    for script in scripts:
        result = view.findall(script.string)
        if len(result):
            print(result)
            r_json = json.loads(result[0])
            if 'pl.content.homeFeed.index' == r_json['ns']:
                weibo_content = r_json['html']
                break
    return weibo_content

