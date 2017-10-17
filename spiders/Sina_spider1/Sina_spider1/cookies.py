# encoding=utf-8

import base64
import requests
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
import logging
from settings import PROPERTIES
from yumdama import identify
import traceback
reload(sys)
sys.setdefaultencoding('utf8')
IDENTIFY = 1  # 验证码输入方式:        1:看截图aa.png，手动输入     2:云打码
# 0 代表从https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18) 获取cookie
# 1 代表从https://weibo.cn/login/获取Cookie
COOKIE_GETWAY = 1
dcap = dict(DesiredCapabilities.PHANTOMJS)  # PhantomJS需要使用老版手机的user-agent，不然验证码会无法通过
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
)
logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)  # 将selenium的日志级别设成WARNING，太烦人


myWeiBo = [
    {'no': '767543579@qq.com', 'psw': 'JOPPER'},
    # {'no': 'shudieful3618@163.com', 'psw': 'a123456'},
    {'no': 'jjzhu_ncu@163.com', 'psw': 'jvs7452014'},
    {'no': 'jjzhu_zju@163.com', 'psw': 'jvs7452014'},
]

def getCookie(account, password):
    if COOKIE_GETWAY == 0:
        return get_cookie_from_login_sina_com_cn(account, password)
    elif COOKIE_GETWAY == 1:
        return get_cookie_from_weibo_cn(account, password)
    else:
        logger.error("COOKIE_GETWAY Error!")


def get_cookie_from_login_sina_com_cn(account, password):
    """ 获取一个账号的Cookie """
    loginURL = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)"
    username = base64.b64encode(account.encode("utf-8")).decode("utf-8")
    postData = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }
    session = requests.Session()
    r = session.post(loginURL, data=postData)
    jsonStr = r.content.decode("gbk")
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        logger.warning("Get Cookie Success!( Account:%s )" % account)
        cookie = session.cookies.get_dict()
        print cookie
        return json.dumps(cookie)
    else:
        logger.warning("Failed!( Reason:%s )" % info["reason"])
        return ""


def get_cookie_from_weibo_cn(account, password):
    """ 获取一个账号的Cookie """
    try:
        browser = webdriver.PhantomJS(desired_capabilities=dcap)
        browser.get("https://weibo.cn/login/")
        time.sleep(1)

        failure = 0
        while "微博" in browser.title and failure < 5:
            failure += 1
            browser.save_screenshot("aa.png")

            username = browser.find_element_by_id("loginName")
            username.clear()
            username.send_keys(account)

            psd = browser.find_element_by_xpath('//input[@type="password"]')
            psd.clear()
            psd.send_keys(password)
            try:
                code = browser.find_element_by_name("loginVCode")
                code.clear()
                if IDENTIFY == 1:
                    code_txt = raw_input("请查看路径下新生成的aa.png，然后输入验证码:")  # 手动输入验证码
                else:
                    from PIL import Image
                    img = browser.find_element_by_xpath('//form[@method="post"]/div/img[@alt="请打开图片显示"]')
                    x = img.location["x"]
                    y = img.location["y"]
                    im = Image.open("aa.png")
                    im.crop((x, y, 100 + x, y + 22)).save("ab.png")  # 剪切出验证码
                    code_txt = identify()  # 验证码打码平台识别
                code.send_keys(code_txt)
            except NoSuchElementException, e:
                pass

            commit = browser.find_element_by_id("loginAction")
            commit.click()
            time.sleep(3)
            # print browser.title
            # print browser.page_source
            # if "手机新浪网" not in browser.title:
            #     time.sleep(4)
            # if '未激活微博' in browser.page_source:
            #     print '账号未开通微博'
            #     return {}

        cookie = {}
        browser.get("https://weibo.cn")
        # if "我的首页" in browser.title:
        for elem in browser.get_cookies():
            cookie[elem["name"]] = elem["value"]
        logger.info("Get Cookie Success!( Account:%s )" % account)
        return json.dumps(cookie)
    except Exception, e:
        logger.warning("Failed %s!" % account)
        traceback.print_exc()
        return ""
    finally:
        try:
            browser.quit()
        except Exception, e:
            pass


def getCookies(weibo):
    """ 获取Cookies """
    cookies = []
    for elem in weibo:
        account = elem['user']
        password = elem['password']
        print account, password
        cookie = getCookie(account, password)
        if cookie is not None:
            print cookie
            if isinstance(cookie, str):
                cookies.append(eval(cookie))
            elif isinstance(cookie, dict):
                cookies.append(cookie)
            else:
                raise "unsupported type[%s] of cookie[%s]" % (type(cookie), cookie)

    return cookies
cookies = getCookies(PROPERTIES['accounts'])
logger.warning("Get Cookies Finish!( Num:%d)" % len(cookies))
