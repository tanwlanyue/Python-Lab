import re

import scrapy
from scrapy import Request
from urllib import parse
import json
from article_spider.items import CnblogsArticleItem, ArticleItemLoader
from article_spider.utils import common

# CnblogsSpider class
# this class is for Crawling data from the site named cnblogs
# created by zhanglei
# copyright USTC
# 26.12.2020
class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['https://news.cnblogs.com/']

    # 广度优先遍历页面
    def parse(self, response):
        post_nodes = response.css('#news_list .news_block')
        for post_node in post_nodes:
            # 正文url
            post_url = post_node.css('h2 a::attr(href)').extract_first("")
            # 图片url
            image_url = post_node.css('.entry_summary a img::attr(src)').extract_first("")
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            # 拼接域名
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)
        next_url = response.xpath("//a[contains(text(), 'Next >')]/@href").extract_first("")
        # 提取下一页
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    # 解析文章详情页
    def parse_detail(self, response):
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            post_id = match_re.group(1)
            item_loader = ArticleItemLoader(item=CnblogsArticleItem(), response=response)
            item_loader.add_css("title", "#news_title a::text")
            item_loader.add_css("create_date", "#news_info .time::text")
            item_loader.add_css("content", "#news_content")
            item_loader.add_css("tags", ".news_tags a::text")
            item_loader.add_value("url", response.url)
            if response.meta.get("front_image_url", []):
                item_loader.add_value("front_image_url", response.meta.get("front_image_url", []))
            response.css(".news_tags a::text").extract_first("")
            yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
                          meta={"article_item": item_loader, "url": response.url},
                          callback=self.parse_nums)
        pass

    # 解析ajax请求的数据
    def parse_nums(self, response):
        j_data = json.loads(response.text)
        item_loader = response.meta.get("article_item", "")
        item_loader.add_value("digg_count", j_data["DiggCount"])
        item_loader.add_value("bury_count", j_data["BuryCount"])
        item_loader.add_value("view_count", j_data["TotalView"])
        item_loader.add_value("comment_count", j_data["CommentCount"])
        item_loader.add_value("url_object_id", common.get_md5(response.meta.get("url", "")))
        article_item = item_loader.load_item()
        yield article_item
