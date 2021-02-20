from django.db import models

# Create your models here.
from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

# ArticleType class
# this class is for create elasticsearch index
# created by zhanglei
# copyright USTC
# 27.12.2020
# 博客园文章类型
class ArticleType(DocType):
    # 用于自动补全
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    digg_count = Integer()
    bury_count = Integer()
    comment_count = Integer()
    view_count = Integer()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    create_date = Date()

    class Meta:
        index = "cnblogs"
        doc_type = "article"


if __name__ == "__main__":
    ArticleType.init()
