import os, sys, re, urllib, urllib2, cgi, json
import  __init__ as ncutils

username = os.environ.get("TEST_NICOUSER")
password = os.environ.get("TEST_NICOPASSWORD")
assert ncutils.login(username, password) 
def _pretty_xml(xmldata):
    """some sites say it can, but idown now"""
    return xmldata
def _pretty_qs(data):
    info = cgi.parse_qs(data)
    return json.dumps(info, sort_keys=True, indent=2, separators=(',', ':'))
def _pretty_json(data):
    return json.dumps(json.loads(data), sort_keys=True, indent=2, separators=(',', ':'))

def pretty_print_gethumbinfo():
    url = "http://www.nicovideo.jp/api/getthumbinfo/sm9"
    xmldata = urllib2.urlopen(url).read()
    print "-----------------------------------------------------------------------------"
    print "---------------- [getthumbinfo] just dump raw xml data ---------- -----------"
    print "-----------------------------------------------------------------------------"
    print _pretty_xml(xmldata)
    print "-----------------------------------------------------------------------------"

def pretty_print_getflv():
    url = "http://www.nicovideo.jp/api/getflv?v=sm9&as3=1"
    data = urllib2.urlopen(url).read()
    print "-----------------------------------------------------------------------------"
    print "---------------- [getflv] convert querystring to dict to jsondump -----------"
    print "-----------------------------------------------------------------------------"
    print _pretty_qs(data)
    print "-----------------------------------------------------------------------------"

def pretty_print_mylistgroup_list():
    def _token():
        html = urllib2.urlopen("http://www.nicovideo.jp/my/mylist").read()
        mo = re.search(r'\s*NicoAPI\.token = "(?P<token>[\d\w-]+)";\s*',html)
        return mo.group("token")
    url = "http://www.nicovideo.jp/api/mylistgroup/list?token=%s" %( _token(), )
    data = urllib2.urlopen(url).read()
    print "-----------------------------------------------------------------------------"
    print "---------------- [mylistgroup/list] json dump -------------------------------"
    print "-----------------------------------------------------------------------------"
    print _pretty_json(data)
    print "-----------------------------------------------------------------------------"

def pretty_print_video_array():
    url = "http://i.nicovideo.jp/v3/video.array?v=sm9,sm9,sm9"
    xmldata = urllib2.urlopen(url).read()
    print "-----------------------------------------------------------------------------"
    print "---------------- [/v3/video.array] just dump raw xml data -------------------"
    print "-----------------------------------------------------------------------------"
    print _pretty_xml(xmldata)
    print "-----------------------------------------------------------------------------"

pretty_print_gethumbinfo()
pretty_print_getflv()
pretty_print_mylistgroup_list()
pretty_print_video_array()
