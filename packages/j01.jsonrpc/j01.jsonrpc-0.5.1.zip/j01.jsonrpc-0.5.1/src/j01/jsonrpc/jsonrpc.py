##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
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
__docformat__ = 'restructuredtext'

from z3c.jsonrpc.publisher import MethodPublisher


class J01LoadContent(MethodPublisher):
    """Can load content via JSONRPC.
    
    Note: This method publisher must be able to traverse the context which is
    a view or a form. Our default JSON-RPC tarverser could be used.
    See: JSONRPCTraversablePage
    
    Note: This method is registered with zope.Public permission and will run
    into Unauthorized if the principal does not have the permission to traverse
    the view. 
    """

    def j01LoadContent(self):
        self.context.update()
        nextURL = self.context.nextURL
        if nextURL is None:
            content = self.context.render()
            nextURL = ''
        else:
            content = None
        # setup target expression at the end, could probably get adjusted
        # in update or render method call
        targetExpression = self.context.contentTargetExpression
        scrollToExpression = self.context.scrollToExpression
        scrollToOffset = self.context.scrollToOffset
        scrollToSpeed = self.context.scrollToSpeed
        nextHash = self.context.nextHash
        return {'content': content,
                'contentTargetExpression': targetExpression,
                'scrollToExpression': scrollToExpression,
                'scrollToOffset': scrollToOffset,
                'scrollToSpeed': scrollToSpeed,
                'nextHash': '%s' % nextHash,
                'nextURL': '%s' % nextURL}


class J01FormProcessor(MethodPublisher):
    """Can process a form button handler via JSONRPC.
    
    Note: This method is registered with zope.Public permission and will run
    into Unauthorized if the principal does not have the permission to traverse
    the view.
    """

    def j01FormProcessor(self):
        self.context.update()
        nextURL = self.context.nextURL
        if nextURL is None:
            content = self.context.render()
            nextURL = ''
        else:
            content = None
        # setup target expression at the end, could probably get adjusted
        # in update or render method call
        targetExpression = self.context.contentTargetExpression
        scrollToExpression = self.context.scrollToExpression
        scrollToOffset = self.context.scrollToOffset
        scrollToSpeed = self.context.scrollToSpeed
        nextHash = self.context.nextHash
        return {'content': content,
                'contentTargetExpression': targetExpression,
                'scrollToExpression': scrollToExpression,
                'scrollToOffset': scrollToOffset,
                'scrollToSpeed': scrollToSpeed,
                'nextHash': '%s' % nextHash,
                'nextURL': '%s' % nextURL}
