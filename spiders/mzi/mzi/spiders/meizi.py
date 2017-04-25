import scrapy
import re
import os
import urllib.request

class Meizi(scrapy.Spider):
    name = 'mzi'
    # allowed_domains = ['http://www.mzitu.com/']
    start_urls = [
        'http://www.mzitu.com/'
    ]
    href_pattern = re.compile('<a href="(.*?)" target="_blank">(.*?)</a>')
    base_dir = '/Users/didi/crawler/mzi/'

    def parse(self, response):

        header_hrefs = response.css('ul.menu li a::attr(href)').extract()
        for ref in header_hrefs:
            print(ref)
            yield scrapy.Request(ref, callback=self.parse_classify)

    def parse_classify(self, response):
        pic_hrefs = response.css('div.postlist ul li a::attr(href)').extract()
        for href in pic_hrefs:
            yield scrapy.Request(url=href, callback=self.parse_detail)

        max_page = int(response.css('a.page-numbers::text').extract()[-2])
        base_url = (response.url if response.url.endswith('/') else response.url+'/') + 'page/'
        for pn in range(max_page+1):
            yield scrapy.Request(url=base_url+str(pn), callback=self.parse_classify)

    def parse_detail(self, response):
        title = response.css('div.main-image img::attr(alt)').extract()[0]
        if not os.path.exists(self.base_dir+title):
            os.mkdir(self.base_dir+title)

        img_src = response.css('div.main-image img::attr(src)').extract()[0]
        img_path = self.base_dir+title+'/'+img_src[img_src.rindex('/')+1:]
        urllib.request.urlretrieve(img_src, img_path)
        max_page = int(response.css('div.pagenavi a span::text').extract()[-2])

        base_url = response.url if response.url.endswith('/') else response.url+'/'
        for pn in range(max_page+1):
            yield scrapy.Request(base_url+str(pn), callback=self.parse_detail)

        print(img_path)

