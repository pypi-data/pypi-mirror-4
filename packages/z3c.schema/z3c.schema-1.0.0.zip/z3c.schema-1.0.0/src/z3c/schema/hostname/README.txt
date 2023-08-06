========
Hostname
========

Let's first create the hostname field:

  >>> from z3c.schema.hostname import HostName
  >>> hostname = HostName()

Let's first check the validation of some common hostnames. Hostnames can be
either domain or IP addresses.

  >>> hostname.validate("www.python.org")
  >>> hostname.validate("123.123.123.123")

A port specification is also allowed:

  >>> hostname.validate("www.python.org:389")

However, the protocol is not permitted:

  >>> hostname.validate("http://www.python.org")
  Traceback (most recent call last):
  ...
  InvalidHostName: http://www.python.org

  >>> hostname.validate("ldap://www.python.org/foo")
  Traceback (most recent call last):
  ...
  InvalidHostName: ldap://www.python.org/foo

Let's check some other invalid forms:

  >>> hostname.validate("$www.python.org")
  Traceback (most recent call last):
  ...
  InvalidHostName: $www.python.org

  >>> hostname.validate("333.123.123.123")
  Traceback (most recent call last):
  ...
  InvalidHostName: 333.123.123.123

Let's also ensure that we can convert to hostnames from unicode:

  >>> hostname.fromUnicode("www.python.org:389")
  'www.python.org:389'
  >>> hostname.fromUnicode("          www.python.org:389")
  'www.python.org:389'
  >>> hostname.fromUnicode("      \n    www.python.org:389\n")
  'www.python.org:389'

  >>> hostname.fromUnicode("www.pyt hon.org:389")
  Traceback (most recent call last):
  ...
  InvalidHostName: www.pyt hon.org:389
