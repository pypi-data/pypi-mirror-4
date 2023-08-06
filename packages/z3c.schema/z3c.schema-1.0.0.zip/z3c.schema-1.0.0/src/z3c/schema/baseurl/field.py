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

from z3c.schema.baseurl import interfaces


isValidBaseURL = re.compile(
    r"[a-zA-z0-9+.-]+:"   # scheme
    r"\S*$"               # non space (should be pickier)
    ).match


@zope.interface.implementer(interfaces.IBaseURL)
class BaseURL(zope.schema.URI):
    """Base URL field.
    
    Such a base url must end with a ``/``. This makes it simpler for
    append a view name.
    """

    def _validate(self, value):
        if isValidBaseURL(value) and value.endswith('/') and \
            not value.endswith(':/'):
            return

        raise interfaces.InvalidBaseURL(value)

    def fromUnicode(self, value):
        v = str(value.strip())
        self.validate(v)
        return v
