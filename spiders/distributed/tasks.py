import requests
from bs4 import BeautifulSoup
from workers import app


@app.task
def crawl(url):
    print 'crawl url:{}'.format(url)
    rsp_test = requests.get(url).text
    soup = BeautifulSoup(rsp_test, 'html.parser')
    return soup.find('h1').text

