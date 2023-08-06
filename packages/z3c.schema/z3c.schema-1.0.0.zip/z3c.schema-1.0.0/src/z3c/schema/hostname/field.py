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

import re

import zope.interface
import zope.schema

from z3c.schema.hostname import interfaces


isValidHostName = re.compile(

    # BEGIN: host
    r"([a-zA-Z]+([a-zA-Z\d\-]*[a-zA-Z\d])*"
    r"(\.[a-zA-Z\d]+([a-zA-Z\d\-]*[a-zA-Z\d])*)*"
    # END: host

    # or
    r"|"

    # BEGIN: IP
    r"([1-9][\d]{0,1}|1[\d]{0,2}|2[0-5]{0,2})"
    r"(\.([\d]{1,2}|1[\d]{0,2}|2[0-5]{0,2})){3})"
    # END: IP

    # port
    r"(:[\d]{1,5})?$"
    ).match


@zope.interface.implementer(interfaces.IHostName)
class HostName(zope.schema.URI):
    """HostName schema field.

    This is a IP Address or a host name.
    """

    def _validate(self, value):
        if isValidHostName(value):
            return
        raise interfaces.InvalidHostName(value)

    def fromUnicode(self, value):
        v = str(value.strip())
        self.validate(v)
        return v
