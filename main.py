from spider.zh_home import zhspider
import time
import utils.mongohelper as mongohelper

if __name__ == '__main__':
    mongohelper.main()
    spider = zhspider()
    spider.user_home_url = spider.start_url
    spider.crawlData(spider.user_home_url)
    while True:
        for pa in range(1, 400):
            items = spider.sql_helper.select_home_url(
                conditions={"flowing": {"$exists": False}}, page=pa, count=100)
            for item in items:
                spider.user_home_url = item["user_home_url"]
                spider.crawlData(spider.base_url +
                                 item["user_home_url"] + "/activities")
        time.sleep(30 * 60)
    spider.browser.quit()
