"""Niconico douga module

See also https://github.com/sakamotomsh/ncutils
"""
__version__ = '0.3.0'

#root logger setting.
import logging, logging.handlers
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
try:
    handler = logging.handlers.SysLogHandler(address="/dev/log")
except:
    handler = logging.StreamHandler()
finally:
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)

import time
import urllib, urllib2, cgi

import network

# module public class
from video  import Video
from mylist import Mylist
from search import Search
from watch  import Watch

def login(user,password):
    """This provides login API.
    returns True if login is done successfully
    """
    return _NicoVideo.login(user,password)

def is_logged_in():
    """This method is provided to ensure I am logged_in.
    returns True if I'm already logged_in. Take care with it,
    because this method internally call niconico API(getflv for sm9). 
    """
    return _NicoVideo.is_logged_in()

class _NicoVideo(object):
    logged_in = False

    @staticmethod
    def login(user, password):

        if _NicoVideo.logged_in: #better to use islogged_in()? but I dont issue getflv more
            return True

        req = urllib2.Request("https://secure.nicovideo.jp/secure/login?site=niconico")
        req.add_data( urllib.urlencode( {"mail":user, "password":password} ))
        res = network.urlopen(req, "login", "logged in.")

        if res.geturl() == 'http://www.nicovideo.jp/':
            #login succeeds if we are redirected to the top page.
            _NicoVideo.logged_in = True

        return _NicoVideo.logged_in

    @staticmethod
    def is_logged_in():
        try:
            video = Video("sm9")
            assert video.me_id is not None
            return True
        except Exception, e:
            return False
