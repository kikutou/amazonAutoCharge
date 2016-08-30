# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class sendGmail:
    username = 'oujunnhaku@gmail.com'
    password = 'iloveu04231993'

    def __init__(self, to, sub, body):
        host, port = 'smtp.gmail.com', 465
        msg = MIMEText(body)
        msg['Subject'] = sub
        msg['From'] = self.username
        msg['To'] = to

        smtp = smtplib.SMTP_SSL(host, port)
        smtp.ehlo()
        smtp.login(self.username, self.password)
        smtp.mail(self.username)
        smtp.rcpt(to)
        smtp.data(msg.as_string())
        smtp.quit()

if __name__ == '__main__':
    to = 'juteng2005@gmail.com'
    sub = 'エラー報告テスト'
    body = 'これはテストです。'
    sendGmail(to, sub, body)
