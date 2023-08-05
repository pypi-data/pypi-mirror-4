import re
import network
import xml.etree.ElementTree

import urllib, urllib2
import json

import base
from video import Video

class Mylist(base.BaseObject):
    """Mylist object.

    There exists two types of mylist. One is public mylists by other users, and
    the other is mylist owned by me. Naturally the former is readonly, and the
    latter is controllable.
    
    This class handles both types of mylist. Every mylist has its unique ID
    matching ^d+$. This ID is required to instantiated except when creating a
    brand new mylist (in this case, ID is set to None, and later mylist.mid
    will be filled). You can access attribute without caring anything, niconico
    API will be called internally.

    attributes to be noted:
        - mid: ID
        - title: title of this mylist
        - videolist: list of ncutils.Video
        - items(owned mylist only): list of items
    """

    def __str__(self):
        return "[mylist] %s" %(self.mid)

    def __init__(self, mid=None):
        self.mid = mid
        self.prop_info = (
            ("token",        self._update_token),
            ("title",        self._update_via_rss),
            ("description",  self._update_via_rss),
            ("videolist",    self._update_via_rss),
            ("items",        self._update_via_mylist_list),
            #
            ("favtoken",     self._update_favtoken),
            #
            ("mine",        self._update_mine),
        )

    def _update_via_rss(self):
        url = "http://www.nicovideo.jp/mylist/%s?rss=2.0" % self.mid
        data = network.urlopen(url, "public_rss", "rss_request for %s"%(self.mid,) ).read()
        etree = xml.etree.ElementTree.XML(data)

        self._title = etree.find("channel/title").text
        self._description = etree.find("channel/description").text
        self._videolist = []
        for itree in etree.findall("channel/item"):
            smid = re.search(r"/([sn]m\d+)$", itree.find("link").text).group(1)
            video = Video(smid)
            video._title = itree.find("title").text
            self._videolist.append(video)

    def _update_via_mylist_list(self):
        url  = "http://www.nicovideo.jp//api/mylist/list?"
        qstr = urllib.urlencode({"token":self.token,"group_id":self.mid})
        info = json.loads( network.urlopen(url+qstr, "mylistAPI", "mylist/list").read()) 

        self._items = []
        class MylistItem(object): pass
        for target in info["mylistitem"]:
            item = MylistItem()
            item.id         = target["item_id"]
            item.video      = Video(target["item_data"]["video_id"])
            item.description= target["description"]

            self._items.append(item)

    def _update_token(self):
        html = network.urlopen("http://www.nicovideo.jp/my/mylist", "mylistAPI", "getToken").read()
        for line in html.splitlines():
            mo = re.match(r'^\s*NicoAPI\.token = "(?P<token>[\d\w-]+)";\s*',line)
            if mo:
                token = mo.group('token')
                break
        self._token = token

    def _update_favtoken(self):
        html = network.urlopen("http://www.nicovideo.jp/mylist/%s"%(self.mid,), "mylistAPI", "getfavToken").read()
        token_re = r'''FavMylist.csrf_token = "([^"]+)"'''
        self._favtoken = re.search(token_re, html).group(1)

    def _update_mine(self):
        cmdurl = "http://www.nicovideo.jp//api/mylistgroup/list"
        q = {}
        q['token'] = self.token
        cmdurl += "?" + urllib.urlencode(q)
        j = json.load( network.urlopen(cmdurl, "mylistAPI", "mylistgroup/list"), encoding='utf8')
        self._mine = []
        if j["status"] == 'ok':
            for item in j["mylistgroup"]:
                m = Mylist(item["id"])
                m._name         = item["name"]
                m._description  = item["description"]
                m._user_id      = item["user_id"]
                m._icon_id      = item["icon_id"]
                m._default_sort = item["default_sort"]
                m._sort_order   = item["sort_order"]
                m._public       = item["public"] == u'1'
                m._update_time  = item["update_time"]
                m._create_time  = item["create_time"]
                self._mine.append(m)

    def truncate(self):
        """this deletes all items in mylist.
        """
        req = urllib2.Request("http://www.nicovideo.jp//api/mylist/delete")
        data = ""
        for item in self.items:
            data += "&id_list[0][]=%s" % item.id
            data += "&token=%s" % self.token
            data += "&group_id=%s" % self.mid
        req.add_data(data)
        network.urlopen(req,"mylistAPI", "mylist/delete").read()

    def add_video(self,video,description=None):
        """this adds a new item.
        """
        url = "http://www.nicovideo.jp//api/mylist/add?"
        qstr = urllib.urlencode({
            "group_id":     self.mid,
            "item_id":      video.smid,
            "item_type":    0,
            "token":self.token,
            })
        if description:
            qstr += "&"+urllib.urlencode({ "description":  description})
        data = network.urlopen( url+qstr ,"mylistAPI", "mylist/add").read()

    def create(self,name,public=False):
        """This creates a brand new mylist, and updates self.mid, which is
        assigned when API calls to niconico.
        """
        assert self.mid is None

        is_public = 0
        if public:
            is_public = 1

        cmdurl = "http://www.nicovideo.jp/api/mylistgroup/add"
        q = {
            'name':         name, 
            'description':  "",
            'public':       is_public,
            'default_sort': 0,
            'icon_id':      0,
            'token':        self.token,
        }
        cmdurl += "?" + urllib.urlencode(q)
        j = json.load( network.urlopen(cmdurl, "mylistAPI", "mylistgroup/add"), encoding='utf8')

        assert j['status'] == 'ok'
        self.mid = j["id"]

    def drop(self):
        """this drops mylist itself. DO NOT USE if you delete all items in mylist.
        use truncate() for that purpose.
        """
        cmdurl = "http://www.nicovideo.jp/api/mylistgroup/delete"
        q = {
            'group_id':     self.mid,
            'token':        self.token,
        }
        cmdurl += "?" + urllib.urlencode(q)
        j = json.load( network.urlopen(cmdurl, "mylistAPI", "mylistgroup/delete"), encoding='utf8')
        assert j['status'] == 'ok'

    def delete_item(self, item):
        """this deletes one item that mylist has. You should know the item object is
        NOT ncutils.Video, so it is a bit difficult to use.
        """
        req = urllib2.Request("http://www.nicovideo.jp//api/mylist/delete")
        data =  ""
        data += "&id_list[0][]=%s" % item.id
        data += "&token=%s" % self.token
        data += "&group_id=%s" % self.mid
        req.add_data(data)
        network.urlopen(req,"mylistAPI", "mylist/delete").read()

