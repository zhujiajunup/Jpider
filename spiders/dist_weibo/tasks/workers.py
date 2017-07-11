# coding:utf-8
import os
from celery import platforms
from celery import Celery
# root权限启动
platforms.C_FORCE_ROOT = True

get_broker_or_backend = ('redis://:''@127.0.0.1:6379/0', 'redis://:''@127.0.0.1:6379/1')

worker_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__))+'/logs', 'celery.log')
beat_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__))+'/logs', 'beat.log')

tasks = ['tasks.login', 'tasks.home_page']
app = Celery('weibo_task', include=tasks, broker=get_broker_or_backend[0], backend=get_broker_or_backend[1])