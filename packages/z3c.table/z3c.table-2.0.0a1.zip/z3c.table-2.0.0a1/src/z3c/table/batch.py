##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
$Id:$
"""
__docformat__ = "reStructuredText"

try:
    # Python 2
    from urllib import urlencode
except ImportError:
    # Python 3
    from urllib.parse import urlencode

import zope.interface
import zope.i18nmessageid
from zope.traversing.browser import absoluteURL

from z3c.table import interfaces
from z3c.batching.batch import first_neighbours_last

_ = zope.i18nmessageid.MessageFactory('z3c')


@zope.interface.implementer(interfaces.IBatchProvider)
class BatchProvider(object):
    """Batch content provider.

    A batch provider is responsible for rendering the batch HTML and not for
    batching. The batch setup is directly done in the table. A batch provider
    get only used if the table rows is a batch.

    This batch provider offers a batch presentation for a given table. The
    batch provides different configuration options which can be overriden in
    custom implementations:
    
    The batch acts like this. If we have more batches than
    (prevBatchSize + nextBatchSize + 3) then the advanced batch subset is used.
    Otherwise, we will render all batch links.    
    Note, the additional factor 3 is the placeholder for the first, current and
    last item.

    Such a batch looks like:

    Renders the link for the first batch, spacers, the amount of links for 
    previous batches, the current batch link, spacers, the amount of links for 
    previous batches and the link for the last batch.
    
    Sample for 1000 items with 100 batches with batchSize of 10 and a     
    prevBatchSize of 3 and a nextBatchSize of 3:

    For the first item:
    [*1*][2][3][4] ... [100]

    In the middle:
    [1] ... [6][7][8][*9*][10][11][12] ... [100]

    At the end:
    [1] ... [97][98][99][*100*]
    """

    batchItems = []

    prevBatchSize = 3
    nextBatchSize = 3
    batchSpacer = u'...'

    _request_args = ['%(prefix)s-sortOn', '%(prefix)s-sortOrder']

    def __init__(self, context, request, table):
        self.__parent__ = context
        self.context = context
        self.request = request
        self.table = table
        self.batch = table.rows
        self.batches = table.rows.batches

    def getQueryStringArgs(self):
        """Collect additional terms from the request to include in links.

        API borrowed from z3c.table.header.ColumnHeader.
        """
        args = {}
        for key in self._request_args:
            key = key % dict(prefix=self.table.prefix)
            value = self.request.get(key, None)
            if value:
                args.update({key: value})
        return args

    def renderBatchLink(self, batch, cssClass=None):
        args = self.getQueryStringArgs()
        args[self.table.prefix +'-batchStart'] = batch.start
        args[self.table.prefix +'-batchSize'] = batch.size
        query = urlencode(sorted(args.items()))
        tableURL = absoluteURL(self.table, self.request)
        idx = batch.index + 1
        css = ' class="%s"' % cssClass
        cssClass = cssClass and css or u''
        return '<a href="%s?%s"%s>%s</a>' % (tableURL, query, cssClass, idx)

    def update(self):
        # 3 is is the placeholder for the first, current and last item.
        total = self.prevBatchSize + self.nextBatchSize + 3
        if self.batch.total <= total:
            # give all batches
            self.batchItems = self.batch.batches
        else:
            # switch to an advanced batch subset
            self.batchItems = first_neighbours_last(self.batches,
                                                    self.batch.index,
                                                    self.prevBatchSize,
                                                    self.nextBatchSize,
                                                    )

    def render(self):
        self.update()
        res = []
        append = res.append
        idx = 0
        lastIdx = len(self.batchItems)
        for batch in self.batchItems:
            idx += 1
            # build css class
            cssClasses = []
            if batch and batch == self.batch:
                cssClasses.append('current')
            if idx == 1:
                cssClasses.append('first')
            if idx == lastIdx:
                cssClasses.append('last')
            
            if cssClasses:
                css = ' '.join(cssClasses)
            else:
                css = None

            # render spaces
            if batch is None:
                append(self.batchSpacer)
            elif idx == 1:
                # render first
                append(self.renderBatchLink(batch, css))
            elif batch == self.batch:
                # render current
                append(self.renderBatchLink(batch, css))
            elif idx == lastIdx:
                # render last
                append(self.renderBatchLink(batch, css))
            else:
                append(self.renderBatchLink(batch))
        return u'\n'.join(res)
