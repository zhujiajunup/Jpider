from dao.redis_cookies import RedisCookies
from model.models import User, Relationship, CrawlInfo
from dao.sqlalchemy_session import db_session
from sqlalchemy.sql import exists
from logger import LOGGER
from tasks.workers import app
from headers import get_header, get_header2
import requests
from bs4 import BeautifulSoup
import re
import json
from time import sleep
import traceback
import datetime
INFO_MAP = {
    '昵称': 'nickname',
    '真实姓名': 'realname',
    '所在地': 'location',
    '性别': 'gender',
    '性取向': 'sexual_ori',
    '感情状况': 'emotion_state',
    '生日': 'birthday',
    '血型': 'blood_type',
    '博客': 'blog',
    '个性域名': 'domain_name',
    '简介': 'intro',
    '注册时间': 'register_time',
    '邮箱': 'email',
    '公司': 'company',
    '大学': 'college',
    '高中': 'high_school',
    '初中': 'mid_school',
    '标签': 'tags',

}


@app.task
def info(user_id):
    sleep(5)
    base_home_url = 'http://weibo.com/p/100505%s/info?mod=pedit_more' % user_id
    LOGGER.info('info task: %s' % base_home_url)
    cookies_json = RedisCookies.fetch_cookies()
    cookies = cookies_json['cookies']
    headers = get_header()
    headers['Host'] = 'weibo.com'
    headers['Referer'] = 'http://weibo.com/u/%s?refer_flag=1005050006_&is_hot=1' % user_id
    # 'http://weibo.com/2606356035/fans?from=100505&wvr=6&mod=headfans&current=fans'
    headers['Upgrade-Insecure-Requests'] = 1
    headers.pop('Connection')
    headers.pop('Accept')
    headers['Proxy-Connection'] = 'keep-alive'
    try_time = 0
    info_html = ''
    info_html_str = ''
    while try_time < 10:
        resp_text = requests.get(url=base_home_url, headers=headers, cookies=cookies, verify=False).text
        view_json = find_fm_view_json(html=resp_text)
        for r_json in view_json:
            if 'Pl_Official_PersonalInfo__58' == r_json['domid']:
                info_html_str = r_json['html']
                break
        if info_html_str != '':
            info_html = BeautifulSoup(info_html_str, 'html.parser')
            iframe = info_html.find_all('iframe')
            if not iframe:
                break
        try_time += 1



    if info_html != '':
        user = User()
        user.user_id = user_id
        if not db_session.query(exists().where(User.user_id == user_id)).scalar():
            db_session.add(user)
            db_session.commit()
        lis = info_html.find_all('li', 'clearfix')
        info_dict = {}
        for li in lis:
            try:
                title = li.find('span', 'pt_title').text
                pt_detail = li.find('span', 'pt_detail')
                all_a = pt_detail.find_all('a')
                if all_a:
                    detail = ','.join([a.text for a in all_a])
                else:
                    detail = pt_detail.text

                detail = detail.replace('\n', '').replace('\t', '').replace('\r', '')

                value = INFO_MAP.get(title[:-1], None)
                if value:
                    info_dict[value] = detail
            except:

                LOGGER.error('info task error: %s' % traceback.format_exc())
                continue
        app.send_task('tasks.user.fans', args=(user_id,))
        if info_dict:
            LOGGER.info('info task result: %s' % info_dict)
            try:
                db_session.query(User).filter(User.user_id == user_id).update(info_dict)
                db_session.commit()
            except:
                db_session.rollback()
                LOGGER.error('info task error: %s' % traceback.format_exc())
        return info_dict
    return None

def find_fm_view_json(html):
    resp_html = BeautifulSoup(html, 'html.parser')
    scripts = resp_html.find_all('script')
    scripts.reverse()
    fm_view_pattern = re.compile('FM.view\((.*)\)')
    view_jsons = []
    for script in scripts:
        r = fm_view_pattern.findall(script.string)
        if len(r):
            view_jsons.append(json.loads(r[0]))
    return view_jsons


@app.task(ignore_result=True)
def fans(user_id):

    if db_session.query(exists().where(CrawlInfo.user_id == user_id)).scalar():
        return
    sleep(3)
    pages = 10
    curr_page = 1
    result = []
    get_pages = False
    while curr_page <= pages:
        curr_page += 1
        page_url = 'http://weibo.com/p/100505%s/follow?pids=Pl_Official_HisRelation__60&relate=fans&page=%d' \
                   '#Pl_Official_HisRelation__60' % (user_id, curr_page)
        while True:
            cookies_json = RedisCookies.fetch_cookies()
            cookies = cookies_json['cookies']
            if cookies_json['unique_id'] != user_id:
                break
        LOGGER.info('login user: %s' % cookies_json['user_name'])
        LOGGER.info('fans task: %s' % page_url)
        resp_text = requests.get(page_url, cookies=cookies, headers=get_header2()).text
        view_json = find_fm_view_json(html=resp_text)

        for j in view_json:
            if 'Pl_Official_HisRelation__60' == j['domid']:
                fans_html_str = j['html']
                break
        else:
            LOGGER.warn('fans  tasks: not found ')

            continue
        fans_html = BeautifulSoup(fans_html_str, 'html.parser')
        follow_list = fans_html.find('ul', 'follow_list')
        user_id_pattern = re.compile('id=(\d*?)&refer_flag=(\d*?)_')
        if follow_list:
            txt_as = follow_list.find_all('a', 'S_txt1')
            for a in txt_as:
                r = {'href': a.get('href'), 'name':a.text, 'usesrcard':a.get('usercard')}
                result.append(r)
                find_result = user_id_pattern.findall(a.get('usercard'))
#                 LOGGER.info("fans info: %s" % str(r))
                if find_result:

                    fans_user_id = find_result[0][0]
                    if not db_session.query(exists().where(
                            Relationship.user_id == user_id
                            and Relationship.fan_id == fans_user_id)).scalar():
                        relationship = Relationship()
                        relationship.user_id = user_id
                        relationship.fan_id = fans_user_id
                        db_session.add(relationship)
                        db_session.commit() 

                    app.send_task('tasks.user.info', args=(fans_user_id, ))
                    

        if not get_pages:
            pages_as = fans_html.find_all('a', 'page')
            if pages_as:
                get_pages = True
                pages = int(pages_as[-2].text)
            else:
                break


    crawl_info = CrawlInfo()
    crawl_info.user_id = user_id
    crawl_info.last_crawl_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db_session.add(crawl_info)
    db_session.commit()



