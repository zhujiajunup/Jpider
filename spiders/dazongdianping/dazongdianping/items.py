# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from spiders.models import ShopInfo, ReviewDedail, ShopId
from scrapy_djangoitem import DjangoItem

class DazongdianpingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ShopInfoItem(DjangoItem):
    django_model = ShopInfo

class ReviewDetailItem(DjangoItem):
    django_model = ReviewDedail

class ShopIdItem(DjangoItem):
    django_model = ShopId