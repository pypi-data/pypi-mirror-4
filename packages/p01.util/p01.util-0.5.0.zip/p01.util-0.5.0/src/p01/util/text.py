##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: __init__.py 203 2007-03-04 01:03:24Z roger.ineichen $
"""

import re


def wrapText(s, length, postfix='...', wrapWords=False):
    """Wrap text with given length but don't cut words."""
    if s is None or len(s) == length:
        return s
    if postfix is not None:
        max = length - len(postfix)
    else:
        max = length
    # remove space if more then one
    s = s.replace('  ', ' ')
    if wrapWords:
        text = s[:length]
        text = text.strip()
    else:
        words = []
        append = words.append
        lines = s.split()
        counter = 0
        for word in lines:
            counter += len(word)
            if counter > max:
                # we reached the max length
                break
            append(word)
            # recognize splitted whitespace
            max = max -1
        text = " ".join(words)
    if text and postfix is not None and len(text) < len(s):
        # add postfix but only if some text get striped and postfix is not None
        text += postfix
    return text


TAGS = re.compile('(<(.*?)>)')
def removeTags(s):
    return TAGS.sub('', s)


def wrapHTML(s, length, postfix='...', wrapWords=False):
    """Wrap HTML with given length but don't cut words and skip tags."""
    if s is None:
        return s
    s = removeTags(s)
    # also remove no breaking space markers
    s = s.replace('&nbsp;', ' ')
    # remove space if more then one
    s = s.replace('  ', ' ').strip()
    return wrapText(s, length, postfix, wrapWords)
