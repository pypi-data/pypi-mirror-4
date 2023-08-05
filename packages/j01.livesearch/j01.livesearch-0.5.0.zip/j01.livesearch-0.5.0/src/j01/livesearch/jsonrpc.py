##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: member.py 462 2007-05-14 05:15:55Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.site import hooks
from zope.traversing.browser import absoluteURL
from zope.security.proxy import removeSecurityProxy

from z3c.jsonrpc.publisher import MethodPublisher

from z3c.template.template import getPageTemplate

import j01.livesearch.browser


class J01LiveSearchResult(j01.livesearch.browser.J01LiveSearchMixin,
    MethodPublisher):
    """JSON live search method with template for rendering the result."""

    template = getPageTemplate()

    # internals
    j01Pages = 0
    j01Page = 1
    j01PageTotal = 0 # can be used as condition for values
    cursor = None

    def getJ01LiveSearchResult(self, searchString=None):
        """Returns the search result as JSON data.

        The returned value provides the following data structure:

        return {'content': 'result content'}

        """
        page = 1
        batchSize = 9999
        if not searchString:
            searchString = None
        cursor, self.j01Page, self.j01Pages, self.j01PageTotal = \
            self.getBatchData(page, batchSize, searchString)
        self.cursor = removeSecurityProxy(cursor)
        return {'content': self.template()}
