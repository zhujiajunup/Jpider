# -*- coding:utf-8 -*-
import scrapy
from scrapy.http import Request
import datetime
from ..items import ZjuItem


class ZjuSpider(scrapy.Spider):
    name = 'zju'
    url = 'http://grs.zju.edu.cn'
    url2 = 'http://grs.zju.edu.cn/redir.php?catalog_id=16313'
    url3 = 'http://grs.zju.edu.cn/redir.php?catalog_id=16313&page=1'
    notified = set()

    def start_requests(self):
        #  ield Request(self.url, dont_filter=True, callback=self.parse)
        yield Request(self.url2, dont_filter=True, callback=self.parse2)
        yield Request(self.url3, dont_filter=True, callback=self.parse2)

    def parse2(self, response):
        lis = response.xpath('//ul[@id="artphs"]/li')
        for li in lis:
            c_url = self.url + '/' + li.xpath('h3/a/@href').extract_first()
            title = li.xpath('h3/a/@title').extract_first()
            time = li.xpath('span/text()').extract_first()
            publish_time = datetime.datetime.strptime(time, '%Y-%m-%d')
            now = datetime.datetime.now()

            if (now - publish_time).days < 1:
                if c_url not in self.notified:
                    zju_item = ZjuItem()
                    zju_item['url'] = c_url
                    zju_item['title'] = title
                    zju_item['time'] = time
                    self.notified.add(c_url)
                    yield zju_item
        yield Request(self.url2, dont_filter=True, callback=self.parse2)
        yield Request(self.url3, dont_filter=True, callback=self.parse2)

    def parse(self, response):

        lis = response.xpath('//ul[@id="arthd"]/li')
        datetime.datetime.strptime('2017-06-01', '%Y-%m-%d')
        for li in lis:
            c_url = self.url + '/' + li.xpath('a/@href').extract_first()
            title = li.xpath('a/@title').extract_first()
            time = li.xpath('span[@class="art-date"]/text()').extract_first()

            publish_time = datetime.datetime.strptime(time,  '%Y-%m-%d')
            now = datetime.datetime.now()

            if(now - publish_time).days < 1:
                if c_url not in self.notified:
                    zju_item = ZjuItem()
                    zju_item['url'] = c_url
                    zju_item['title'] = title
                    zju_item['time'] = time
                    self.notified.add(c_url)
                    yield zju_item
        yield Request(self.url, dont_filter=True, callback=self.parse)
