import chardet
import re


cp1252 = {
    u'\x80': u'\u20AC',  # EURO SIGN
    u'\x82': u'\u201A',  # SINGLE LOW-9 QUOTATION MARK
    u'\x83': u'\u0192',  # LATIN SMALL LETTER F WITH HOOK
    u'\x84': u'\u201E',  # DOUBLE LOW-9 QUOTATION MARK
    u'\x85': u'\u2026',  # HORIZONTAL ELLIPSIS
    u'\x86': u'\u2020',  # DAGGER
    u'\x87': u'\u2021',  # DOUBLE DAGGER
    u'\x88': u'\u02C6',  # MODIFIER LETTER CIRCUMFLEX ACCENT
    u'\x89': u'\u2030',  # PER MILLE SIGN
    u'\x8A': u'\u0160',  # LATIN CAPITAL LETTER S WITH CARON
    u'\x8B': u'\u2039',  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    u'\x8C': u'\u0152',  # LATIN CAPITAL LIGATURE OE
    u'\x8E': u'\u017D',  # LATIN CAPITAL LETTER Z WITH CARON
    u'\x91': u'\u2018',  # LEFT SINGLE QUOTATION MARK
    u'\x92': u'\u2019',  # RIGHT SINGLE QUOTATION MARK
    u'\x93': u'\u201C',  # LEFT DOUBLE QUOTATION MARK
    u'\x94': u'\u201D',  # RIGHT DOUBLE QUOTATION MARK
    u'\x95': u'\u2022',  # BULLET
    u'\x96': u'\u2013',  # EN DASH
    u'\x97': u'\u2014',  # EM DASH
    u'\x98': u'\u02DC',  # SMALL TILDE
    u'\x99': u'\u2122',  # TRADE MARK SIGN
    u'\x9A': u'\u0161',  # LATIN SMALL LETTER S WITH CARON
    u'\x9B': u'\u203A',  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    u'\x9C': u'\u0153',  # LATIN SMALL LIGATURE OE
    u'\x9E': u'\u017E',  # LATIN SMALL LETTER Z WITH CARON
    u'\x9F': u'\u0178',  # LATIN CAPITAL LETTER Y WITH DIAERESIS
}


def encode_and_fix(string):
    _, encoding = chardet.detect(string).values()
    string = string.decode(encoding)
    if encoding in ['cp1252', 'cp-1252', 'windows1252', 'windows-1252', 'ISO-8859-2']:
        string = re.sub(u'[\x80-\x9f]', lambda m: cp1252.get(m.group(0)), string)
    return string
