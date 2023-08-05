#!/usr/bin/python
# -*- coding: utf-8 -*-

from initial_load import InitialLoad
from update_from_google import UpdateFromGoogle
from update_to_google import UpdateToGoogle
from settings import Settings
from mekk.greader import GoogleReaderClient, GoogleLoginFailed #, GoogleOperationFailed
from mekk.feeds.orgfile import OrgFile
import sys,os

import logging
#logging.basicConfig(level = logging.DEBUG)
logging.basicConfig(level = logging.WARN)

COMMANDS = dict(
    init = InitialLoad,
    get = UpdateFromGoogle,
    put = UpdateToGoogle,
)

def help():
    print """Usage:
    
%(name)s init  - create initial feeds.org

   Downloads your current Google Reader subscriptions, and saves
   them as (new) feeds.org file. Use it only once.

%(name)s get   - update feeds.org

   Checks for the feeds newly subscribed in Google Reader and 
   adds them to the (existing) feeds.org file.

%(name)s put   - push changes back to Google Reader

   Analyzes the feeds.org file (= your edits) and saves those changes
   back to Google Reader:
   - unsubscribes feeds marked as :disabled:
   - adds/removes Reader tags according to the file structure
   - subscribes new feeds (in particular, those no longer :disabled:)

%(name)s configure - reconfigure the script

   Change your Google username, customize the feeds file location.

""" % dict(name = os.path.basename(sys.argv[0]))

def main():
    settings = Settings()

    command = ""
    if len(sys.argv) == 2:
        command = sys.argv[1]
    if not command or command == "help":
        help()
        sys.exit(1)

    if command == "configure":
        settings.reconfigure()

    while True:
        try:
            auth = settings.google_auth()
            reader = GoogleReaderClient(** auth)
        except GoogleLoginFailed:
            print "Login to Google (as %s) failed" % auth['login']
            settings.query_google_credentials()
        else:
            break

    if command == "configure":
        return

    org_file = OrgFile(settings.org_file(), True)
    
    cmdobj = COMMANDS[sys.argv[1]](reader, org_file)
    cmdobj.execute()


