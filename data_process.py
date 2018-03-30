# coding:utf-8


import sqlite3
import csv


class DataProcess(object):

    def __init__(self, dbname, table_name):
        self.dbname = dbname
        self.table_name = table_name
        self.con = sqlite3.connect('test.db')

    def get_goods(self):
        cur = self.con.cursor()
        cur.execute('select name from sqlite_master where type="table"')
        values = cur.fetchall()
        table_need_create = True
        for x in values:
            if x[0] == self.table_name:
                table_need_create = False
                break
        if table_need_create is True:
            cur.close()
            return False, None

        cur.execute('select url, price, name from {}'.format(self.table_name))
        values = cur.fetchall()
        cur.close()

        goods_data = []

        for x in values:
            good = {}
            good['url'] = x[0]
            good['price'] = x[1]
            good['name'] = x[2]
            goods_data.append(good)

        return True, goods_data

    def add_good(self, url, price=-1, name='', date=''):
        cur = self.con.cursor()
        cur.execute('select name from sqlite_master where type="table"')
        values = cur.fetchall()
        table_need_create = True
        for x in values:
            if x[0] == self.table_name:
                table_need_create = False
                break

        if table_need_create is True:
            print("No table:" + self.table_name + ", need create.")
            try:
                cur.execute(
                    'create table {} (url text primary key not null, price real not null, name text, date text)'
                    .format(self.table_name))
            except Exception as e:
                print("create goods table error: " + str(e))
                cur.close()
                return False

        try:
            cur.execute(
                'insert into {} values (?, ?, "{}", ?)'.format(
                    self.table_name, name), (url, price, date))
        except Exception as e:
            print("add good error: " + str(e))
            cur.close()
            return False

        self.con.commit()
        cur.close()
        print("add good over.")
        return True

    def update_good(self, url, price, name, date):
        cur = self.con.cursor()
        cur.execute('select name from sqlite_master where type="table"')
        values = cur.fetchall()
        table_need_create = True
        for x in values:
            if x[0] == self.table_name:
                table_need_create = False
                break

        if table_need_create is True:
            print("No table: " + self.table_name)
            cur.close()
            return False

        try:
            cur.execute(
                'update {} set price = {}, name = "{}", date = "{}" where url = "{}"'
                .format(self.table_name, price, name, date, url))
        except Exception as e:
            print("update good's data error:" + str(e))
            cur.close()
            return False

        self.con.commit()
        cur.close()
        print("update good over.")
        return True

    def delete_good(self, url):
        cur = self.con.cursor()
        cur.execute('select name from sqlite_master where type="table"')
        values = cur.fetchall()
        table_need_create = True
        for x in values:
            if x[0] == self.table_name:
                table_need_create = False
                break

        if table_need_create is True:
            print("No table:" + self.table_name)
            cur.close()
            return False

        try:
            cur.execute('delete from {} where url = "{}"'.format(
                self.table_name, url))
        except Exception as e:
            print("delete good's data error:" + str(e))
            cur.close()
            return False

        self.con.commit()
        cur.close()

        print("delete good over.")
        return True

    def find_good(self, url):
        cur = self.con.cursor()
        try:
            cur.execute(
                'select url from {} where url="{}"'.format(
                    self.table_name, url))
            values = cur.fetchall()
            cur.close()
            if len(values) > 0:
                return True
            return False
        except Exception as e:
            print("find_good error:" + str(e))
            cur.close()
            return False

    def export_csv(self, csvfilename):
        cur = self.con.cursor()
        try:
            cur.execute('select * from {}'.format(self.table_name))
            with open(csvfilename, 'w') as f:
                f.write(",".join([x[0] for x in cur.description]) + "\n")
                for x in cur:
                    f.write(",".join([str(i) for i in x]) + "\n")
            cur.close()
            return True

        except Exception as e:
            print("export_csv error:" + str(e))
            return False

    def urls_in_csvfile(self, csvfilename):
        urls = []
        try:
            with open(csvfilename) as f:
                f_csv = csv.DictReader(f)
                for row in f_csv:
                    urls.append(row['url'])
            return urls
        except Exception as e:
            print("open %s error: %s" % (csvfilename, str(e)))
            return None

    def add_from_csv(self, csvfilename):
        # try:
        #     with open(csvfilename) as f:
        #         f_csv = csv.DictReader(f)
        #         for row in f_csv:
        #             ret = self.find_good(row['url'])
        #             if ret is False:
        #                 print("There were no good: %s in database, add it." %
        #                       row['url'])
        #                 self.add_good(row['url'])
        #             else:
        #                 print("Find good: %s in database." % row['url'])
        # except Exception as e:
        #     print("open %s error: %s" % csvfilename, str(e))

        urls = self.urls_in_csvfile(csvfilename)
        if urls is None:
            return False
        for url in urls:
            ret = self.find_good(url)
            if ret is False:
                print("There were no good: %s in database, add it." %
                      url)
                self.add_good(url)
            else:
                print("Find good: %s in database." % url)

    def sync_with_csv(self, csvfilename):
        cur = self.con.cursor()
        cur.execute('select name from sqlite_master where type="table"')
        values = cur.fetchall()
        table_need_create = True
        for x in values:
            if x[0] == self.table_name:
                table_need_create = False
                break

        if table_need_create is True:
            print("No table:" + self.table_name + ", need create.")
            try:
                cur.execute(
                    'create table {} (url text primary key not null, price real not null, name text, date text)'
                    .format(self.table_name))
            except Exception as e:
                print("create goods table error: " + str(e))
                cur.close()
                return False

        cur.execute('select url from {}'.format(self.table_name))
        values = cur.fetchall()
        database_urls = [x[0] for x in values]
        cur.close()

        ret = self.add_from_csv(csvfilename)
        if ret is False:
            return False

        csv_urls = self.urls_in_csvfile(csvfilename)
        for x in database_urls:
            if x not in csv_urls:
                print("url: %s is not in: %s, delete it." % (x, csvfilename))
                self.delete_good(x)

        print("sync with csv files: %s over." % csvfilename)
        return True


def main():
    print("In function main()")
    dataprocess = DataProcess('test.db', 'goods')
    # ret = dataprocess.add_good(
    #     'https://item.jd.com/1208740.html', 79.0,
    #     'luoji',
    #     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # ret = dataprocess.add_good(
    #     'https://item.jd.com/5025715.html', 479.0,
    #     'Yeelight 皎月LED卧室吸顶灯纯白版客厅智能吸顶灯调光调色遥控器手机控制现代简约圆形书房灯具',
    #     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # ret = True
    # if ret is True:
    #     goods_data = dataprocess.get_goods()
    #     print("goods_data: " + goods_data)
    #     ret = dataprocess.update_good(
    #         'https://item.jd.com/1208740.html', 79.0,
    #         '罗技（Logitech）M275（M280）无线鼠标 黑色',
    #         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    #     ret = dataprocess.delete_good(
    #         'https://item.jd.com/5025715.html')
    #     ret = dataprocess.delete_good(
    #         'https://item.jd.com/1208740.html')
    #     goods_data = dataprocess.get_goods()
    #     print("goods_data: " + goods_data)

    ret = dataprocess.find_good('https://item.jd.com/1208740.html')
    if ret is True:
        print("found it")
    else:
        print("found nothing")


if __name__ == '__main__':
    main()
