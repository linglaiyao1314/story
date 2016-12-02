# coding=utf-8
import scrapy
from scrapy.http import Request
from story.items import BaseArticleItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, MapCompose, Join, TakeFirst
import simplejson as json
from utils.text_process import get_number


class AcFunSpider(scrapy.Spider):
    name = "acfun"
    # 综合区的文章
    general_domain = "http://www.acfun.tv/v/list110/"
    domain = "http://www.acfun.tv/"
    user_domain = "http://www.acfun.tv/u/"

    def start_requests(self):
        urls = ["index.htm"] + ["index_{0}.htm".format(i) for i in range(2, 834)]
        general_urls = [self.general_domain + u for u in urls]
        for url in general_urls:
            yield Request(url=url,
                          callback=self.parse_url,
                          headers={"User-Agent": "Mozilla/5.0"})

    def parse_url(self, response):
        article_links = response.xpath("//div[@class='mainer']//div[@class='item']/a/@href").extract()
        article_summarys = response.xpath("//div[@class='mainer']//div[@class='item']/div['desc']//text()").extract()
        for link, summary in zip(article_links, article_summarys):
            url = self.domain + link
            yield Request(url=url,
                          callback=self.parse,
                          headers={"User-Agent": "Mozilla/5.0"},
                          meta={"article_link": url, "article_summary": summary})

    def parse(self, response):
        meta = response.meta
        loader = ItemLoader(item=BaseArticleItem(), response=response)
        # add xpath
        loader.add_xpath("author", "//a[@id='btn-follow-author']/@data-name")
        loader.add_xpath("pubtime", "//span[@class='time']//text()")
        loader.add_xpath("article_content", "//div[@id='area-player']//text()",
                         MapCompose(lambda x: x.strip() if x.strip() else None),
                         Join("\n"))
        loader.add_xpath("article_title", "//p[@id='title_1']/span[@class='txt-title-view_1']//text()")
        # add raw value
        loader.add_value("article_link", meta["article_link"])
        loader.add_value("article_summary", meta["article_summary"])
        yield loader.load_item()


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
    process.crawl(AcFunSpider)
    process.start()
