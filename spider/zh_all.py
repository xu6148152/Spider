from lxml import etree
from selenium import webdriver
import time, random, sys,urllib,json
from utils.mongohelper import MongoHelper as SqlHelper
import utils.config as config



class Answer():
    def __init__(self):
        self.black_page = 'https://www.zhihu.com/account/unhuman?type=unhuman&message=%E7%B3%BB%E7%BB%9F%E6%A3%80%E6%B5%8B%E5%88%B0%E6%82%A8%E7%9A%84%E5%B8%90%E5%8F%B7%E6%88%96IP%E5%AD%98%E5%9C%A8%E5%BC%82%E5%B8%B8%E6%B5%81%E9%87%8F%EF%BC%8C%E8%AF%B7%E8%BE%93%E5%85%A5%E4%BB%A5%E4%B8%8B%E5%AD%97%E7%AC%A6%E7%94%A8%E4%BA%8E%E7%A1%AE%E8%AE%A4%E8%BF%99%E4%BA%9B%E8%AF%B7%E6%B1%82%E4%B8%8D%E6%98%AF%E8%87%AA%E5%8A%A8%E7%A8%8B%E5%BA%8F%E5%8F%91%E5%87%BA%E7%9A%84'
        self.start_url = 'https://zhuanlan.zhihu.com/yinjiaoshou886/answer'
        #self.browser = webdriver.PhantomJS()
        self.SqlH = SqlHelper()
        self.SqlH.init_db('zhiHu', 'zhihu_all')
        self.base_url = 'https://www.zhihu.com'
        self.user_home_url = ''
        self.current = 1

    def crawl(self, url):
        self.browser = webdriver.Chrome(executable_path='/home/caidong/developProgram/selenium/chromedriver')
        self.browser.get(url)
        self.browser.implicitly_wait(5)
        if self.browser.current_url == self.black_page:
            print("输入验证")
            sys.exit()
        if self.current == 1:
            time.sleep(15)
            self.logoin(random.choice(config.ACCOUNT),"123456")
            self.current=self.current + 1
        time.sleep(random.randint(2,5))
        self.browser.implicitly_wait(3)
        try:
           self.parse_special_column(self.browser.page_source, self.browser.current_url)
        except:

           pass

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

        if len(answer_list) == 0:
            answer_list = "none"

        if int(article)>0:
            self.browser.get(self.base_url+self.user_home_url+'/posts')
            time.sleep(2)
            self.browser.implicitly_wait(5)
            article_list = self.parse_article(self.browser.page_source)
        else:
            article_list='none'
        obj={
            "user_name":user_name,"article_comment":article_list,"followers": follower, "flowing": flowing,
                                                                 "collect": save, "article": article,
                                                                 "answer": answer, "answer_comment": answer_list,"new":"true"}
        self.SqlH.insert(obj)
        # self.SqlH.update({"user_home_url": self.user_home_url}, {
        #     "user_name":user_name,"article_comment":article_list,"followers": follower, "flowing": flowing,
        #                                                          "collect": save, "article": article,
        #                                                          "answer": answer, "answer_comment": answer_list,"new":"true"})
        print(user_name, "关注了", flowing, str(save), '回答',answer,'文章', article, "跟随者",follower, special_column,'文章',article_list,'回答',answer_list)

    def parse_article(self,html):
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
        return  article_list



    def logoin(self,username,password):
        login = self.browser.find_elements_by_xpath("//div[@class='AppHeader-profile']/div/button")[0]
        login.click()
        self.browser.implicitly_wait(10)
        userinput=self.browser.find_element_by_xpath("//input[@name='username']")
        userinput.send_keys(username)
        pwdinput=self.browser.find_element_by_xpath("//input[@name='password']")
        pwdinput.send_keys(password)
        log_bt = self.browser.find_element_by_xpath("//button[@class='Button SignFlow-submitButton Button--primary Button--blue']")
        log_bt.click()

    def start(self):
        while True:
            start_time = time.time()
            for pa in range(1, 500):
                sharedata = urllib.request.urlopen('http://47.92.140.243:8090/share_data/?&count=50').read().decode('utf-8')
                items = json.loads(sharedata)
                for item in items:
                    self.user_home_url = item["user_home_url"]
                    self.crawl(self.base_url + item["user_home_url"] + '/answers')
            self.browser.quit()