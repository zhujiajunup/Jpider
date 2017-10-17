# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .myemail import Email
from .wechat import Wechat


class ZjuPipeline(object):
    wc = Wechat()

    def process_item(self, item, spider):
        msg = item['title'] + '\n' + item['url'] + '\n' + item['time']
        self.wc.send(msg)

        e = Email()
        e.content_from = 'jjzhu_ncu@163.com'
        e.content_to = 'jjzhu_zju@163.com'
        e.content_pwd = 'jvs7452014'
        e.content_subject = u'浙大研究生官网发布新消息啦！'
        e.content_msg = item['title'] + '\n' + item['url'] + '\n' + item['time']
        e.send_163()

        return item
