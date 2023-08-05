import urllib, json, time, re
import logging
logger = logging.getLogger(__name__)

import network
import base
from video import Video

class Search(base.BaseObject):
    """Search object.

    niconico provides search API. We have two methods for searching video, one
    is keywordsearch, and the other is tagsearch. This class handles both by
    passing ''mode'' keword when instantiated.If you need more than 32 videoes,
    max_pages keyword is required.
    """

    def __str__(self):
        if self.mode == "keyword":
            return "[keyword] %s" % self.keyword
        else:
            return "[tag] %s" % self.keyword

    def __init__(self, keyword, mode="keyword", max_pages=1, search_option="n"):
        assert mode in ["keyword", "tag"]
        self.keyword = keyword
        self.mode = mode
        self.max_pages = max_pages
        assert re.match(r"[vnrmfl][da]?" ,search_option)
        self.search_option = search_option
        self.search_string = self._get_search_string(search_option)

        self.prop_info = (
            ("status",      self._search),
            ("count",       self._search),
            ("page",        self._search),
            ("videolist",   self._search),
            ("favtoken",    self._gettoken),
        )

    def _get_search_string(self, optstr):
        mo = re.match(r"([vnrmfl])([da]?)", optstr)
        assert mo
        search_string = "sort=%s" % mo.group(1)
        if mo.group(2):
            search_string += "&order=%s" % mo.group(2)
        return search_string

    def _gettoken(self):
        if self.mode == 'keyword':
            return None
        url   = "http://www.nicovideo.jp/tag//%s?" % (urllib.quote(self.keyword.encode("utf8")),)
        html = network.urlopen(url, "mylistAPI", "getfavToken").read()
        token_re = r'''FavTag.csrf_token = "([^"]+)"'''
        self._favtoken = re.search(token_re, html).group(1)

    def _search(self):
        if self.mode == 'keyword':
            API_URL   = "http://www.nicovideo.jp/api/search/search/%s?" % (urllib.quote(self.keyword.encode("utf8")),)
        else:
            API_URL   = "http://www.nicovideo.jp/api/search/tag/%s?" % (urllib.quote(self.keyword.encode("utf8")),)

        self._videolist = []
        for i in range (self.max_pages):
            query_str = "mode=watch&order=d&page=%d&%s" % (i+1, self.search_string)
            data = json.loads(network.urlopen(API_URL+query_str, "searchAPI", "search").read())

            self._status    = data["status"]
            self._count     = data["count"]
            self._page      = data["page"]

            for vinfo in data["list"]:
                video = Video(vinfo["id"])
                video._title            = vinfo["title"]
                video._length           = vinfo["length"]
                video._mylist_counter   = int(vinfo["mylist_counter"])
                video._view_counter     = int(vinfo["view_counter"])
                video._comment_num      = int(vinfo["num_res"]) #attr name differs from getthumbinfo.
                self._videolist.append(video)

            if (i+1) * 32 > self.count: #32 denotes items/search
                break
            time.sleep(1)

