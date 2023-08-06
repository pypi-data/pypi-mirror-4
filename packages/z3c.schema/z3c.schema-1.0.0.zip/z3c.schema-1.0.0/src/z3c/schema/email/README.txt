====================
RFC 822 Mail Address
====================

Let's first generate an E-mail field:

  >>> from z3c.schema.email import RFC822MailAddress
  >>> email = RFC822MailAddress()

Check that the constraints of the value are fulfilled:

  >>> email.constraint('foo\n')
  False
  >>> email.constraint('foo\r')
  False
  >>> email.constraint('foo')
  True

Now make sure the E-mail addresses validate:

  >>> email.validate(10)
  Traceback (most recent call last):
  ...
  WrongType: (10, <type 'unicode'>, '')

  >>> email.validate(u'foo@bar.')
  Traceback (most recent call last):
  ...
  NotValidRFC822MailAdress: foo@bar.

  >>> email.validate(u'foo@bar.com')

Since the field uses a simple function to validate its E-mail fields, it is
easier to use it for the tests:

  >>> from z3c.schema.email import isValidMailAddress
  >>> isValidMailAddress(u'foo@bar.com')
  True
  >>> isValidMailAddress(u'foo.blah@bar.com')
  True

  # Name failures

  >>> isValidMailAddress(u'foo\r@bar.com')
  False
  >>> isValidMailAddress(u'foo<@bar.com')
  False
  >>> isValidMailAddress(u'foo:@bar.com')
  False

  # Overall failures

  >>> isValidMailAddress(u'')
  False
  >>> isValidMailAddress(u'foo.')
  False
  >>> isValidMailAddress(u'foo.@bar.com')
  False
  >>> isValidMailAddress(u'.foo@bar.com')
  False
  >>> isValidMailAddress(u'foo@bar.com.')
  False

  # Domain failures

  >>> isValidMailAddress(u'foo@')
  False
  >>> isValidMailAddress(u'foo@bar.')
  False
  >>> isValidMailAddress(u'foo@bar')
  False
  >>> isValidMailAddress(u'foo@bar..com')
  False
  >>> isValidMailAddress(u'foo@bar\r.com')
  False
  >>> isValidMailAddress(u'foo@bar<.com')
  False
  >>> isValidMailAddress(u'foo@bar:.com')
  False
