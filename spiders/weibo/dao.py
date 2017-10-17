from spiders.models import Weibo, WeiboUser, UserRelationship
from spiders.logger import LOGGER
from django.db.models import Q

def save_blog_info( blog_info):

    try:
        # 存在就更新，不存在就创建
        weibo = Weibo.objects.get(pk=blog_info['id'])
    except Weibo.DoesNotExist:
        weibo = Weibo()
    weibo.id = str(blog_info['id'])
    weibo.created_timestamp = blog_info['created_at']
            # self.user_enqueue(ret_weibo.user.id)
    weibo.source = blog_info['source']
    weibo.text = blog_info['text']
    try:
        user = WeiboUser.objects.get(pk=blog_info['user']['id'])
    except WeiboUser.DoesNotExist:
        user = save_user_info(blog_info['user'])
    weibo.user = user
    weibo.save()
    LOGGER.info(weibo)
    if weibo.retweented_status is not None:  # 添加关系

        try:
            r = UserRelationship.objects.get(Q(user=weibo.retweented_status.user) & Q(follower=weibo.user))
            LOGGER.info('relationship already exist:' + str(r))
        except UserRelationship.DoesNotExist:
            LOGGER.info('relationship not exist')
            relation = UserRelationship()
            relation.user = weibo.retweented_status.user
            relation.follower = weibo.user
            LOGGER.info(relation)
            relation.save()
    return weibo


def save_user_info( user_info):
    try:
        user = WeiboUser.objects.get(pk=user_info['id'])
    except WeiboUser.DoesNotExist:
        user = WeiboUser()
        user.id = user_info['id']

    user.attNum = user_info['attNum'] if 'attNum' in user_info \
        else user_info['follow_count'] if 'follow_count' in user_info \
        else ''
    user.created_at = user_info['created_at'] if 'created_at' in user_info else ''
    user.screen_name = user_info['screen_name'] if 'screen_name' in user_info else ''
    user.description = user_info['description'] if 'description' in user_info else ''
    user.fansNum = user_info['fansNum'] if 'fansNum' in user_info \
        else user_info['followers_count'] if 'followers_count' in user_info \
        else ''
    user.mblogNum = user_info['mblogNum'] if 'mblogNum' in user_info \
        else user_info['statuses_count'] if 'statuses_count' in user_info \
        else ''
    user.nativePlace = user_info['nativePlace'] if 'nativePlace' in user_info else ''
    user.profile_url = user_info['profile_url'] if 'profile_url' in user_info else ''
    user.gender = WeiboUser.GENDER.index(user_info['gender'] if 'gender' in user_info else 'u')
    user.save()

    LOGGER.info(user)
    return user


def save_relationship(user, fan):
    try:
        r = UserRelationship.objects.get(Q(user=user) & Q(follower=fan))
        LOGGER.info('relationship already exist:' + str(r))
    except UserRelationship.DoesNotExist:
        LOGGER.info('relationship not exist')
        relation = UserRelationship()
        relation.user = user
        relation.follower = fan
        LOGGER.info(relation)
        relation.save()


def insert_pic_info(self, pic_info):
    pass


def insert_comment_info(self, comment_info):
    pass


def save_pic(self):
    url = 'http://ww2.sinaimg.cn/large/c0788b86jw1f2xfstebzaj20dc0hst9r.jpg'
    # opener = my_http.make_my_opener()
    # rsp = opener.open(url)
    # pic_data = rsp.read()
    # try:
    #     file = open("d:\\weibo_pic\\1.jpg", 'wb')
    #     file.write(pic_data)
    #     file.close()
    # except FileNotFoundError:
    #     os.mkdir("d:\\weibo_pic")
    # except FileExistsError:
    #     pass