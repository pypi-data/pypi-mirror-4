import os, sys, re, tempfile, logging, StringIO
import urllib ,urllib2, cgi
import xml.etree.ElementTree

import base
import network

logger = logging.getLogger(__name__)

class Video(base.BaseObject):
    """Video object.

    All video has its unique ID matching ^[sn]md+$. You can see that by its
    watch URL. For example, sm9 is a famous Onmoji video.
    
    ncutils.Video has to be instantiated with this ID. Once instantiated, you
    can access varieties of attributes such as title, comment_num, and so on.
    These attributes originally needs API call to niconico, but you need not
    care about it, because this attribute accessor internally calls them.

    Attributes to be noted
        - smid: ID
        - title: title
        - tags: 
        - comments
        - thumbdata
    """

    def __str__(self):
        return "[video] %s" % (self.smid , )

    def __unicode__(self):
        return "[video] %s %s" % (self.smid , self.title[:15])

    def __init__(self,smid):
        self.smid  = smid
        # properties gethumbinfo provides
        self.prop_info = (
            #getthumbinfo
            ("status",          self._update_via_getthumbinfo),
            ("title",           self._update_via_getthumbinfo),
            ("description",     self._update_via_getthumbinfo),
            ("thumbnail_url",   self._update_via_getthumbinfo),
            ("first_retrieve",  self._update_via_getthumbinfo),
            ("length",          self._update_via_getthumbinfo),
            ("movie_type",      self._update_via_getthumbinfo),
            ("size_high",       self._update_via_getthumbinfo),
            ("size_low",        self._update_via_getthumbinfo),
            ("view_counter",    self._update_via_getthumbinfo),
            ("comment_num",     self._update_via_getthumbinfo),
            ("mylist_counter",  self._update_via_getthumbinfo),
            ("last_res_body",   self._update_via_getthumbinfo),
            ("watch_url",       self._update_via_getthumbinfo),
            ("thumb_type",      self._update_via_getthumbinfo),
            ("embeddable",      self._update_via_getthumbinfo),
            ("no_live_play",    self._update_via_getthumbinfo),
            ("user_id",         self._update_via_getthumbinfo),
            ("tags",            self._update_via_getthumbinfo),
            #getflv
            ("thread_id",       self._update_via_getflv),
            ("l",               self._update_via_getflv),
            ("url",             self._update_via_getflv),
            ("link",            self._update_via_getflv),
            ("ms",              self._update_via_getflv),
            ("me_id",           self._update_via_getflv),
            ("me_premium",      self._update_via_getflv),
            ("me_nickname",     self._update_via_getflv),
            ("done",            self._update_via_getflv),
            ("hms",             self._update_via_getflv),
            ("hmsp",            self._update_via_getflv),
            ("hmst",            self._update_via_getflv),
            ("hmstk",           self._update_via_getflv),
            ("rpu",             self._update_via_getflv),
            #msg api
            ("comments",        self._update_via_msgapi),
            ("ticket",          self._update_msg_token),
            ("postkey",         self._update_msg_token),
            # other properties
            ("thumbdata",       self._update_thumbdata),
            ("proper_name",     self._update_proper_name),
        )

    def _update_via_getthumbinfo(self,image=False):
        APIURL = "http://www.nicovideo.jp/api/getthumbinfo/%s"
        data = network.urlopen( APIURL%(self.smid,), "getthumbinfo", "getthumbinfo").read()
        etree = xml.etree.ElementTree.XML(data)

        restype = etree.attrib["status"]
        if restype == 'ok':
            self._status = 'ok'
        else:
            self._status = etree.find("error/code").text.lower()
            description = etree.find("error/description").text
            logger.warn("getthumbinfo for %s cannot success: %s, %s",self.smid,self.status,description) 
            logger.warn("getthumbinfo for %s cannot success",self.smid) 

        # extract information
        def _data(name, errvalue=None): 
            try:
                return etree.find("thumb/%s" % (name,)).text
            except Exception,e:
                logger.warn("cannot retrieve %s" % name ) 
                return errvalue

        self._title         = _data("title")
        self._description   = _data("description")
        self._thumbnail_url = _data("thumbnail_url")
        self._first_retrieve= _data("first_retrieve")
        self._length        = _data("length")
        self._movie_type    = _data("movie_type")
        self._size_high     = int(_data("size_high",0))
        self._size_low      = int(_data("size_low",0))
        self._view_counter  = int(_data("view_counter",0))
        self._comment_num   = int(_data("comment_num",0))
        self._mylist_counter= int(_data("mylist_counter",0))
        self._watch_url     = _data("watch_url")
        self._thumb_type    = _data("thumb_type")
        self._embeddable    = int(_data("embeddable",0))
        self._no_live_play  = int(_data("no_live_play",0))
        self._user_id       = int(_data("user_id",0))

        # tag manupulation
        self._tags          = []
        for tags in etree.findall("thumb/tags"):
            if tags.attrib["domain"] != "jp":
                continue
            for tag in tags.findall("tag"):
                self._tags.append(tag.text)    

    def _update_via_getflv(self):
        APIURL = "http://www.nicovideo.jp/api/getflv?v=%s&as3=1"

        self._update_via_getthumbinfo()

        resdata = network.urlopen(APIURL%(self.smid,), "getflv", "getflv for %s"%(self.smid,)).read()
        response = cgi.parse_qs(resdata)

        self._thread_id = response.get("thread_id", [None])[0]
        self._l         = response.get("l", [None])[0]
        self._url       = response.get("url", [None])[0] #important. video src url
        self._link      = response.get("link", [None])[0] #ihan?
        self._ms        = response.get("ms", [None])[0] #message server? i.e. http://msg.nicovideo.jp/10/api/
        self._me_id     = response.get("user_id", [None])[0] #WARN:name duplicate (from getthumbinfo).
        self._me_premium= response.get("is_premium", [None])[0]
        self._me_nickname=response.get("nickname", [None])[0]
        self._calltime  =response.get("time", [None])[0]#unix_epoch when getflv has been called.
        self._done      =response.get("done", [None])[0]
        self._hms       =response.get("hms",[None])[0] #hiroba url?
        self._hmsp      =response.get("hmsp",[None])[0] #????
        self._hmst      =response.get("hmst",[None])[0] #????
        self._hmstk     =response.get("hmstk",[None])[0] #????
        self._rpu       =response.get("rpu",[None])[0] #????
        return self

    def _update_via_msgapi(self):
        APIURL = "%sthread" %(self.ms, )
        APIURL += "?" + urllib.urlencode({"version":"20061206", "thread" :self.thread_id,})

        data = network.urlopen(APIURL, "messageAPI", "").read()
        etree = xml.etree.ElementTree.XML(data)

        self._comments = []
        class Comment(object): pass
        for msg in etree.findall("chat"):
            comment = Comment()
            comment.no              = msg.attrib.get("no", 0)
            comment.vpos            = msg.attrib.get("vpos", 0)
            comment.date            = msg.attrib.get("date", 0)
            comment.mail            = msg.attrib.get("mail", 0)
            comment.user_id         = msg.attrib.get("user_id", 0)
            comment.premium         = msg.attrib.get("premium", 0)
            comment.anonymity       = msg.attrib.get("anonymity", 0)
            comment.content         = msg.text

            self._comments.append(comment)
        self._comments.sort(lambda x,y: cmp(int(x.vpos), int(y.vpos) ))

    def _update_thumbdata(self):
        self._thumbdata  = network.urlopen(self.thumbnail_url, "getthumbnail", "getthumbnail data").read()

    def _update_proper_name(self):
        proper_name  = self.title
        proper_name  = proper_name.encode("sjis","ignore").decode("sjis")
        proper_name  = re.sub(r"[/?*:<>\| ]","_", proper_name)
        proper_name += ".%s.%s" % (self.smid, self.movie_type)
        # set
        self._proper_name = proper_name

    def _update_msg_token(self):
        # set _ticket and retrieve block_no
        url = self.ms + "thread?" + urllib.urlencode({"version":"20061206", "thread":self.thread_id, "res_from":"-1"})
        etree = xml.etree.ElementTree.XML(network.urlopen(url, "messageAPI", "get message token.").read())
        block_no = ( int( etree.find("chat").attrib.get("no") ) + 1 )/ 100 
        self._ticket = etree.find("thread").get("ticket")

        # set _postkey
        APIURL = "http://www.nicovideo.jp/api/getpostkey/?"
        query  = urllib.urlencode({"yugi":None, "block_no": block_no, "thread": self.thread_id, })
        data = network.urlopen(APIURL+query, "messageAPI", "getpostkey").read()
        self._postkey = cgi.parse_qs(data).get("postkey",[None])[0]

    def add_comment(self, msg, vpos="0"):
        """This enables a submission of comments.
        I dont test this much, nor will I.
        """
        # postkey varies time by time, so update _postkey is required
        self._update_msg_token()

        # setup postdata
        tmpl = '''<chat thread="%(thread_id)s" vpos="%(vpos)s" postkey="%(postkey)s" mail="184" ticket="%(ticket)s" user_id="%(user_id)s">%(msg)s</chat>'''
        info = {
            "thread_id" : self.thread_id,
            "vpos"      : vpos,
            "msg"       : msg.encode("utf8"),
            "ticket"    : self.ticket,
            "user_id"   : self.me_id,
            "postkey"   : self.postkey,
        }
        postdata = tmpl % info

        # do the work
        req = urllib2.Request(self.ms)
        req.add_data(postdata)
        res = network.urlopen(req, "messageAPI", "msg postcomment").read()

    def download(self, callback=None, storagedir=".", charaset="utf8"):
        """This downloads a video.
        the filename is automatically determined by self.proper_name.
        You can pass callback which is called every time downloaded 1MB.
        """
        #TODO: users should choose filename.
        def _dl_iterator():
            res = network.urlopen( self.url, "download", "video srcurl")
            size = res.info().getheader("Content-Length")
            chunk = res.read(1024*1024)
            yield chunk
            while chunk:
                chunk = res.read(1024*1024)
                yield chunk
            raise StopIteration()

        # Download & Save
        if self.status != 'ok':
            logger.warn("cannnot download %s", self.smid)
            return False
        with tempfile.NamedTemporaryFile() as data_fh:
            network.urlopen(self.watch_url, "watch", "watch_url access").read() #niconico requires...
            for data in _dl_iterator():
                data_fh.write(data)
                if callback: callback.downloaded_1MB()
            data_fh.seek(0)
            filepath = os.path.join(storagedir, self.proper_name)
            with open(filepath,"wb") as ofh:
                ofh.write(data_fh.read())
        return True
