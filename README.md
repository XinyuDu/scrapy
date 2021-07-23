# 网页爬虫

scrapy爬虫，配合无头浏览器splash使用。

1. 启动splash的容器：

`docker run -itd -p 8050:8050 scrapinghub/splash`

2. 进入conda环境：

`conda activate scrapy`

3. 创建爬虫

 ```
scrapy startproject xxx
cd xxx
scrapy genspider example example.com
 ```

   

5. 启动爬虫

```python
cd xxx
scrapy crawl example
```

 
