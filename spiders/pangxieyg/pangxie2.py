# -*- edcoding=utf-8 -*-
import requests
import json
import pyaudio
import wave
import logging
from logging.handlers import RotatingFileHandler
import ConfigParser
import os
import traceback

PLAY_TIME = 10


def logger():
    logging.basicConfig(
        level=logging.DEBUG,  # 设置日志级别
        # 设置日志输出格式
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        # 设置时间格式
        datefmt='%Y-%m-%d %H:%M:%S',
        # 设置日志输出文件名
        filename='my.log',
        # 设置文件读写方式
        filemode='w')
    # 设置StreamHandler
    console = logging.StreamHandler()
    # 设置输出日志级别
    console.setLevel(logging.DEBUG)
    rotating_handler = RotatingFileHandler(
        'my.log',  # 设置输出日志文件名
        maxBytes=10 * 1024 * 1024,  # 指定每个日志文件的大小（字节），这里是10M
        backupCount=10  # 指定备份的日志文件数
    )
    rotating_handler.setLevel(logging.DEBUG)  # 设置级别
    formatter = logging.Formatter(
        fmt='%(asctime)s  %(name)-12s: %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    rotating_handler.setFormatter(formatter)
    # 可以通过addHandler添加其他的处理方式
    logging.getLogger('').addHandler(rotating_handler)

    console.setFormatter(fmt=formatter)
    logging.getLogger('').addHandler(console)


def notify():
    if not os.path.exists(r'.\notify.wav'):
        logging.error('notify.wav does not exists! please put a wav file named notify.wav in %s' % os.path.abspath('.'))
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


def get_conf():
    try:
        cf = ConfigParser.ConfigParser()

        cf.read(r'.\conf\info.conf')

        username = cf.get('user', 'username')
        password = cf.get('user', 'password')
        goods = cf.get('user', 'goods').split(' ')
        return username, password, goods
    except Exception, e:
        logging.error(e.message)
logger()


def login(username, password):
    login_url = 'https://www.pangxieyg.com/mobile/index.php?act=login'
    rsp = requests.post(login_url, data={'username': username,
                                         'password': password,
                                         'client': 'wap'})
    rsp_json = json.loads(str(rsp.content))
    logging.info('login....username:%s\tpassword:%s' % (username, password))
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
    rsp = requests.post(buy_step1_url, data=data, cookies=cookies)
    rsp_json = json.loads(str(rsp.content))
    return rsp_json


def buy_step2(step1_json, cookies):
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
    for k, v in store_final_total_list:
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
    rsp = requests.post(buy_step2_url, data=data, cookies=cookies)
    rsp_json = json.loads(str(rsp.content))
    logging.info('购买成功过，快到订单界面付款吧！！！！')

username, password, goods = get_conf()
good_id = goods[0]
buy_goods_url = 'https://www.pangxieyg.com/wap/tmpl/order/buy_step2.html?goods_id=%s&buynum=1&type=5' % good_id
good_detail = 'https://www.pangxieyg.com/mobile/index.php?act=goods&op=goods_detail&goods_id=%s' % good_id

# login_url = 'https://www.pangxieyg.com/mobile/index.php?act=login'
# username = '13486178520'
# password = 'vs7452014'
# rsp = requests.post(login_url, data={'username': username,
#                                      'password': password,
#                                      'client': 'wap'})
# rsp_json = json.loads(str(rsp.content))
rsp_json = login(username, password)


cookies = dict(username=rsp_json['datas']['username'], key=rsp_json['datas']['key'])
# rsp = requests.get('https://www.pangxieyg.com/mobile/index.php?act=goods&op=calc&goods_id=117892&area_id=175')
# rsp = requests.post('https://www.pangxieyg.com/mobile/index.php?'
#                     'act=member_order&op=order_list&page=10&curpage=1',
#                     data={'key': cookies['key'], 'state_type': '', 'order_key': ''},
#                     cookies=cookies)
# rsp_json = json.loads(str(rsp.content))
# if len(rsp_json['datas']['order_group_list']) > 0:
#     print rsp_json['datas']['order_group_list'][0]['order_list'][0]['extend_order_goods'][0]['goods_name']
# data = dict(
#     key=cookies['key'],
#     cart_id='%s|%s' % (good_id, '1'),
#     ifcart='',
#     address_id='',
#     type='5'
# )
# rsp = requests.post(buy_step1, data=data, cookies=cookies)
# rsp_json = json.loads(str(rsp.content))
# rsp_json = buy_step1(cookies, good_id)
# buy_step2(rsp_json, cookies)
# print rsp_json['datas']['address_api']
# address_api = rsp_json['datas']['address_api']
# address_info = rsp_json['datas']['address_info']
# store_cart_list = rsp_json['datas']['store_cart_list']
# store_final_total_list = rsp_json['datas']['store_final_total_list']
#
# voucher_tmp = []
# for k, v in store_cart_list.items():
#     store_voucher_info = v['store_voucher_info']
#     if len(store_voucher_info) == 0:
#         voucher_tmp.append('undefined|'+str(k)+'|undefined')
# pay_message_tmp = []
# for k, v in store_final_total_list:
#     pay_message_tmp.append(str(k)+'|')
#
# data = dict(
#     key=cookies['key'],
#     ifcart='',
#     cart_id='%s|%s' % (good_id, '1'),
#     address_id=address_info['address_id'],
#     vat_hash=rsp_json['datas']['vat_hash'],
#     offpay_hash=address_api['offpay_hash'],
#     offpay_hash_batch=address_api['offpay_hash_batch'],
#     pay_name='online',
#     invoice_id='0',
#     voucher=','.join(voucher_tmp),
#     pd_pay='0',
#     password='',
#     fcode='',
#     return_bank='',
#     return_account='',
#     return_account_user='',
#     return_bank_addr='',
#     rcb_pay='0',
#     rpt='',
#     fbcart='',
#     pay_message=','.join(pay_message_tmp)
# )
# rsp = requests.post(buy_step2, data=data, cookies=cookies)


for _ in range(2):
    rsp_json = buy_step1(cookies, good_id)
    if 'error' in rsp_json['datas']:
        print rsp_json['datas']['error']
    else:
        buy_step2(rsp_json, cookies)
        notify()

