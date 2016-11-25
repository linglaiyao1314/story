# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class StoryItem(scrapy.Item):
    author = scrapy.Field()
    state = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    article_link = scrapy.Field()
    article_content = scrapy.Field()

