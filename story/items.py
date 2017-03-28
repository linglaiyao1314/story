# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaseUserItem(scrapy.Item):
    """
    用户id、用户名、用户简述、用户关注数、用户粉丝数, 用户主页
    """
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    user_info = scrapy.Field()
    follows = scrapy.Field()
    fans = scrapy.Field()
    user_link = scrapy.Field()


class BaseRelationItem(scrapy.Item):
    user_id = scrapy.Field()


class AcfunUserItem(BaseUserItem):
    """
    用户头像链接
    """
    user_icon_link = scrapy.Field()


class AcfunUserFllowItem(BaseRelationItem):
    """"""
    follow_user_id = scrapy.Field()


class AcfunUserFansItem(BaseRelationItem):
    fan_user_id = scrapy.Field()
