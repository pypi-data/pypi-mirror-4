# -*- coding: utf-8 -*-

import os
import ConfigParser
import keyring
import getpass

AUTH_SECTION = 'google-auth'
FILE_SECTION = 'files'
USERNAME_OPTION = 'login'
FILE_OPTION = 'feeds_file'

KEYRING_ENTRY = 'greader2org'

class Settings(object):

    SETTINGS_DIR = os.path.abspath(os.path.expanduser("~/.feeds")) 

    def __init__(self, dir = SETTINGS_DIR):
        self._dir = dir
        if not os.path.exists(self._dir):
            os.mkdir(self._dir)

        self._ini_file = os.path.join(self._dir, "feeds.ini")

        config = ConfigParser.SafeConfigParser({})
        config.read(self._ini_file)
        self._config = config

        if not config.has_section(AUTH_SECTION):
            config.add_section(AUTH_SECTION)
        if not config.has_section(FILE_SECTION): 
            config.add_section(FILE_SECTION)
           
        if not config.has_option(AUTH_SECTION, USERNAME_OPTION):
            self.query_google_credentials()
        if not config.has_option(FILE_SECTION, FILE_OPTION):
            self.query_feeds_location()

        self._config = config

    def google_auth(self):
        login = self.google_login()
        password = self.google_password()
        if not password:
            self.query_google_credentials()
            return self.google_auth()
        return dict(login = login,
                    password = password)

    def org_file(self):
        name = self.org_file_name()
        if not name:
            self.query_feeds_location()
            name = self.org_file_name()
        return name

    def google_login(self):
        return self._config.get(AUTH_SECTION, USERNAME_OPTION)
    def google_password(self):
        return keyring.get_password(KEYRING_ENTRY, self.google_login())

    def org_file_name(self):
        return self._config.get(FILE_SECTION, FILE_OPTION)

    def query_feeds_location(self):
        self._query_option("Feeds file location",
                           FILE_SECTION, FILE_OPTION,
                           os.path.join(self._dir, "feeds.txt"))
        self._config.write(open(self._ini_file, 'w'))

    def query_google_credentials(self):
        login = self._query_option("Your Google account name",
                                   AUTH_SECTION, USERNAME_OPTION)
        if login.find('@') < 0:
            login = login + '@gmail.com'
            self._config.set(AUTH_SECTION, USERNAME_OPTION, login)
        self._config.write(open(self._ini_file, 'w'))

        self._query_password("Your Google password", login)

    def reconfigure(self):
        self.query_feeds_location()
        self.query_google_credentials()

    def _query_password(self, label, login):
        old_password = self.google_password()
        while True:
            if old_password:
                new_password = getpass.getpass("%s for %s (or Enter to keep old password): " % (label, login)).strip()
                if not new_password:
                    new_password = old_password
            else:
                new_password = getpass.getpass("%s for %s: " % (label, login)).strip()
            if new_password:
                break
        keyring.set_password(KEYRING_ENTRY, login, new_password)

    def _query_option(self, label, section, option, default = None):
        config = self._config
        if config.has_option(section, option):
            prev_value = config.get(section, option)
        else:
            prev_value = default
        while True:
            if prev_value:
                new_value = raw_input("%s (or Enter to keep %s): " % (label, prev_value)).strip()
                if not new_value:
                    new_value = prev_value
            else:
                new_value = raw_input("%s: " % label).strip()
            if new_value:
                break
        config.set(section, option, new_value)
        return new_value


