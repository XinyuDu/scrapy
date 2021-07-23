# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BaidunewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    source = scrapy.Field()
    pubtime = scrapy.Field()
    real_pubtime = scrapy.Field()
    abstract = scrapy.Field()
