# -*- coding: utf-8 -*-

"""
Obsługa modyfikowania pliku .org
"""

import os, re
from org_parse import OrgParser

FILL_COLUMN = 65
STOP_COLUMN = 80

class Folder(object):
    def __init__(self, folder_label):
        self.folder_label = folder_label
        self.feeds = []
    def add_feed(self, feed):
        self.feeds.append(feed)
    def save(self, f):
        f.write("* %s\n\n" % self.folder_label.encode("utf-8"))
        for feed in self.feeds:
            feed.save(f)
    def find_feed(self, url):
        for c in (f.find_feed(url) for f in self.feeds):
            if c:
                return c
        return None
    def remove_feed(self, feed):
        self.feeds.remove(feed)
    def find_folder(self, folder_label):
        if self.folder_label == folder_label:
            return self
        else:
            return None
    def sort_items(self):
        self.feeds.sort( key = lambda x: (x.title, x.feed, hash(x)) )

class Feed(object):
    def __init__(self, title, tags, feed, level, comment):
        self.title = title.replace("\n", " ").replace("\r", "")
        self.tags = (tags or [])
        self.feed = feed
        self.level = level
        self.comment = comment

    def save(self, f):
        f.write("** %s" % self.title.encode("utf-8"))
        if self.tags:
            tag_txt = ":".join([''] + self.tags + [''])
            spaces = max(2, STOP_COLUMN - len(tag_txt) - len(self.title) - 3)
            f.write(" " * spaces)
            f.write(tag_txt)
        f.write("\n\n")
        for name, value in [
            ('feed', self.feed),
            ('level', self.level),
            ('comment', self.comment),
            ]:
            if value:
                f.write(("   %s: %s\n" % (name, value)).encode("utf-8"))
        f.write("\n")

    def find_feed(self, url):
        """
        Jeśli url jest równy "mojemu" urlowi - to zwracam siebie. Wpp None
        """
        if self.feed and self.feed == url:
            return self
        return None

class OrgFile(object):

    _re_tags = re.compile(":((?:[a-z]+:)+)\s*$")

    def __init__(self, file_name, auto_sort_items = False):
        """
        Otwiera i parsuje plik, wczytując z niego dane.
        Jeśli pliku nie ma, zapamiętuje wyłącznie nazwę.

        Parametr auto_sort_items pozwala decydować, czy przesortować
        wyniki alfabetycznie (foldery i feedy w ramach folderów)
        po wczytaniu
        """
        self.file_name = file_name
        
        self.folders = []

        if os.path.exists(file_name):
            parser = OrgParser()
            parsed = parser.parse(self.file_name)
            for lbidx in xrange(0, len(parsed)):
                lb = parsed[lbidx]
                folder = Folder(lb.folder_label.decode("utf-8"))
                for feed in lb.feeds:
                    title = feed.title.decode("utf-8")
                    tags = []
                    m = self._re_tags.search(title)
                    if m:
                        title = m.string[0:m.start(0)].rstrip()
                        tags = m.group(1).split(':')[0:-1]
                    folder.add_feed(
                        Feed(title=title,
                             tags=tags,
                             feed=feed.feed.decode("utf-8"), 
                             level=feed.level,
                             comment=feed.comment.decode("utf-8")))
                    for name, value in feed.items():
                        if not name in ['feed', 'title', 'level', 'comment']:
                            print "Removing unknown attribute %s (value %s) from feed %s" % (name, value, title)
                self.folders.append(folder)
            if auto_sort_items:
                self.sort_items()

    def sort_items(self):
        self.folders.sort( key = lambda x: (x.folder_label, hash(x)) )
        for f in self.folders:
            f.sort_items()

    def exists(self):
        return os.path.exists(self.file_name)

    def save_to(self, file_name = None):
        if not file_name:
            file_name = self.file_name
        f = file(file_name, "w")
        self.save(f)

    def save(self, f):
        f.write("""# -*- mode: org; fill-column: %d -*-
#
#+STARTUP: showstars
#+TITLE: Subscribed feeds
#+TAGS: disabled private important alert massive

""" % FILL_COLUMN)
        for folder in self.folders:
            folder.save(f)
    
    def find_feed(self, url):
        for c in (l.find_feed(url) for l in self.folders):
            if c:
                return c
        return None

    def add_folder(self, folder):
        self.folders.append(folder)

    def find_folder(self, folder_label):
        for c in (l.find_folder(folder_label) for l in self.folders):
            if c:
                return c
        return None
        
    def find_or_create_folder(self, folder_label):
        f = self.find_folder(folder_label)
        if not f:
            f = Folder(folder_label)
            self.folders.append(f)
        return f
