# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaseItem(scrapy.Item):
    """
    作者、发布时间、文章标题、文章链接、文章id、文章内容、文章摘要、文章分类
    """
    author = scrapy.Field()
    pubtime = scrapy.Field()
    article_title = scrapy.Field()
    article_link = scrapy.Field()
    article_id = scrapy.Field()
    article_content = scrapy.Field()
    article_summary = scrapy.Field()
    article_category = scrapy.Field()


class BaseArticleItem(BaseItem):
    article_comments = scrapy.Field()
    article_clicks = scrapy.Field()


class StoryItem(BaseArticleItem):
    state = scrapy.Field()


class PengpaiItem(BaseItem):
    """"""
    article_image = scrapy.Field()
