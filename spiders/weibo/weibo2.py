
import json
import os
import sys
import django
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
from django.db.models import Q
from spiders import logger
from spiders.weibo import dao
from spiders.weibo import weibo_http
from spiders.weibo import constants

class WeiboCrawler:

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.weibo_queue = queue.Queue()  # 微博任务队列
        self.user_queue = queue.Queue()  # 用户信息队列
        self.fans_queue = queue.Queue()  # 用户粉丝队列
        self.follower_queue = queue.Queue()  # 用户关注队列
        self.m_info_queue = queue.Queue()  # 用户关注队列
        self.M_INFO_CRAWLED_USER = set()
        self.CRAWLED_USERS = set()
        self.WEIBO_CRAWLED_USERS = set()
        self.FANS_CRAWLED_USERS = set()
        self.FOLLOWER_CRAWLED_USERS = set()
        self.weibo_set_lock = Lock()
        self.m_info_set_lock = Lock()
        self.user_set_lock = Lock()
        self.fans_set_lock = Lock()
        self.follower_set_lock = Lock()
        self.logger = logger.LOGGER
        self.init_thread()  # 开启进程


    def init_thread(self):
        self.logger.info('init  threads: %d' % constants.THREAD_NUM)
        for i in range(constants.THREAD_NUM):
            thread_weibo = threading.Thread(target=self.crawl_weibo, name='weibo_thread_'+str(i))
            thread_user = threading.Thread(target=self.crawl_user, name='user_thread_' + str(i))
            thread_fans = threading.Thread(target=self.crawl_fans, name='fans_thread_' + str(i))
            thread_follower = threading.Thread(target=self.crawl_follower, name='follower_thread_' + str(i))
            thread_m_info = threading.Thread(target=self.crawl_m_info, name='m_info_thread_' + str(i))
            thread_weibo.start()
            thread_user.start()
            thread_fans.start()
            thread_follower.start()
            thread_m_info.start()

    def crawl_weibo(self):
        while True:
            user_id = self.weibo_queue.get()
            try:
                self.grab_user_blogs(user_id)

            except:
                self.logger.error(traceback.print_exc())
                sleep(5 * 60)

    def crawl_fans(self):
        while True:
            try:
                user_id = self.fans_queue.get()
                self.grab_user_fans(user_id)
            except:
                self.logger.error(traceback.print_exc())
                sleep(5 * 60)

    def crawl_follower(self):
        while True:
            try:
                user_id = self.follower_queue.get()
                self.grab_user_follower(user_id)
            except:
                self.logger.error(traceback.print_exc())
                sleep(5 * 60)

    def crawl_m_info(self):
        while True:
            try:
                user_id = self.m_info_queue.get()
                self.grab_m_info(user_id)
            except:
                self.logger.error(traceback.print_exc())
                sleep(5 * 60)

    def crawl_user(self):
        while True:
            user_id = self.user_queue.get()
            try:
                self.grab_user(user_id)
                self.id_enqueue(user_id, self.fans_set_lock, self.FANS_CRAWLED_USERS, self.fans_queue)
                self.id_enqueue(user_id, self.follower_set_lock, self.FOLLOWER_CRAWLED_USERS, self.follower_queue)
                self.id_enqueue(user_id, self.weibo_set_lock, self.WEIBO_CRAWLED_USERS, self.weibo_queue)
                self.id_enqueue(user_id, self.m_info_set_lock, self.M_INFO_CRAWLED_USER, self.m_info_queue)
                time = constants.SLEEP_TIME[random.randint(0, len(constants.SLEEP_TIME) - 1)]
                self.logger.info('sleep time:%d seconds' % time)
                sleep(time)
            except: # 可以细化
                self.logger.error(traceback.print_exc())
                sleep(1 * 60)

    def id_enqueue(self, user_id, id_lock, id_set, id_queue):
        if user_id in id_set:
            self.logger.info('\n\n\nuser_id: %s is already crawled\n\n\n' % user_id)
            return
        with id_lock:
            id_set.add(user_id)
            id_queue.put(user_id)

    def grab_m_info(self, user_id):
        try:
            user = WeiboUser.objects.get(Q(id=user_id))
        except WeiboUser.DoesNotExist:
            user = WeiboUser()
            user.id = user_id
        self.logger.info('grab follower for user:%s' % user_id)
        opener = weibo_http.get_openner()

        weibo_http.change_header(opener)
        url = constants.INFO_URL_PATTERN % str(user_id)
        self.logger.info(url)
        rsp = opener.open(url)
        rsp_data = rsp.read().decode()

        return_json = json.loads(rsp_data)
        for card in return_json['cards']:
            for item in filter(lambda i: 'item_name' in i, card['card_group']):
                print(item)
                if item['item_name'] in constants.USER_INFO_MAP:
                    setattr(user, constants.USER_INFO_MAP[item['item_name']], item['item_content'])

        user.save()
        # self.weibo_enqueue(user.id)
        self.logger.info('user info: %s' % user)
        return user
        pass

    def grab_user_fans(self, user_id):
        opener = weibo_http.get_openner()
        weibo_http.change_header(opener, {'Refer': constants.FANS_URL_PATTERN2 % (user_id, user_id)})
        page = 1

        user = self.grab_user(user_id)
        fans_num = user.fansNum
        max_page = int(int(fans_num)/20)
        while page <= max_page:

            resp = opener.open(constants.FANS_URL_PATTERN % (user_id, user_id, str(page)))
            self.logger.info(constants.FANS_URL_PATTERN % (user_id, user_id, str(page)))
            r = resp.read()
            print(r)
            resp_json = json.loads(r.decode())
            if 'msg' in resp_json:
                break
            for card in resp_json['cards']:
                for cg in card['card_group']:
                    print(cg['user'])
                    fan = dao.save_user_info(cg['user'])
                    dao.save_relationship(user, fan)
                    self.id_enqueue(fan.id, self.user_set_lock, self.CRAWLED_USERS, self.user_queue)

            print(resp_json)
            page += 1

    def grab_user_follower(self, user_id):
        opener = weibo_http.get_openner()
        user = self.grab_user(user_id)
        att_num = user.attNum
        max_page = int(int(att_num) / 20)
        page = 1
        while page <= max_page:
            resp = opener.open(constants.FOLLOWER_URL_PATTERN % (user_id, user_id, str(page)))
            self.logger.info(constants.FOLLOWER_URL_PATTERN % (user_id, user_id, str(page)))
            r = resp.read()
            resp_json = json.loads(r.decode())
            if 'msg' in resp_json:
                break
            for card in resp_json['cards']:

                for cg in filter(lambda c: 'user' in c, card['card_group']):
                    print(cg)
                    print(cg['user'])
                    follower = dao.save_user_info(cg['user'])
                    dao.save_relationship(follower, user)
                    self.id_enqueue(follower.id, self.user_set_lock, self.CRAWLED_USERS, self.user_queue)
            page += 1
        pass

    def grab_user_blogs(self, user_id):
        opener = weibo_http.get_openner()
        has_get_pages = False
        max_page = 2
        page = 1
        while page <= max_page:
            url = constants.WEIBO_URL_PATTERN % (str(user_id), str(page))
            self.logger.info("正在打开："+url)
            rsp = opener.open(url)
            # print(rsp.read())
            return_json = json.loads(rsp.read().decode())

            cards = return_json['cards']
            # print(card['maxPage'])
            if not has_get_pages:
                total = return_json['cardlistInfo']['total']
                max_page = int(int(total)/9)
                has_get_pages = True

            print('-'*16+"\n"+str(cards))
            for card in filter(lambda c: 'mblog' in c and 'msg' not in c, cards):
                blog_info = card['mblog']
                weibo = dao.save_blog_info(blog_info)
                if 'retweeted_status' in blog_info:
                    rew_json = blog_info['retweeted_status']
                    # 这里，转发的微博可能被删除、举报，user就为null
                    if rew_json['user'] is not None and rew_json['user']['id'] is not None:
                        try:
                            ret_weibo = Weibo.objects.get(pk=rew_json['id'])
                        except Weibo.DoesNotExist:
                            ret_weibo = dao.save_blog_info(rew_json)
                        weibo.retweented_status = ret_weibo
                        weibo.save()
            page += 1
            time = constants.SLEEP_TIME[random.randint(0, len(constants.SLEEP_TIME)-1)]
            self.logger.info('sleep time:%d seconds' % time)
            sleep(time)
            weibo_http.change_proxy(opener)


    def grab_user(self, user_id):
        self.logger.info('grab follower for user:%s' % user_id)
        opener = weibo_http.get_openner()

        weibo_http.change_header(opener)
        url = constants.WEIBO_URL_PATTERN % (str(user_id), str(1))
        self.logger.info(url)
        rsp = opener.open(url)
        rsp_data = rsp.read().decode()
        print(rsp_data)
        return_json = json.loads(rsp_data)
        card = return_json['cards'][0]
        user = dao.save_user_info(card['mblog']['user'])
        # self.weibo_enqueue(user.id)
        return user


    def relogin(self, opener):
        print(constants.USERS[self.CURR_USER_INDEX]['username']+" logout")
        opener.open('http://m.weibo.cn/home/logout')  # 登出
        print('logout successful')
        curr_index = random.randint(0, len(constants.USERS)-1)
        while curr_index == self.CURR_USER_INDEX:
            curr_index = random.randint(0, len(constants.USERS)-1)
        self.CURR_USER_INDEX = curr_index
        print(constants.USERS[self.CURR_USER_INDEX]['username'] + " login")
        weibo_http.login(constants.USERS[self.CURR_USER_INDEX]['username'],
                         constants.USERS[self.CURR_USER_INDEX]['password'])
        weibo_http.change_header(opener)


    def get_comment_by_page(self, blog_id, page_num):
        url = 'http://m.weibo.cn/single/rcList?format=cards&id='
        req_url = url + str(blog_id) + '&type=comment&hot=0&page='+str(page_num)
        print('浏览器正在打开url：'+req_url)
        opener = weibo_http.make_my_opener()
        rsp = opener.open(req_url)
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

    def start(self):
        self.id_enqueue('2813742940', self.user_set_lock, self.CRAWLED_USERS, self.user_queue)

def main():
    my = WeiboCrawler("", "")
    my.start()

if __name__ == '__main__':
    main()
