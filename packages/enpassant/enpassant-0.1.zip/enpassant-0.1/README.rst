Provides a general-purpose *en passant* assignment / naming
mechanism for Python.

Many languages support en passant (in passing) assignment, like so::

    if result = expensive_request():
        print result.report()

Python does not. This leads to more code lines and (in my opinion) less visual
clarity::

    result = expensive_request()
    if result:
        print result.report()

Or worse, in the case of looping structures::

    result = expensive_request()
    while result:
        print result.report()
        result = expensive_request()

It doesn't look so bad here, in a highly distilled example, but in real programs,
the called function
often has parameters to be managed, and the surrounding code is invariably
longer and more compliated. The more complicated the surrounding computations
and requests, the simpler
the comparision itself should be.

I hope that Python
will eventually provide a concise way of handling this, such as::

    while expensive_request() as result:
        print result.report()

But in the meanwhile, this module provides a workaround.

Usage
=====

::

    from enpassant import *
    result = Passer()
    
    while result / expensive_request():
        print result.value.report()

``result`` is merely a proxy object that, when it encounters the division
operator, returns the denominator. That
is, ``result / whatever == whatever``. But it also *remembers* the denominator
value.
Then, whenever you want the result
value provided (presumably, later in the body of your loop or conditional),
simply ask for ``result.value``. Easy peasy!

Details and Options
===================

``enpassant`` "assignment" is transparent to conditional
expressions, because the value of the expression is always the value of
the denominator. But 
``Passers`` are also guaranteed to have an boolean value identical to that of the
value they contain, should you wish to use them in subsequent tests.

If you prefer the look of the less-than (``<``) or less-than-or-equal (``<=``)
operators
as indicators that ``result`` takes the value of the following value, they
are supported as aliases of the division operation (``/``). Thus, the following
are identical::

    if result / expensive_request():
        print "yes"
        
    if result < expensive_request():
        print "yes"
        
    if result <= expensive_request():
        print "yes"
    
It's a matter of preference which seems most logical, appropriate, and expressive.
Note, however, that the operation usually known as division (``/``) has a much
higher precedence
(i.e.
tighter binding 
to its operands) than the typical
comparison operations (``<`` and ``<=``). If used with a more complex
expressions, either know your prececence or use parenthesis to disambiguate!

Notes
=====

 *  En passant assignment / naming is discussed in
    `Issue1714448 <http://bugs.python.org/issue1714448>`_
    and `PEP 379 <http://www.python.org/dev/peps/pep-0379/>`_, which have
    been rejected and withdrawn, respectively. But they are years gone
    by. I hope the idea will be productively reconsidered in the future.
   
 *  Automated multi-version testing is managed with the wonderful
    `pytest <http://pypi.python.org/pypi/pytest>`_
    and `tox <http://pypi.python.org/pypi/tox>`_. ``enpassant`` is
    successfully packaged for, and tested against, all late-model verions of
    Python: 2.6, 2.7, 3.2, and 3.3, as well as PyPy 1.9 (based on 2.7.2).
 
 *  The `simplere <http://pypi.python.org/pypi/simplere>`_
    package provides
    more extensive en passant handling in the important,
    common case of regular expression
    searches.
 
 *  The author, `Jonathan Eunice <mailto:jonathan.eunice@gmail.com>`_ or
    `@jeunice on Twitter <http://twitter.com/jeunice>`_
    welcomes your comments and suggestions.

Installation
============

To install the latest version::

    pip install -U enpassant

To ``easy_install`` under a specific Python version (3.3 in this example)::

    python3.3 -m easy_install --upgrade enpassant
    
(You may need to prefix these with "sudo " to authorize installation.)