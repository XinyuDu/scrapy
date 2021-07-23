# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from ..items import Stocks163Item
from ..dbutil import DataMemorizer

# splash lua script
script = """
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
        # 'http://quotes.money.163.com/trade/lsjysj_600519.html',
        # 'http://quotes.money.163.com/trade/lsjysj_601398.html',
        # 'http://quotes.money.163.com/trade/lsjysj_600036.html',
    # ]

    # url = []
    # db = DataMemorizer()
    # names, nums = db.getAll('stocks_num')
    # for num in nums:
    #     url.append('http://quotes.money.163.com/trade/lsjysj_'+num+'.html')

    url = []
    nums = ['601318', '000063', '600760', '000651', '600519', '000538', '600436', '000725',
            '600085', '600276', '000858', '600031', '002230', '600036']
            #中国平安, 中兴通讯, 中航沈飞, 格力电器, 贵州茅台, 云南白药, 片仔癀, 京东方Ａ,
            #同仁堂, 恒瑞医药, 五 粮 液, 三一重工, 科大讯飞, 招商银行

    for num in nums:
        url.append('http://quotes.money.163.com/trade/lsjysj_'+num+'.html')

    # print('****start stockspider',url)

    # start request
    def start_requests(self):
        for url in self.url:
            yield scrapy.Request(url, callback=self.parse_year)

    def parse_year(self, response):
        years = response.xpath("/html/body/div[2]/div[4]/div/form/select[1]/*/text()").extract()
        seasons = ['1', '2', '3', '4']
        local_url = []
        for year in years:  # [0] 最近一年
            for season in seasons:
                url = response.url + '?year=' + year + '&season=' + season
                local_url.append(url)
        for url in local_url:
            yield scrapy.Request(url, callback=self.parse_data)
        # print('*****************', years, local_url)

    def parse_data(self, response):
        days = response.xpath("/html/body/div[2]/div[4]/table/tr[*]")
        stock_name = response.xpath('/html/body/div[2]/div[1]/div[3]/table/tr/td[1]/h1/a/text()').extract_first()
        # print('*****days: ', days, stock_name)
        for day in days:
            item = Stocks163Item()
            item['name'] = stock_name
            item['date'] = day.xpath('.//td[1]/text()').extract_first()
            item['open'] = day.xpath('.//td[2]/text()').extract_first().replace(',', '')
            item['max'] = day.xpath('.//td[3]/text()').extract_first().replace(',', '')
            item['min'] = day.xpath('.//td[4]/text()').extract_first().replace(',', '')
            item['close'] = day.xpath('.//td[5]/text()').extract_first().replace(',', '')
            item['change'] = day.xpath('.//td[6]/text()').extract_first().replace(',', '')
            item['change_rate'] = day.xpath('.//td[7]/text()').extract_first().replace(',', '')
            item['volumn_hand'] = day.xpath('.//td[8]/text()').extract_first().replace(',', '')
            item['volumn'] = day.xpath('.//td[9]/text()').extract_first().replace(',', '')
            item['amplitude'] = day.xpath('.//td[10]/text()').extract_first().replace(',', '')
            item['turnover_rate'] = day.xpath('.//td[11]/text()').extract_first().replace(',', '')

            # print('***items:', item['name'], item['date'], item['open'], item['max'], \
            #       item['min'], item['close'], item['change'], item['change_rate'], \
            #       item['volumn_hand'], item['volumn'], item['amplitude'], item['turnover_rate'])

            yield item
