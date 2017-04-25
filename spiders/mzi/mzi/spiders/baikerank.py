import scrapy
import json
class BaikeRank(scrapy.Spider):
    name = 'baikerank'
    start_urls = [
        'http://baike.baidu.com/starflower/api/starflowerstarlist?rankType=thisWeek'
    ]

    def parse(self, response):
        rt = json.loads(response.body())
        print('_'*50)
        print(rt)