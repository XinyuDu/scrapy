# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from news163.dbutil import DataMemorizer

class News163Pipeline(object):
    def open_spider(self,spider):
        self.db=DataMemorizer()
    #     self.file=open('result.txt','w',encoding='utf-8')

    def process_item(self, item, spider):
        # line="%s,%s,%s,%s\n"%(item['title'],item['link'],item['source'],item['pubtime'])
        # self.file.write(line)
        self.db.insertData('news_163',item['title'],item['link'],item['source'],item['pubtime'],item['real_pubtime'])
        return item

    # def close_spider(self,spider):
    #     self.db.__del__()
    #     print('the file is closed')