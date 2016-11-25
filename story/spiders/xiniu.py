import scrapy
from scrapy.http import FormRequest, Request, HtmlResponse
from story.items import StoryItem
import simplejson as json


class XiniuSpider(scrapy.Spider):
    name = "xiniu"
    channel_url = "http://www.xiniugushi.com/function/story.inc.php?action=channelstorylist"
    storydetail_url = "http://www.xiniugushi.com/function/story.inc.php?action=getstorydetails"

    def start_requests(self):
        urls = [self.channel_url]
        for url in urls:
            yield FormRequest(url=url,
                              callback=self.channel_parse,
                              formdata={"channel": "1", "hot": "1", "start": "0", "limit": "20"},
                              headers={"User-Agent": "Mozilla/5.0"})

    def channel_parse(self, response):
        story_data = json.loads(response.body.decode("utf-8")).get("data")
        if not story_data:
            return
        for data in story_data:
            item = StoryItem()
            item["summary"] = data["summary"]
            item["title"] = data["title"]
            item["state"] = data["state"]
            item["author"] = data["nickname"]
            item["article_link"] = data["shareurl"]
            storyid = data["randcode"]
            headers = response.request.headers
            headers["Referer"] = data["shareurl"]
            yield FormRequest(url=self.storydetail_url,
                              formdata={"storyid": storyid, "start": "0",
                                        "limit": "1000"},
                              callback=self.parse,
                              headers=headers,
                              meta={"item": item})

    def parse(self, response):
        item = response.meta["item"]
        content_list = json.loads(response.body.decode("utf-8"))["data"]
        content = ""
        for c in content_list:
            section = c["content"].replace("<br>", "").strip()
            content += section + "\n"
        content = "\n".join([c["content"].strip() for c in content_list])
        item["article_content"] = content
        yield item

if __name__ == '__main__':
    # test
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(XiniuSpider)
    process.start()