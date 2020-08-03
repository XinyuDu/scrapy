# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from index163.dbutil import DataMemorizer

class Index163Pipeline(object):
    def open_spider(self, spider):
        self.db = DataMemorizer()

    def process_item(self, item, spider):
        self.db.insertData('index_163', item['name'], item['date'], item['open'], item['max'], item['min'],
                           item['close'], item['change'], item['change_rate'], item['volumn_hand'], item['volumn'],
                           )
        return item