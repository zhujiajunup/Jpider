# -*- coding=utf-8 -*-
import requests
import json
import pyaudio
import wave
import logging
import logging.config
from logging.handlers import RotatingFileHandler
import ConfigParser
from multiprocessing import Lock
import os
import smtplib
import platform
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep
import traceback
import threading
from queue import Queue
import sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")

if not os.path.exists('./record'):
    os.makedirs('record')

if not os.path.exists('./log'):
    os.mkdir('log')

PLAY_TIME = 10
ordered = set()


def logger_conf():
    """
    load basic logger configure
    :return: configured logger
    """

    if platform.system() == 'Windows':

        logging.config.fileConfig(os.path.abspath('.')+'\\conf\\logging.conf')
    elif platform.system() == 'Linux':

        logging.config.fileConfig(os.path.abspath('.')+'/conf/logging.conf')
    elif platform.system() == 'Darwin':
        print(os.path.abspath('../../'))
        logging.config.fileConfig(os.path.abspath('.') + '/conf/logging.conf')
    logger = logging.getLogger('simpleLogger')

    return logger
LOGGER = logger_conf()


def get_conf():
    if not os.path.exists(r'.\conf\info.conf'):
        LOGGER.error('conf\info.conf does not exists! please create a folder named conf under this'
                      ' path %s and put a file named info.conf' % os.path.abspath('.'))
        exit(-1)
    LOGGER.info('get configure from %s\conf\info.conf' % os.path.abspath('.'))
    try:
        cf = ConfigParser.ConfigParser()
        cf.read(r'.\conf\info.conf')
        username = cf.get('user', 'username')
        password = cf.get('user', 'password')
        goods = cf.get('user', 'goods').split(' ')
        receives = cf.get('mail', 'to').split(' ')
        thread_num = int(cf.get('thread', 'thread_num'))
        timeout = float(cf.get('main', 'timeout'))
        sleep_time = int(cf.get('main', 'sleep'))
        LOGGER.info('configuration infomation:'
                     '\n\tusername:%s\n\tpassword:%s\n\tgood_ids:%s\n\tmail_to:%s\n\tthread_num:%d\n' %
                     (username, password, ','.join(goods), ','.join(receives), thread_num))
        return username, password, goods, receives, thread_num, timeout, sleep_time
    except Exception as e:
        LOGGER.error(traceback.format_exc())

username, password, goods, receives, thread_num, timeout, sleep_time = get_conf()

def send_email2(subject, text, to):
    LOGGER.info('send email')

    if not isinstance(to, list):
        LOGGER.error('input error, receive mail should a type of list, but get %s' % type(to))
        exit(-1)
    SERVER = 'smtp.163.com'
    FROM = 'u9334486fenpo3@163.com'
    LOGGER.info('from:%s\tto:%s' % (FROM, ','.join(to)))
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = FROM
    msg['To'] = ', '.join(to)
    part = MIMEText(text, 'plain', 'utf-8')
    msg.attach(part)
    server = smtplib.SMTP(SERVER, port=25)
    server.login(FROM, 'jvs7452014')
    server.sendmail(FROM, to, msg.as_string())
    server.quit()
    LOGGER.info('email send successful')


def notify():
    if not os.path.exists(r'.\notify.wav'):
        LOGGER.error('notify.wav does not exists! please put a wav file named notify.wav in %s' % os.path.abspath('.'))
        exit(-1)
    for _ in range(PLAY_TIME):
        chunk = 1024
        wf = wave.open(r'.\notify.wav', 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # 写声音输出流进行播放
        while True:
            data = wf.readframes(chunk)
            if data == b'':
                break
            stream.write(data)
        stream.close()
        p.terminate()


def login(username, password):
    LOGGER.info('login    username:%s\tpassword:%s' % (username, password))
    login_url = 'https://www.pangxieyg.com/mobile/index.php?act=login'
    rsp = requests.post(login_url, data={'username': username,
                                         'password': password,
                                         'client': 'wap'}, timeout=timeout)
    rsp_json = json.loads(str(rsp.content))
    LOGGER.info('login successful')
    return rsp_json


def buy_step1(cookies, good_id):
    buy_step1_url = 'https://www.pangxieyg.com/mobile/index.php?act=member_buy&op=buy_step1'
    data = dict(
        key=cookies['key'],
        cart_id='%s|%s' % (good_id, '1'),
        ifcart='',
        address_id='',
        type='5'
    )
    rsp = requests.post(buy_step1_url, data=data, cookies=cookies, timeout=timeout)
    rsp_json = json.loads(str(rsp.content))
    return rsp_json


def buy_step2(step1_json, cookies, good_id):
    buy_step2_url = 'https://www.pangxieyg.com/mobile/index.php?act=member_buy&op=buy_step2'
    rsp_json = step1_json
    address_api = rsp_json['datas']['address_api']
    address_info = rsp_json['datas']['address_info']
    store_cart_list = rsp_json['datas']['store_cart_list']
    store_final_total_list = rsp_json['datas']['store_final_total_list']

    voucher_tmp = []
    for k, v in store_cart_list.items():
        store_voucher_info = v['store_voucher_info']
        if len(store_voucher_info) == 0:
            voucher_tmp.append('undefined|' + str(k) + '|undefined')
    pay_message_tmp = []
    for k, v in store_final_total_list.items():
        pay_message_tmp.append(str(k) + '|')

    data = dict(
        key=cookies['key'],
        ifcart='',
        cart_id='%s|%s' % (good_id, '1'),
        address_id=address_info['address_id'],
        vat_hash=rsp_json['datas']['vat_hash'],
        offpay_hash=address_api['offpay_hash'],
        offpay_hash_batch=address_api['offpay_hash_batch'],
        pay_name='online',
        invoice_id='0',
        voucher=','.join(voucher_tmp),
        pd_pay='0',
        password='',
        fcode='',
        return_bank='',
        return_account='',
        return_account_user='',
        return_bank_addr='',
        rcb_pay='0',
        rpt='',
        fbcart='',
        pay_message=','.join(pay_message_tmp)
    )
    requests.post(buy_step2_url, data=data, cookies=cookies, timeout=timeout)



good_detail = 'https://www.pangxieyg.com/mobile/index.php?act=goods&op=goods_detail&goods_id=%s'
good_detail_page_url = 'https://www.pangxieyg.com/wap/tmpl/product_detail.html?goods_id=%s&goods_promotion_type=5'

goods_queue = Queue(maxsize=100)
ordered_lock = Lock()
for g in goods:
    f = open('./record/%s_%s.txt' % (g, datetime.datetime.now().strftime('%Y-%m-%d')), 'a')
    f.close()
    goods_queue.put(g)

while True:
    try:
        rsp_json = login(username, password)
        if 'datas' in rsp_json:
            break
    except Exception as e:
        LOGGER.error(traceback.format_exc())
        sleep(sleep_time)
cookies = dict(username=rsp_json['datas']['username'], key=rsp_json['datas']['key'])


def monitor(good_id):
    LOGGER.info('--'*4 + 'get good id: %s' % good_id + '--'*4)
    try:
        LOGGER.info('open url: %s ' % (good_detail % good_id))
        good_detail_rsp = requests.get(good_detail % good_id, cookies=cookies, timeout=timeout)
        good_detail_rsp_json = json.loads(str(good_detail_rsp.content))
        if good_detail_rsp_json['code'] == 200:
            good_name = good_detail_rsp_json['datas']['goods_info']['goods_name']
        else:
            LOGGER.error(good_detail % good_id + ' failed')
            return
        LOGGER.info('buy step1: %s' % good_id)
        rsp_json = buy_step1(cookies, good_id)
        good_name = good_name.encode('utf-8')
        if 'error' in rsp_json['datas']:

            LOGGER.info(u'%s(%s):%s' % (good_name, good_id, rsp_json['datas']['error']))
        else:
            with open('./record/%s_%s.txt' % (good_id, datetime.datetime.now().strftime('%Y-%m-%d')), 'a') as f:
                f.write('%s\t%s\t有货啦\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), good_name))

            if good_id in ordered:

                LOGGER.info(u"%s[%s] 有货，已下单" % (good_name, good_id))

            else:
                LOGGER.info(u'buy step2:%s[%s]' % (good_name, good_id))
                # buy_step2(rsp_json, cookies, good_id)
                # LOGGER.info(u'%s[%s]购买成功了，快到订单界面付款吧！！！！' % (good_name, good_id))
                with ordered_lock:
                    ordered.add(good_id)
                send_email2(u'【螃蟹云购】有库存啦', u'商品名：%s\n商品id:%s\n商品链接:%s\n' %
                            (good_name, good_id, good_detail_page_url % good_id), receives)
                notify()
    except Exception as e:

        LOGGER.error(traceback.format_exc())
    finally:
        goods_queue.put(good_id)
        LOGGER.info('--' * 4 + 'put good id back: %s' % good_id + '--' * 4)


def worker():
    while True:
        good_id = goods_queue.get()
        monitor(good_id)

for i in range(thread_num):
    t = threading.Thread(target=worker, name='pangxie-thread-%d' % i)
    t.start()


