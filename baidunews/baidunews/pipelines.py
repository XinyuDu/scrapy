# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from baidunews.dbutil import DataMemorizer
# from baidunews.wxmsg import wxmsg
from baidunews.wxpusher import wxpusher

class BaidunewsPipeline:
    def open_spider(self, spider):
        self.db=DataMemorizer()

    def process_item(self, item, spider):
        try:
            self.db.insertData('baidu_news', item['title'], item['link'], item['source'], item['pubtime'],
                           item['real_pubtime'])
            #send message
            content = "<a href=\"%s\">%s</a>"%(item['link'],item['title']+'</br>'+item['abstract']) #item['abstract']
            body = {
                "appToken": "AT_a2fSMuBxfl5WEOkOkq13NixH7ZTKYJqG",
                "content": content,
                "summary": item['abstract'],
                "contentType": 2,
                "uids": ["UID_RxY9fJ8MaWCFWdXzOfMCkCmYhdPY"],
                "url": item['link']
            }
            msg = wxpusher(body)
            re = msg.send()
            print(re.text)
        except Exception as e:
            print('exist!', e)
        return item
