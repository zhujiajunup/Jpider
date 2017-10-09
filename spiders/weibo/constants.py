from spiders.weibo.weibo_conf import get_account
PROXIES = [{"HTTP": "58.248.137.228:80"}, {"HTTP": "58.251.132.181:8888"}, {"HTTP": "60.160.34.4:3128"},
                        {"HTTP": "60.191.153.12:3128"}, {"HTTP": "60.191.164.22:3128"}, {"HTTP": "80.242.219.50:3128"},
                        {"HTTP": "86.100.118.44:80"}, {"HTTP": "88.214.207.89:3128"}, {"HTTP": "91.183.124.41:80"},
                        {"HTTP": "93.51.247.104:80"}]

SLEEP_TIME = [6, 7, 8, 10, 10, 13, 15]

ROOT_URL = 'https://m.weibo.cn'
LOGIN_URL = 'https://passport.weibo.cn/sso/login'
WEIBO_URL_PATTERN = 'https://m.weibo.cn/api/container/getIndex?' \
                         'containerid=230413%s_-_WEIBO_SECOND_PROFILE_MORE_WEIBO&page=%s'
FOLLOWER_URL_PATTERN = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_' \
                            '%s&luicode=10000011&lfid=100505%s1&page=%s'
FANS_URL_PATTERN2 = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_%s&luicode=10000011&lfid=100505%s'
FANS_URL_PATTERN = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_%s&luicode=10000011&lfid=100505%s&since_id=%s'
INFO_URL_PATTERN = 'https://m.weibo.cn/api/container/getIndex?containerid=230283%s_-_INFO'
USER_INFO_MAP = {
    '昵称': 'screen_name',
    '性别': 'gender',
    '所在地': 'nativePlace',
    '学校': 'school',
    '博客': 'blog',
    '等级': 'level',
    '注册时间': 'created_at'
}
# 登陆重试时间
TRY_TIME = 3

THREAD_NUM = 5

USERS = get_account()