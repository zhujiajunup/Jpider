import scrapy
import json
from ..items import BaiKeRankItem
import datetime
class BaiduRank(scrapy.Spider):
    name = 'baidurank'
    start_urls = [
        'http://baike.baidu.com/starflower/api/starflowerstarlist?rankType=thisWeek'
    ]
    url_p = 'http://baike.baidu.com/starflower/api/starflowerstarlist?rankType=thisWeek&pg=%d'
    max_page = 50
    curr_page = 1
    curr_time = ''
    def start_requests(self):
        self.curr_time = datetime.datetime.now()
        for url in self.start_urls:
            yield self.make_requests_from_url(url)
        for pg in range(1, 50):
            yield self.make_requests_from_url(self.url_p % pg)

    def parse(self, response):

        rt = json.loads(response.body)

        this_week = rt['data']['thisWeek']
        for record in this_week:
            baike_rank = BaiKeRankItem()
            baike_rank['rank'] = str(record['rank'])
            baike_rank['name'] = record['name']
            baike_rank['ori_score'] = str(record['oriScore'])
            baike_rank['rank_time'] = self.curr_time.strftime('%Y-%m-%d %H:%M:%S')
            baike_rank.save()
            print(str(record['rank'])+'\t'+record['name']+'\t'+str(record['oriScore']))

