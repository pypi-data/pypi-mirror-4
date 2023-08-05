=========================================
Python bindings for The Best Spinner API.
=========================================

`The Best Spinner <http://thebestspinner.com/>`_ is an online
service for spinning text (synonym substitution) that creates unique version(s)
of existing text. This package provides a way to easily interact with
The Best Spinner API.

* `Source code @ GitHub <https://github.com/niteoweb/thebestspinner>`_


Install from package to virtualenv
==================================

.. sourcecode:: bash

    $ virtualenv --no-site-packages foo
    $ cd foo
    $ bin/pip install thebestspinner


Install within virtualenv
=========================

.. sourcecode:: bash

    $ virtualenv --no-site-packages foo
    $ cd foo
    $ git clone git://github.com/niteoweb/thebestspinner.git
    $ bin/pip install thebestspinner/

    # running tests:
    $ bin/pip install unittest2 mock
    $ bin/test


Buildout
========

.. sourcecode:: bash

    $ git clone git://github.com/niteoweb/thebestspinner.git
    $ virtualenv --no-site-packages thebestspinner
    $ cd thebestspinner
    $ bin/python bootstrap.py
    $ bin/buildout

    # running tests:
    $ bin/test

    # check code for imperfections
    $ source bin/activate
    $ vvv src/tbs


Usage
=====

.. sourcecode:: python

    >>> original_text = "This is the text we want to spin"
    >>> import tbs
    >>> thebestspinner = tbs.Api('your_username', 'your_password')
    >>> spin_text = thebestspinner.identifySynonyms(original_text)
    >>> print spin_text
    u"{This is|This really is|That is|This can be} some text that we'd
     {like to|prefer to|want to|love to} spin"
    >>> thebestspinner.randomSpin(spin_text)
    u"This really is some text that we'd love to spin"

