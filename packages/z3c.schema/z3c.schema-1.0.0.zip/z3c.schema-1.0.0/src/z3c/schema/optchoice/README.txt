================
Optional Choices
================

The optional choice field is desiged to offer a set of default choices or
allow, optionally, to enter a custom value. The custom value has to conform to
a specified field.

Here is an example of creating such a field:

  >>> import zope.schema
  >>> from z3c.schema.optchoice import OptionalChoice

  >>> optchoice = OptionalChoice(
  ...     title=u'Occupation',
  ...     values=(u'Programmer', u'Designer', u'Project Manager'),
  ...     value_type=zope.schema.TextLine())

Note that the value type *must* be a field:

  >>> OptionalChoice(
  ...     title=u'Occupation',
  ...     values=(u'Programmer', u'Designer', u'Project Manager'),
  ...     value_type=object())
  Traceback (most recent call last):
  ValueError: 'value_type' must be field instance.

Let's now ensure that we can validate not only choices, but also custom
values:

  >>> optchoice.validate(u'Programmer')
  >>> optchoice.validate(u'Project Manager')
  >>> optchoice.validate(u'Scripter')

  >>> optchoice.validate(u'Scripter\nHTML\n')
  Traceback (most recent call last):
  ...
  ConstraintNotSatisfied: Scripter
  HTML

Let's now ensure that we can convert values from unicode to a real value as
well. To demonstrate this feature, we have to create a more restrictive
optional choice field:

  >>> optchoice = OptionalChoice(
  ...     title=u'Age',
  ...     values=(10, 20, 30, 40, 50),
  ...     value_type=zope.schema.Int(min=0))

  >>> optchoice.fromUnicode(u'10')
  10
  >>> optchoice.fromUnicode(u'40')
  40
  >>> optchoice.fromUnicode(u'45')
  45

  >>> optchoice.fromUnicode(u'-10')
  Traceback (most recent call last):
  ...
  TooSmall: (-10, 0)
