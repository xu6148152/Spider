from spider.zh_home import zhspider

if __name__ == '__main__':
    spider = zhspider()
    spider.user_home_url = spider.start_url
    spider.crawlData(spider.user_home_url)
# while True:
# for pa in range(1, 400):
#
# crawl.user_home_url =
