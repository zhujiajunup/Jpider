import scrapy
from spiders.models import ShopInfo, ReviewDedail
from django.db import connection
import traceback
from ..items import ReviewDetailItem
from spiders.user_agent import agents
import random

class DazongRepair(scrapy.Spider):
    name = 'dazongrepair'

    url_pattern = 'http://www.dianping.com/shop/%s/review_more_newest#start=10'
    shop_url_p = 'http://www.dianping.com/shop/%s'

    def start_requests(self):
        with connection.cursor() as cursor:
            cursor.execute("select shop_id from spiders_shopinfo where shop_id not in (select shop_id from spiders_reviewdedail)")
            rows = cursor.fetchall()
            for row in rows:
                url = self.url_pattern % row[0]
                referer = self.shop_url_p % row[0]
                header = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip,deflate,sdch',
                    'Accept-Language': 'zdeprecatedh-CN,zh;q=0.8,en;q=0.6',
                    'Host': 'www.dianping.com',

                    'User-Agent': random.choice(agents),
                    'Referer': referer,
                }


                yield scrapy.Request(url, callback=self.parse, headers=header)

    def parse(self, response):
        print(response.url)
        review_detail = ReviewDetailItem()
        try:
            shop_id = response.url.split('/')[-2]
            main_body = response.css('div.main')
            comment_tab = main_body.css('div.comment-tab span')
            cnt = '0'
            for c_t in comment_tab:
                title = c_t.css('a::text').extract()[0]
                if title.strip() == '全部点评':
                    cnt = c_t.css('em.col-exp::text').extract()[0].strip()[1:-1]
                    break
            if cnt == '0':
                review_detail['shop_id'] = shop_id
                review_detail['star_all'] = 0
                review_detail.save()
                self.logger.error('%s - %s: %s' % (response.url, '全部点评', cnt))
                print('%s - %s: %s' % (response.url, '全部点评', cnt))
                return None

            stars = main_body.css('div.comment-mode div.comment-star span em.col-exp::text').extract()
            first_review_time = main_body.css('div.comment-mode div.comment-list ul li span.time::text').extract_first().strip()
            first_review_content = main_body.css('div.comment-mode div.comment-list div.comment-txt div::text').extract_first().strip()
            review_detail['first_review_time'] = first_review_time
            review_detail['first_review_content'] = first_review_content
            review_detail['star_all'] = stars[0][1:-1]
            review_detail['star_5'] = stars[1][1:-1]
            review_detail['star_4'] = stars[2][1:-1]
            review_detail['star_3'] = stars[3][1:-1]
            review_detail['star_2'] = stars[4][1:-1]
            review_detail['star_1'] = stars[5][1:-1]
            review_detail['shop_id'] = shop_id
            review_detail.save()
            print(shop_id+'\t'+str(stars)  + '\t' + first_review_time)
        except Exception:
            self.logger.error(traceback.format_exc())

