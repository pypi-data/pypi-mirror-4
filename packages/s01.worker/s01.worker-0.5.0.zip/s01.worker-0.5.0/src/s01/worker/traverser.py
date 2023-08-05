###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.publisher.interfaces

import m01.mongo.traverser

import s01.worker.layer
from s01.worker import interfaces


# IScrapyRoot traverser
class ScrapyRootTraverser(m01.mongo.traverser.MongoTraverserMixin):
    """A traverser that will lookup views before mongodb items"""

    zope.component.adapts(interfaces.IScrapyRoot, s01.worker.layer.IScrapyLayer)

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""

        view = zope.component.queryMultiAdapter((self.context, request), 
            name=name)
        if view is not None:
            return view
        try:
            return self.context[name]
        except KeyError:
            pass

        raise zope.publisher.interfaces.NotFound(self.context, name, request)
