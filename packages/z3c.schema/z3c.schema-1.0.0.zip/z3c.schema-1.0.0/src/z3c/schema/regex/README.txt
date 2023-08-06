========================
Regular expression field
========================

Let's first create the regex field.

  >>> from z3c.schema.regex import Regex
  >>> regex = Regex()

The regex field only allows compilable regular expressions.

  >>> regex.validate(r'.*')
  >>> regex.validate(r'^\s+$')

It does not validate regular expressions that do not compile.

  >>> regex.validate('(i')
  Traceback (most recent call last):
  ...
  InvalidRegex: '(i', unbalanced parenthesis

