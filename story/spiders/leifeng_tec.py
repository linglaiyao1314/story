# coding=utf-8
import scrapy
from scrapy.http import Request
from story.items import PengpaiItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
import os

class LeifengSpider(scrapy.Spider):
    name = "leifeng_tec"

    domain = "http://www.leiphone.com/"
    collection_name = "leifeng_tec"

    def start_requests(self):
        url = {"technology": "http://www.leiphone.com/"}
        for category, category_url in url.items():
            yield Request(url=category_url,
                          callback=self.parse_url,
                          meta={"article_category": category})

    def parse_url(self, response):
        meta = response.meta
        article_images = response.xpath("//div[@class='img']/a/img//@data-original").extract()
        article_links = response.xpath("//div[@class='word']/h3/a/@href").extract()
        article_titles = response.xpath("//div[@class='word']/h3/a//@title").extract()
        print(article_links)
        print(article_images)

        for image, link, title in zip(article_images, article_links, article_titles):
            article_id = os.path.split(link)[-1].split(".")[0]
            yield Request(
                url=link,
                callback=self.parse,
                meta={
                    "article_link": link, "article_id": article_id,
                    "article_category": meta["article_category"],
                    "article_image": image,
                    "article_title": title
                }
            )

    def parse(self, response):
        meta = response.meta
        loader = ItemLoader(item=PengpaiItem(), response=response)
        loader.add_xpath("author", "//td[@class='aut']/a//text()")
        loader.add_xpath("pubtime", "//td[@class='time']//text()",
                         MapCompose(lambda x : x.strip() if x.strip() else None))
        loader.add_xpath("article_content", "//div[@class='lph-article-comView']//text()",
                         MapCompose(lambda x : x.strip() if x.strip() else None),
                         Join("\n"))

        loader.add_value("article_title", meta["article_title"])
        loader.add_value("article_link", meta["article_link"])
        loader.add_value("article_id", meta["article_id"])
        loader.add_value("article_category", meta["article_category"])
        loader.add_value("article_image", meta["article_image"])
        yield loader.load_item()

if __name__ == "__main__":
    import sys
    from scrapy.crawler import CrawlerProcess
    sys.path.append(r"C:/test/story/story")

    process = CrawlerProcess(
            settings={"User-Agent": "Mozilla/5.0",
                      "ITEM_PIPELINES": {'story.pipelines.MongoPipeline': 300},
                      "MONGO_URI": "localhost:27017",
                      "MONGO_DATABASE": "story"})

    process.crawl(LeifengSpider)
    process.start()











