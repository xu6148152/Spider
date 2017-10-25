import time, random
from lxml import etree
from selenium import webdriver
from utils.mongohelper import MongoHelper as SqlHelper
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from spider.zh_all import Answer
from selenium.webdriver.common.action_chains import ActionChains
import utils.config as config

class ZHSpider():
    def __init__(self, start_page, end_page):
        self.black_page = 'https://www.zhihu.com/account/unhuman?type=unhuman&message=%E7%B3%BB%E7%BB%9F%E6%A3%80%E6%B5%8B%E5%88%B0%E6%82%A8%E7%9A%84%E5%B8%90%E5%8F%B7%E6%88%96IP%E5%AD%98%E5%9C%A8%E5%BC%82%E5%B8%B8%E6%B5%81%E9%87%8F%EF%BC%8C%E8%AF%B7%E8%BE%93%E5%85%A5%E4%BB%A5%E4%B8%8B%E5%AD%97%E7%AC%A6%E7%94%A8%E4%BA%8E%E7%A1%AE%E8%AE%A4%E8%BF%99%E4%BA%9B%E8%AF%B7%E6%B1%82%E4%B8%8D%E6%98%AF%E8%87%AA%E5%8A%A8%E7%A8%8B%E5%BA%8F%E5%8F%91%E5%87%BA%E7%9A%84'
        self.start_page = start_page
        self.end_page = end_page
        self.toatal = self.start_page - self.end_page
        self.start_url = 'https://www.zhihu.com/people/zhang-jia-wei/followers?page=' + str(self.start_page)
        self.base_url = 'https://www.zhihu.com'
        self.SqlH = SqlHelper()
        self.SqlH.init_db('zhiHu', 'zhihu_all')
        service_args = [
            '--ignore-ssl-errors=true',
            '--proxy=61.54.25.34:80',
            '--proxy-type=http',
        ]
        #self.browser = webdriver.Chrome(executable_path='/home/caidong/chromedriver/chromedriver')
        self.browser = webdriver.Chrome(executable_path='/Users/xubinggui/Downloads/chromedriver')

        # self.browser = webdriver.PhantomJS(service_args=service_args)
        self.current = 1

        for c_page in range(self.start_page, self.end_page):
            self.crawlData(c_page)
        self.browser.quit()

    def crawlData(self, c_page=1):
        url = 'https://www.zhihu.com/people/zhang-jia-wei/followers?page=' + str(c_page)
        self.browser.get(url)
        self.browser.implicitly_wait(3)
        if self.browser.current_url == self.black_page:
            exit()
        if self.current == 1:
            time.sleep(5)
            self.logoin(random.choice(config.ACCOUNT), "123456")
            self.current = self.current + 1
        time.sleep(2)
        c_page = self.browser.find_element_by_xpath(
            '//button[@class="Button PaginationButton PaginationButton--current Button--plain"]').text
        print('当前页:', c_page)
        # for curren_page in range(int(self.toatal)):
        #     self.browser.implicitly_wait(5)
        #     try:
        #         c_page = self.browser.find_element_by_xpath(
        #             '//button[@class="Button PaginationButton PaginationButton--current Button--plain"]').text
        #         print('当前页:', c_page)
        #         # 点击下一页
        #         # self.browser.find_element_by_xpath(
        #         #    '//Button PaginationButton PaginationButton-next Button--plain"]').click()
        #         # 点击上一页
        #         #self.browser.find_element_by_xpath(
        #         #    '//button[@class="Button PaginationButton PaginationButton-prev Button--plain"]').click()
        #         #self.browser.implicitly_wait(3)
        #     except:
        #         print("翻页出错")
        if self.start_page <= int(c_page) <= self.end_page:
            self.browser.implicitly_wait(5)
            intervalue = 2 + random.randrange(1, 4, 1)
            time.sleep(intervalue)
            self.parse_user_list(self.browser.page_source)

            # try:
            #     self.parse_user_list(self.browser.page_source)
            # except:
            #     print('循环点击列表出错')

        else:
            exit()

    def parse_user_list(self, html):
        tree = etree.HTML(html)
        items = self.browser.find_elements_by_xpath('//div[@class="ContentItem-head"]//a[@class="UserLink-link"]')
        print("当前页用户数目", len(items))
        follower_list = tree.xpath('//div[@class="List-item"]')
        for item in follower_list:
            index = follower_list.index(item)
            #print(len(follower_list))
            print(str(index))
            follower_info = etree.ElementTree(item)
            # name = followerInfo.xpath("//a[@class='UserLink-link']/text()")[0]#用户名
            home_page = follower_info.xpath("//a[@class='UserLink-link']/@href")[0]  # 主页
            follower_c = follower_info.xpath("//span[@class='ContentItem-statusItem']/text()")[2]  # 关注数
            print("链接", home_page)
            if self.SqlH.count({"user_home_url": home_page}) == 0 and int(follower_c[:-3].strip()) > 0:
                # 不出现点击点问题
                time.sleep(random.randrange(5))
                while not items[index].is_displayed():
                    time.sleep(1)
                self.browser.implicitly_wait(5)
                # self.browser.
                ActionChains(self.browser).move_to_element(items[index]).click().release().perform()
                # items[index].click()
                # try:
                #     items[index].click()
                # except:
                #     print('点击错误')
                #     return
                self.browser.implicitly_wait(1)
                handle_cnt = len(self.browser.window_handles) - 1
                # print('标签数',handle_cnt)
                self.browser.switch_to.window(self.browser.window_handles[handle_cnt])
                # print(self.browser.current_url)
                if self.browser.current_url == self.black_page:
                    time.sleep(10 * 60)
                self.browser.implicitly_wait(3)
                self.parse_special_column(self.browser.page_source, self.browser.current_url)

                # try:
                #     self.browser.implicitly_wait(3)
                #     #self.parse_home_page(self.browser.page_source, self.browser.current_url)
                #     self.parse_special_column(self.browser.page_source,self.browser.current_url)
                # except:
                #     print("页面解析错误")
                if handle_cnt > 0:
                    self.browser.close()
                    self.browser.switch_to.window(self.browser.window_handles[0])
            else:
                print("已存在,")

            time.sleep(random.randrange(2))

    def parse_special_column(self, html, url):
        tree = etree.HTML(html)
        follow = tree.xpath("//div[@class='NumberBoard-value']/text()")
        if follow:
            flowing = follow[0].strip()
            follower = follow[1].strip()
        else:
            flowing = 'none'
            follower = 'none'
        page_header = tree.xpath(
            "//div[@class='Card ProfileMain']//ul[@class='Tabs ProfileMain-tabs']/li[@class='Tabs-item']/a/span/text()")
        answer = page_header[0]
        article = page_header[2]
        special_column = page_header[3]
        user_name = tree.xpath("//span[@class='ProfileHeader-name']/text()")[0]
        collecter = tree.xpath("//div[@class='Profile-sideColumnItemValue']/text()")
        # print("收藏数", collecter)
        if collecter:
            for item in collecter:
                if str(item).endswith("次收藏"):
                    save = item.strip()[:-3]
                else:
                    save = 0
        else:
            save = 0

        comment_list = tree.xpath('//div[@class="ContentItem-actions"]')
        answer_list = []
        if len(comment_list) > 4:
            comment_list = comment_list[1:4]
        else:
            comment_list = comment_list[1:]
        for item in comment_list:
            item = etree.ElementTree(item)
            answer_comment = item.xpath('//button[@class="Button ContentItem-action Button--plain"]/text()')[0]
            if str(answer_comment).startswith('添加'):
                answer_comment = 0
            else:
                answer_comment = str(answer_comment).strip()[:-3]
            answer_list.append(answer_comment)
        print("文章数", article)
        if len(answer_list) == 0:
            answer_list = "none"
        if int(article) > 0:
            self.browser.find_elements_by_xpath(
                "//div[@class='Card ProfileMain']//ul[@class='Tabs ProfileMain-tabs']/li[@class='Tabs-item']/a")[
                2].click()
            self.browser.implicitly_wait(5)
            time.sleep(3)
            article_list = self.parse_article(self.browser.page_source)
        else:
            article_list = 'none'
        obj = {
            "user_name": user_name, "article_comment": article_list, "followers": follower, "flowing": flowing,
            "collect": save, "article": article,
            "answer": answer, "answer_comment": answer_list, "new": "true"}
        self.SqlH.insert_zh(obj)
        # self.SqlH.update({"user_home_url": self.user_home_url}, {
        #     "user_name":user_name,"article_comment":article_list,"followers": follower, "flowing": flowing,
        #                                                          "collect": save, "article": article,
        #                                                          "answer": answer, "answer_comment": answer_list,"new":"true"})
        print(user_name, "关注了", flowing, str(save), '回答', answer, '文章', article, "跟随者", follower,
              special_column, '文章', article_list, '回答', answer_list)

    def parse_article(self, html):
        tree = etree.HTML(html)
        comment_list = tree.xpath('//div[@class="ContentItem-actions"]')
        if len(comment_list) > 4:
            comment_list = comment_list[1:4]
        else:
            comment_list = comment_list[1:]
        article_list = []
        for item in comment_list:
            item = etree.ElementTree(item)
            answer_comment = item.xpath('//button[@class="Button ContentItem-action Button--plain"]/text()')[0]
            if str(answer_comment).startswith('添加'):
                answer_comment = 0
            else:
                answer_comment = str(answer_comment).strip()[:-3]
            print(answer_comment)
            article_list.append(answer_comment)

        if len(article_list) == 0:
            article_list = "none"
        return article_list

    def logoin(self, username, password):
        login = self.browser.find_elements_by_xpath("//div[@class='AppHeader-profile']/div/button")[0]
        login.click()
        self.browser.implicitly_wait(10)
        userinput = self.browser.find_element_by_xpath("//input[@name='username']")
        userinput.send_keys(username)
        pwdinput = self.browser.find_element_by_xpath("//input[@name='password']")
        pwdinput.send_keys(password)
        log_bt = self.browser.find_element_by_xpath(
            "//button[@class='Button SignFlow-submitButton Button--primary Button--blue']")
        log_bt.click()

def main():
    crawl = ZHSpider(1000, 2000)

if __name__ == '__main__':
    main()