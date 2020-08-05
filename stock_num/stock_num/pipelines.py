# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from stock_num.dbutil import DataMemorizer

class StockNumPipeline(object):
    def open_spider(self, spider):
        self.db = DataMemorizer()

    def process_item(self, item, spider):
        self.db.insertData('stocks_num', item['name'], item['num'])
        return item
