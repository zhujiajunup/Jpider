from celery import Celery

redis_host = '127.0.0.1'
redis_port = 6379
app = Celery('crawl_task', include=['tasks'], broker='redis://%s:%d/1' % (redis_host, redis_port),
             backend='redis://%s:%d/2' % (redis_host, redis_port))
app.conf.update(
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
)
