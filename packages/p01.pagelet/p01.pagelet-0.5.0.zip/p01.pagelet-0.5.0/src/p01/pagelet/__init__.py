###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

from zope.traversing.browser import absoluteURL

from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

import z3c.pagelet.browser


class BrowserPagelet(z3c.pagelet.browser.BrowserPagelet):
    """Pagelet with layout and template lookup and url support.

    Get rid of template and layout multi adapter call in render method from
    original pagelet implementation. Just use our template and layout lookup
    methods

    """

    _contextURL = None
    _pageURL = None
    nextURL = None

    layout = getLayoutTemplate()
    template = getPageTemplate()

    @property
    def contextURL(self):
        """Setup and cache context URL"""
        if self._contextURL is None:
            self._contextURL = absoluteURL(self.context, self.request)
        return self._contextURL

    @property
    def pageURL(self):
        """Setup and cache context URL"""
        if self._pageURL is None:
            self._pageURL = '%s/%s' % (absoluteURL(self.context, self.request),
                self.__name__)
        return self._pageURL

    def render(self):
        if self.nextURL is not None:
            return None
        return self.template()

    def __call__(self):
        self.update()
        if self.nextURL is not None:
            self.request.response.redirect(self.nextURL)
            return u''
        return self.layout()
