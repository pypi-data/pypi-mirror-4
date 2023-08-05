# -*- coding: utf-8 -*-

"""
Prosty parser pliku .org - szczególny, zakładający 'mój' format
"""

import pyparsing as pyp

class OrgParser(object):
    """
    Obsługa parsowania 'mojego' dialektu plików .org. Zakładamy
    dwa poziomy zagnieżdżenia (główny - foldery i drugi - feedy),
    do tego feedy mogą mieć :atrybuty: a tekst ma specyficzny
    format
    
    tag: wartość
    tag2: wartość
    """

    # Nie łap mi newline
    pyp.ParserElement.setDefaultWhitespaceChars(" \t")

    NL = pyp.LineEnd().suppress()

    comment_line = pyp.Suppress(
        pyp.Literal("#") + pyp.restOfLine + NL)("comment_line")
    empty_line = pyp.Suppress(
        pyp.Empty() + NL)("empty_line")
    ignored_line = pyp.Or([comment_line, empty_line])("ignored_line")

    setting_list = pyp.dictOf(
         pyp.Word(pyp.alphas + "_") \
         + pyp.Literal(": ").suppress(),
         pyp.restOfLine + NL)
    
    feed_title_only = pyp.restOfLine.copy()
    feed_title_only.setParseAction(lambda t: t[0].rstrip(' '))

    feed_title = \
        pyp.Literal("** ").suppress() \
        + feed_title_only.setResultsName("title") \
        + NL

    folder_title = \
        pyp.Literal("* ").suppress() \
        + pyp.restOfLine.copy().setResultsName("folder_label") \
        + NL

    feed_info = pyp.Group( 
        feed_title
        + pyp.ZeroOrMore(empty_line)
        + setting_list
        + pyp.ZeroOrMore(empty_line)
        )

    folder = pyp.Group(
        folder_title
        + pyp.ZeroOrMore(empty_line)
        + pyp.OneOrMore(feed_info).setResultsName("feeds") )

    content = pyp.OneOrMore(
        pyp.MatchFirst([
                folder,
                comment_line,
                empty_line,
                ] ))

    grammar = pyp.Dict(content)

    def parse(self, org_file):
        f = open(org_file, "r")
        contents = f.read()
        f.close()

        reply = self.grammar.parseString(contents, parseAll = True)
        return reply


