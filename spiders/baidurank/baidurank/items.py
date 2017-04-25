# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from spiders.models import BaiKeRank
from scrapy_djangoitem import DjangoItem

class BaidurankItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BaiKeRankItem(DjangoItem):
    django_model = BaiKeRank