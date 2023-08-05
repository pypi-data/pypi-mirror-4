"""Some examples to use ncutils.

functions are loaded and transformed to executables by setuptools.
"""
import os, json, optparse
import __init__ as ncutils

class Config(object):
    def __init__(self):
        parser = optparse.OptionParser()
        opts, args = parser.parse_args()
        self.conf = {
            "opts": opts,
            "args": args,
        }
        self._update_conf_via_file()

    def _update_conf_via_file(self):
        confpath = os.path.expanduser(os.path.join( "~", ".ncutils"))
        with open(confpath) as f:
            self.conf.update(json.load(f))

    def get_config(self):
        return self.conf

def setup():
    conf = Config().get_config()
    assert ncutils.login( conf["username"], conf["password"] )
    return conf

def download_video():
    conf = setup()
    for smid in conf["args"]:
        try:
            video = ncutils.Video(smid)
            video.download()
        except Exception, e:
            print e

def download_video_in_mylist():
    conf = setup()
    mlist = ncutils.Mylist(conf["args"][0])
    for video in mlist.videolist:
        try:
            video.download()
        except Exception, e:
            print e

def download_video_and_remove_entry_from_mylist():
    conf   = setup()
    queue  = ncutils.Mylist(conf["queue_id"])
    dstdir = conf["queue_storage"]

    os.chdir(dstdir)
    targets = queue.items
    for target in targets:
        try:
            print "start: smid:%s" % (target.video.smid,)
            target.video.download()
            queue.delete_item(target)
        except Exception, e:
            print "err" + e.__str__()

