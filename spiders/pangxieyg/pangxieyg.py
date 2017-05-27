import urllib
import urllib.request
import http.cookiejar
# from . import user_agent
import random
class PangXie:
    def make_opener(self):
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        header = []
        head = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Length': '254',
            'Host': 'www.pangxieyg.com',

            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            # 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML,'
            #           ' like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        opener.addheaders = header
        return opener

if __name__ == '__main__':
    px = PangXie()
    opener = px.make_opener()
    opener.open('http://www.pangxieyg.com/wap/')
