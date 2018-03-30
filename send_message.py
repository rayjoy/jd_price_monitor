# coding:utf-8


import smtplib
from email.mime.text import MIMEText


class SendMessage(object):
    def __init__(self):
        pass

    def mail_init(self, host, user, password, port):
        self.host = host
        self.user = user
        self.password = password
        self.port = port

    def send_mail(self, to_list, sub, content):
        me = "降价通知" + "<" + self.user + ">"
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = sub
        msg['From'] = me
        msg['To'] = ";".join(to_list)

        try:
            s = smtplib.SMTP_SSL(self.host, self.port)
            s.login(self.user, self.password)
            s.sendmail(me, to_list, msg.as_string())
            s.close()
            print("mail has been sent.")
            return True
        except Exception as e:
            print(str(e))
            return False
