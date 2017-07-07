import requests


def send_request():
    result = requests.get('http://music.163.com/')
    print(result.text)

send_request()