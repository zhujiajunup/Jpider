# coding: utf-8
from wxpy import *
from wechat_sender import *

bot = Bot()
my_friend = bot.friends().search('jopper')[0]
my_friend.send('hello')
group = bot.groups().search('Team of single dogs')[0]
group.send('send from python, for test\n zhujiajunup@163.com')

