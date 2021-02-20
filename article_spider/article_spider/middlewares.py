# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class ArticleSpiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ArticleSpiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)



# RandomUserAgentMiddleware class
# this class is for change user-agent randomly used by fake-useragent
# created by zhanglei
# copyright USTC
# 26.12.2020
class RandomUserAgentMiddleware(object):
    # 获取useragent策略
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    # 设置 user-agent 和cookie
    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        useragent = get_ua()
        print(useragent)
        request.headers.setdefault('User-Agent', useragent)
        request.cookies = {".Cnblogs.AspNetCore.Cookies": "CfDJ8AHUmC2ZwXVKl7whpe9_latYZYRDbXEdfOWMfCLgHnmpJ3dvvKIo1lVWP2Epb9Azj6qDDYHl04s6BkdgnOaEBuCSWe58j6NqDu5tZFqPOK5yk29LIxs77f1dWodZ6yIS8nVxtNrTn7gsRvBeE7hWs2H1GwDszo-MZVQKFX7OJwyDV10qEMatvu0ri6KEW5j9Sbry61VmBDPV_ND3X8X-cNqy9hKfDct-vRjjP87837_HN1or8koQoXjEEW8wrFJ2BXHlDsxnZaXaTgsnumzGxzOgyooOUbYnU7U1-2OHh1eUUkeNp22u3ZRh737avdGgAGTYlLlh_5FGjfQA65khkUXw_sobv-GBdNfOlpONOKLscpCZZLGdSsPvy7sCaoZ_qbWvYskWbS75O4k2zjox_Xkn9ldeVCGWnNJWa6WJaj964JYyAEv_PYx1txLvV6xI3Z-JaDEIeSiVcM4KfPTGfOlREcT00ESxkOToK4EJSBK_Wz9wwKvk-KA4pZjqvxO_QMitGYupgZL0WlaPKmn2XQeB0Px_obwbH-j_df6HUVg7nPqRrQeYZpNL3_Wrl2uS4A", ".CNBlogsCookie": "06341BEAD7A45B5C63AF4D6402AFE026892132ADBF22F1733A741B996DE5675C27E650B24515B5EE61702ADDEAF4257D37273B426D894D89A929AD91B846C3D2525BF0B2F8E3F2F9CE097ADEE85F230CEA50086A"}
