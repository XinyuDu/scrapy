import scrapy
from scrapy_splash import SplashRequest
from ..items import ScrapyTrainItem

script = '''
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(1))
  return {
    html = splash:html(),
    png = splash:png(),
    har = splash:har(),
  }
end
'''
class TrainSpider(scrapy.Spider):
    name = 'train'
    allowed_domains = ['huochepiao.com']
    start_urls = ['http://search.huochepiao.com/update/bianhao/?p=%d&key='%i for i in range(154, 155)]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, callback=self.parse, endpoint='execute',
                                args={'lua_source': script, 'wait': 1, 'images': 0, 'resource_timeout': 10})

    def parse(self, response):
        page_start = response.url.find("p=")
        page_end = response.url.find("&key")
        print("***************start scrapy****************:", response.url[page_start+2:page_end])
        trs = response.xpath("/html/body/table[4]/tbody/tr[*]")
        for i, tr in enumerate(trs):
            if i!=0:
                item = ScrapyTrainItem()
                item['page_num'] = response.url[page_start+2:page_end]
                item['num'] = "%d"%i
                item['train_num'] = tr.xpath(".//td[1]/a//text()").extract_first()
                item['start'] = tr.xpath(".//td[2]//text()").extract_first()
                item['end'] = tr.xpath(".//td[3]//text()").extract_first()
                print('************',item['train_num'], item['start'], item['end'])
                yield item
