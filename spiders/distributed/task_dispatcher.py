from workers import app

crawl_urls = [
    'http://docs.celeryproject.org/en/latest/getting-started/introduction.html',
    'http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html',
    'http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html',
    'http://docs.celeryproject.org/en/latest/getting-started/next-steps.html',
    'http://docs.celeryproject.org/en/latest/getting-started/resources.html',
    'http://docs.celeryproject.org/en/latest/userguide/application.html',
    'http://docs.celeryproject.org/en/latest/userguide/tasks.html',
    'http://docs.celeryproject.org/en/latest/userguide/canvas.html',
    'http://docs.celeryproject.org/en/latest/userguide/workers.html',
    'http://docs.celeryproject.org/en/latest/userguide/daemonizing.html',
    'http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html'
]


def manage_crawl_task(urls):
    for url in urls:
        app.send_task('tasks.crawl', args=(url,))

if __name__ == '__main__':
    manage_crawl_task(crawl_urls)
