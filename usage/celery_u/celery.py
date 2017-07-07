from celery import Celery

app = Celery('celery_u',
             broker='redis://:''@127.0.0.1:6379/0',
             backend='redis://:''@127.0.0.1:6379/1',
             include=['celery_u.tasks']
)
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_ROUTES={
        'celery.taks.add': {'qqueue': 'hipri'}
    }
)

if __name__ == '__main__':
    app.start()
