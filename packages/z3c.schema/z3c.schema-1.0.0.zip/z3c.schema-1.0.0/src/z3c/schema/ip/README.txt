================
IP Address Field
================

This module provides a field for IP addresses. Let's first generate an IP
field:

  >>> from z3c.schema import ip
  >>> myip = ip.IPAddress()

Now make sure the IP addresses validate:

  >>> myip.validate(10)
  Traceback (most recent call last):
  ...
  WrongType: (10, <type 'str'>, '')

  >>> myip.validate('12.123.231.wee')
  Traceback (most recent call last):
  ...
  NotValidIPAdress: 12.123.231.wee

  >>> myip.validate('10.0.0.1')

Since the field uses a simple function to validate its IP addresses, it is
easier to use it for the tests:

  >>> from z3c.schema.ip import isValidIPAddress
  >>> isValidIPAddress('0.0.0.0')
  True
  >>> isValidIPAddress('255.255.255.255')
  True

  # Number of pieces failures

  >>> isValidIPAddress('12.3.1')
  False
  >>> isValidIPAddress('1.0.0.0.0')
  False
  >>> isValidIPAddress('1.0.0.0.')
  False

  # Not integers failures

  >>> isValidIPAddress('x.0.0.0')
  False
  >>> isValidIPAddress('0x8.0.0.0')
  False

  # Not in range failures

  >>> isValidIPAddress('-1.0.0.0')
  False
  >>> isValidIPAddress('256.0.0.0')
  False
  >>> isValidIPAddress('1.-1.256.0')
  False
