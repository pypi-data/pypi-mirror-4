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
"""ISO 7812 Credit Card
"""
import zope.interface
from . import interfaces

def isValidCreditCard(cardNum):
    """Returns True if the credit card number is a valid Luhn (Mod 10) number
       and False if not. This, of course, does not validate the number, but
       will catch typos. There is the chance that two typographic errors could
       return a false positive if they offset one anoter, but the likelihood
       is low and pre-validating is fast"""

    financialIndustries = ['3','4','5','6']
    if cardNum[1] not in financialIndustries:
        return False

    total = pos = 0
    for digit in cardNum[::-1]:
        if pos % 2 == 0:
            multiplier = 1
        else:
            multiplier = 2
        product = int(digit) * multiplier
        total += product // 10 + product % 10
        pos += 1
    if total % 10 == 0:
        return True
    return False

@zope.interface.implementer(interfaces.IISO7812CreditCard)
class ISO7812CreditCard(zope.schema.TextLine):
    """A valid ISO 7812 credit card number."""
    __doc__ = interfaces.IISO7812CreditCard.__doc__

    def constraint(self, value):
        allDigits = True
        for char in value[:]:
            if not char.isdigit():
                allDigits = False
        return '\n' not in value and '\r' not in value and allDigits

    def _validate(self, value):
        super(ISO7812CreditCard, self)._validate(value)
        if not isValidCreditCard(value):
            raise interfaces.NotValidISO7812CreditCard(value)
