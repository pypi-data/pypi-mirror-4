#!/usr/bin/python
# Thomas Perl <thp@gpodder.org>, 2009-01-03

"""
Summary

Text-based visual translation completeness summary

Usage: make statistics | python summary.py

"""

import re
import sys
import math


#pylint: disable-msg=R0913
class Language(object):
    """Language calculator"""
    def __init__(self, code, updated, translated, fuzzy, untranslated):
        self.code = code
        self.updated = updated
        self.translated = int(translated)
        self.fuzzy = int(fuzzy)
        self.untranslated = int(untranslated)

    def __get_ratio(self, value):
        "get ratio"
        return value / float(self.translated + self.fuzzy + self.untranslated)

    def get_translated_ratio(self):
        "translated strings ratio"
        return self.__get_ratio(float(self.translated))

    def get_fuzzy_ratio(self):
        "fuzzy strings ratio"
        return self.__get_ratio(float(self.fuzzy))

    def get_untranslated_ratio(self):
        "untranslated strings ratio"
        return self.__get_ratio(float(self.untranslated))

    def __cmp__(self, other):
        return cmp(self.get_translated_ratio(), other.get_translated_ratio())

if __name__ == '__main__':
    WIDTH = 40
    LANGUAGES = []
    for line in sys.stdin:
        match = re.match(
            '^(..)\.po \(([^)]*)\): ('
            '(\d+) translated message[s]?)?'
            '(, (\d+) fuzzy translation[s]?)?'
            '(, (\d+) untranslated message[s]?)?\.', line).groups()

        LANGUAGES.append(Language(
                match[0], match[1], match[3] or '0',
                match[5] or '0',
                match[7] or '0')
        )

        sys.stdout.write("\n")
        sys.stdout.write(" " * 20 + "--== Sleipnir translation summary == --")
        sys.stdout.write("\n")

    for language in sorted(LANGUAGES):
        tc = '#' * (int(math.floor(WIDTH * language.get_translated_ratio())))
        fc = '~' * (int(math.floor(WIDTH * language.get_fuzzy_ratio())))
        uc = ' ' * (WIDTH - len(tc) - len(fc))

        sys.stdout.write(
            ' %s (%s) [%s%s%s] -- %3.0f %% translated' %
            (language.code,
             language.updated,
             tc, fc, uc,
             language.get_translated_ratio() * 100)
            )

    sys.stdout.write("\n")
    sys.stdout.write('\tTotal translations: %d' % len(LANGUAGES))
    sys.stdout.write("\n")
