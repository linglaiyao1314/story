# coding=utf-8
from scrapy.exceptions import IgnoreRequest
from scrapy.http.request import Request
from scrapy.http.response import Response
from story.items import StoryItem

class MyCustomDownloaderMiddleware(object):
    """
    下载中间件有三个基本的方法：
    process_request  处理每个通过中间件的请求
    process_response 处理每个通过中间件的响应
    process_exception 处理异常
    """
    def process_request(self, request, spider):
        """
        :param request: 待处理的请求(Request 对象)
        :param spider:  发出该请求的spider对象
        :return 可以返回:
          None  表明该中间件不对请求做任何处理，Scrapy会继续向后处理这个请求(通过后面的其他下载中间件....)
          Request Scrapy会暂停调用其他的process_request方法，重新安排这个请求(假如请求队列)，
          Response 相当于直接返回了Response，然后开始走process_response的路线
          或者抛出IgnoreRequest异常: 会去调用当前中间件的process_exception方法,
        """
        print("downloader request", request.url)
        return None

    def process_response(self, request, response, spider):
        """
        :param request:  请求对象
        :param response: 待处理的响应(Response 对象)
        :param spider: 要响应的目标spider对象
        :return: 可以返回
         Response 正常的响应链(执行后续其他中间件的process_response方法)
         Request 和process_request返回Request的逻辑一样（从process_response的路上下来）
         抛出IgnoreRequest异常 和process_requests返回IgnoreRequest的逻辑一样
        """
        print("downloader response", request.url)
        return response

    def process_exception(self, request, exception, spider):
        """
        :param request: 请求对象
        :param exception: 异常对象
        :param spider: spider对象
        :return:
          None 执行其他中间件的process_exeception
          Request 和process_request返回Request的逻辑一样（从process_exctption的路上下来）
          Response 开车前往proecee_response的路上
        """
        return None


class MyCustomSpiderMiddleware(object):
    """
    爬虫中间件主要有：
        process_spider_input 处理每个从engine到达spider的response
        process_spider_output 处理从spider返回到engine的结果(Request & Item)
    """
    def process_spider_input(self, response, spider):
        """
        :param response: 从engine过来的response
        :param spider: spider对象
        :return:
            None 继续往后执行(进入下一个中间件)
            触发异常 则进行process_spider_exception方法链的执行
        """
        print("spider response", response.url)
        return None

    def process_spider_output(self, response, result, spider):
        """
        :param response: engine过来的response对象
        :param result: response处理后的结果，可以是Request或者Item
        :param spider: spider对象
        :return:
            Item对象
            可以迭代的Request对象（通过yield返回）
        """
        print("spider result", response.url)
        for i in result:
            yield i

