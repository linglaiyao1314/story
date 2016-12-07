# coding=utf-8
import scrapy
from scrapy.http import Request
from story.videoitems import WeloveadItem


class WeloveadSpider(scrapy.Spider):
    name = "welovead"

    # 综合新闻区
    domain = "http://www.welovead.com"

    # 存储的collection
    collection_name = "ad_collection"

    def start_requests(self):
        # 只抓中国的品牌
        start_url = "http://www.welovead.com/cn/works/basic_search?r=40"
        # 提取出所有url，然后进行请求
        yield Request(url=start_url,
                      callback=self.parse_url,
                      meta={"area": ["中国"]})

    def parse_url(self, response):
        detail_urls = response.xpath("//ul[@id='ul_works_list']//li//a/@href").extract()
        for url in detail_urls:
            yield Request(url=self.domain + url,
                          callback=self.parse,
                          meta=response.meta)
        next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").extract()
        # 翻页
        if next_url:
            yield Request(url=self.domain + next_url[0], callback=self.parse_url, meta=response.meta)

    def parse(self, response):
        """
        解析广告信息
        """
        meta = response.meta
        item = WeloveadItem()
        item["brand"] = response.xpath("//a[@class='iconBrand']//text()").extract()
        item["designer"] = response.xpath("//a[@class='iconAgency']//text()").extract()
        item["description"] = response.xpath("//div[@id='main']/h1/text()").extract()
        item["area"] = meta["area"]
        item["ad_id"] = [self.name + "-" + response.url.split("/")[-1]]
        # 获取行业和媒体
        for rule in response.xpath("//table[@class='tabWork information_1']//td//a"):
            href = rule.xpath("./@href").extract()
            text = rule.xpath("./text()").extract()
            if not href or not text:
                continue
            if href[0].find("?i=") > 0:
                item["industry"] = text
            elif href[0].find("?m=") > 0:
                item["media_type"] = text
            else:
                continue
        # 获取广告资源和广告类型
        if response.xpath("//div[@class='works_box']//video"):
            item["ad_type"] = [2]
            item["ad_uri"] = response.xpath("//div[@class='works_box']/video/@src").extract()
        else:
            item["ad_type"] = [1]
            if response.xpath("//div[@class='SeriesImg']//a//img/@src"):
                item["ad_uri"] = response.xpath("//div[@class='SeriesImg']//a//img/@src").extract()
            else:
                item["ad_uri"] = response.xpath("//div[@class='works_box']//a//img/@src").extract()
        yield item


if __name__ == '__main__':
    # test
    import sys
    from scrapy.crawler import CrawlerProcess

    sys.path.append(r"C:/test/story/story")
    # 初始化一个下载中间件的配置
    process = CrawlerProcess(settings={"User-Agent": "Mozilla/5.0",
                                       "ITEM_PIPELINES": {'story.pipelines.MongoPipeline': 300},
                                       "MONGO_URI": "localhost:27017",
                                       "MONGO_DATABASE": "story"
                                       })
    process.crawl(WeloveadSpider)
    process.start()
