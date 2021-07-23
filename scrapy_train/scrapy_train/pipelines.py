# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy_train.dbutil import DataMemorizer

class ScrapyTrainPipeline:
    def open_spider(self, spider):
        self.db = DataMemorizer()

    def process_item(self, item, spider):
        self.db.insertData('trains', item['page_num'],item['num'], item['train_num'], item['start'], item['end'])
        # print('************item**************',item)
        return item
