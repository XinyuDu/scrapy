# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from ..items import Index163Item

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


class IndexspiderSpider(scrapy.Spider):
    name = 'indexspider'
    allowed_domains = ['163.com']
    start_urls = ['http://163.com/']

    url = [
        'http://quotes.money.163.com/trade/lsjysj_zhishu_000001.html',  # 上证指数
        'http://quotes.money.163.com/trade/lsjysj_zhishu_399001.html',  # 深成指数
        'http://quotes.money.163.com/trade/lsjysj_zhishu_399300.html',  # 沪深300指数
    ]

    # start request
    def start_requests(self):
        for url in self.url:
            yield SplashRequest(url, callback=self.parse_year, endpoint='execute',
                                args={'lua_source': script, 'wait': 1})

    def parse_year(self, response):
        years = response.xpath("/html/body/div[2]/div[3]/div/form/select[1]/*/text()").extract()
        # print('*****',years)
        seasons = ['1', '2', '3', '4']
        local_url = []
        for year in years[0]: #[0]表示只爬取最近一年的数据。
            for season in seasons:
                url = response.url+'?year='+year+'&season='+season
                local_url.append(url)
        for url in local_url:
            yield SplashRequest(url, callback=self.parse_data, endpoint='execute', args={'lua_source': script, 'wait': 1})
        # print('*****************', local_url)

    def parse_data(self, response):
        days = response.xpath("/html/body/div[2]/div[3]/table/tbody/tr[*]")
        stock_name = response.xpath('/html/body/div[2]/div[1]/div[3]/table/tbody/tr/td[1]/div/a/text()').extract_first()
        # print('*******', stock_name)

        for day in days:
            item = Index163Item()
            item['name'] = stock_name
            date = day.xpath('.//td[1]/text()').extract_first()
            item['date'] = date[:4]+'-'+date[4:6]+'-'+date[6:]
            item['open'] = day.xpath('.//td[2]/text()').extract_first().replace(',', '')
            item['max'] = day.xpath('.//td[3]/text()').extract_first().replace(',', '')
            item['min'] = day.xpath('.//td[4]/text()').extract_first().replace(',', '')
            item['close'] = day.xpath('.//td[5]/text()').extract_first().replace(',', '')
            item['change'] = day.xpath('.//td[6]/text()').extract_first().replace(',', '')
            item['change_rate'] = day.xpath('.//td[7]/text()').extract_first().replace(',', '')
            item['volumn_hand'] = str(float(day.xpath('.//td[8]/text()').extract_first().replace(',', ''))/100.0)
            item['volumn'] = day.xpath('.//td[9]/text()').extract_first().replace(',', '')

            # print('***items:', item['name'], item['date'], item['open'], item['max'], \
            #       item['min'], item['close'], item['change'], item['change_rate'], \
            #       item['volumn_hand'], item['volumn'])

            yield item

