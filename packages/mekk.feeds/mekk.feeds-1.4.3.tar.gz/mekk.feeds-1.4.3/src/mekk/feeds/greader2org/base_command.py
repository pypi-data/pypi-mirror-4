# -*- coding: utf-8 -*-

class BaseCommand(object):
    """
    Bazowa klasa polecenia. Po prostu zapisanie standardowych
    atrybutów
    """

    def __init__(self, reader_client, org_file):
        self.reader = reader_client
        self.org = org_file

    def execute(self):
        """
        Metoda nadmazywana w klasach potomnych. Właściwe wykonanie
        skryptu. Może używać wszystkich poniższych metod
        """
        raise NotImplementedError

