import scrapy
import urllib.request

class OnePiece(scrapy.Spider):
    name = 'onepiece'
    start_urls = [
        'http://www.dlkoo.com/down/3/2015/368456186.html',
    ]
    base_dir = '/Users/didi/crawler/onepiece/'
    def parse(self, response):
        url = response.url
        link_list = response.xpath("//div[@id='dlinklist']").css("a::attr(href)").extract()
        torrent_url = 'http://www.dlkoo.com/down/downfile.asp?act=subb&n=%s/downfile2.asp?act=down&n=%s'

        for link in link_list:
            id = link.split("=")[1]

            urllib.request.urlretrieve(torrent_url % (id, id))

        pass
