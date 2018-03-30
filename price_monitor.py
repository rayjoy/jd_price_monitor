#!/usr/bin/env python
# coding:utf-8


import datetime
from data_process import DataProcess
from html_parse import HtmlParse
from send_message import SendMessage
import time
import threading
import sys
import getopt


def monitor(mail_user, mail_pass, mail_to, mail_host):
    before = time.time()
    print("price monitor start.")

    dataprocess = DataProcess('test.db', 'goods')
    send_message = SendMessage()

    ret = dataprocess.sync_with_csv('in.csv')
    if ret is False:
        print("sync with csv file error.")
        return False

    # dataprocess.add_from_csv('in.csv')

    mail_content = ""
    html_parse = HtmlParse()

    ret, goods_data = dataprocess.get_goods()
    if ret is False:
        html_parse.driver.quit()
        return
    for x in goods_data:
        url = x['url']
        price = x['price']
        ret, data = html_parse.get_goods_data(url)
        if ret is False:
            continue
        price_now, goods_name = data
        print("price_now:" + str(price_now))
        if price_now < price or price is None or price <= 0:
            ret = dataprocess.update_good(
                url, price_now, goods_name,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if ret is False:
                continue
            mail_content = mail_content + goods_name\
                + "\n降价为：" + str(price_now) + "\n"
    if len(mail_content) != 0:
        mail_sub = "降价通知"
        mailto_list = [mail_to]
        mail_port = 465

        send_message.mail_init(mail_host, mail_user, mail_pass, mail_port)
        send_message.send_mail(mailto_list, mail_sub, mail_content)
    else:
        print("There were no good which price has reduced.")

    html_parse.quit()

    # dataprocess.export_csv("out.csv")
    after = time.time()
    print('Thread ended, asumed time : %.2f' % (after - before))


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:o:t:")
    except Exception as e:
        print(
            "Call this program like this:\n"
                "main.py -u xxx@xxx.com -p password -o smtp.xxx.com -t xxx@xxx.com\n")
        exit()

    mail_user, mail_pass, mail_host, mail_to = None, None, None, None

    for opt, arg in opts:
        if opt == '-u':
            mail_user = arg
        elif opt == '-p':
            mail_pass = arg
        elif opt == '-o':
            mail_host = arg
        elif opt == '-t':
            mail_to = arg

    for x in (mail_user, mail_pass, mail_host, mail_to):
        print(x)
        if x is None:
            print(
                "Call this program like this:\n"
                "main.py -u xxx@xxx.com -p password -o smtp.xxx.com -t xxx@xxx.com\n")
            exit()

    while True:
        # monitor()
        print('Now time is: %s' %
              datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        kwargs = {'mail_to': mail_to, 'mail_host': mail_host,
                  'mail_user': mail_user, 'mail_pass': mail_pass}
        t = threading.Thread(target=monitor, kwargs=kwargs)
        t.start()

        # look for price redection every 30 minutes
        time.sleep(1800)


if __name__ == '__main__':
    main()
