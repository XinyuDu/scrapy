# 网页爬虫

scrapy爬虫，配合无头浏览器splash使用。

1. 启动splash的容器：

`docker run -itd -p 8050:8050 scrapinghub/splash`

2. 进入conda环境：

`conda activate scrapy`

3. 启动爬虫

```
cd stocks163
   scrapy crawl stockspider
```

 
