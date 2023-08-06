##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""IP Address Field Interfaces
"""
import zope.schema
import zope.schema.interfaces

from z3c.schema.i18n import MessageFactory as _

class IIPAddress(zope.schema.interfaces.INativeStringLine):
    """A valid IP address field."""

class NotValidIPAdress(zope.schema.ValidationError):
    __doc__ = _("""Not a valid IP address.""")
