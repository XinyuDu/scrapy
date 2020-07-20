# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Stocks163Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date = scrapy.Field()
    name = scrapy.Field()
    open = scrapy.Field()
    max = scrapy.Field()
    min = scrapy.Field()
    close = scrapy.Field()
    change = scrapy.Field()
    change_rate = scrapy.Field()
    volumn_hand = scrapy.Field()
    volumn = scrapy.Field()
    amplitude = scrapy.Field()
    turnover_rate = scrapy.Field()
