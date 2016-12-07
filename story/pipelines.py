# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


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
        if spider.name == "welovead":
            insert_item = {key: value[0] for key, value in item.items() if value}
            insert_item["ad_uri"] = item["ad_uri"]
        else:
            insert_item = {key: value[0] for key, value in item.items() if value}
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
