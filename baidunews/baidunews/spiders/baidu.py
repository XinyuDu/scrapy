import scrapy
from scrapy_splash import SplashRequest
import datetime
from ..items import BaidunewsItem
# splash lua script
script ="""
        function main(splash, args)
          assert(splash:go(args.url))
          assert(splash:wait(0.5))
          return {
            html = splash:html()
          }
        end
        """

class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    allowed_domains = ['baidu.com']
    urls = ['https://www.baidu.com/s?tn=news&rtt=4&bsst=1&cl=2&wd=%E6%AF%94%E4%BA%9A%E8%BF%AA&medium=0']

    def cal_time(self,pubtime):
        real_pubtime = datetime.datetime.now()
        if pubtime==None:
            pass
        elif u'小时前' in pubtime:
            hour = int(pubtime[0:-3])
            real_pubtime = real_pubtime-datetime.timedelta(hours=hour)
        elif u'昨天' in pubtime:
            real_pubtime = real_pubtime-datetime.timedelta(days=1)
        elif u'前天' in pubtime:
            real_pubtime = real_pubtime-datetime.timedelta(days=2)
        elif u'天前' in pubtime:
            day = int(pubtime[0:-2])
            real_pubtime = real_pubtime-datetime.timedelta(days=day)
        elif u'分钟前' in pubtime:
            minute = int(pubtime[0:-3])
            real_pubtime = real_pubtime-datetime.timedelta(minutes=minute)
        elif u'刚刚' in pubtime:
            pass
        else:
            print('unrecognized time',pubtime)
            pass

        return real_pubtime.strftime("%Y-%m-%d %H:%M:%S")

    def start_requests(self):
        for url in self.urls:
            yield SplashRequest(url, callback=self.parse, endpoint='execute', args={'lua_source': script, 'wait': 1})

    def parse(self, response):
        articles = response.xpath("/html/body/div/div[3]/div[1]/div[4]/div[2]/div[*]")
        for ar in articles:
            item = BaidunewsItem()
            titles = ar.xpath(".//div/h3/a//text()").extract()#/html/body/div/div[3]/div[1]/div[4]/div[2]/div[2]/div/h3/a/text()[1]
            titles = "".join(titles)

            link = ar.xpath(".//div/h3/a/@href").extract_first() #/html/body/div/div[3]/div[1]/div[4]/div[2]/div[1]/div/h3/a
            source = ar.xpath(".//div/div/div[2]/div/span[1]//text()").extract_first() #/html/body/div/div[3]/div[1]/div[4]/div[2]/div[1]/div/div/div[2]/div/span[1]
            pubtime = ar.xpath(".//div/div/div[2]/div/span[2]//text()").extract_first()  #/html/body/div/div[3]/div[1]/div[4]/div[2]/div[1]/div/div/div[2]/div/span[2]
            realtime = self.cal_time(pubtime)
            abstract = ar.xpath(".//div/div/div[2]/span//text()").extract() #/html/body/div/div[3]/div[1]/div[4]/div[2]/div[1]/div/div/div[2]/span
            abstract = "".join(abstract)

            item['title'] = titles
            item['link'] = link
            item['source'] = source
            item['pubtime'] = pubtime
            item['real_pubtime'] = realtime
            item['abstract'] = abstract
            # print("*****", item)
            yield item


