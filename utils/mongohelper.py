import time
import pymongo
from .sqlhelper import SqlHelper

from .config import DB_CONFIG


class MongoHelper(SqlHelper):
    def __init__(self):
        self.client = pymongo.MongoClient(
            DB_CONFIG['DB_CONNECT_STRING'], connect=False)

    def init_db(self, db_name, col_name):
        create_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.db = self.client[db_name]
        self.collection = self.db[col_name]

    def drop_db(self):
        self.client.drop_database(self.db)

    def insert(self, value=None):
        if value:
            newsObj = dict(title=value['title'], content=value['content'], category=value['category'], secCategory=value['secCategory'],
                           img_path=value['image'],
                           time=value['time'], fromTO=value['from'], url=value['url'])
            self.collection.insert(newsObj)

    def delete(self, conditions=None):
        if conditions:
            self.collection.remove(conditions)
            return ('deleteNum', 'ok')
        else:
            return ('deleteNum', 'None')

    def update(self, conditions=None, value=None):
        if conditions and value:
            self.collection.update(conditions, {"$set": value})
            return {'updateNum': 'ok'}
        else:
            return {'updateNum': 'None'}

    def select_csv(self, count=None, conditions=None, page=None):
        items = self.collection.find({"$and": [{'article_comment': {"$exists": True}},
                                               {'answer_comment': {
                                                   "$exists": True}},
                                               {'flowing': {"$exists": True}},
                                               {'export_flag': {"$exists": False}},
                                               ]}, {'_id': 0, 'special_comment': 0, "special_url": 0, "comment_sort": 0,
                                                    "special_follower": 0, "special_name": 0, "home_page": 0})
        results = [item for item in items]
        return results, items

    def select_home_url(self, conditions=None, page=None, count=0):
        return self.collection.find(conditions, {'_id', 0}, limit=count).skip(int(page))

    def select(self, count=None, conditions=None, page=None):
        if count:
            count = int(count)
        else:
            count = 0

        if conditions:
            conditions = dict(conditions)
            conditions_name = ['types', 'protocol']
            for condition_name in conditions_name:
                value = conditions.get(condition_name)
                if value:
                    conditions[condition_name] = value
        else:
            conditions = {}

        items = self.collection.find(conditions, {'_id': 0}, limit=count).skip(
            int(page)).sort([("time", pymongo.DESCENDING)])
        results = [item for item in items]

        return results, items

    def close_client(self):
        self.client.close()

    def count(self, conditions=None):
        conditions = dict(conditions)
        return self.collection.find(conditions).count()


if __name__ == '__main__':
    sql_helper = MongoHelper()
    sql_helper.init_db('zhihu', 'zhihu_all')
    pre = sql_helper.count()
    print('sum: {0}'.format(str(pre)))
    time.sleep(10)
    now = sql_helper.count()
    url = sql_helper.select_home_url({'user_name': 'Jack'}, count=100, page=1)
    print([item for item in url])
