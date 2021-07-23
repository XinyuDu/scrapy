# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyTrainItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    page_num = scrapy.Field()
    num = scrapy.Field()
    train_num = scrapy.Field()
    start = scrapy.Field()
    end = scrapy.Field()
