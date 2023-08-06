========
BaseURL
========

A base url field is useful if you need to append view names to a url and 
doesn't like to check every time if the url ends with a backslash before you 
append the view name.

Let's first create the BaseURL field:

  >>> from z3c.schema.baseurl import BaseURL
  >>> baseURL = BaseURL()

Let's first check the validation of some common base urls.

  >>> baseURL.validate("http://www.python.org/")
  >>> baseURL.validate("http://www.python.org/foo/")
  >>> baseURL.validate("http://123.123.123.123/")
  >>> baseURL.validate("http://123.123.123.123/foo/")

A port specification is also allowed:

  >>> baseURL.validate("http://www.python.org:389/")
  >>> baseURL.validate("http://www.python.org:389/foo/")

However, a missing backslash is not permitted:

  >>> baseURL.validate("http://www.python.org/foo")
  Traceback (most recent call last):
  ...
  InvalidBaseURL: http://www.python.org/foo

And a missing protocol is also not permitted:

  >>> baseURL.validate("www.python.org/foo/")
  Traceback (most recent call last):
  ...
  InvalidBaseURL: www.python.org/foo/

Let's check some other invalid forms:

  >>> baseURL.validate("$www.python.org/")
  Traceback (most recent call last):
  ...
  InvalidBaseURL: $www.python.org/

  >>> baseURL.validate("333.123.123.123/")
  Traceback (most recent call last):
  ...
  InvalidBaseURL: 333.123.123.123/

Let's also ensure that we can convert to base urls from unicode:

  >>> baseURL.fromUnicode("http://www.python.org:389/")
  'http://www.python.org:389/'
  >>> baseURL.fromUnicode("          http://www.python.org:389/")
  'http://www.python.org:389/'
  >>> baseURL.fromUnicode("      \n    http://www.python.org:389/\n")
  'http://www.python.org:389/'

  >>> baseURL.fromUnicode("http://www.pyt hon.org:389/")
  Traceback (most recent call last):
  ...
  InvalidBaseURL: http://www.pyt hon.org:389/
