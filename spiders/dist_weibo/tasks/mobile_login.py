import requests

args = {
            'username': '767543579@qq.com',
            'password': 'JOPPER',
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

session = requests.session()
session.post('https://passport.weibo.cn/sso/login', data=args)
resp = session.get('https://m.weibo.cn/api/container/getIndex?containerid=2304132210643391_-_WEIBO_SECOND_PROFILE_MORE_WEIBO&page=1')

print(session.cookies.get_dict())
print(session.get('http://weibo.com/47452014').text)
print(resp.text)


