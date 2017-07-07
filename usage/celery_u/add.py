from celery_u.tasks import add
print(add.delay(3, 3).get(timeout=1))
