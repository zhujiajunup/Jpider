from wxpy import *
bot = Bot()


class Wechat(object):
    def __init__(self):
        self.group = bot.groups().search('English exam')[0]
        self.my_friends = [bot.friends().search('jopper')[0]]

    def send(self, msg):
        self.group.send(msg)

    def send2(self, msg):
        for f in self.my_friends:
            f.send(msg)
