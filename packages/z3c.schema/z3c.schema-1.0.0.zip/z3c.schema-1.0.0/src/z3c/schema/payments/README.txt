===================
z3c.schema.payments
===================

z3c.schema.payments provides some level of error detection in payment data
prior to storing the information or sending it to a payment processor.
Currently this module only supports validation of credit card numbers, but
this could conceivably be extended to other payment forms


Credit Cards
------------

Credit card numbering specifications are defined in ISO 7812-1:1983. Verifying
that the credit card number supplied by a user conforms to the ISO standard
provides some error checking which can catch typographical errors,
transposition, etc. This does not validate the card against the financial
networks as a valid account. However, verifying that the card number is well
formed is fast and catching typographical errors in this way is much faster
than sending the card number to a credit card processor.

First, let's setup a credit card field:

    >>> from z3c.schema.payments import CreditCard
    >>> from z3c.schema.payments import interfaces
    >>> cc = CreditCard()
    >>> interfaces.IISO7812CreditCard.providedBy(cc)
    True

The simple restrictions are quick to check. Credit cards should be all numeric, no alpha characters allowed:

    >>> cc.constraint('44444444444AAAA8')
    False

    >>> cc.constraint('4444444444444448')
    True

Also, we can't have any returns or line endings in the number:

    >>> cc.constraint('444444444444\n4448')
    False

    >>> cc.constraint('44444444\r44444448')
    False

One of the first specifications of ISO 7812 is a "Major Industry Identifier,"
which is the first number of an ISO 7812 compliant account number. Originally,
banking, financial, and merchandizing (store account) cards were limited to
the  major industry identifiers 4, 5, and 6. However American Express, Diner's
Club, and Carte Blanche were all assigned a major industry number 3. So a
valid card must start with one of these numbers:

    >>> cc.validate(u'0000000000000000')
    Traceback (most recent call last):
    ...
    NotValidISO7812CreditCard: 0000000000000000

    >>> cc.validate(u'1111111111111117')
    Traceback (most recent call last):
    ...
    NotValidISO7812CreditCard: 1111111111111117

    >>> cc.validate(u'2222222222222224')
    Traceback (most recent call last):
    ...
    NotValidISO7812CreditCard: 2222222222222224

    >>> cc.validate(u'3333333333333331')
    >>> cc.validate(u'4444444444444448')
    >>> cc.validate(u'5555555555555557')
    >>> cc.validate(u'3333333333333331')
    >>> cc.validate(u'6666666666666664')

    >>> cc.validate(u'7777777777777771')
    Traceback (most recent call last):
    ...
    NotValidISO7812CreditCard: 7777777777777771

    >>> cc.validate(u'8888888888888888')
    Traceback (most recent call last):
    ...
    NotValidISO7812CreditCard: 8888888888888888

    >>> cc.validate(u'9999999999999995')
    Traceback (most recent call last):
    ...
    NotValidISO7812CreditCard: 9999999999999995

The ISO specification also defines a check digit which should always
be the last digit of a card number. The check digit is calculated using the
Luhn (Mod 10) formula. In this way, each credit card number contains its own
CRC of sorts. This is our main validation that a credit card number is well
formed.

Validating a number with a check digit that uses the LUHN formula:

Step 1:
Starting with the next-to-last digit and moving left, double the value of
every other digit. The calculation starts with the next-to-last digit because
the last digit is the check digit.

* When selecting every other digit, always work right-to-left and do not start
  with the rightmost digit (since that is the check digit).

* The last digit (check digit) is considered #1 (odd number) and the
  next-to-last digit is #2 (even number). You will only double the values of
  the even-numbered digits.

Step 2:
Add all unaffected digits to the values obtained in Step 1.

* If any of the values resulting from Step 1 are double-digits, do not add
  the double-digit value to the total, but rather add the two digits, and
  add this sum to the total.

Result:
The total obtained in Step 2 must be a number ending in zero (exactly
divisible by 10) for the number to be valid.

The validate method of z3c.schema.payments.ISO7812CreditCard does the Luhn
calculation on the provided card number. If the calculation fails, there is
either an error in the number or the card is simply not valid. We use in our
tests here and above numbers that technically meet the criteria of the ISO
specification without the risk of the number actually being a valid card
number registered with a financial institution:

    >>> cc.validate(u'4444444444444448')
    >>> cc.validate(u'4444444444444449')
    Traceback (most recent call last):
    ...
    NotValidISO7812CreditCard: 4444444444444449

