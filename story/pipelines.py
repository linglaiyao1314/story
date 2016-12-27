# -*- coding: utf-8 -*-
import pymongo
import time
from story.items import AcFunUserItem, AcFunArticleItem


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'story')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        insert_item = {key: value[0] for key, value in item.items() if value}
        if isinstance(item, AcFunUserItem):
            if self.db["user"].find_one({"user_id": insert_item["user_id"]}):
                pass
            else:
                self.db["user"].insert(insert_item)
            return insert_item
        else:
            if self.db[spider.collection_name].find_one({"article_id": insert_item["article_id"]}):
                return insert_item
            insert_item.update({"capture_time": int(time.time())})
            self.db[spider.collection_name].insert(insert_item)
        return insert_item


class SentimentAnalysisPipeline(object):
    analysis_url = "http://ictclas.nlpir.org/nlpir/index4/getEmotionResult.do"

    def process_item(self, item, spider):
        pass

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass
