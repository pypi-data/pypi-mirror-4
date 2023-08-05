##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""

from zope.viewlet import viewlet


J01LiveSearchJavaScript = viewlet.JavaScriptViewlet('j01.livesearch.js')
J01LiveSearchCSS = viewlet.CSSViewlet('j01.livesearch.css')

j01_livesearch_template = """
<script type="text/javascript">
  $("%s").j01LiveSearch({%s
  });
</script>
"""

def j01LiveSearchJavaScript(data):
    """LiveSearch JavaScript generator.
    
    Knows how to generate customization for j01LiveSearch JS.
    This is usefull for generate custom image path.
    """
    try:
        widgetExpression = data.pop('widgetExpression')
    except KeyError, e:
        widgetExpression = '#j01LiveSearch'

    lines = []
    append = lines.append
    try:
        resultExpression = data.pop('resultExpression')
    except KeyError, e:
        resultExpression = '#j01LiveSearchResult'
    append("\n    resultExpression: '%s'" % resultExpression)

    for key, value in data.items():
        if key in ['onAfterRender']:
            append("\n    %s: %s" % (key, value))
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is None:
            append("\n    %s: null" % key)
        elif isinstance(value, int):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, str):
            if value.startswith('$'):
                append("\n    %s: %s" % (key, value))
            else:
                append("\n    %s: '%s'" % (key, value))
        else:
            append("\n    %s: %s" % (key, value))
    code = ','.join(lines)

    return j01_livesearch_template % (widgetExpression, code)


class LiveSearchMixin(object):
    """Context independent livesearch mixin class also useable for JSON-RPC"""

    # internals
    j01LiveSearchWidgetExpression = '#form-widgets-searchText'
    j01LiveSearchResultExpression = '#j01LiveSearchResult'
    j01LiveSearchMethodName = 'getJ01LiveSearchResult'
    j01LiveSearchOnAfterRender = 'j01LiveSearchOnAfterRender'

    # sizes
    j01LiveSearchMinQueryLenght = 2
    j01LiveSearchCacheResult = False

    @property
    def j01LiveSearchURL(self):
        return absoluteURL(self.context, self.request)

    @property
    def j01LiveSearchJavaScript(self):
        data = {'widgetExpression': self.j01LiveSearchWidgetExpression,
                'resultExpression': self.j01LiveSearchResultExpression,
                'methodName': self.j01LiveSearchMethodName,
                'url': self.j01LiveSearchURL,
                'minQueryLenght': self.j01LiveSearchMinQueryLenght,
                'cacheResults': self.j01LiveSearchCacheResult,
                'onAfterRender': self.j01LiveSearchOnAfterRender,
               }
        return j01LiveSearchJavaScript(data)
