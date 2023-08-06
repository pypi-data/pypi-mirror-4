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

import zope.interface
import zope.schema
from zope.schema.interfaces import IField, ValidationError

from z3c.schema.optchoice import interfaces


@zope.interface.implementer(interfaces.IOptionalChoice)
class OptionalChoice(zope.schema.Choice):
    """Optional Choice field."""

    def __init__(self, value_type, **kw):
        super(OptionalChoice, self).__init__(**kw)
        # whine if value_type is not a field
        if value_type is not None and not IField.providedBy(value_type):
            raise ValueError("'value_type' must be field instance.")
        self.value_type = value_type

    def _validate(self, value):
        try:
            super(OptionalChoice, self)._validate(value)
        except ValidationError:
            self.value_type._validate(value)

    def fromUnicode(self, value):
        try:
            return super(OptionalChoice, self).fromUnicode(value)
        except ValidationError:
            return self.value_type.fromUnicode(value)
