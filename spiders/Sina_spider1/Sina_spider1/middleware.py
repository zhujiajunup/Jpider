# encoding=utf-8
import random
from cookies import cookies
from user_agents import agents
import logging

class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
    """ 换Cookie """

    def process_request(self, request, spider):
        cookie = random.choice(cookies)
        logging.info("use cookie %s" % cookie)
        request.cookies = cookie
