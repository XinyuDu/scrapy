# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy_splash import SplashRequest
from ..items import News163Item
import datetime

# splash lua script
script ="""
        function main(splash)
            local num_scrolls = 20
            local scroll_delay = 1

            local scroll_to = splash:jsfunc("window.scrollTo")
            local get_body_height = splash:jsfunc(
                "function() {return document.body.scrollHeight;}"
            )
            assert(splash:go(splash.args.url))
            splash:wait(splash.args.wait)

            for _ = 1, num_scrolls do
                scroll_to(0, get_body_height())
                splash:wait(scroll_delay)
            end        
            return splash:html()
        end
        """

class newsSpider(Spider):
    name = 'news'
    allowed_domains = ['163.com']
    url = [
            'https://3g.163.com/touch/#/recommend',
            'https://3g.163.com/touch/tech/',
            'https://3g.163.com/touch/money',
            'https://3g.163.com/touch/news'
            ]
    
    # start request
    def start_requests(self):
        for url in self.url:
            yield SplashRequest(url, callback=self.parse, endpoint='execute', args={'lua_source': script, 'wait': 1})
    # parse the html content 
    def parse(self, response):
        if response.url==self.url[0]:
            articles = response.xpath("//div[@class='rec-news-item']")
        else:# response.url==self.url[1]:
            articles = response.xpath("//article[@class='news-card card-type-news']")

        print('****',len(articles),response.url)
        for ar in articles:
            item=News163Item()
            item['title']=ar.xpath(".//h3/text()").extract_first()
            link=ar.xpath(".//a/@href").extract_first()
            link_end=link.find('?')
            item['link']=link[0:link_end]
            # print(item['link'])
            item['source']=response.url
            pubtime=ar.xpath(".//span[@class='pubtime']/text()").extract_first()
            item['pubtime'] = pubtime
            item['real_pubtime']=self.cal_time(pubtime)
            yield item


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
