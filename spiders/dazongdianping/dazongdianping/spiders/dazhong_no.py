
import random
import http.cookiejar
import urllib.request
import datetime
import sys
import os
import json
import django
from django.db import connection

sys.path.append('../../../../Jpider')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Jpider.settings'
django.setup()
from time import sleep
import traceback
from spiders.models import ShopId, ShopInfo
from lxml import etree
from spiders import user_agent

import queue
import threading



class Dazhong:

    def __init__(self):
        self.start_urls = [
            'http://www.dianping.com/search/category/2/10/g110', # 北京火锅
            'http://www.dianping.com/search/category/2/10/g107', # 北京台湾菜
            'http://www.dianping.com/search/category/2/10/g112', # 北京小吃快餐
            'http://www.dianping.com/search/category/2/10/g250', # 北京创意菜
            'http://www.dianping.com/search/category/2/10/g116', # 北京西餐
            'http://www.dianping.com/search/category/2/10/g113', # 北京日本菜
            'http://www.dianping.com/search/category/2/10/g103', # 北京粤菜
            'http://www.dianping.com/search/category/2/10/g115', # 北京东南亚菜
            'http://www.dianping.com/search/category/2/10/g102', # 北京川菜
            'http://www.dianping.com/search/category/1/10/g113', # 上海日本菜？？？
            'http://www.dianping.com/search/category/1/10/g110', # 上海火锅
            'http://www.dianping.com/search/category/1/10/g107', # 上海台湾菜
            'http://www.dianping.com/search/category/1/10/g103', # 上海粤菜
            'http://www.dianping.com/search/category/1/10/g102', # 上海川菜
            'http://www.dianping.com/search/category/1/10/g112', # 上海小吃快餐
            'http://www.dianping.com/search/category/1/10/g115', # 上海东南亚菜
            'http://www.dianping.com/search/category/1/10/g116',  # 上海西餐
            'http://www.dianping.com/search/category/1/10/g116',  # 上海西餐

        ]
        self.shop_queue = queue.Queue()
        self.feature_url_queue = queue.Queue()
        self.star_url_queue = queue.Queue()
        self.THREAD_NUM = 5
        self.index = 0
        self.proxies = [{"HTTP": "58.248.137.228:80"}, {"HTTP": "58.251.132.181:8888"}, {"HTTP": "60.160.34.4:3128"},
                        {"HTTP": "60.191.153.12:3128"}, {"HTTP": "60.191.164.22:3128"}, {"HTTP": "80.242.219.50:3128"},
                        {"HTTP": "86.100.118.44:80"}, {"HTTP": "88.214.207.89:3128"}, {"HTTP": "91.183.124.41:80"},
                        {"HTTP": "93.51.247.104:80"}]
        self.url_pattern = 'http://www.dianping.com/shop/%s/review_more_newest'
        self.spec_pattern = 'http://www.dianping.com/ajax/json/shopDynamic/searchPromo?shopId=%s&power=%s&cityId=%s&shopType=%s'
        self.star_pattern = 'http://www.dianping.com/ajax/json/shopDynamic/reviewAndStar?shopId=%s&cityId=%s&mainCategoryId=%s'
        self.init_thread()

    def init_thread(self):
        print('init  threads: %d' % self.THREAD_NUM)
        for i in range(self.THREAD_NUM):
            feature_thread = threading.Thread(target=self.crawl_feature, name='feature_thread_'+str(i+1))
            # star_thread = threading.Thread(target=self.crawl_star, name='star_thread_' + str(i + 1))
            feature_thread.start()
            # star_thread.start()
            # thread_shop = threading.Thread(target=self.crawl_shop, name='shop_thread_'+str(i))

            # thread_shop.start()
    def crawl_star(self):
        while True:
            star_url = self.star_url_queue.get()
            try:
                self.get_star(star_url)
                sleep(5)
            except Exception:
                print('-' * 50)
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                print(traceback.format_exc())
                self.star_url_queue.put(star_url)
                sleep(5*60)

    def crawl_shop(self):
        while True:
            url = self.shop_queue.get()
            try:
                self.get_shop_id(url)
            except Exception:
                self.shop_queue.put(url)
                print('-' * 50)
                print(traceback.format_exc())
                sleep(60)

    def crawl_feature(self):
        while True:
            feature_url = self.feature_url_queue.get()
            try:
                self.get_feature(feature_url)
                sleep(4)
            except Exception:
                self.feature_url_queue.put(feature_url)

                print('-' * 50)
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                print(traceback.format_exc())
                sleep(5* 60)

    def change_header(self, opener):
        head = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zdeprecatedh-CN,zh;q=0.8,en;q=0.6',
            'Host': 'www.dianping.com',
            'Proxy-Connection': 'keep-alive',
            'User-Agent': user_agent.agents[random.randint(0, len(user_agent.agents)-1)]

            # 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
            #           ' (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }


        header = []
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        opener.addheaders = header

    def change_proxy(self, opener):
        proxy_handler = urllib.request.ProxyHandler(self.proxies[self.index % self.proxies.__len__()])
        print("换代理了..."+str(self.proxies[self.index % self.proxies.__len__()]))
        self.index += 1
        if self.index >= 1000:
            self.index = 0
        # proxy_auth_handler = urllib.request.ProxyBasicAuthHandler()

        opener.add_handler(proxy_handler)

    def make_my_opener(self):
        """
        模拟浏览器发送请求
        :return:
        """
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        header = []
        head = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zdeprecatedh-CN,zh;q=0.8,en;q=0.6',
            'Host': 'www.dianping.com',
            'Proxy-Connection': 'keep-alive',
            'User-Agent': user_agent.agents[random.randint(0, len(user_agent.agents)-1)]

            # 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
            #           ' (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'
        }
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        opener.addheaders = header
        return opener

    def get_shop_id(self, url):
        print(url)
        opener = self.make_my_opener()
        rsp = opener.open(url)

        html_tree = etree.HTML(rsp.read().decode('utf-8'))

        shops_li = html_tree.xpath('//div[@id="shop-all-list"]/ul/li')

        for li in shops_li:
            href = li.xpath('./div[@class="pic"]/a/@href')

            if href != []:
                shopId = ShopId()
                shop_id = href[0][href[0].rindex('/') + 1:]
                shopId.shop_id = shop_id
                shopId.from_url = url
                shopId.save()
                print(shop_id + '\t' + url)
        print('_' * 40)

    def get_review(self):
        opener = self.make_my_opener()
        with connection.cursor() as cursor:
            cursor.execute("select shop_id from spiders_shopinfo where shop_id not in (select shop_id from spiders_reviewdedail)")
            rows = cursor.fetchall()
            for row in rows:
                url = self.url_pattern % row[0]
                print(url)
                self.change_proxy(opener)
                rsp = opener.open(url)

                print(rsp)




    def start2(self):
        opener = self.make_my_opener()
        for url in self.start_urls:
            print(url)
            url = url+'o3p%d'
            rsp = opener.open(url % 1)
            html_tree = etree.HTML(rsp.read().decode('utf-8'))
            max_page = int(html_tree.xpath('//div[@class="page"]/a/@data-ga-page')[-2])

            for i in range(1, max_page+1):

                rsp = opener.open(url % i)

                html_tree = etree.HTML(rsp.read().decode('utf-8'))



                shops_li = html_tree.xpath('//div[@id="shop-all-list"]/ul/li')

                for li in shops_li:
                    href = li.xpath('./div[@class="pic"]/a/@href')
                    print(href)
                    tit = li.xpath('./div[@class="txt"]/div[@class="tit"]/a/div[@class="promo-icon"]/text()')
                    print(tit)
                    if href != []:
                        shopId = ShopId()
                        shop_id = href[0][href[0].rindex('/')+1:]
                        shopId.shop_id = shop_id
                        shopId.save()
                        print(shop_id)
                print('_'*40)
                self.change_header(opener)
                # self.change_proxy(opener)

    def get_shop_info(self, url):
        opener = self.make_my_opener()
        rsp = opener.open(url)
        html_tree = etree.HTML(rsp.read().decode('utf-8'))

    def start(self):
        opener = self.make_my_opener()
        for url in self.start_urls:
            print(url)
            url = url+'o3p%d'
            rsp = opener.open(url % 1)
            html_tree = etree.HTML(rsp.read().decode('utf-8'))
            max_page = int(html_tree.xpath('//div[@class="page"]/a/@data-ga-page')[-2])

            for i in range(1, max_page+1):
                self.shop_queue.put(url % i)

            self.change_header(opener)
            # self.change_proxy(opener)


    def get_feature(self, url):
        print('get_feature:'+url)
        opener = self.make_my_opener()
        self.change_proxy(opener)
        rsp = opener.open(url)
        rsp_json = json.loads(rsp.read())
        shopInfo = ShopInfo.objects.get(shop_id = rsp_json['shopId'])
        tuan = rsp_json['tuan']
        features = []
        if tuan:
            features.append('团购')
        ding = rsp_json['ding']
        if ding:
            features.append('预定')
        wai = rsp_json['wai']
        if wai:
            features.append('外卖')
        cu = rsp_json['cu']
        if cu:
            features.append('促销')
        huo = rsp_json['huo']
        if huo:
            features.append('huo')
        guo = rsp_json['guo']
        if guo:
            features.append('guo')
        zuo = rsp_json['zuo']
        if zuo:
            features.append('zuo')
        piao = rsp_json['piao']
        if piao:
            features.append('piao')
        ka = rsp_json['ka']
        if ka:
            features.append('ka')
        print(url)
        with open('./features.txt', 'a') as f:
            f.write(str(rsp_json['shopId'])+'\t'+'\t'.join(features)+'\n')

        shopInfo.feature2 = ';'.join(features) if ';'.join(features) != '' else '无'
        shopInfo.save()
        opener.close()



    def get_star(self, url):
        print('get_star:'+url)
        opener = self.make_my_opener()
        rsp = opener.open(url)
        rsp_json = json.loads(rsp.read())
        shopInfo = ShopInfo.objects.get(shop_id=rsp_json['shopId'])

        star_all = rsp_json['totalReviewCount']
        star_1 = rsp_json['reviewCountStar1']
        star_2 = rsp_json['reviewCountStar2']
        star_3 = rsp_json['reviewCountStar3']
        star_4 = rsp_json['reviewCountStar4']
        star_5 = rsp_json['reviewCountStar5']
        shopInfo.star_all = star_all
        shopInfo.star_1 = star_1
        shopInfo.star_2 = star_2
        shopInfo.star_3 = star_3
        shopInfo.star_4 = star_4
        shopInfo.star_5 = star_5
        shopInfo.save()
        opener.close()
        sleep(2)

    def test(self):
        import re
        import json
        shop_config_pattern = re.compile(r'window.shop_config=(.*)')

        # shopCityId:(.*?),(.*?)cityId:(.*?),(.*?)power:(.*?), (.*?)shopType:(.*?),(.*?)mainCategoryId:(.*?),(.*)')
        info_pattern = re.compile(
            r'{(.*?)shopCityId:(\d),(.*?)cityId:(\d),(.*?)power:(\d)(.*)shopType:(\d)(.*)mainCategoryId:(\d)(.*)')
        # http://www.dianping.com/ajax/json/shopDynamic/searchPromo?shopId=10334671&power=5&cityId=1&shopType=10


        with connection.cursor() as cursor:
            cursor.execute('select shop_id from spiders_shopinfo where feature2 = ""')
            rows = cursor.fetchall()
            for row in rows:
                opener = self.make_my_opener()
                try:
                    print('opening http://www.dianping.com/shop/' + row[0])
                    rsp = opener.open('http://www.dianping.com/shop/'+row[0])
                except Exception:
                    print(traceback.format_exc())
                    sleep(5 * 60)

                    continue
                print('http://www.dianping.com/shop/'+row[0]+'  ok')
                html_tree = etree.HTML(rsp.read().decode('utf-8'))
                scripts = html_tree.xpath('//script/text()')
                for script in scripts:
                    content = script.strip().replace('\n', '').replace(' ', '')
                    # print(content)
                    # print('_'*10)
                    result = shop_config_pattern.findall(content)

                    if result != []:

                        info = info_pattern.findall(result[0])
                        if info != []:
                            info = info[0]
                            feature_url = self.spec_pattern % (row[0], info[5], info[3], info[7])
                            # http://www.dianping.com/ajax/json/shopDynamic/reviewAndStar?shopId=10334671&cityId=1&mainCategoryId=205
                            star_url = self.star_pattern % (row[0], info[3], info[9])

                            self.feature_url_queue.put(feature_url)
                            # self.star_url_queue.put(star_url)
                            break
                opener.close()

if __name__ == '__main__':

    dazhong = Dazhong()
    dazhong.test()
