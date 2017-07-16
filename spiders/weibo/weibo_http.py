from spiders.logger import LOGGER
from spiders import user_agent
from spiders.weibo import constants

import traceback
import random

import http.cookiejar
import urllib.parse
import urllib.request
from time import sleep
import threading


def login(user_name, password, opener):
    LOGGER.info(user_name + ' login')
    args = {
        'username': user_name,
        'password': password,
        'savestate': 1,
        'ec': 0,
        'pagerefer': 'https://passport.weibo.cn/signin/'
                     'welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F&wm=3349&vt=4',
        'entry': 'mweibo',
        'wentry': '',
        'loginfrom': '',
        'client_id': '',
        'code': '',
        'qq': '',
        'hff': '',
        'hfp': ''
    }

    post_data = urllib.parse.urlencode(args).encode()
    try_time = 0
    while try_time < constants.TRY_TIME:
        try:
            opener.open(constants.LOGIN_URL, post_data)

            LOGGER.info("login successful" + ', thread name:' + threading.current_thread().getName())
            sleep(1)
            break
        except :
            LOGGER.error("login failed")
            LOGGER.error(traceback.print_exc())
            try_time += 1
            LOGGER.info('try %d time' % try_time)


def get_openner():
    opener = make_my_opener()
    curr_index = random.randint(0, len(constants.USERS) - 1)  # 随机选取用户
    LOGGER.info('user index : %d' % curr_index)
    login(constants.USERS[curr_index]['username'], constants.USERS[curr_index]['password'], opener)
    change_header(opener)
    return opener


def change_header(opener, ext=None):
    head = {
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Host': 'm.weibo.cn',
        'Proxy-Connection': 'keep-alive',
        'User-Agent': user_agent.agents[random.randint(0, len(user_agent.agents) - 1)]
    }
    if ext:
        head.update(ext)
    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header


def change_proxy( opener):
    proxy_handler = urllib.request.ProxyHandler(constants.PROXIES[random.randint(0, len(constants.PROXIES) -1)])
    opener.add_handler(proxy_handler)


def make_my_opener():
    """
            模拟浏览器发送请求
            :return:
            """
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    header = []
    head = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Connection': 'keep-alive',
        'Content-Length': '254',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'passport.weibo.cn',
        'Origin': 'https://passport.weibo.cn',
        'Referer': 'https://passport.weibo.cn/signin/login?'
                   'entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F',
        'User-Agent': user_agent.agents[random.randint(0, len(user_agent.agents) - 1)]
    }
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header
    return opener