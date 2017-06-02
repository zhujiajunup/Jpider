import smtplib
import email.mime.multipart
import email.mime.text


class Email(object):
    content_from = None
    content_to = None
    content_subject = None
    content_msg = None
    content_pwd = None

    def send_163(self):
        assert self.content_from is not None
        assert self.content_to is not None
        assert self.content_pwd is not None
        msg = email.mime.multipart.MIMEMultipart()
        msg['from'] = self.content_from
        msg['to'] = self.content_to
        msg['subject'] = self.content_subject
        txt = email.mime.text.MIMEText(self.content_msg)
        msg.attach(txt)
        smtp = smtplib.SMTP(host='smtp.163.com', port=25)

        smtp.login(self.content_from, self.content_pwd)
        smtp.sendmail(self.content_from, self.content_to, str(msg))
        smtp.quit()


def send_email(subject, msg):
    e = Email()
    e.content_from = 'jjzhu_ncu@163.com'
    e.content_to = '767543579@qq.com'
    e.content_pwd = 'vs7452014'
    e.content_subject = 'hello world'
    e.content_msg = 'hello word'
    e.send_163()

if __name__ == '__main__':
    send_email('', '')
