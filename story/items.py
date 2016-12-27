# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaseArticleItem(scrapy.Item):
    """
    作者、发布时间、文章标题、文章链接、文章id、文章内容、文章分类
    """
    author = scrapy.Field()
    pubtime = scrapy.Field()
    article_title = scrapy.Field()
    article_link = scrapy.Field()
    article_id = scrapy.Field()
    article_content = scrapy.Field()
    article_category = scrapy.Field()


class BaseUserItem(scrapy.Item):
    """
    用户id、用户名、用户签名
    """
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    user_info = scrapy.Field()


class AcFunArticleItem(BaseArticleItem):
    """waiting for new field"""


class AcFunUserItem(BaseUserItem):
    """"""

class AcFunCommentItem(scrapy.Item):
    """评论id、评论引用id、评论时间、评论内容、评论用户id"""
    article_id = scrapy.Field()
    comment_id = scrapy.Field()
    comment_quote_id = scrapy.Field()
    comment_date = scrapy.Field()
    comment_content = scrapy.Field()
    comment_user_id = scrapy.Field()
