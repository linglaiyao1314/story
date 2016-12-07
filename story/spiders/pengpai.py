# coding=utf-8
import scrapy
from scrapy.http import Request
from story.items import PengpaiItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
from utils.text_process import get_number, parse_others


class PengpaiSpider(scrapy.Spider):
    name = "pengpai"

    # 综合新闻区
    domain = "http://www.thepaper.cn/"
    # 存储的collection
    collection_name = "news"

    def start_requests(self):
        catagory_urls = {"general": "http://www.thepaper.cn/index_scroll.jsp"}
        # 提取出所有url，然后进行请求
        for catagory, category_url in catagory_urls.items():
            yield Request(url=category_url,
                          callback=self.parse_url,
                          meta={"article_category": catagory})

        next_urls = ["http://www.thepaper.cn/load_index.jsp?pageidx={0}".format(i) for i in range(2, 6)]
        for url in next_urls:
            yield Request(url=url,
                          callback=self.parse_url,
                          meta={"article_category": "general"})

    def parse_url(self, response):
        meta = response.meta
        article_links = response.xpath("//div[@class='news_li']/h2/a/@href").extract()
        article_images = response.xpath("//div[@class='news_tu']//img//@src").extract()
        # 从当前页面获取所有的文章链接以及文章摘要
        for image, link in zip(article_images, article_links):
            url = self.domain + link
            yield Request(url=url,
                          callback=self.parse,
                          meta={"article_link": url,
                                "article_id": self.name + "-" + get_number(url),
                                "article_category": meta["article_category"],
                                "article_image": image})

    def parse(self, response):
        """
        解析具体的文章页面
        """
        meta = response.meta
        loader = ItemLoader(item=PengpaiItem(), response=response)
        # add xpath
        loader.add_xpath("author", "//div[@class='news_about']/p[1]//text()")
        loader.add_xpath("pubtime", "//div[@class='news_about']/p[2]//text()",
                         MapCompose(lambda x: parse_others(x).strip()[:-1].strip()))
        loader.add_xpath("article_content", "//div[@data-size='standard']//text()",
                         MapCompose(lambda x: x.strip() if x.strip() else None),
                         Join("\n"))
        loader.add_xpath("article_title", "//h1//text()")
        # add raw value
        loader.add_value("article_link", meta["article_link"])
        loader.add_value("article_id", meta["article_id"])
        loader.add_value("article_category", meta["article_category"])
        loader.add_value("article_image", meta["article_image"])
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
    process.crawl(PengpaiSpider)
    process.start()
