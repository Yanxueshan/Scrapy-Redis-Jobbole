# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobboleItem(scrapy.Item):
    '''
        示例Item
    '''
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleArticleItem(scrapy.Item):
    '''
        设置要保存的数据字段
    '''
    title = scrapy.Field()
    url = scrapy.Field()
    url_id = scrapy.Field()
    content = scrapy.Field()
    support_nums = scrapy.Field()
    collection_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    publish_date = scrapy.Field()
    tags = scrapy.Field()
