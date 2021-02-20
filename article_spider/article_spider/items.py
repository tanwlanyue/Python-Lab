# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join, Identity
import re
from w3lib.html import remove_tags
from article_spider.models.es_types import ArticleType
from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using)

class ArticleSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def date_convert(value):
    match_re = re.match(".*?(\d+.*)", value)
    if match_re:
        return match_re.group(1)
    else:
        return "2000-01-01"

# CnblogsArticleItem class
# this class is for define a item to save data frm spider
# created by zhanglei
# copyright USTC
# 26.12.2020
class CnblogsArticleItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(output_processor=Identity())
    digg_count = scrapy.Field()
    bury_count = scrapy.Field()
    comment_count = scrapy.Field()
    view_count = scrapy.Field()
    tags = scrapy.Field(output_processor=Join(separator=","))
    content = scrapy.Field()
    create_date = scrapy.Field(input_processor=MapCompose(date_convert))

    # 存mysql
    def get_insert_sql(self):
        insert_sql = """
            insert into cnblogs_article VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE comment_count=VALUES(comment_count)
        """
        params = (
            self.get("title", ""),
            self.get("url", ""),
            self.get("url_object_id", ""),
            self.get("front_image_url", ""),
            self.get("digg_count", 0),
            self.get("bury_count", 0),
            self.get("comment_count", 0),
            self.get("view_count", 0),
            self.get("tags", ""),
            self.get("content", ),
            self.get("create_date", "0000-00-00"),
        )
        return insert_sql, params
    # 存elasticsearch
    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.url = self["url"]
        article.meta.id = self["url_object_id"]
        article.front_image_url = self["front_image_url"]
        article.digg_count = self["digg_count"]
        article.bury_count = self["bury_count"]
        article.comment_count = self["comment_count"]
        article.view_count = self["view_count"]
        article.tags = self["tags"]
        article.content = remove_tags(self["content"])
        article.create_date = self["create_date"]
        article.suggest = gen_suggest(ArticleType._doc_type.index, ((article.title, 10), (article.tags, 5)))
        article.save()
        return

def gen_suggest(index, info_tuple):
    # 根据字符串生成搜索建议数组
    used_words = set()
    suggest = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串
            # 分词完成
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            # 去掉无意义字符
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = analyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggest.append({"input": list(new_words), "weight": weight})

    return suggest