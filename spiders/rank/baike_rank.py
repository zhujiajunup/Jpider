
import http.cookiejar
import urllib.request
from spiders import user_agent
import random
import json

class Rank():
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
            # 'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Host': 'baike.baidu.com',
            'Proxy-Connection': 'keep-alive',
            'User-Agent': user_agent.agents[random.randint(0, len(user_agent.agents) - 1)]

            # 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
            #           ' (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        opener.addheaders = header
        return opener

    def start(self):
        opener = self.make_my_opener()
        max_page = 50
        rsp = opener.open('http://baike.baidu.com/starflower/api/starflowerstarlist?rankType=thisWeek')

        rsp_json = json.loads(rsp.read().decode())

        print(rsp_json)
        for pn in range(1, max_page):

            rsp = opener.open('http://baike.baidu.com/starflower/api/starflowerstarlist?rankType=thisWeek&pg=%d' % pn)
            rsp_json = json.loads(rsp.read().decode())

            print(rsp_json)


if __name__ == '__main__':
    rank = Rank()
    rank.start()