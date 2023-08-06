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

import zope.schema
import zope.schema.interfaces

from z3c.schema.i18n import MessageFactory as _


class IISO7812CreditCard(zope.schema.interfaces.ITextLine):
    """A credit card with a valid check digit"""
    
class NotValidISO7812CreditCard(zope.schema.ValidationError):
    __doc__ = _("""The credit card number is incorrect.""")