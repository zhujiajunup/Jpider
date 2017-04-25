import scrapy
import json
from ..items import ShopInfoItem, ReviewDetailItem, ShopIdItem
from spiders.user_agent import agents
import traceback
from django.db import connection

class Dazong(scrapy.Spider):
    name = 'dazongdianping'
    count = 0
    start_urls = [
        'http://www.dianping.com/search/category/2/10/g103',
        # 'http://www.dianping.com/search/category/2/10/g107',
        # 'http://www.dianping.com/search/category/2/10/g112',
        # 'http://www.dianping.com/search/category/2/10/g115',
        # 'http://www.dianping.com/search/category/2/10/g116',
        # 'http://www.dianping.com/search/category/2/10/g250',
        # 'http://www.dianping.com/search/category/2/10/g113',
        # 'http://www.dianping.com/search/category/2/10/g110',
        # 'http://www.dianping.com/search/category/1/10/g102',
        # 'http://www.dianping.com/search/category/1/10/g107',
    ]

    custom_settings = {
        'LOG_FILE': 'dazongdianping.log',
    }
    root_url = 'http://www.dianping.com'
    save_dir = '/Users/didi/crawler/dazhongdianping/'
    url_pattern = 'http://www.dianping.com/shop/%s'


    # def start_requests(self):
    #     with connection.cursor() as cursor:
    #         cursor.execute("select shop_id from spiders_shopid where shop_id not in (select shop_id from spiders_shopinfo)")
    #         rows = cursor.fetchall()
    #         for row in rows:
    #             url = self.url_pattern % row[0]
    #             yield scrapy.Request(url, callback=self.parse_detail)

    def start_requests(self):
        with connection.cursor() as cursor:
            # where shop_id not in (select shop_id from spiders_shopinfo)")
            cursor.execute("select shop_id from spiders_shopid where shop_id not in (select shop_id from spiders_shopinfo)")
            rows = cursor.fetchall()
            for row in rows:
                url = self.url_pattern % row[0]
                yield scrapy.Request(url, callback=self.parse_detail)

    def parse(self, response):
        yield scrapy.Request(response.url, callback=self.parse_pg)
        pages = int(response.css('div.page a::text').extract()[-2])
        for pg in range(1, pages+1):
            print(response.url + 'p' + str(pg))
            yield scrapy.Request(response.url + 'p' + str(pg), callback=self.parse_pg)

    def parse_pg(self, response):
        print(response.url)
        shops = response.css('div.content div.shop-list li')
        for s in shops:
            shop_id_item = ShopIdItem()
            short_url = s.css('div.tit a::attr(href)').extract()[0].strip()
            shop_url = self.root_url+short_url
            shop_id = short_url.split('/')[2]

            shop_id_item['shop_id'] = shop_id

            shop_id_item.save()

            self.count += 1
            yield scrapy.Request(shop_url, callback=self.parse_detail)
        self.logger.error('total count %d' % self.count)

    def parse_detail(self, response):
        print(response.url)

        shop_id = response.url[response.url.rindex('/')+1:]


        basic_info = response.css('div.basic-info')

        closed_class = basic_info.css('p.shop-closed').extract()

        if closed_class != []:  # 未营业
            shop_info = ShopInfoItem()
            shop_info['shop_id'] = shop_id
            shop_name = basic_info.css('h1.shop-name::text').extract()[0].strip()
            shop_info['shop_name'] = shop_name
            shop_info.save()
            self.logger.error('%s 未营业' % response.url)
            return None
        try:
            rank_star = basic_info.css('div.brief-info span.mid-rank-stars::attr(title)').extract()[0].strip()
            shop_name = basic_info.css('h1.shop-name::text').extract()[0].strip()
            review_count = basic_info.css('div.brief-info').xpath('./span/text()').extract()[0].strip()
            avg_price = basic_info.css('div.brief-info').xpath('./span[@id="avgPriceTitle"]/text()').extract()[0].strip()
            comment_score = basic_info.css('div.brief-info').xpath('./span[@id="comment_score"]').css('span.item::text').extract()
            address = basic_info.css('div.address').xpath('./span[@itemprop="street-address"]/text()').extract()[0].strip()
            info_indent = basic_info.css('div.other p.info')

            print(basic_info.css('div.promosearch-wrapper').extract())
            tuan = basic_info.css('div.promosearch-wrapper p.expand-info').css('span.info-name::text').extract()

            print('-'*10+str(tuan)+'-'*10)

            breadcrumb = response.css('div.breadcrumb')
            bars = breadcrumb.css('a::text').extract()
            if len(bars) >= 3:

                place = bars[1].strip()
                classify = bars[2].strip()
            else:
                place = ''
                classify = ''


            open_time = ''
            for ind in info_indent:
                # print(ind.css('span.info-name::text').extract())
                if ind.css('span.info-name::text').extract()[0].strip().startswith('营业时间'):
                    open_time = ind.css('span.item::text').extract()[0].strip()
                    break

            # print(shop_id+'\t'+shop_name+'\t'+review_count+'\t'+avg_price+'\t'+str(comment_score)+'\t'+str(address)+'\t'+open_time)
            shop_info = ShopInfoItem()
            shop_info['shop_id'] = shop_id
            shop_info['shop_name'] = shop_name
            shop_info['review_count'] = review_count
            shop_info['avg_price'] = avg_price
            shop_info['address'] = address
            shop_info['open_time'] = open_time
            shop_info['taste'] = comment_score[0]
            shop_info['env'] = comment_score[1]
            shop_info['service'] = comment_score[2]
            shop_info['rank_star'] = rank_star
            shop_info['place'] = place
            shop_info['classify'] = classify
            shop_file = open(self.save_dir + 'shop/' + str(shop_id) + '.html', 'w')
            shop_file.write(response.body.decode('utf-8'))
            shop_info.save()
            yield scrapy.Request(response.url+'/review_more_newest', callback=self.parse_review)
        except Exception:
            self.logger.error(response.url+' exception')
            self.logger.error(traceback.format_exc())

    def parse_review(self, response):
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
