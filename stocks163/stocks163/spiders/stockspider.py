# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from ..items import Stocks163Item
from ..dbutil import DataMemorizer

# splash lua script
script ="""
        function main(splash)
            local num_scrolls = 1
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

class StockspiderSpider(scrapy.Spider):
    name = 'stockspider'
    allowed_domains = ['163.com']
    start_urls = ['http://163.com/']
    # url = [
    #     'http://quotes.money.163.com/trade/lsjysj_002594.html', #比亚迪
    #     'http://quotes.money.163.com/trade/lsjysj_601398.html', #工商银行
    #     'http://quotes.money.163.com/trade/lsjysj_600036.html', #招商银行
    # ]
    url = []
    db = DataMemorizer()
    names, nums = db.getAll('stocks_num')
    for num in nums:
        url.append('http://quotes.money.163.com/trade/lsjysj_'+num+'.html')

    # print('****start stockspider',url)

    # start request
    def start_requests(self):
        for url in self.url:
            yield SplashRequest(url, callback=self.parse_data, endpoint='execute', args={'lua_source': script, 'wait': 1})

    def parse_year(self, response):
        years = response.xpath("/html/body/div[2]/div[4]/div/form/select[1]/*/text()").extract()
        seasons = ['1', '2', '3', '4']
        local_url = []
        for year in years[0]: #[0] 最近一年
            for season in seasons:
                url = response.url+'?year='+year+'&season='+season
                local_url.append(url)
        for url in local_url:
            yield SplashRequest(url, callback=self.parse_data, endpoint='execute', args={'lua_source': script, 'wait': 1})
        # print('*****************', local_url)

    def parse_data(self, response):
        days = response.xpath("/html/body/div[2]/div[4]/table/tbody/tr[*]")
        stock_name = response.xpath('/html/body/div[2]/div[1]/div[3]/table/tbody/tr/td[1]/h1/a/text()').extract_first()

        for day in days:
            item = Stocks163Item()
            item['name'] = stock_name
            item['date'] = day.xpath('.//td[1]/text()').extract_first()
            item['open'] = day.xpath('.//td[2]/text()').extract_first()
            item['max'] = day.xpath('.//td[3]/text()').extract_first()
            item['min'] = day.xpath('.//td[4]/text()').extract_first()
            item['close'] = day.xpath('.//td[5]/text()').extract_first()
            item['change'] = day.xpath('.//td[6]/text()').extract_first()
            item['change_rate'] = day.xpath('.//td[7]/text()').extract_first()
            item['volumn_hand'] = day.xpath('.//td[8]/text()').extract_first().replace(',', '')
            item['volumn'] = day.xpath('.//td[9]/text()').extract_first().replace(',', '')
            item['amplitude'] = day.xpath('.//td[10]/text()').extract_first()
            item['turnover_rate'] = day.xpath('.//td[11]/text()').extract_first()

            # print('***items:', item['name'], item['date'], item['open'], item['max'], \
            #       item['min'], item['close'], item['change'], item['change_rate'], \
            #       item['volumn_hand'], item['volumn'], item['amplitude'], item['turnover_rate'])

            yield item

