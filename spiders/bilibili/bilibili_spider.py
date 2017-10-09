import requests
import json
import sys
import os
import django

sys.path.append('../../../Jpider')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Jpider.settings'
django.setup()
from spiders.models import BilibiliMovie

search_url = 'https://s.search.bilibili.com/cate/search'
tag_url = 'https://api.bilibili.com/x/tag/hots'
curr_page = 1
t_params = dict(
    rid=145,
    type=0,
    jsonp='jsonp'
)
q_params = dict(
    main_ver='v3',
    search_type='video',
    view_type='hot_rank',
    pic_size='160x100',
    order='hot',
    copy_righ='-1',
    cate_id=145,
    page=curr_page,
    pagesize=20,
    keyword='恐怖'
)
req = requests.get(url=tag_url, params=t_params, verify=False)
req_json = json.loads(req.text)
tags = req_json['data'][0]['tags']
for tag in tags:
    print(tag)
    q_params['keyword'] = tag['tag_name']
    req = requests.get(url=search_url, params=q_params, verify=False)
    req_json = json.loads(req.text)
    pages = req_json['numPages']
    for r in req_json['result']:
        movie = BilibiliMovie()
        movie.arcurl = r['arcurl']
        movie.author = r['author']
        movie.description = r['description']
        movie.favorites = r['favorites']
        movie.play = r['play']
        movie.video_review = r['video_review']
        movie.tag = r['tag']
        movie.title = r['title']
        movie.id = r['id']
        movie.save()
        print(movie)
    curr_page += 1
    while curr_page <= pages:
        q_params['page'] = curr_page
        req = requests.get(url=search_url, params=q_params, verify=False)
        req_json = json.loads(req.text)
        for r in req_json['result']:
            movie = BilibiliMovie()
            movie.arcurl = r['arcurl']
            movie.author = r['author']
            movie.description = r['description']
            movie.favorites = r['favorites']
            movie.play = r['play']
            movie.video_review = r['video_review']
            movie.tag = r['tag']
            movie.title = r['title']
            movie.id = r['id']
            movie.save()
            print(movie)
        curr_page += 1
