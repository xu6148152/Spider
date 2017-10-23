# coding:utf-8
import time
import random
import os
import sys
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from utils.mongohelper import MongoHelper as SqlHelper


class zhspider():
    def __init__(self):
        self.black_page = 'https://www.zhihu.com/account/unhuman?type=unhuman&message=%E7%B3%BB%E7%BB%9F%E6%A3%80%E6%B5%8B%E5%88%B0%E6%82%A8%E7%9A%84%E5%B8%90%E5%8F%B7%E6%88%96IP%E5%AD%98%E5%9C%A8%E5%BC%82%E5%B8%B8%E6%B5%81%E9%87%8F%EF%BC%8C%E8%AF%B7%E8%BE%93%E5%85%A5%E4%BB%A5%E4%B8%8B%E5%AD%97%E7%AC%A6%E7%94%A8%E4%BA%8E%E7%A1%AE%E8%AE%A4%E8%BF%99%E4%BA%9B%E8%AF%B7%E6%B1%82%E4%B8%8D%E6%98%AF%E8%87%AA%E5%8A%A8%E7%A8%8B%E5%BA%8F%E5%8F%91%E5%87%BA%E7%9A%84'
        self.start_url = 'https://www.zhihu.com/people/xiong-mao-de-hei-bai-zhao/activities'
        self.base_url = 'https://www.zhihu.com'
        self.sql_helper = SqlHelper()
        self.sql_helper.init_db('zhihu', 'zhihu_all')
        self.browser = webdriver.Chrome(
            executable_path='/Users/xubinggui/Downloads/chromedriver')
        self.start_page = 8725
        self.end_page = 1
        self.total = self.start_page - self.end_page
        self.user_home_url = ''
        self.current = 1

    def crawlData(self, url=None):
        self.browser.get(url)
        if self.browser.current_url == self.black_page:
            print("CAPTCHA")
            sys.exit()
        if self.current == 2:
            time.sleep(30)
        self.current = self.current + 1
        self.browser.implicitly_wait(3)
        time.sleep(2)
        try:
            self.parse_home_page(self.browser.page_source)
        except:
            pass

    def parse_home_page(self, html):
        tree = etree.HTML(html)
        follow = tree.xpath("//div[@class='NumberBoard-value']/text()")
        if follow:
            following = follow[0].strip()
            follower = follow[1].strip()
        else:
            following = 'none'
            follower = 'none'
        print('flowing {0}, follower {1}'.format(
            following, follower), end='\n')
        page_header = tree.xpath(
            "//div[@class='Card ProfileMain']//ul[@class='Tabs ProfileMain-tabs']/li[@class='Tabs-item']/a/span/text()")
        answer = page_header[0]
        article = page_header[2]
        print('answer:{0}, article:{1}'.format(answer, article), end='\n')
        special_column = page_header[3]
        if int(special_column) > 0:
            special_url = self.browser.find_element_by_xpath(
                '//h2[@class="ContentItem-title"]/a').get_attribtue("href")
            print(special_url, end='\n')
        else:
            special_url = 'none'

        user_name = tree.xpath("//span[@class='ProfileHeader-name']/text()")[0]
        print('user_name: {0}'.format(user_name), end='\n')
        collecters = tree.xpath(
            "//div[@class='Profile-sideColumnItemValue']/text()")

        if collecters:
            for item in collecters:
                if str(item).endswith("次收藏"):
                    save = item.strip()[:-3]
                else:
                    save = 0
        else:
            save = 0

        print(user_name, "关注l", following, str(save),
              answer, article, follower, special_column)
        zhihu_obj = dict(followers=follower, following=following,
                         collect=save, article=article,
                         answer=answer, special_url=special_url)
        result = self.sql_helper.update(
            {"user_home_url": self.user_home_url}, zhihu_obj)
        print(result)


if __name__ == '__main__':
    spider = zhspider()
    spider.user_home_url = spider.start_url
    spider.crawlData(spider.user_home_url)
# while True:
# for pa in range(1, 400):
#
# crawl.user_home_url =
