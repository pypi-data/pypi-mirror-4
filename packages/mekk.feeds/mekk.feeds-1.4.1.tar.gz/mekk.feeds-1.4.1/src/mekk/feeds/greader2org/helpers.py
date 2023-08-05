# -*- coding: utf-8 -*-

"""
Drobne funkcje pomocnicze
"""

def true_categories(names):
    """
    Przefiltrowywuje listę kategorii pobraną z readera, odrzucając
    śmieci typu blogger-following.

    Parametr to lista słowników o polach id i label
    """
    return [ x for x in names 
             if x['id'].startswith('user/') and not x['label'] == 'blogger-following' ]
