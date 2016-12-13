# coding=utf-8
import scrapy
from scrapy.http import Request
from story.items import NeteasyItem
import json
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
from utils.text_process import get_number


class NeteasySpider(scrapy.Spider):
    name = "neteasy"
    domain = "http://ent.163.com//"
    # 存储的collection
    collection_name = "news"

    def start_requests(self):
        catagory_urls = {"gossip": "http://ent.163.com/special/000380VU/newsdata_index.js?callback=data_callback"}
        # 提取出所有url，然后进行请求
        for catagory, category_url in catagory_urls.items():
            yield Request(url=category_url,
                          callback=self.parse_url,
                          meta={"article_category": catagory})
        other_urls = ["http://ent.163.com/special/000380VU/newsdata_index_0{0}.js?callback=data_callback".format(i)
                      for i in range(2, 6)]
        for url in other_urls:
            yield Request(url=url,
                          callback=self.parse_url,
                          meta={"article_category": "gossip"})

    def parse_url(self, response):
        meta = response.meta
        extract_items = json.loads(response.body.decode("gbk")[:-1].replace("data_callback(", ""))
        # 从当前页面获取所有的文章链接以及文章摘要
        for item in extract_items:
            url = item["docurl"]
            yield Request(url=url,
                          callback=self.parse,
                          meta={"article_link": url,
                                "article_id": self.name + "-" + str(item["tienum"]),
                                "article_category": meta["article_category"],
                                "article_image": item["imgurl"],
                                "article_title": item["title"],
                                "pubtime": item["time"]
                                })

    def parse(self, response):
        """
        解析具体的文章页面
        """
        meta = response.meta
        loader = ItemLoader(item=NeteasyItem(), response=response)
        # add xpath
        loader.add_xpath("author", "//a[@id='ne_article_source']//text()")
        loader.add_xpath("article_content", "//div[@id='endText']//text()",
                         MapCompose(lambda x: x.strip() if x.strip() else None),
                         Join("\n"))
        # add raw value
        loader.add_value("article_link", meta["article_link"])
        loader.add_value("article_id", meta["article_id"])
        loader.add_value("article_category", meta["article_category"])
        loader.add_value("article_image", meta["article_image"])
        loader.add_value("article_title", meta["article_title"])
        loader.add_value("pubtime", meta["pubtime"])
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
    process.crawl(NeteasySpider)
    process.start()
