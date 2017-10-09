# encoding=utf-8
import os
from items import CommentItem, TweetsItem, FlagItem, FansItem


class FilePipeline(object):
    FILE_CACHE = {}

    def process_item(self, item, spider):

        if isinstance(item, CommentItem):
            f = self.FILE_CACHE[item['weibo_id']]
            f.write('%s\t%s\t%s\t%s\n' % (item['user'], item['content'], item['source'] if 'source' in item else '', item['time']))
        if isinstance(item, TweetsItem):
            path = './' + item['ID']
            if not os.path.exists(path):
                os.makedirs(path)
            f = open(path + '/' + item['_id'].split('-')[1]+'.txt', 'a')
            self.FILE_CACHE[item['_id'].split('-')[1]] = f
            f.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (item['Content'], item['PubTime'], item['Tools'],
                                                  item['Comment'], item['Like'], item['Transfer']))
        if isinstance(item, FlagItem):
            f = self.FILE_CACHE[item['weibo_id']]
            f.close()
            del self.FILE_CACHE[item['weibo_id']]
# class MongoDBPipeline(object):
#     def __init__(self):
#         clinet = pymongo.MongoClient("localhost", 27017)
#         db = clinet["Sina"]
#         self.Information = db["Information"]
#         self.Tweets = db["Tweets"]
#         self.Follows = db["Follows"]
#         self.Fans = db["Fans"]
#
#     def process_item(self, item, spider):
#         """ 判断item的类型，并作相应的处理，再入数据库 """
#         if isinstance(item, InformationItem):
#             try:
#                 self.Information.insert(dict(item))
#             except Exception:
#                 pass
#         elif isinstance(item, TweetsItem):
#             try:
#                 self.Tweets.insert(dict(item))
#             except Exception:
#                 pass
#         elif isinstance(item, FollowsItem):
#             followsItems = dict(item)
#             follows = followsItems.pop("follows")
#             for i in range(len(follows)):
#                 followsItems[str(i + 1)] = follows[i]
#             try:
#                 self.Follows.insert(followsItems)
#             except Exception:
#                 pass
#         elif isinstance(item, FansItem):
#             fansItems = dict(item)
#             fans = fansItems.pop("fans")
#             for i in range(len(fans)):
#                 fansItems[str(i + 1)] = fans[i]
#             try:
#                 self.Fans.insert(fansItems)
#             except Exception:
#                 pass
#         return item
