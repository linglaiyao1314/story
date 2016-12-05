# coding=utf-8
import scrapy
from scrapy.http import Request
from story.items import BaseArticleItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
import simplejson as json
from utils.text_process import get_number


class AcFunSpider(scrapy.Spider):
    name = "acfun"

    # 综合区的文章
    domain = "http://www.acfun.tv"
    user_domain = "http://www.acfun.tv/u/"
    content_view_url = "http://www.acfun.tv/content_view.aspx"
    comment_list_json_url = "http://www.acfun.tv/comment_list_json.aspx"

    def start_requests(self):
        catagory_urls = {"general": "http://www.acfun.tv/v/list110/index.htm",
                         "work": "http://www.acfun.tv/v/list73/index.htm",
                         "animei": "http://www.acfun.tv/v/list74/index.htm",
                         "novel": "http://www.acfun.tv/v/list75/index.htm",
                         "game": "http://www.acfun.tv/v/list164/index.htm"}
        # 提取出所有url，然后进行请求
        for catagory, category_url in catagory_urls.items():
            yield Request(url=category_url, callback=self.parse_url)

    def parse_url(self, response):
        article_links = response.xpath("//div[@class='mainer']//div[@class='item']/a[1]/@href").extract()
        article_summarys = response.xpath("//div[@class='mainer']//div[@class='item']/div['desc']//text()").extract()
        # 从当前页面获取所有的文章链接以及文章摘要
        for link, summary in zip(article_links, article_summarys):
            url = self.domain + link
            yield Request(url=url,
                          callback=self.parse_info,
                          meta={"article_link": url,
                                "article_summary": summary,
                                "article_id": get_number(url)})
        base_url, page = response.url.split("index")
        page = get_number(page) or 1
        new_urls = list({base_url + url for url in response.xpath("//div[@class='area-pager']//a//@href").extract()})
        # 翻页
        if new_urls:
            print(base_url + "index_{0}.htm".format(int(page) + 1))
            yield Request(url=base_url + "index_{0}.htm".format(int(page) + 1), callback=self.parse_url)

    def parse_info(self, response):
        """
        解析具体的文章页面
        """
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
        loader.add_value("article_id", meta["article_id"])
        meta["loader"] = loader
        # 获取点击数和评论数
        params_str = "contentId={0}".format(meta["article_id"])
        yield Request(url=self.content_view_url+"?{0}".format(params_str),
                      callback=self.parse,
                      meta=meta)

    def parse(self, response):
        """
        解析最终点击数和评论数
        """
        meta = response.meta
        try:
            response_data = json.loads(response.text)
        except:
            response_data = [0, 0]
        loader = meta["loader"]
        loader.add_value("article_clicks", response_data[0])
        loader.add_value("article_comments", response_data[1])
        yield loader.load_item()


if __name__ == '__main__':
    # test
    import sys
    from scrapy.crawler import CrawlerProcess
    import logging
    from scrapy.utils.log import configure_logging
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )
    sys.path.append(r"C:/test/story/story")
    # 初始化一个下载中间件的配置
    process = CrawlerProcess(settings={"User-Agent": "Mozilla/5.0",
                                       "ITEM_PIPELINES": {'story.pipelines.MongoPipeline': 300},
                                       "MONGO_URI": "localhost:27017",
                                       "MONGO_DATABASE": "story"
                                       })
    process.crawl(AcFunSpider)
    process.start()
