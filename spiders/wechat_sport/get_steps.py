import requests
import re
import json
import datetime
from pprint import pprint
import sys
import os
import django
from time import sleep
sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Jpider.settings'
django.setup()
from spiders.models import Step
HEADERS = {

    'Host': 'hw.weixin.qq.com',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',

    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI '
                  'WindowsWechat QBCore/3.43.556.400 QQBrowser/9.0.2524.400',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4',
    'Cookie': 'hwstepranksk=uiNfWaL2l5E6ItwiqWdoU9gbuSnCWw2vxj-5_7i7U6QH6eWZ;'
}

url = 'https://hw.weixin.qq.com/steprank/step/personal'
while True:
    resp = requests.get(url=url, params={
       #  'pass_ticket': 'wHHOyL%2BvmKG1LE5VIuKgnrVj825Zv9dFN6HzwqXRZ9IpyQ6I6EcmRXkBtXTB5fAY'
    }, headers=HEADERS).text
    match_strings = re.findall(r"window.json = (\S+);", resp)

    resp_json = json.loads(match_strings[0])
    step = Step()
    step.steps = resp_json['rankdesc']['score']
    step.curr_time = datetime.datetime.now()
    step.save()
    pprint(step)
    sleep(1*60)
