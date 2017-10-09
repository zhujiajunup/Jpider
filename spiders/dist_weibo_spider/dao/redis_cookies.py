#-*- coding:utf-8 -*-
import redis
import json
import datetime

class RedisCookies(object):
    redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

    @classmethod
    def save_cookies(cls, user_name, unique_id, cookies):
        pickled_cookies = json.dumps({
            'cookies': cookies,
            'unique_id': unique_id,
            'login_time': datetime.datetime.now().timestamp()
        })
        r = redis.Redis(connection_pool=cls.redis_pool)
        r.hset('account', user_name, pickled_cookies)
        cls.user_in_queue(user_name)

    @classmethod
    def user_in_queue(cls, user_name):
        r = redis.Redis(connection_pool=cls.redis_pool)
        if not r.sismember('users', user_name):
            r.sadd("users", user_name)

    @classmethod
    def fetch_cookies(cls):
        r = redis.Redis(connection_pool=cls.redis_pool)
        user = r.spop('users')
        r.sadd('users', user)
        return r.hget('account', user).decode('utf-8')
