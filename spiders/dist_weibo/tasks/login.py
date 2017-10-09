import execjs
import requests
import re
import json
import os
from tasks.workers import app
from dao.redis_cookies import RedisCookies
from headers import get_header
from logger import LOGGER

def get_session():
    return requests.session()


def get_js_exec(path):
    phantom = execjs.get('PhantomJS')
    with open(path, 'r') as f:
        source = f.read()
    return phantom.compile(source)


def get_encodename(name, js_exec):
    return js_exec.call('get_name', name)


def get_password(password, pre_obj, exec_js):
    nonce = pre_obj['nonce']
    pubkey = pre_obj['pubkey']
    servertime = pre_obj['servertime']
    return exec_js.call('get_pass', password, nonce, servertime, pubkey)


def get_prelogin_info(prelogin_url, session):
    json_pattern = r'.*?\((.*)\)'
    response_str = session.get(prelogin_url).text
    m = re.match(json_pattern, response_str)
    return json.loads(m.group(1))


def get_redirect(data, post_url, session):
    print(data)
    print(post_url)
    logining_page = session.post(post_url, data=data, headers=get_header())
    print(logining_page)
    login_loop = logining_page.content.decode('GBK')
    pa = r'location\.replace\([\'"](.*?)[\'"]\)'
    return re.findall(pa, login_loop)[0]


def do_login(session, url):
    return session.get(url).text

@app.task(ignore_result=True)
def clean():
    RedisCookies.clean()

@app.task(ignore_result=True)
def login(name='', password=''):
    json_pattern = r'.*?\((.*)\)'
    session = get_session()
    exec_js = get_js_exec(os.path.split(os.path.realpath(__file__))[0]+'/../js/ssologin.js')
    su = get_encodename(name, exec_js)
    post_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
    prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&' \
                   'su=' + su + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)'

    pre_obj = get_prelogin_info(prelogin_url, session)
    ps = get_password(password=password, pre_obj=pre_obj, exec_js=exec_js)
    data = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'useticket': '1',
        'pagerefer': "http://login.sina.com.cn/sso/logout.php?"
                     "entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl",
        'vsnf': '1',
        'su': su,
        'service': 'miniblog',
        'servertime': pre_obj['servertime'],
        'nonce': pre_obj['nonce'],
        'pwencode': 'rsa2',
        'rsakv': pre_obj['rsakv'],
        'sp': ps,
        'sr': '1366*768',
        'encoding': 'UTF-8',
        'prelt': '115',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&'
               'callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META',
    }
    url = get_redirect(data, post_url, session)
    print(url)
    login_info = do_login(session, url)
    m = re.match(json_pattern, login_info)
    info = json.loads(m.group(1))
    RedisCookies.save_cookies(name, info['userinfo']['uniqueid'],
                              cookies=session.cookies.get_dict())

#     return session, info

    # session.get('http://weibo.com/u')
if __name__ == '__main__':
    login()
