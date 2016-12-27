# coding=utf-8
import scrapy
from scrapy.http import Request
from story.items import AcFunArticleItem, AcFunUserItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
from utils.text_process import get_number
import simplejson as json


class AcFunSpider(scrapy.Spider):
    # spider name
    name = "acfun"
    # mongo collection name
    collection_name = "acfun"
    domain = "http://www.acfun.cn"
    # 用户基础信息页
    user_domain = "http://www.acfun.cn/u/"
    # 评论页
    comment_list_json_url = "http://www.acfun.cn/comment_list_json.aspx"
    # 用户信息详情页
    page_url = "http://www.acfun.cn/space/next"

    def start_requests(self):
        """
        从文章页开始抓取，整体流程：
         1 获取文章链接
         2 获取用户信息 -> 获取用户文章链接 -> 获取用户关注与粉丝信息-> 2
         3 获取评论信息 -> 2
        """
        catagory_urls = {"综合": "http://www.acfun.tv/v/list110/index.htm",
                         "工作情感": "http://www.acfun.tv/v/list73/index.htm",
                         "动漫文化": "http://www.acfun.tv/v/list74/index.htm",
                         "漫画轻小说": "http://www.acfun.tv/v/list75/index.htm",
                         "游戏": "http://www.acfun.tv/v/list164/index.htm"}
        # 提取出所有url，然后进行请求
        for catagory, category_url in catagory_urls.items():
            yield Request(url=category_url, callback=self.parse_article_url,
                          meta={"article_category": catagory})

    def parse_article_url(self, response):
        """
         解析文章链接
        """
        meta = response.meta
        article_links = response.xpath("//div[@class='mainer']//div[@class='item']/a[1]/@href").extract()
        # 从当前页面获取所有的文章链接以及文章摘要
        for link in article_links:
            url = self.domain + link
            meta["article_link"] = url
            meta["article_id"] = get_number(url)
            yield Request(url=url,
                          callback=self.parse_article_info,
                          meta=meta)
        # 然后翻页查询新文章
        base_url, page = response.url.split("index")
        page = get_number(page) or 1
        new_urls = list({base_url + url for url in response.xpath("//div[@class='area-pager']//a//@href").extract()})
        if new_urls:
            print(base_url + "index_{0}.htm".format(int(page) + 1))
            yield Request(url=base_url + "index_{0}.htm".format(int(page) + 1), callback=self.parse_article_url,
                          meta=meta)

    def parse_article_info(self, response):
        """
        1、解析具体的文章页面
        2、请求解析用户信息页
        3、请求解析评论页
        """
        meta = response.meta
        loader = ItemLoader(item=AcFunArticleItem(), response=response)
        # add xpath
        loader.add_xpath("author", "//a[@id='btn-follow-author']/@data-name")
        loader.add_xpath("pubtime", "//span[@class='time']//text()")
        loader.add_xpath("article_content", "//div[@id='area-player']//text()",
                         MapCompose(lambda x: x.strip() if x.strip() else None),
                         Join("\n"))
        loader.add_xpath("article_title", "//p[@id='title_1']/span[@class='txt-title-view_1']//text()")
        # add raw value
        loader.add_value("article_link", meta["article_link"])
        loader.add_value("article_id", meta["article_id"])
        loader.add_value("article_category", meta["article_category"])
        yield loader.load_item()
        # 抓取用户信息
        yield Request(url=self.user_domain + str(meta["article_id"]) + ".aspx",
                      callback=self.parse_user_info,
                      meta={"user_id": meta["article_id"]})
        # 抓取评论
        # params_str = "?contentId={0}&currentPage=1".format(meta["article_id"])
        # yield Request(url=self.comment_list_json_url+params_str,
        #               callback=self.parse_comment_info,
        #               meta={"article_id": meta["article_id"]})

    def parse_user_info(self, response):
        meta = response.meta
        user_loader = ItemLoader(item=AcFunUserItem(), response=response)
        # add xpath
        user_loader.add_xpath("user_name", "//div[@class='mesL fl']//div[@class='name fl text-overflow']//text()")
        user_loader.add_xpath("user_info", "//div[@class='mesL fl']//div[@class='infoM']//text()")
        # add raw value
        user_loader.add_value("user_id", meta["user_id"])
        # 获取用户文章信息
        yield user_loader.load_item()
        # user_params_str = "?uid={0}&type=article&orderBy=2&pageNo=1".format(meta["user_id"])
        # yield Request(url=self.page_url+user_params_str,
        #               callback=self.parse_user_detail_article,
        #               meta={"page": 1,
        #                     "uid": meta["user_id"]})

    def parse_user_detail_article(self, response):
        meta = response.meta
        article_obj = json.loads(response.text)

    def parse_comment_info(self, response):
        return


if __name__ == '__main__':
    # test
    from scrapy.crawler import CrawlerProcess
    # 初始化一个下载中间件的配置
    process = CrawlerProcess(settings={"User-Agent": "Mozilla/5.0",
                                       "ITEM_PIPELINES": {'story.pipelines.MongoPipeline': 300},
                                       "MONGO_URI": "localhost:27017",
                                       "MONGO_DATABASE": "story"
                                       })
    process.crawl(AcFunSpider)
    process.start()
