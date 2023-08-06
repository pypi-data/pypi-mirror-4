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

import zope.interface
import zope.schema

from z3c.schema.email import interfaces

rfc822_specials = '()<>@,;:\\"[]'


def isValidMailAddress(addr):
    """Returns True if the email address is valid and False if not."""

    # First we validate the name portion (name@domain)
    c = 0
    while c < len(addr):
        if addr[c] == '@':
            break
        # Make sure there are only ASCII characters
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127:
            return False
        # A RFC-822 address cannot contain certain ASCII characters
        if addr[c] in rfc822_specials:
            return False
        c = c + 1

    # check whether we have any input and that the name did not end with a dot
    if not c or addr[c - 1] == '.':
        return False

    # check also starting and ending dots in (name@domain)
    if addr.startswith('.') or addr.endswith('.'):
        return False

    # Next we validate the domain portion (name@domain)
    domain = c = c + 1
    # Ensure that the domain is not empty (name@)
    if domain >= len(addr):
        return False
    count = 0
    while c < len(addr):
        # Make sure that domain does not end with a dot or has two dots in a row
        if addr[c] == '.':
            if c == domain or addr[c - 1] == '.':
                return False
            count = count + 1
        # Make sure there are only ASCII characters
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127:
            return False
        # A RFC-822 address cannot contain certain ASCII characters
        if addr[c] in rfc822_specials:
            return False
        c = c + 1
    if count >= 1:
        return True
    else:
        return False


@zope.interface.implementer(interfaces.IRFC822MailAddress)
class RFC822MailAddress(zope.schema.TextLine):
    """A valid email address."""
    __doc__ = interfaces.IRFC822MailAddress.__doc__

    def constraint(self, value):
        return '\n' not in value and '\r' not in value

    def _validate(self, value):
        super(RFC822MailAddress, self)._validate(value)
        if not isValidMailAddress(value):
            raise interfaces.NotValidRFC822MailAdress(value)
