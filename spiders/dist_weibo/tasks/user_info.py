from dao.redis_cookies import RedisCookies
import json
from tasks.workers import app
from headers import headers
import requests

@app.task(ignore_result=True)
def user_info(user_id):
    base_home_url = 'http://weibo.com/p/100505%s/info' % user_id
    user_cookies = RedisCookies.fetch_cookies()
    cookies_json = json.loads(user_cookies)
    cookies = cookies_json['cookies']
    print(cookies)

    resp = requests.get(url=base_home_url,params={'mod': 'pedit_more'}, headers=headers, cookies=cookies, verify=False).text
    print(resp)
    return resp