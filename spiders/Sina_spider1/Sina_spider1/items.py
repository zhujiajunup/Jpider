# encoding=utf-8

from scrapy import Item, Field


class InformationItem(Item):
    """ 个人信息 """
    _id = Field()  # 用户ID
    NickName = Field()  # 昵称
    Gender = Field()  # 性别
    Province = Field()  # 所在省
    City = Field()  # 所在城市
    Signature = Field()  # 个性签名
    Birthday = Field()  # 生日
    Num_Tweets = Field()  # 微博数
    Num_Follows = Field()  # 关注数
    Num_Fans = Field()  # 粉丝数
    Sex_Orientation = Field()  # 性取向
    Marriage = Field()  # 婚姻状况
    URL = Field()  # 首页链接


class FlagItem(Item):
    weibo_id = Field()


class CommentItem(Item):
    weibo_id = Field()
    id = Field()  # 评论id
    user = Field()  # 评论用户
    content = Field()  # 评论内容
    source = Field()  # 评论来源
    time = Field()  # 评论发表时间

    def __str__(self):
        return self['user'] + "\t"+self['content']+"...\t"+self['time']


class TweetsItem(Item):
    """ 微博信息 """
    _id = Field()  # 用户ID-微博ID
    ID = Field()  # 用户ID
    Content = Field()  # 微博内容
    PubTime = Field()  # 发表时间
    Coordinates = Field()  # 定位坐标
    Tools = Field()  # 发表工具/平台
    Like = Field()  # 点赞数
    Comment = Field()  # 评论数
    Transfer = Field()  # 转载数

    def __str__(self):
        return '--------------------------------------------------------------------------\n' \
            '|\t用户\t|\t\t微博\t\t|\t来源\t|\t发布时间\t|\t微博id\t|\n' \
            '------------------------------------------------------------------------------\n' \
            '|%s\t|\t%s\t|\t%s\t|\t%s\t|\t%s\t|\n' \
            '------------------------------------------------------------------------------\n'\
            % (self["ID"], self["Content"][:20], self["Tools"] if 'Tools' in self else '', self['PubTime'], self['_id'])



class FollowsItem(Item):
    """ 关注人列表 """
    _id = Field()  # 用户ID
    follows = Field()  # 关注


class FansItem(Item):
    """ 粉丝列表 """
    _id = Field()  # 用户ID
    fans = Field()  # 粉丝
