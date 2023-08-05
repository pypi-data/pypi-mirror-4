#!/usr/bin/python
# -*- coding: utf-8 -*-

from mekk.feeds.orgfile import Folder, Feed
from collections import defaultdict
from base_command import BaseCommand
from helpers import true_categories
import logging, re

log = logging.getLogger("greader2org")

WARN_MULTIPLE_CATEGORIES = False

class UpdateFromGoogle(BaseCommand):
    """
    Uzupełnia plik feeds.org na bazie zawartości w Google
    """

    def execute(self):
        if not self.org.exists():
            raise Exception("%s does not exist. Use\n  greader2org init\nto create initial version" % self.org.file_name)

        subs = self.reader.get_subscription_list()

        # tag (dla nieotagowanych 'ZZZ: Unlabeled') ---> lista elementów
        subscribed = defaultdict(lambda : [])
        
        all_google_feeds = set()

        for item in subs['subscriptions']:
            feed_url = item['id']
            if feed_url.startswith("feed/"):
                feed_url = feed_url[5:]
            elif feed_url.startswith("user/"):
                continue   # starred, broadcast itp
            else:
                raise Exception("Ugly feed: %s" % feed_url)
        
            title = item['title']
        
            folder = "ZZZ: Unlabeled"
            cat = true_categories( item['categories'] )
            if len(cat) > 0:
                folder = cat[0]['label']
                if len(cat) > 1:
                    if WARN_MULTIPLE_CATEGORIES:
                        log.warn("Multiple categories for %s. Using first one of: %s" % (
                            item['id'], ", ".join((x['label'] for x in cat))))
        
            if not self.org.find_feed(feed_url):
                print "New feed %s in category %s" % (title, folder)
                lab = self.org.find_or_create_folder(folder)
                lab.add_feed(
                    Feed(title=title, 
                         tags=[], 
                         feed=feed_url, 
                         level=None, 
                         comment=None))
        
            all_google_feeds.add(feed_url)
        
        # Marking unsubscribed feeds as disabled, and other cleanups
        for folder in self.org.folders:
            for org_feed in folder.feeds:
                if org_feed.feed not in all_google_feeds:
                    if 'disabled' not in org_feed.tags:
                        print "Marking unsubscribed feed %s as disabled" % org_feed.title
                        org_feed.tags.append('disabled')
        
        self.org.save_to()
