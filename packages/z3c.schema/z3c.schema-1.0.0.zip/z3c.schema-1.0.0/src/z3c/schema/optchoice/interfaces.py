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
"""
$Id$
"""
__docformat__ = "reStructuredText"

import zope.schema
import zope.schema.interfaces

from z3c.schema.i18n import MessageFactory as _


class IOptionalChoice(zope.schema.interfaces.IChoice,
                      zope.schema.interfaces.IFromUnicode):
    """Optional Choice

    This field can either represent a choice or a textline value.

    Validation proceeds as follows:

    1. Check whether the value is one of the choices. If so, return
       successfully.

    2. If no choice match was found, validate the value against the
       ``value_type`` field.

    The conversion from unicode values proceeds in a similar fashion:

    1. Try to match the unicode value to a token in the vocabulary.

    2. If no match was made, call the unicode conversion method of the
       ``value_type`` field.
    """

    value_type = zope.schema.Field(
        title = _("Value Type"),
        description = _(u"The freely entered values must be of this type."),
        required=True)
