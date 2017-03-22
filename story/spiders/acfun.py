# coding=utf-8
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.statscollectors import MemoryStatsCollector
import simplejson as json
import re

from story.items import AcfunUserItem, AcfunUserFllowItem, AcfunUserFansItem
from utils.text_process import get_number

ICON_PATTERN = re.compile("(\(.*?\))")


class AcfunSpider(scrapy.Spider):
    FOLLOW = "flow"  # 关注
    FANS = "flowed"  # 粉丝
    name = "acfun"
    domain = "http://www.acfun.cn"
    user_domain = "http://www.acfun.cn/u/{0}.aspx"
    flow_domain = "http://www.acfun.cn/space/next?uid={user_id}&type={ftype}&orderBy=2&pageNo={page}"

    def start_requests(self):
        """
        以文章区为起始页开始抓取
        """
        start_urls = ["http://www.acfun.cn/v/list110/index.htm",
                      "http://www.acfun.cn/v/list73/index.htm",
                      "http://www.acfun.cn/v/list74/index.htm",
                      "http://www.acfun.cn/v/list75/index.htm",
                      "http://www.acfun.cn/v/list164/index.htm"]
        # 提取出所有url，然后进行请求
        for url in start_urls:
            yield Request(url=url, callback=self.parse_article_page)

    def parse_article_page(self, response):
        """
        1.提取用户详情页
        2.判断是否提取到用户信息
          2.1 满足，则向后执行
          2.2 否则return，终止抓取
        3.回调用户详情页请求
        4.翻页请求
        """
        # 提取用户详情页连接
        user_links = response.xpath("//p[@class='article-info']//@href").extract()
        # 若无链接被提取，说明该页提取完毕
        if not user_links:
            return
        user_ids = {get_number(link) for link in user_links}
        # 用户详情页
        for user_id in user_ids:
            yield Request(url=self.user_domain.format(user_id), callback=self.parse_user_page,
                          meta={"user_id": user_id})
            # 翻页，提取后续用户详情页
            base_url, page = response.url.split("index")
            page = get_number(page) or 1
            yield Request(url=base_url + "index_{0}.htm".format(int(page) + 1), callback=self.parse_article_page)

    def parse_user_page(self, response):
        meta = response.meta
        user_item = AcfunUserItem()
        # 基本信息提取
        user_item["user_id"] = meta["user_id"]
        user_item["user_icon_link"] = self.get_icon_link(response.xpath(
            "//div[@id='anchorMes']//div[@class='img']//@style").extract_first())
        user_item["user_name"] = response.xpath(
            "//div[@class='clearfix']//div[@class='name fl text-overflow']//text()").extract_first()
        user_item["user_info"] = response.xpath("//div[@class='infoM']//text()").extract_first()
        user_item["follows"] = response.xpath(
            "//div[@class='clearfix']//span[@class='fl follow']//text()").extract_first()
        user_item["fans"] = response.xpath("//div[@class='clearfix']//span[@class='fl fans']//text()").extract_first()
        # 返回item
        yield user_item
        # 关注关系提取
        flow_url = self.flow_domain.format(user_id=meta["user_id"], ftype=self.FOLLOW, page=1)
        yield Request(url=flow_url, callback=self.parse_relationship,
                      meta={"user_id": meta["user_id"], "relation_type": self.FOLLOW, "page": 1})
        # 粉丝关系提取
        flowed_url = self.flow_domain.format(user_id=meta["user_id"], ftype=self.FANS, page=1)
        yield Request(url=flowed_url, callback=self.parse_relationship,
                      meta={"user_id": meta["user_id"], "relation_type": self.FANS, "page": 1})

    def parse_relationship(self, response):
        """
        1.首先提取关系link
        2.返回所有Item， 提取新的user，并请求user信息
        3.对关系页进行翻页
        """
        meta = response.meta
        # 提取json中的关注信息
        relation_datas = json.loads(response.text)
        page_content = relation_datas["data"]["html"]
        user_links = Selector(text=page_content).xpath("//a//@href").extract()
        relation_user_ids = {get_number(link) for link in user_links}
        # 请求其他用户页
        for relation_user_id in relation_user_ids:
            if meta["relation_type"] == self.FOLLOW:
                yield AcfunUserFllowItem(user_id=meta["user_id"], follow_user_id=relation_user_id)
            elif meta["relation_type"] == self.FANS:
                yield AcfunUserFansItem(user_id=meta["user_id"], fan_user_id=relation_user_id)
        for link in user_links:
            yield Request(url=self.domain + link, callback=self.parse_user_page, meta={
                "user_id": get_number(link)
            })
        # 确定是否翻页
        if relation_datas["data"]["page"]["totalPage"] > meta["page"]:
            yield Request(url=self.flow_domain.format(user_id=meta["user_id"],
                                                      ftype=meta["relation_type"],
                                                      page=meta["page"] + 1),
                          callback=self.parse_relationship,
                          meta={"user_id": meta["user_id"], "relation_type": meta["relation_type"], "page": meta["page"] + 1})

    def get_icon_link(self, raw_link):
        return re.search(ICON_PATTERN, raw_link).group()[2:-2]


if __name__ == '__main__':
    # test
    import scrapy.spidermiddlewares.httperror
    from scrapy.crawler import CrawlerProcess

    # 初始化一个下载中间件的配置
    process = CrawlerProcess(settings={"User-Agent": "Mozilla/5.0",
                                       "ITEM_PIPELINES": {'story.pipelines.MongoPipeline': 300},
                                       "MONGO_URI": "localhost:27017",
                                       "MONGO_DATABASE": "story",
                                       "LOG_LEVEL": "DEBUG"
                                       })
    process.crawl(AcfunSpider)
    process.start()
