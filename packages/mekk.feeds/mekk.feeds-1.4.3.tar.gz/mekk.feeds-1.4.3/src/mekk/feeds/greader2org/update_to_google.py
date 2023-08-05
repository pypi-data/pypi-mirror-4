#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict
import re
import sys
import logging

from base_command import BaseCommand
from helpers import true_categories

log = logging.getLogger("greader2org")

CHANGES_LIMIT = 10000

class UpdateToGoogle(BaseCommand):
    """
    Forward changes from feeds file to GoogleReader
    """

    def execute(self):

        rc = self.reader

        subs = rc.get_subscription_list()
        
        # tag (dla nieotagowanych 'ZZZ: Unlabeled') ---> lista elementów
        subscribed = defaultdict(lambda : [])
        
        # Klucz: url feedu
        # Wartości: słowniczek o polach feed_url, title, categories (lista!)
        all_google_feeds = dict()

        for item in subs['subscriptions']:
            feed_url = item['id']
            if feed_url.startswith("feed/"):
                feed_url = feed_url[5:]
            elif feed_url.startswith("user/"):
                continue   # starred, broadcast itp
            else:
                raise Exception("Ugly feed: %s" % feed_url)

            title = item['title']
            cat = [ x['label'] for x in true_categories(item['categories']) ]
        
            all_google_feeds[ feed_url ] = dict(
                title = title, categories = cat, feed_url = feed_url )

        changes_count = 0
        
        for folder in self.org.folders:
            for org_feed in folder.feeds:
                gf = all_google_feeds.get( org_feed.feed )
                if gf:
                    old_url = gf['feed_url']
        
                if 'disabled' in org_feed.tags:
                    if gf:
                        print "Disabled feed, unsubscribing: %s" % org_feed.title
                        rc.unsubscribe_feed(old_url)
                        changes_count += 1
                        if changes_count >= CHANGES_LIMIT:
                            sys.exit(0)
                    continue
        
                new_url = org_feed.feed
        
                if not gf:
                    print "New (or un-disabled) feed, subscribing: %s" % org_feed.title
                    rc.subscribe_feed(new_url, org_feed.title)
                    rc.add_feed_tag(new_url, org_feed.title, folder.folder_label)
                    changes_count += 1
                    if changes_count >= CHANGES_LIMIT: sys.exit(0)
        
                elif new_url != old_url:
                    print "Feed url changed from %s to %s, resubscribing" % (old_url, new_url)
                    rc.subscribe_feed(new_url, org_feed.title)
                    rc.add_feed_tag(new_url, org_feed.title, folder.folder_label)
                    rc.unsubscribe_feed(old_url)
                    changes_count += 1
                    if changes_count >= CHANGES_LIMIT: sys.exit(0)
                else:
                    if org_feed.title != gf['title']:
                        print "Changing title from %s to %s" % (gf['title'], org_feed.title)
                        rc.change_feed_title(new_url, org_feed.title)
                    categories = gf['categories']
                    if not (folder.folder_label in categories):
                        print "Adding feed %s to folder %s" % (
                            org_feed.title, folder.folder_label)
                        rc.add_feed_tag(new_url, org_feed.title, folder.folder_label)
                        changes_count += 1
                        if changes_count >=CHANGES_LIMIT: sys.exit(0)
                    for cat in categories:
                        if cat != folder.folder_label:
                            print "Removing feed %s from folder %s" % (
                                org_feed.title, cat)
                            rc.remove_feed_tag(new_url, org_feed.title, cat)
                            changes_count += 1
                            if changes_count >= CHANGES_LIMIT: sys.exit(0)
        
                
