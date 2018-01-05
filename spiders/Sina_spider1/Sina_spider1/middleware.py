# encoding=utf-8
import random
from cookies import cookies
from user_agents import agents
import logging
import re

class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class RefererMiddleware(object):
    page_pattern = re.compile('https://weibo.cn/(.*?)\?page=(\d+)')

    def process_request(self, request, spider):

        if 'Referer' in request.headers:
            page_result = self.page_pattern.findall(request.url)
            if len(page_result) == 1:
                curr_page = int(page_result[0][1]) - 1
                request.headers['Referer'] = 'https://weibo.cn/%s?page=%d' % (page_result[0][0], curr_page)
        print request.url
        print request.headers
        print request.cookies
        print request.headers['Referer'] if 'Referer' in request.headers else ''


class CookiesMiddleware(object):
    """ 换Cookie """

    def process_request(self, request, spider):
        cookie = random.choice(cookies)
        logging.info("use cookie %s" % cookie)
        request.cookies = cookie
