# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from ..items import StockNumItem

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

page_num = """
            function main(splash, args)
              assert(splash:go(args.url))
              assert(splash:wait(2))
              input = splash:select(".paginate_input")
              input:send_keys('<Right> <Backspace> %s')
              assert(splash:wait(0.5))
              go = splash:select(".paginte_go")
              go:mouse_click()
              assert(splash:wait(2))
              return splash:html()
            end
            """

class StocknumSpider(scrapy.Spider):
    name = 'stocknum'
    allowed_domains = ['eastmoney.com']
    start_urls = ['http://eastmoney.com/']

    url = [
        'http://quote.eastmoney.com/stocklist.html'
    ]

    # start request
    def start_requests(self):
        for url in self.url:
            yield SplashRequest(url, callback=self.parse_page_num, endpoint='execute',
                                args={'lua_source': script, 'wait': 1})

    def parse_page_num(self, response):
        pages = response.xpath("/html/body/div[1]/div[2]/div[2]/div[5]/div/div[2]/div/span[1]/a[5]/text()").extract_first()

        for i in range(int(pages)):
            # print(page_num%i)
            yield SplashRequest(response.url, callback=self.parse, endpoint='execute',
                                args={'lua_source': page_num%(i+1), 'wait': 1})
            # break

    def parse(self, response):
        stocks = response.xpath("/html/body/div[1]/div[2]/div[2]/div[5]/div/table/tbody/tr[*]")

        for stock in stocks:
            item = StockNumItem()
            # /html/body/div[1]/div[2]/div[2]/div[5]/div/table/tbody/tr[1]/td[3]
            # //*[@id="table_wrapper-table"]/tbody/tr[1]/td[3]/a

            item['num'] = stock.xpath(".//td[2]/a/text()").extract_first()
            item['name'] = stock.xpath(".//td[3]/a/text()").extract_first()
            # print('***items:', item['num'],',',item['name'])
            yield item