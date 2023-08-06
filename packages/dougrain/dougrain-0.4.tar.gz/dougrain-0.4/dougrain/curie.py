# Copyright (c) 2013 Will Harris
# See the file license.txt for copying permission.

import urlparse

class CurieCollection(dict):
    def expand(self, link):
        terms = link.split(':')

        if len(terms) < 2:
            return link

        key, value = terms

        if key not in self:
            return link

        return self[key].url(rel=value)
