# -*- coding: utf-8 -*-
import pymongo
from story.items import AcfunUserItem, AcfunUserFansItem, AcfunUserFllowItem


def register_process_class(spidername):
    class_name_prefix = spidername.capitalize()
    # 动态构建item处理类
    process_class = globals().get(class_name_prefix + "ItemProcess", ItemProcess)
    return process_class


class ItemProcess(object):
    def process_item(self, item):
        return item


class AcfunItemProcess(ItemProcess):
    def process_item(self, item):
        if isinstance(item, AcfunUserItem):
            return self.parse_user_item(item)
        elif isinstance(item, AcfunUserFllowItem):
            return self.parse_follow_item(item)
        elif isinstance(item, AcfunUserFansItem):
            return self.parse_fans_item(item)

    def parse_user_item(self, item):
        return {
            "fans": int(item["fans"]),
            "follows": int(item["follows"]),
            "user_icon_link": item["user_icon_link"],
            "user_id": int(item["user_id"]),
            "user_info": item["user_info"],
            "user_name": item["user_name"],
            "scheme": "acfun_user",
            "unique": ["user_id"]
        }

    def parse_follow_item(self, item):
        return {
            "user_id": int(item["user_id"]),
            "follow": int(item["follow_user_id"]),
            "scheme": "acfun_user_relation",
            "unique": ["user_id", "follow"]
        }

    def parse_fans_item(self, item):
        return {
            "user_id": int(item["fan_user_id"]),
            "follow": int(item["user_id"]),
            "scheme": "acfun_user_relation",
            "unique": ["user_id", "follow"]
        }


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.count = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'story'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.process_class = register_process_class(spider.name)


    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        process = self.process_class()
        item = process.process_item(item)
        collection = item.pop("scheme")
        unique_keys = item.pop("unique")
        condition_clauses = {key: item[key] for key in unique_keys}
        if self.db[collection].find_one(condition_clauses):
            self.db[collection].update_one(condition_clauses, {"$set": item})
        else:
            self.db[collection].insert_one(item)
            self.count += 1
        if self.count % 2000 == 0:
            print(spider.crawler.stats.get_stats())
        return item




