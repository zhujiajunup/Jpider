# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SERVER = 'smtp.163.com'
FROM = 'jjzhu_ncu@163.com'
TO = ['767543579@qq.com']

SUBJECT = u'测试UTF8编码'
TEXT = u'ABCDEFG一二三四五六七'

msg = MIMEMultipart('alternative')
# 注意包含了非ASCII字符，需要使用unicode
msg['Subject'] = SUBJECT
msg['From'] = FROM
msg['To'] = ', '.join(TO)
part = MIMEText(TEXT, 'plain', 'utf-8')
msg.attach(part)

server = smtplib.SMTP(SERVER, port=25)
server.login(FROM, 'vs7452014')
server.sendmail(FROM, TO, msg.as_string().encode('ascii'))
server.quit()