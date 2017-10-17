from scrapy import cmdline

cmdline.execute("scrapy crawl sinaSpider".split())
# import yaml
# f = open('./Sina_spider1/conf/weibo.yaml')
# print yaml.load(f)