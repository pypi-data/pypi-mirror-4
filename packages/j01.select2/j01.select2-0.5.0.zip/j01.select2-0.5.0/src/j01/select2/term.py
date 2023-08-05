##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: term.py 3030 2012-08-26 04:26:26Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.i18n

from j01.select2 import interfaces


class LiveListTerms(list):
    """LiveList terms wrapper"""

    zope.interface.implements(interfaces.ILiveListTerms)

    total = None

    def __init__(self, data, page, size, total):
        """Initialize given values in a new list"""
        self.data = list(data)
        self.page = page
        self.size = size
        self.total = total
        # calculate pages
        pages = self.total/self.size
        if pages == 0 or self.total % self.size:
            pages += 1
        self.pages = pages
        # as next we approve our page position
        if self.page > self.pages:
            # reset page to pages
            self.page = pages
        if self.page < self.pages:
            self.more = True
        else:
            self.more = False

    def append(self, item):
        self.data.append(item)

    def insert(self, i, item):
        self.data.insert(i, item)

    def pop(self, i=-1):
        return self.data.pop(i)

    def remove(self, item):
        self.data.remove(item)

    def sort(self, *args, **kwargs):
        self.data.sort(*args, **kwds)

    def __len__(self):
        return len(self.data)

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, i, item):
        self.data[i] = item

    def __delitem__(self, i):
        del self.data[i]

    def __iter__(self):
        for v in self.data:
            yield v

    def __cast(self, other):
        """Allows to compare other LiveListTerms lists."""
        if isinstance(other, LiveListTerms):
            return other.data
        else:
            return other

    def __cmp__(self, other):
        return cmp(self.data, self.__cast(other))

    def __repr__(self):
        return repr(self.data)


class LiveListTerm(object):
    """Tokenized term with group support."""

    zope.interface.implements(interfaces.ILiveListTerm)

    groupName = None

    def __init__(self, value, token=None, title=None, groupName=None):
        """Create a term for value and token. If token is omitted,
        str(value) is used for the token.
        
        Additional to the SimpleTerm this implementation provides a groupName
        argument which can be used for group terms which will get shown as a
        block in the live list result grid.
        
        The widget uses getTitle for get the title with a request as attribute.
        This allows to translate the title if needed. See I18nLiveListTerm
        as a sample.
        """
        self.value = value
        if token is None:
            token = value
        self.token = str(token)
        self.title = title
        self.groupName = groupName

    def getTitle(self, request):
        return self.title


class I18nLiveListTerm(LiveListTerm):
    """Tokenized term with group support and built-in title translation."""

    def getTitle(self, request):
        return zope.i18n.translate(self.title, context=request,
            default=self.title)
