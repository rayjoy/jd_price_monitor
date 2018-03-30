#! /usr/bin/env python
# coding:utf-8


from selenium import webdriver
import re


def get_goods_name(driver):
    try:
        goods_name = driver.find_element_by_class_name("sku-name").text
        print(u"\t商品:" + goods_name)
        return goods_name
    except Exception as e:
        try:
            goods_name = driver.find_element_by_xpath(
                "//*[@id='name']/h1").text
            print("\tname:" + goods_name)
            return goods_name
        except Exception as e:
            print("get goods_name error: " + str(e))
            return None


def get_goods_price(driver):
    pattern = re.compile("\d+\.?\d*")
    try:
        price = driver.find_element_by_xpath(
            '//*[@class="itemInfo-wrap"]//*[@class="p-price"]/span[2]').text
        search = pattern.search(price)
        if search is None:
            return None
        print(u"\t价格:" + price)
        return float(search.group())
    except Exception as e:
        try:
            price = driver.find_element_by_xpath(
                '//div[@id="itemInfo"]//*[@class="p-price"]').text
            print("\tprice:" + price)
            search = pattern.search(price)
            if search is None:
                return None
            return float(search.group())
        except Exception as e:
            print("get price error: " + str(e))
            return None


def get_goods_plus_price(driver):
    pattern = re.compile("\d+\.?\d*")
    try:
        plus_price = driver.find_element_by_xpath(
            "//*[@class='p-price-plus']/span").text
        if plus_price != "":
            search = pattern.search(plus_price)
            if search is None:
                return None
            print("\tPlus会员价：" + plus_price)
            return float(search.group())
        else:
            return None
    except Exception as e:
        print("get plus price error: " + str(e))
        return None


class HtmlParse(object):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('no-sandbox')
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=options)

    def get_goods_data(self, url, use_plus=True):
        '''
        use_plus: use the plus member price as price
        '''
        self.driver.get(url)
        if url != self.driver.current_url:
            print("good's url has jump to:" + self.driver.current_url)
        else:
            print("")

        goods_price = get_goods_price(self.driver)
        if goods_price is None:
            return False, None
        goods_name = get_goods_name(self.driver)
        if goods_name is None:
            return False, None

        # use plus member price
        if use_plus is True:
            goods_plus_price = get_goods_plus_price(self.driver)
            if goods_plus_price is not None:
                # print("plus price: %.2f" % goods_plus_price)
                if goods_price > goods_plus_price:
                    goods_price = goods_plus_price

        return True, (goods_price, goods_name)

    def quit(self):
        self.driver.quit()
