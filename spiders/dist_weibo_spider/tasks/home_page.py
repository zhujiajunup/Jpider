import json
from spiders.dist_weibo_spider.dao.redis_cookies import RedisCookies
from spiders.dist_weibo_spider.headers import headers
import requests

home_url = 'http://weibo.com/u/{}?is_ori=1&is_tag=0&profile_ftype=1&page=1'

user_cookies = RedisCookies.fetch_cookies()
cookies_json = json.loads(user_cookies)

cookies = cookies_json['cookies']
print(cookies)
unique_id = cookies_json['unique_id']
print(home_url.format(unique_id))
resp = requests.get(url=home_url.format(unique_id), headers=headers, cookies=cookies, verify=False).text
print(resp)

