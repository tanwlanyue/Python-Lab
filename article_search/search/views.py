from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import render
from django.views.generic.base import View
from search.models import ArticleType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import redis

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis(decode_responses=True)

re_data = []
s = ArticleType.search()
s = s.suggest('my_suggest', "苹果", completion={
    "field": "suggest", "fuzzy": {
        "fuzziness": 2
    },
    "size": 10
})
suggestions = s.execute_suggest()
for match in suggestions.my_suggest[0].options:
    source = match._source
    re_data.append(source["title"])


# IndexView class
# this class is for show index.html top search key words
# created by zhanglei
# copyright USTC
# 27.12.2020
class IndexView(View):
    # 首页
    def get(self, request):
        top_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        return render(request, "index.html", {"top_search": top_search})


# SearchSuggest class
# this class is for give search suggest
# created by zhanglei
# copyright USTC
# 27.12.2020
class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_data = []
        if key_words:
            s = ArticleType.search()
            s = s.suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_data.append(source["title"])
        return HttpResponse(json.dumps(re_data), content_type="application/json")

# SearchSuggest class
# this class is for set data to search result update the key word times
# created by zhanglei
# copyright USTC
# 27.12.2020
class SearchView(View):
    def get(self, request):
        key_words = request.GET.get("q", "")
        index_name = "cnblogs"
        source = "cnblogs"
        if key_words:
            redis_cli.zincrby("search_keywords_set", 1, key_words)

        # 逆序取值
        top_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1

        start_time = datetime.now()
        if key_words:
            response = client.search(
                index=index_name,
                body={
                    "query": {
                        "multi_match": {
                            "query": key_words,
                            "fields": ["tags", "title", "content"]
                        }
                    },
                    "from": (page - 1) * 10,
                    "size": 10,
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {
                            "title": {},
                            "content": {},
                        }
                    }
                }
            )
        else:
            response = client.search(
                index=index_name,
                body={
                    "query": {
                        "match_all": {
                        }
                    },
                    "from": (page - 1) * 10,
                    "size": 10,
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {
                            "title": {},
                            "content": {},
                        }
                    }
                }
            )
        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        # 总数量
        total_nums = response["hits"]["total"]
        if (page % 10) > 0:
            page_nums = int(total_nums / 10) + 1
        else:
            page_nums = int(total_nums / 10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            from collections import defaultdict
            hit_dict = defaultdict(str)
            if "highlight" not in hit:
                hit["highlight"] = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]
            # 正文只取500
            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
            else:
                hit_dict["content"] = hit["_source"]["content"][:500]

            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)

        return render(request, "result.html", {"page": page,
                                               "all_hits": hit_list,
                                               "key_words": key_words,
                                               "total_nums": total_nums,
                                               "page_nums": page_nums,
                                               "source": source,
                                               "index_name": index_name,
                                               "last_seconds": last_seconds,
                                               "top_search": top_search})
