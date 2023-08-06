========================
The Date Selection Field
========================

The date selection field was designed to support the UI requirement of
allowing users to select a date using multi-select input fields. The
``DateSelect`` field extends the ``Date`` field merely by a few additional
attributes.

  >>> from z3c.schema.dateselect import field

the first attribute is the range of years that will be offered to the user:

  >>> birthday = field.DateSelect(
  ...     title=u'Birthday',
  ...     yearRange=list(range(1920, 2007)))

In this case the user will be offered all years from 1920 to 2007.

  >>> birthday.yearRange
  [1920, ..., 2006]

The second attribute allows you to specify an initial date for the selection:

  >>> import datetime
  >>> birthday = field.DateSelect(
  ...     title=u'Birthday',
  ...     yearRange=range(1920, 2007),
  ...     initialDate=datetime.date(2000, 1, 1))

  >>> birthday.initialDate
  datetime.date(2000, 1, 1)

And this is really it. Please read the documentation on the ``Date`` for more
information.
