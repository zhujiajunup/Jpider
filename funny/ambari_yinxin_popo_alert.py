# -*- coding:utf-8 -*-
__doc__ = """
        ambari alert by yixin & popo
        """
import sys
import requests
import ConfigParser

netease_alert_url = 'https://master.mail.netease.com/omnew/alert/sendMultiAlert'
conf_path = './alert.conf'


def send_alert(data):
    if isinstance(data, dict):
        requests.post(url=netease_alert_url, json=data)


def main():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    data = {}
    type = int(cf.get('main', 'type'))
    product = cf.get('main', 'product')
    data['product'] = product
    data['type'] = type
    # get message from ambari alert
    definitionName = sys.argv[1]
    definitionLabel = sys.argv[2]
    serviceName = sys.argv[3]
    alertState = sys.argv[4]
    alertText = sys.argv[5]
    alert_msg = "definitionName:%s\ndefinitionLabel:%s\nserviceName:%s\nalertState:%s\nalertText:%s\n" % \
                (definitionName, definitionLabel, serviceName, alertState, alertText)

    if type >> 3 == 1:  # send by yixin
        type &= 7
        mobile = cf.get('main', 'mobile')
        data['mobile'] = mobile
        data['yixinMsg'] = alert_msg

    if type >> 2 == 1:  # duanxin
        type &= 3
        mobile = cf.get('main', 'mobile')
        data['mobile'] = mobile
        data['mobileMsg'] = alert_msg

    if type >> 1 == 1:  # email
        type &= 1
        account = cf.get('main', 'account')
        data['account'] = account
        data['emailMsg'] = alert_msg
        data['subject'] = cf.get('main', 'subject')

    if type == 1:  # popo
        data['account'] = cf.get('main', 'account')
        data['popoMsg'] = alert_msg

    send_alert(data=data)

main()
