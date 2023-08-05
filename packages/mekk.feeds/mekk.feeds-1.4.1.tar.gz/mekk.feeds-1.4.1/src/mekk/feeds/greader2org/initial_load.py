# -*- coding: utf-8 -*-

from base_command import BaseCommand
from collections import defaultdict
from helpers import true_categories
from mekk.feeds.orgfile import Folder, Feed

import logging

log = logging.getLogger("greader2org")

class InitialLoad(BaseCommand):
    """
    Initial import from Google Reader (creating first version
    of text mirror file).
    """

    def execute(self):

        if self.org.exists():
            raise Exception("File %s already exists.\nTo update it, use 'get' option instead of 'init'" % self.org.file_name)
        
        subs = self.reader.get_subscription_list()
        
        # tag (for untagged 'ZZZ: Unlabeled') ---> list of matching elements
        subscribed = defaultdict(lambda : [])
        
        for item in subs['subscriptions']:
            feed = item['id']
            if feed.startswith("feed/"):
                feed = feed[5:]
            elif feed.startswith("user/"):
                continue   # starred, broadcast itp
            else:
                raise Exception("Ugly feed: %s" % feed)
        
            title = item['title']
        
            label = "ZZZ: Unlabeled"
            cat = true_categories( item['categories'] )
            if len(cat) > 0:
                label = cat[0]['label']
                if len(cat) > 1:
                    log.warn("Multiple folders for %s. Using first one of: %s" % (
                        item['id'], ", ".join((x['label'] for x in cat))))
        
            subscribed[label].append( dict(feed = feed, title = title) )

        for label in sorted(subscribed.keys()):
            folder = Folder(label)
            self.org.add_folder(folder)

            print "Creating folder %s" % label

            for info in subscribed[label]:
                feed = Feed(title=info['title'],
                            tags=[], 
                            feed=info['feed'],
                            level=None, 
                            comment="")
                folder.add_feed(feed)
                print "   adding feed %s" % info['title']
        
        self.org.save_to()
                
