##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH and Contributors.
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
$Id: jsonrpc.py 3487 2012-11-23 04:02:48Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from z3c.jsonrpc.publisher import MethodPublisher

import p01.editor.util


class XEditorPaste(MethodPublisher):
    """Knows how to cleanup any text pasted into XEditor"""

    def doXEditorPaste(self, textBefore, textAfter):
        return p01.editor.util.simpleHTML(textAfter)
