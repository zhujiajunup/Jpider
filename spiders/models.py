from django.db import models

# Create your models here.


class ShopId(models.Model):
    shop_id = models.CharField(max_length=20, primary_key=True)
    from_url = models.CharField(max_length=200, null=True)


class BaiKeRank(models.Model):
    rank = models.IntegerField(max_length=20, null=True)
    name = models.CharField(max_length=50, null=True)
    ori_score = models.CharField(max_length=50, null=True)
    rank_time = models.CharField(max_length=20)

    def __str__(self):
        return str(self.rank) +'\t' + self.name + '\t' + self.ori_score


class ShopInfo(models.Model):
    shop_id = models.CharField(max_length=20, primary_key=True)
    shop_name = models.CharField(max_length=200, default='')
    review_count = models.CharField(max_length=20, default='')
    avg_price = models.CharField(max_length=20, default='')
    taste = models.CharField(max_length=10, default='')
    env = models.CharField(max_length=10, default='')
    service = models.CharField(max_length=10, default='')
    address = models.CharField(max_length=200, default='')
    open_time = models.CharField(max_length=200, default='')
    rank_star = models.CharField(max_length=20, default='')
    place = models.CharField(max_length=20, default='')
    classify = models.CharField(max_length=20, default='')
    star_all = models.CharField(max_length=20, default='')
    star_5 = models.CharField(max_length=20, default='')
    star_4 = models.CharField(max_length=20, default='')
    star_3 = models.CharField(max_length=20, default='')
    star_2 = models.CharField(max_length=20, default='')
    star_1 = models.CharField(max_length=20, default='')
    feature = models.BooleanField(default=False)
    feature2 = models.CharField(max_length=200, default='')


class ReviewDedail(models.Model):
    shop_id = models.CharField(max_length=20, primary_key=True)
    star_all = models.CharField(max_length=20, null=True)
    star_5 = models.CharField(max_length=20, null=True)
    star_4 = models.CharField(max_length=20, null=True)
    star_3 = models.CharField(max_length=20, null=True)
    star_2 = models.CharField(max_length=20, null=True)
    star_1 = models.CharField(max_length=20, null=True)
    first_review_time = models.CharField(max_length=100, null=True)
    first_review_content = models.TextField(null=True)


class WeiboUser(models.Model):
    GENDER = ('m', 'f', 'u')
    id = models.CharField(max_length=12, primary_key=True)  # 用户id
    profile_url = models.CharField(max_length=400, null=True)  # url
    description = models.CharField(max_length=1000, null=True)  # 简介
    created_at = models.CharField(max_length=100, null=True)  # 创建时间
    screen_name = models.CharField(max_length=100, null=True)  # 昵称
    nativePlace = models.CharField(max_length=10, null=True)  # 所在地
    mblogNum = models.CharField(max_length=20, null=True)  # 微博数
    attNum = models.CharField(max_length=20, null=True)  # 关注数
    fansNum = models.CharField(max_length=20, null=True)  # 粉丝数
    gender = models.IntegerField(choices=enumerate(GENDER), null=True)  # 性别

    def __str__(self):
        return '\n\t'+'user: ' + self.screen_name + '\n\t'+'id: '+str(self.id)+'\n\t'\
               + '昵称:'+self.screen_name + '\n\t'+'微博数:'+str(self.mblogNum)+'\n\t'+'关注:'+str(self.attNum)


class UserRelationship(models.Model):
    user = models.ForeignKey(WeiboUser, related_name='user')
    follower = models.ForeignKey(WeiboUser, related_name='follower')

    class Meta:
        unique_together = ('user', 'follower')
    primary = ('user', 'follower')

    def __str__(self):
        return self.follower.screen_name +'--->'+self.user.screen_name


class Weibo(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    user = models.ForeignKey(WeiboUser)
    text = models.TextField(null=False)
    created_timestamp = models.IntegerField(null=True)
    retweented_status = models.ForeignKey('self', null=True)
    source = models.CharField(max_length=200, null=True)

    def __str__(self):
        return '\n\t'+'user:'+self.user.screen_name+'\n\t'+'blog_id:'+self.id


class BilibiliMovie(models.Model):
    id = models.IntegerField(primary_key=True)
    arcurl = models.URLField()
    author = models.CharField(max_length=255)
    description = models.TextField()
    favorites = models.CharField(max_length=100)
    video_review = models.CharField(max_length=100)
    play = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)

    def __str__(self):
        return "id:%d\ttitle:%s\t播放量:%s\t收藏数:%d\t评论数:%d" % \
               (self.id, self.title, self.play, self.favorites, self.video_review)


