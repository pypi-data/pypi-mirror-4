##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Date Selection Field interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.schema.interfaces


class IDateSelect(zope.schema.interfaces.IDate):

    yearRange = zope.interface.Attribute(u"Year range.")

    initialDate = zope.interface.Attribute(
        u"Initial date displayed or ``None``. If ``None``, `today()`` is used.")
