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
"""Date Selection field implementation

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

from z3c.schema.dateselect import interfaces


@zope.interface.implementer(interfaces.IDateSelect)
class DateSelect(zope.schema.Date):

    yearRange = list(range(1900, 2100))
    initialDate = None # set a date or today is used

    def __init__(self, yearRange=None, initialDate=None, **kw):
        super(DateSelect, self).__init__(**kw)
        self.initialDate = initialDate
        if yearRange is not None:
            self.yearRange = yearRange
