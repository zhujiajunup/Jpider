# encoding=utf-8
import re
import datetime
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from Sina_spider1.items import InformationItem, TweetsItem, FollowsItem, FansItem, CommentItem, FlagItem
from Sina_spider1.constant import *
from Sina_spider1.settings import PROPERTIES
import ssl
import json

ssl._create_default_https_context = ssl._create_unverified_context


class Spider(CrawlSpider):
    name = "sinaSpider"
    host = "https://weibo.cn"
    start_urls = []  # PROPERTIES['users'] if PROPERTIES['users'] is not None else []
    weibos = []  # PROPERTIES['weibos'] if PROPERTIES['weibos'] is not None else []
    scrawl_ID = set(start_urls)  # 记录待爬的微博ID
    finish_ID = set()  # 记录已爬的微博ID
    comment_pattern = 'https://weibo.cn/comment/%s?page=%d'
    like_pattern = "https://m.weibo.cn/api/container/getSecond?" \
                   "containerid=100505%s_-_WEIBO_SECOND_PROFILE_LIKE_WEIBO&page=%d"
    tweets_pattern = "https://weibo.cn/%s/profile?page=%d"
    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'weibo.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    def start_requests(self):
        yield Request(url="https://weibo.com/47452014", )
        while self.scrawl_ID.__len__():
            ID = self.scrawl_ID.pop()
            self.finish_ID.add(ID)  # 加入已爬队列
            ID = str(ID)
            follows = []
            followsItems = FollowsItem()
            followsItems["_id"] = ID
            followsItems["follows"] = follows
            fans = []
            fansItems = FansItem()
            fansItems["_id"] = ID
            fansItems["fans"] = fans

            url_follows = "https://weibo.cn/2210643391/follow"  # url_follows = "http://weibo.cn
            like_url = self.like_pattern % (ID, 1)
            url_fans = "http://weibo.cn/%s/fans" % ID
            # url_tweets = "http://weibo.cn/%s/profile?page=1" % ID
            url_information0 = "http://weibo.cn/attgroup/opening?uid=%s" % ID

            meta_data = {"id": ID, "current_page": 1}
            # yield Request(url=url_follows, meta={"item": followsItems, "result": follows},
            #             callback=self.parse3)  # 去爬关注人
            # yield Request(url=url_fans, meta={"item": fansItems, "result": fans}, callback=self.parse3)  # 去爬粉丝
            # yield Request(url=url_information0, meta={"ID": ID}, callback=self.parse0)  # 去爬个人信息
            yield Request(url=self.tweets_pattern % (ID, 1), meta={"ID": ID, "current_page": 1},
                          dont_filter=True,
                          callback=self.parse_weibo,
                          headers=self.default_headers)  # 去爬微博
            # yield Request(url=like_url, meta=meta_data, callback=self.parse_weibo2)
            # yield Request(url=comment_url, meta={"weiboId": weibo_id}, callback=self.parse_comment)
        for weibo in self.weibos:
            yield Request(url=self.comment_pattern % (weibo, 1), meta={"weiboId": weibo, "current_page": 1},
                          dont_filter=True, callback=self.parse_comment, headers=self.default_headers)

    def parse_comment2(self, response):
        weiboId = response.meta['weiboId']
        selector = Selector(response)
        comments = selector.xpath('body/div[@class="c" and starts-with(@id, "C_")]')

        for c in comments:
            commentItem = CommentItem()
            commentItem['weibo_id'] = weiboId
            # print comments
            commentItem["user"] = c.xpath('a/text()').extract_first()
            user = c.xpath('span[@class="ctt"]/a/text()').extract_first()
            comments = c.xpath('span[@class="ctt"]/text()').extract()
            comments.insert(1, user if user else "")
            commentItem["content"] = ''.join(comments)

            others = c.xpath('span[@class="ct"]/text()').extract_first()
            if others:
                others = others.split(u"\u6765\u81ea")
                commentItem["time"] = others[0]
                if len(others) == 2:
                    commentItem["source"] = others[1]
            yield commentItem

    def parse_comment(self, response):

        weiboId = response.meta['weiboId']
        selector = Selector(response)
        max_page = selector.xpath('body/div[@id="pagelist"]/form/div/input[@name="mp"]/@value').extract_first()
        for page in range(1, int(max_page), 1):
            if page != 1:
                self.default_headers['Referer'] = self.comment_pattern % (weiboId, page-1)

            yield Request(url=self.comment_pattern % (weiboId, page), meta=response.meta,
                          callback=self.parse_comment2, headers=self.default_headers)

    def parse0(self, response):
        """ 抓取个人信息1 """
        informationItems = InformationItem()
        selector = Selector(response)
        text0 = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').extract_first()
        if text0:
            num_tweets = re.findall(u'\u5fae\u535a\[(\d+)\]', text0)  # 微博数
            num_follows = re.findall(u'\u5173\u6ce8\[(\d+)\]', text0)  # 关注数
            num_fans = re.findall(u'\u7c89\u4e1d\[(\d+)\]', text0)  # 粉丝数
            if num_tweets:
                informationItems["Num_Tweets"] = int(num_tweets[0])
            if num_follows:
                informationItems["Num_Follows"] = int(num_follows[0])
            if num_fans:
                informationItems["Num_Fans"] = int(num_fans[0])
            informationItems["_id"] = response.meta["ID"]
            url_information1 = "http://weibo.cn/%s/info" % response.meta["ID"]
            yield Request(url=url_information1, meta={"item": informationItems}, callback=self.parse1)

    def parse1(self, response):
        """ 抓取个人信息2 """
        informationItems = response.meta["item"]
        selector = Selector(response)
        text1 = ";".join(selector.xpath('body/div[@class="c"]/text()').extract())  # 获取标签里的所有text()
        nickname = re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', text1)  # 昵称
        gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)  # 性别
        place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)  # 地区（包括省份和城市）
        signature = re.findall(u'\u7b80\u4ecb[:|\uff1a](.*?);', text1)  # 个性签名
        birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?);', text1)  # 生日
        sexorientation = re.findall(u'\u6027\u53d6\u5411[:|\uff1a](.*?);', text1)  # 性取向
        marriage = re.findall(u'\u611f\u60c5\u72b6\u51b5[:|\uff1a](.*?);', text1)  # 婚姻状况
        url = re.findall(u'\u4e92\u8054\u7f51[:|\uff1a](.*?);', text1)  # 首页链接

        if nickname:
            informationItems["NickName"] = nickname[0]
        if gender:
            informationItems["Gender"] = gender[0]
        if place:
            place = place[0].split(" ")
            informationItems["Province"] = place[0]
            if len(place) > 1:
                informationItems["City"] = place[1]
        if signature:
            informationItems["Signature"] = signature[0]
        if birthday:
            try:
                birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                informationItems["Birthday"] = birthday - datetime.timedelta(hours=8)
            except Exception:
                pass
        if sexorientation:
            if sexorientation[0] == gender[0]:
                informationItems["Sex_Orientation"] = "gay"
            else:
                informationItems["Sex_Orientation"] = "Heterosexual"
        if marriage:
            informationItems["Marriage"] = marriage[0]
        if url:
            informationItems["URL"] = url[0]
        yield informationItems

    def parse_weibo2(self, response):
        json_data = json.loads(response.text)
        if response.meta['current_page'] == 1:
            response.meta['max_page'] = int(json_data['count']) / 10
        response.meta['current_page'] += 1

        def map_func(card):
            print card['mblog']['text']
        if 'cards' in json_data:
            map(map_func, json_data['cards'])
        if response.meta['current_page'] <= response.meta['max_page']:
            yield Request(url=self.like_pattern % (response.meta['id'], response.meta['current_page']),
                          meta=response.meta, callback=self.parse_weibo2)
        pass

    def parse_weibo1(self, response):
        selector = Selector(response)
        tweets = selector.xpath('body/div[@class="c" and @id]')
        for tweet in tweets:
            tweetsItem = TweetsItem()
            weibo_id = tweet.xpath('@id').extract_first()[2:]  # 微博ID
            cmts = tweet.xpath('div/span[@class="cmt"]').extract()
            if len(tweet.xpath('div/span[@class="cmt"]').extract()) > 2:
                r = tweet.xpath(u'div/span[text() = "转发理由:"]')
                content = r.xpath('./../text()').extract_first()
                like = re.findall(u'\u8d5e\[(\d+)\]', ','.join(r.xpath(u'./../a/text()').extract()))  # 点赞数
                transfer = re.findall(u'\u8f6c\u53d1\[(\d+)\]', ','.join(r.xpath(u'./../a/text()').extract()))  # 转载数
                comment = re.findall(u'\u8bc4\u8bba\[(\d+)\]', ','.join(r.xpath(u'./../a/text()').extract()))  # 评论数
                tweetsItem['Type'] = REPOST
                coordinates = None
            else:
                content = tweet.xpath('div/span[@class="ctt"]/text()').extract_first()  # 微博内容
                coordinates = tweet.xpath('div/a/@href').extract_first()  # 定位坐标
                tweetsItem['Type'] = ORIGINAL
                like = re.findall(u'\u8d5e\[(\d+)\]', tweet.extract())  # 点赞数
                transfer = re.findall(u'\u8f6c\u53d1\[(\d+)\]', tweet.extract())  # 转载数
                comment = re.findall(u'\u8bc4\u8bba\[(\d+)\]', tweet.extract())  # 评论数
            others = tweet.xpath('div/span[@class="ct"]/text()').extract_first()  # 求时间和使用工具（手机或平台）

            tweetsItem["ID"] = response.meta["ID"]

            tweetsItem["_id"] = response.meta["ID"] + "-" + weibo_id
            if content:
                tweetsItem["Content"] = content.strip(u"[\u4f4d\u7f6e]")  # 去掉最后的"[位置]"
            if coordinates:
                coordinates = re.findall('center=([\d|.|,]+)', coordinates)
                if coordinates:
                    tweetsItem["Coordinates"] = coordinates[0]
            if like:
                tweetsItem["Like"] = int(like[0])
            if transfer:
                tweetsItem["Transfer"] = int(transfer[0])
            if comment:
                tweetsItem["Comment"] = int(comment[0])
            if others:
                others = others.split(u"\u6765\u81ea")
                tweetsItem["PubTime"] = others[0]
                if len(others) == 2:
                    tweetsItem["Tools"] = others[1]

            # yield Request(url=comment_url, meta={"weiboId": weibo_id, "current_page": 1}, callback=self.parse_comment)
            yield tweetsItem

    def parse_weibo(self, response):
        """ 抓取微博数据 """
        selector = Selector(response)
        max_page = selector.xpath('body/div[@id="pagelist"]/form/div/input[@name="mp"]/@value').extract_first()
        if max_page:
            for page in range(1, int(max_page)):
                yield Request(url=self.tweets_pattern % (response.meta['ID'], page),
                              meta=response.meta, callback=self.parse_weibo1)
        else:
            return


    def parse3(self, response):
        """ 抓取关注或粉丝 """
        items = response.meta["item"]

        selector = Selector(response)
        # //table/ttbody/tr/td/a[text()="关注他" '
        # u'or text()="关注她"'
        #    u'or text()="取消关注"]/@href
        text2 = selector.xpath(
            u'//body/table/tr/td/a[text()="取消关注" or text()="关注她" or text()="关注他"]/@href').extract()
        # print '\n'.join(text2)
        # for elem in text2:
        #     elem = re.findall('uid=(\d+)', elem)
        #     if elem:
        #         response.meta["result"].append(elem[0])
        #         ID = int(elem[0])
        #         if ID not in self.finish_ID:  # 新的ID，如果未爬则加入待爬队列
        #             self.scrawl_ID.add(ID)
        # url_next = selector.xpath(
        #     u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        # if url_next:
        #     yield Request(url=self.host + url_next[0], meta={"item": items, "result": response.meta["result"]},
        #                   callback=self.parse3)
        # else:  # 如果没有下一页即获取完毕
        #     yield items
