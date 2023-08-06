##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: jsonrpc.py 3635 2013-01-21 04:38:36Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from z3c.jsonrpc.publisher import MethodPublisher

import j01.scroller.browser


class J01ScrollerResult(j01.scroller.browser.J01Scroller, MethodPublisher):
    """JSON scroller result"""

    def getJ01ScrollerResult(self, page, batchSize=None, sortName=None,
        sortOrder=None, searchString=None):
        """Returns the next scroller batch as JSON data.

        The returned value provides the following data structure:

        return {'content': 'result content'}

        Where the key/values are:

        content: a list of items represented as html content.

        Note: this class uses an named and not an unnamed template called
        j01Scroller. Normaly you will register this j01Scroller template for
        the mixin class shared within your J01ScrollerPage.

        """
        # update additional scroller data
        self.j01ScrollerUpdate()

        # setup cursor
        self.setUpJ01ScrollerBatchData(page, batchSize, sortName, sortOrder,
            searchString)

        # setup content
        content = self.j01Scroller

        # setup more after cursor setup in j01Scroller property
        more = self.showMoreJ01Scroller

        # return pager batch data as content
        return {'content': content, 'more': more}

