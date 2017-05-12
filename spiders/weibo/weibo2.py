import http.cookiejar
import urllib.request
import urllib.parse
import urllib.error
import json

import os
import sys
import django
from django.db.models import Q
from time import sleep
import queue
import threading
from multiprocessing import Lock
import random
import traceback
sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Jpider.settings'
django.setup()
from spiders.models import WeiboUser, Weibo, UserRelationship
from spiders.weibo import user_agent
from spiders import logger



class WeiboCrawler:
    def __init__(self, user, password, db='weibo'):

        self.user = user
        self.password = password
        self.weibo_queue = queue.Queue()
        self.user_queue = queue.Queue()
        # self.opener = self.make_my_opener()
        self.CRAWLED_USERS = set()
        self.CRAWLED_WEIBO_USERS = set()
        self.weibo_set_lock = Lock()
        self.user_set_lock = Lock()
        self.THREAD_NUM = 10
        self.logger = logger.LOGGER
        self.TRY_TIME = 3
        self.index = 0
        self.SLEEP_TIME = [5, 6, 7, 8, 9, 10, 15]
        self.login_url = 'https://passport.weibo.cn/sso/login'
        self.root_url = 'http://m.weibo.cn'
        self.weibo_url_pattern = 'http://m.weibo.cn/page/json?containerid=100505%s_-_WEIBO_SECOND_PROFILE_WEIBO&page=%s'
        self.followes_url_pattern = 'http://m.weibo.cn/api/container/getSecond?containerid=100505%s_-_FOLLOWERS&page=%s'
        self.fans_url_pattern = 'http://m.weibo.cn/api/container/getSecond?containerid=100505%s_-_FANS&page=%s'
        # self.mysqlconn = MysqlConnection(db=db)
        self.proxies = [{"HTTP": "58.248.137.228:80"}, {"HTTP": "58.251.132.181:8888"}, {"HTTP": "60.160.34.4:3128"},
                        {"HTTP": "60.191.153.12:3128"}, {"HTTP": "60.191.164.22:3128"}, {"HTTP": "80.242.219.50:3128"},
                        {"HTTP": "86.100.118.44:80"}, {"HTTP": "88.214.207.89:3128"}, {"HTTP": "91.183.124.41:80"},
                        {"HTTP": "93.51.247.104:80"}]

        self.USERS = [{'username': '18270916129', 'password':'VS7452014'},
                      {'username': 'jjzhu_ncu@163.com', 'password':'vs7452014'},
                      {'username': 'jjzhu_zju@163.com', 'password':'jvs7452014'},
                      {'username': '767543579@qq.com', 'password': 'JOPPER'},]

        self.head = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Host': 'm.weibo.cn',
            'Proxy-Connection': 'keep-alive',
            'User-Agent': user_agent.agents[random.randint(0, len(user_agent.agents)-1)]

                # 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
                #           ' (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        self.init_thread()  # 开启进程
        # self.seed = 'http://m.weibo.cn/login?ns=1&backURL=http%3A%2F%2Fm.weibo.cn%2F&backTitle=%CE%A2%B2%A9&vt=4&'
    def init_thread(self):
        self.logger.info('init  threads: %d' % self.THREAD_NUM)
        for i in range(self.THREAD_NUM):
            thread_weibo = threading.Thread(target=self.crawl_weibo, name='weibo_thread_'+str(i))
            thread_user = threading.Thread(target=self.crawl_user, name='user_thread_' + str(i))
            thread_weibo.start()
            thread_user.start()

    def crawl_weibo(self):
        while True:
            user_id = self.weibo_queue.get()
            try:
                self.grab_user_blogs(user_id)
            except urllib.error.HTTPError:
                self.logger.error(traceback.print_exc())
                sleep(5 * 60)

    def crawl_user(self):
        while True:
            user_id = self.user_queue.get()
            try:
                self.grab_user(user_id)
            except urllib.error.HTTPError:
                self.logger.error(traceback.print_exc())
                sleep(5 * 60)


    def change_proxy(self, opener):
        proxy_handler = urllib.request.ProxyHandler(self.proxies[self.index % self.proxies.__len__()])
        self.logger.info("换代理了..."+str(self.proxies[self.index % self.proxies.__len__()]))
        self.index += 1
        if self.index >= 1000:
            self.index = 0
        # proxy_auth_handler = urllib.request.ProxyBasicAuthHandler()

        opener.add_handler(proxy_handler)

    def login(self, user_name, password, opener):
        self.logger.info(user_name+' login')
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
        while try_time < self.TRY_TIME:
            try:
                opener.open(self.login_url, post_data)
                self.logger.info("login successful"+', thread name:'+threading.current_thread().getName())
                sleep(1)
                break
            except Exception :
                self.logger.error("login failed")
                self.logger.error(traceback.print_exc())
                try_time += 1
                self.logger.info('try %d time' %  try_time)



    def make_my_opener(self):
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
            'User-Agent': user_agent.agents[random.randint(0, len(user_agent.agents)-1)]
                # 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML,'
                #           ' like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        opener.addheaders = header
        return opener

    def change_header(self, opener):
        head = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip,deflate,sdch',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Host': 'm.weibo.cn',
            # 'Referer': 'http://m.weibo.cn/page/tpl?containerid=1005052210643391_-_WEIBO_SECOND_PROFILE_WEIBO',
            # 'Referer': 'http://m.weibo.cn/',
            'Proxy-Connection': 'keep-alive',
            'User-Agent': user_agent.agents[random.randint(0, len(user_agent.agents)-1)]
        }
        header = []
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        opener.addheaders = header

    def user_enqueue(self, user_id):
        if user_id in self.CRAWLED_USERS:
            self.logger.info('\n\n\nuser_id: %s is already crawled\n\n\n' % user_id)
            return
        with self.user_set_lock:
            self.CRAWLED_USERS.add(str(user_id))
            # self.logger.info('\n\n\n'+str(self.CRAWLED_USERS)+'\n\n\n')
            self.user_queue.put(str(user_id))
    def weibo_enqueue(self, user_id):
        if user_id in self.CRAWLED_WEIBO_USERS:
            self.logger.info('\n\n\nuser_id: %s is already crawled\n\n\n' % user_id)
            return
        with self.weibo_set_lock:
            self.CRAWLED_WEIBO_USERS.add(str(user_id))
            self.weibo_queue.put(str(user_id))
    def save_blog_info(self, blog_info):

        try:
            weibo = Weibo.objects.get(pk=blog_info['id'])
        except Exception:
            weibo = Weibo()
        weibo.id = str(blog_info['id'])
        weibo.created_timestamp = blog_info['created_timestamp']


        if 'retweeted_status' in blog_info:
            rew_json = blog_info['retweeted_status']
            if rew_json['user']['id'] is not None:

                try:
                    ret_weibo = Weibo.objects.get(pk=rew_json['id'])
                except Exception:
                    ret_weibo = self.save_blog_info(rew_json)
                weibo.retweented_status = ret_weibo

                self.user_enqueue(ret_weibo.user.id)
        weibo.source = blog_info['source']
        weibo.text = blog_info['text']
        try:
            user  = WeiboUser.objects.get(pk=blog_info['user']['id'])
        except Exception:
            user = self.save_user_info(blog_info['user'])


        weibo.user = user

        weibo.save()
        self.logger.info(str(weibo))
        if weibo.retweented_status is not None:  # 添加关系

            try:
                r = UserRelationship.objects.get(Q(user=weibo.retweented_status.user) & Q(follower=weibo.user))
                self.logger.info('relationship already exist:' + str(r))
            except Exception:
                self.logger.info('relationship not exist')
                relation = UserRelationship()
                relation.user = weibo.retweented_status.user
                relation.follower = weibo.user
                self.logger.info(relation)
                relation.save()
        return weibo

    def insert_pic_info(self, pic_info):
        pass

    def save_user_info(self, user_info):
        user = WeiboUser()
        user.id = user_info['id']
        user.attNum = user_info['attNum'] if 'attNum' in user_info \
            else user_info['follow_count'] if 'follow_count' in user_info \
            else ''
        user.created_at = user_info['created_at'] if 'created_at' in user_info else ''
        user.screen_name = user_info['screen_name'] if 'screen_name' in user_info else ''
        user.description = user_info['description'] if 'description' in user_info else ''
        user.fansNum = user_info['fansNum'] if 'fansNum' in user_info \
            else user_info['followers_count'] if 'followers_count' in user_info \
            else ''
        user.mblogNum = user_info['mblogNum'] if 'mblogNum' in user_info \
            else user_info['statuses_count'] if 'statuses_count' in user_info \
            else ''
        user.nativePlace = user_info['nativePlace'] if 'nativePlace' in user_info else ''
        user.profile_url = user_info['profile_url'] if 'profile_url' in user_info else ''
        user.gender = WeiboUser.GENDER.index(user_info['gender'] if 'gender' in user_info else 'u')
        user.save()

        self.logger.info(user)
        return user

    def insert_comment_info(self, comment_info):
        pass

    def grab_user_blogs(self, user_id):
        opener = self.make_my_opener()
        curr_index = random.randint(0, len(self.USERS)-1)
        self.logger.info('user index : %d' % curr_index)
        self.login(self.USERS[curr_index]['username'], self.USERS[curr_index]['password'], opener)
        self.change_header(opener)

        error = False
        page = 1
        url = self.weibo_url_pattern % (str(user_id), str(page))
        self.logger.info("正在打开："+url)
        rsp = opener.open(url)
        # print(rsp.read())
        return_json = json.loads(rsp.read().decode())

        card = return_json['cards'][0]
        # print(card['maxPage'])
        max_page = card['maxPage']
        card_group = card['card_group']
        for blog_info in card_group:
            if blog_info['card_type'] != 9:
                continue

            self.save_blog_info(blog_info['mblog'])
        page += 1
        while page <= max_page:
            url = self.weibo_url_pattern % (str(user_id), str(page))
            self.logger.info("正在打开："+url)
            rsp = opener.open(url)
            return_json = json.loads(rsp.read().decode())
            # print('返回数据：'+str(return_json))
            cards = return_json['cards']

            for card in cards:
                if card.__contains__('msg'):
                    error = True
                    break
                card_group = card['card_group']
                error = False
                for blog_info in card_group:
                    if blog_info['card_type'] != 9:
                        continue

                    self.save_blog_info(blog_info['mblog'])
            if not error:
                page += 1
            time = self.SLEEP_TIME[random.randint(0, len(self.SLEEP_TIME)-1)]
            self.logger.info('sleep time:%d seconds'%time)
            sleep(time)
            self.change_proxy(opener)
        # self.relogin() # 重新登入

    def save_relationship(self, user, fan):
        try:
            r = UserRelationship.objects.get(Q(user=user) & Q(follower=fan))
            self.logger.info('relationship already exist:' + str(r))
        except Exception:
            self.logger.info('relationship not exist')
            relation = UserRelationship()
            relation.user = user
            relation.follower = fan
            self.logger.info(relation)
            relation.save()

    def grab_user(self, user_id):
        self.logger.info('grab follower for user:%s' % user_id )
        opener = self.make_my_opener()
        curr_index = random.randint(0, len(self.USERS) - 1)
        self.logger.info('user index : %d' % curr_index)
        self.login(self.USERS[curr_index]['username'], self.USERS[curr_index]['password'], opener)
        self.change_header(opener)
        page = 1
        try:
            user = WeiboUser.objects.get(pk=user_id)
        except Exception:
            url = self.weibo_url_pattern % (str(user_id), str(1))
            rsp = opener.open(url)
            # print(rsp.read())
            return_json = json.loads(rsp.read().decode())

            card = return_json['cards'][0]
            card_group = card['card_group'][0]
            user = self.save_user_info(card_group['mblog']['user'])

            self.weibo_enqueue(user.id)

        rsp = opener.open(self.followes_url_pattern % (str(user_id), str(page)))
        rsp_json = json.loads(rsp.read().decode())
        max_page = rsp_json['maxPage']

        for user_json in rsp_json['cards']:
            follower = self.save_user_info(user_json['user'])
            self.user_enqueue(str(follower.id))
            self.save_relationship(follower, user)
            self.weibo_enqueue(follower.id)
        page += 1
        while page <= max_page:
            rsp = opener.open(self.followes_url_pattern % (str(user_id), str(page)))
            rsp_json = json.loads(rsp.read().decode())
            for user_json in rsp_json['cards']:
                follower = self.save_user_info(user_json['user'])
                self.user_enqueue(str(follower.id))
                self.save_relationship(follower, user)
                self.weibo_enqueue(follower.id)
            page += 1
            time = self.SLEEP_TIME[random.randint(0, len(self.SLEEP_TIME) - 1)]
            self.logger.info('sleep time:%d seconds' % time)
            sleep(time)
            self.change_proxy(opener)

    def relogin(self, opener):
        print(self.USERS[self.CURR_USER_INDEX]['username']+" logout")
        opener.open('http://m.weibo.cn/home/logout') # 登出
        print('logout successful')
        self.opener = self.make_my_opener()
        curr_index = random.randint(0, len(self.USERS)-1)
        while curr_index  == self.CURR_USER_INDEX:
            curr_index = random.randint(0, len(self.USERS)-1)

        self.CURR_USER_INDEX = curr_index
        print(self.USERS[self.CURR_USER_INDEX]['username'] + " login")
        self.login(self.USERS[self.CURR_USER_INDEX]['username'], self.USERS[self.CURR_USER_INDEX]['password'])
        self.change_header(opener)

    def start(self):
        # url = 'http://m.weibo.cn/home/me?format=cards'
        # opener = self.make_my_opener()
        # curr_index = random.randint(0, len(self.USERS) - 1)
        # self.login(self.USERS[curr_index]['username'], self.USERS[curr_index]['password'], opener)
        # self.change_header(opener)
        # rsp = opener.open('http://weibo.com/chenkun')
        # print(rsp.read().decode(encoding='gbk'))
        # rsp = opener.open()
        # page = 1
        # user_id = 2210643391
        # rsp = opener.open('http://m.weibo.cn/api/container/getSecond?containerid=100505%s_-_FOLLOWERS&page=%d' % (str(user_id), page))
        # rsp_json = json.loads(rsp.read().decode())
        # max_page = rsp_json['maxPage']
        # print(rsp_json['maxPage'])
        # print(rsp_json['cards'])
        # for user_json in rsp_json['cards']:
        #     self.save_user_info(user_json['user'])
        # page += 1
        # while page <= max_page:
        #     rsp = opener.open('http://m.weibo.cn/api/container/getSecond?containerid=100505%s_-_FOLLOWERS&page=%d' % (
        #     str(user_id), page))
        #     rsp_json = json.loads(rsp.read().decode())
        #     for user_json in rsp_json['cards']:
        #         self.save_user_info(user_json['user'])
        #     page += 1
        self.user_queue.put('1235919683')
        # self.queue.put('2210643391')

    def save_pic(self):
        url = 'http://ww2.sinaimg.cn/large/c0788b86jw1f2xfstebzaj20dc0hst9r.jpg'
        rsp = self.opener.open(url)
        pic_data = rsp.read()
        try:
            file = open("d:\\weibo_pic\\1.jpg", 'wb')
            file.write(pic_data)
            file.close()
        except FileNotFoundError:
            os.mkdir("d:\\weibo_pic")
        except FileExistsError:
            pass

    def get_comment_by_page(self, blog_id, page_num):
        url = 'http://m.weibo.cn/single/rcList?format=cards&id='
        req_url = url + str(blog_id) + '&type=comment&hot=0&page='+str(page_num)
        print('浏览器正在打开url：'+req_url)
        rsp = self.opener.open(req_url)
        return_json = json.loads(rsp.read().decode())
        print('请求返回数据:\t'+str(return_json))
        if page_num == 1:
            comment_json = return_json[1]
        else:
            comment_json = return_json[0]
        return comment_json

    def grab_comment(self, blog_id):
        page = 1
        comment_json = self.get_comment_by_page(blog_id, page)
        print('评论——json\t' + str(comment_json))
        if 'maxPage' not in comment_json:
            return
        max_page = comment_json['maxPage']
        page += 1
        if 'card_group' in comment_json:
            comment_card_group = comment_json['card_group']
            for comment_group in comment_card_group:
                pass
        print("总页面数：max_page：\t"+str(max_page))
        while page <= max_page:
            print("curr_page:\t"+str(page)+"\t    max_page\t:"+str(max_page))
            comment_json = self.get_comment_by_page(blog_id, page)
            if 'card_group' in comment_json:
                comment_card_group = comment_json['card_group']
                for comment_group in comment_card_group:
                    pass
            page += 1

    def grab_weibo(self):
        open_url = 'http://m.weibo.cn/index/feed?format=cards'
        print('浏览器正在打开url：' + open_url)
        rsp = self.opener.open(open_url)
        return_json = json.loads(rsp.read().decode())
        print(return_json)
        card_group = return_json[0]['card_group']
        next_cursor = return_json[0]['next_cursor']
        previous_cursor = return_json[0]['previous_cursor']
        page = return_json[0]['page']
        max_page = return_json[0]['maxPage']
        page = 1


        c = '3963770537235924&type=comment&hot=0&page=2'
        for group in card_group:
            mblog = group['mblog']
            curr_blog_id = mblog['id']
            user = mblog['user']
            user_id = user['id']
            self.grab_comment(curr_blog_id)
            # page += 1

        n = 20
        while n > 0:
            n -= 1
            open_url = 'http://m.weibo.cn/index/feed?format=cards&next_cursor='+str(next_cursor) + '&page='+str(page)
            print('浏览器正在打开url：' + open_url)
            rsp = self.opener.open(open_url)
            return_json = json.loads(rsp.read().decode())
            card_group = return_json[0]['card_group']
            next_cursor = return_json[0]['next_cursor']
            previous_cursor = return_json[0]['previous_cursor']
            for group in card_group:
                mblog = group['mblog']
                curr_blog_id = mblog['id']
                user = mblog['user']
                user_id = user['id']
                self.grab_comment(curr_blog_id)
            self.change_proxy()
            sleep(1*60)
        return


    def didi(self):
        opener = self.make_my_opener()
        rsp = opener.open('http://100.69.76.2/sqoopRelationship/all?_=1491994174432')
        print(rsp.read().decode())


def main():
    my = WeiboCrawler("", "")
    my.start()

if __name__ == '__main__':
    main()
