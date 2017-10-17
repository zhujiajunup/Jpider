# -*- coding:utf-8 -*-
"""
2015-01-16 by Camel
https://github.com/daoluan/WXSender-Python/ is acknowledged

"""
import requests
import hashlib
import re
import time


class WeiXin:

    def __init__(self):
        # 公众号登陆账号密码
        self.unm = "silence.v@foxmail.com"
        self.pwd = "Jvs7452014@jjzhu"
        self.token = ''
        self.fakeid = ''
        # 字典存储用户与fakeid的关系
        self.users = {}
        self.msg2user_capable = {}
        # session自动处理cookies
        self.session = requests.Session()

    def login(self):
        """登陆"""
        headers = {
            "Host": "mp.weixin.qq.com",
            "Referer": "https://mp.weixin.qq.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
        }
        data = {
            "username": self.unm,
            "pwd": hashlib.md5(self.pwd.encode('utf-8')).hexdigest(),
            "imgcode": '',
            "f": "json"
        }
        url_login = "https://mp.weixin.qq.com/cgi-bin/login"
        r_login = self.session.post(url_login, data=data, headers=headers)
        print(r_login)
        try:
            self.token = re.findall("token=(\d*)", r_login.content)[0]
            print("token ", self.token)
            if self.token != '':
                print("login success and get token!")
                # 登陆之后转入首页，可去掉
                url_index = "https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=%s" % self.token
                r_index = self.session.get(url_index)
                if r_index.status_code == 200:
                    print("get the index")
                else:
                    print("get index failed")
            else:
                print("login failed")
        except:
            print("get token error")

    def get_fakeid(self):
        """得到自己的fakeid"""
        url_fakeid = "https://mp.weixin.qq.com/cgi-bin/settingpage?t=setting/index&action=index&token=%s&lang=zh_CN" % self.token
        r_fakeid = self.session.get(url_fakeid)
        try:
            self.fakeid = re.findall("fakeid=(\d{10})", r_fakeid.content)[0]
            print("get fakeid ", self.fakeid)
        except:
            print("get fakeid error")

    def get_users(self):
        """微信更改网址，推荐用users_capable
           得到用户昵称和对应fakeid，写入users字典"""
        url_user = "https://mp.weixin.qq.com/cgi-bin/contactmanage?t=user/index&pageidx=0&type=0&token=%s&lang=zh_CN" % self.token
        r_user = self.session.get(url_user)
        total_users = int(re.findall("totalCount : '(\d*)'", r_user.content)[0])
        page_count = int(re.findall("pageCount : (\d*)", r_user.content)[0])
        page_size = int(re.findall("pageSize : (\d*),", r_user.content)[0])
        user_ids = []
        user_names = []
        for pageidx in range(page_count):
            url_userpage = "https://mp.weixin.qq.com/cgi-bin/contactmanage?t=user/index&pageidx=%s&type=0&token=%s&lang=zh_CN" % (
                str(pageidx), self.token)
            r_userid = self.session.get(url_userpage)
            thepage_user = re.findall("\"id\":\"(.*?){28}\"", r_userid.content)
            thepage_username = re.findall(
                "\"nick_name\":\"(.*?)\"", r_userid.content)
            user_ids += thepage_user
            user_names += thepage_username
        self.users = dict(zip(user_names, user_ids))
        print("get users done")

    def get_users_capable(self):
        url_msgusers = "https://mp.weixin.qq.com/cgi-bin/message?t=message/list&action=&keyword=&offset=0&count=%d&day=7&filterivrmsg=&token=%s&lang=zh_CN"
        r_msgusers = self.session.get(url_msgusers % (20, self.token))
        print(r_msgusers)
        total_msg = int(re.findall(r'total_count : (\d*)', r_msgusers.content)[0])
        r_allmsgusers = self.session.get(url_msgusers % (total_msg,self.token))
        fakeid = re.findall(r"\"fakeid\":\"(.*?){28}\"", r_allmsgusers.content)
        nick_name = re.findall(r"\"nick_name\":\"(.*?)\"", r_allmsgusers.content)
        date_time = map(int, re.findall(r"\"date_time\":(\d*)", r_allmsgusers.content))
        now = time.time()
        less_than_48h = [i for i in date_time if now-i < 172800]
        msg_capable = len(less_than_48h)
        fakeid_capable = list(set(fakeid[:msg_capable]))
        nick_name_capable = list(set(nick_name[:msg_capable]))
        self.msg2user_capable = dict(zip(nick_name_capable, fakeid_capable))
        print("get users_capable done")

    def msg2user(self, msg, touserid):
        """发送消息给单个指定用户"""
        url_msg = "https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&f=json&token=%s&lang=zh_CN" % self.token
        msg_headers = {
            "Host": "mp.weixin.qq.com",
            "Origin": "https://mp.weixin.qq.com",
            "Referer": "https://mp.weixin.qq.com/cgi-bin/singlesendpage?t=message/send&action=index&tofakeid=%s&token=%s&lang=zh_CN" % (touserid, self.token),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
        }
        msg_data = {
            "token": self.token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
            "random": "0.4469808244612068",
            "type": "1",
            "content": msg,
            "tofakeid": touserid,
            "imgcode": ''
        }
        r_msg = self.session.post(url_msg, data=msg_data, headers=msg_headers)
        if r_msg.status_code == 200:
            err_msg = re.findall("\"err_msg\":\"(.*?)\"", r_msg.content)[0]
            # 发送成功
            if err_msg == 'ok':
                print("send msg %s to %s done" % (msg,touserid))
            # 微信限制，用户48小时内没有主动发送消息，则公众号无法发送消息给该用户
            elif err_msg == 'customer block':
                print("denied because the user hasn't send msg to you in the past 48 hours")
            else:
                print("failed,", err_msg)
        else:
            print("send msg to %s failed,and the err_msg %s" % (touserid, r_msg.status_code))

    def msg2users(self, msg):
        for user in self.msg2user_capable:
            self.msg2user(msg, self.msg2user_capable[user])

    def send2user(self, msg, touser):
        """msg : str
           touser : 用户的昵称"""
        self.login()
        self.get_fakeid()
        self.get_users_capable()
        if touser in self.msg2user_capable:
            print("user %s exists" % touser)
            self.msg2user(msg, self.msg2user_capable[touser])
        else:
            print("user %s not exists" % touser)

    def send2users(self, msg):
        self.login()
        self.get_fakeid()
        self.get_users_capable()
        self.msg2users(msg)

wx = WeiXin()
wx.send2user('test测试', 'jopper') # 'Camel'是我的昵称，请替换成自己的
## wx.send2users('test测试二')
