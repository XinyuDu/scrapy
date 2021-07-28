# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from baidunews.dbutil import DataMemorizer
from baidunews.wxmsg import wxmsg

class BaidunewsPipeline:
    def open_spider(self,spider):
        self.db=DataMemorizer()

    def process_item(self, item, spider):
        try:
            self.db.insertData('baidu_news', item['title'], item['link'], item['source'], item['pubtime'],
                           item['real_pubtime'])
            #send message
            content = "<a href=\"%s\">%s</a>"%(item['link'],item['title']+'</br>'+item['abstract']) #item['abstract']
            msg = wxmsg(token='95ffa823a2bd41a5b9119fe491d5c0f8', title=item['title'], content=content)
            msg.send()
        except Exception as e:
            print('exist!', e)
        return item
