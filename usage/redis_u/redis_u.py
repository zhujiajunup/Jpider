__author__ = 'jjzhu'
import redis

r = redis.StrictRedis(db=0)
print(r.get('foo'))

