#!/usr/bin/env python
import os, sys, cmd, json
import re
import  __init__ as ncutils

class BaseContext(object):
    def __str__(self):
        return self.obj.__str__()
    def ls(self): raise Exception("Not Implemented.")
    def download(self): raise Exception("Not Implemented.")

class VideoContext(BaseContext):
    def __init__(self,smid):
        self.obj = ncutils.Video(smid)
    def ls(self):
        print "%s %s by user/%s"%(self.obj.smid, self.obj.title, self.obj.user_id)
        print "--------------------------------"
        print self.obj.description
    def download(self):
        self.obj.download()

class MylistContext(BaseContext):
    def __init__(self,mid):
        self.obj = ncutils.Mylist(mid)
    def ls(self):
        for video in self.obj.videolist:
            print video.smid, video.title
    def download(self):
        for video in self.obj.videolist:
            video.download()

class KeywordContext(BaseContext):
    def __init__(self,keyword):
        self.obj = ncutils.Search(keyword)
    def ls(self):
        for video in self.obj.videolist:
            print video.smid, video.title

class TagContext(BaseContext):
    def __init__(self,keyword):
        self.obj = ncutils.Search(keyword,mode="tag")
    def ls(self):
        for video in self.obj.videolist:
            print video.smid, video.title

class RootContext(BaseContext):
    def __str__(self):
        return "[/]"
    def __init__(self,obj=None):
        self.obj = ncutils.Mylist(None)
    def ls(self):
        for mlist in self.obj.mine:
            print "mylist/%s %s" %(mlist.mid, mlist.name)

class Context(object):
    @staticmethod
    def get_context(line):
        if line == '':
            return RootContext(None)
        elif re.match(r"^[sn]m\d+$", line):
            return VideoContext(line)
        elif re.match(r"^mylist/(\d+)$",line):
            mid = re.match(r"^mylist/(\d+)$",line).group(1)
            return  MylistContext(mid)
        elif re.match(r"^keyword/(\w+)$",line):
            keyword = re.match(r"^keyword/(\w+)$",line).group(1)
            return KeywordContext(keyword)
        elif re.match(r"^tag/(\w+)$",line):
            keyword = re.match(r"^tag/(\w+)$",line).group(1)
            return TagContext(keyword)
        else :
            return None

class NicoShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self._login()
        self.onecmd("cd")
        self.prompt  = "[/] > "
    def _login(self):
        confpath = os.path.expanduser(os.path.join( "~", ".ncutils"))
        with open(confpath) as f:
            conf = json.load(f)
        assert ncutils.login(conf["username"],conf["password"])
    def precmd(self,line):
        return line
    def postcmd(self,stop,line):
        self.prompt = self.context.__str__() + "> "
    def default(self,line):
        pass
    def do_cd(self, line):
        ctx= Context.get_context(line)
        if ctx:
            self.context = ctx
    def do_lcd(self, line):
        try:
            os.chdir(line)
        except:
            pass
    def do_lls(self, line):
        try:
            for f in os.listdir("."):
                print f
        except:
            pass

    #context related_commands
    def do_ls(self, line):
        self.context.ls()
    def do_download(self,line):
        self.context.download()
    def do_quit(self,line):
        sys.exit()
    def do_exit(self,line):
        sys.exit()

def main():
    shell = NicoShell()
    shell.cmdloop()

if __name__ == '__main__':
    main()
