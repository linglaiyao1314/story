# -*- coding: utf-8 -*-

import scrapy


class BaseItem(scrapy.Item):
    """
    品牌、行业、设计者(设计公司)、广告类型（目前就是2.video、1.image）、广告uri、媒体类型、广告描述
    """
    brand = scrapy.Field()
    industry = scrapy.Field()
    designer = scrapy.Field()
    ad_type = scrapy.Field()
    ad_uri = scrapy.Field()
    media_type = scrapy.Field()
    description = scrapy.Field()


class WeloveadItem(BaseItem):
    """
    投放地区
    """
    area = scrapy.Field()
