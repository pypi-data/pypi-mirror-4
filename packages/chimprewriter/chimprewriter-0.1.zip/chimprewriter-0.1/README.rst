======================================
Python bindings for ChimpRewriter API.
======================================

`Chimp Rewriter <http://chimprewriter.com>`_ is an online
service for spinning text (synonym substitution) that creates unique version(s)
of existing text. This package provides a way to easily interact with
`ChimpRewriter API <http://chimprewriter.com/api>`_.
Usage requires an API subscription, `get it here <http://chimprewriter.com/api>`_.

* `Source code @ GitHub <https://github.com/niteoweb/chimprewriter>`_


Install within virtualenv
=========================

.. sourcecode:: bash

    $ virtualenv foo
    $ cd foo
    $ git clone https://github.com/niteoweb/chimprewriter
    $ bin/pip install chimprewriter/

    # running tests:
    $ bin/pip install unittest2 mock
    $ bin/python -m unittest discover -s chimprewriter/src/chimprewriter/tests


Buildout
========

.. sourcecode:: bash

    $ git clone https://github.com/niteoweb/chimprewriter
    $ cd chimprewriter
    $ python bootstrap.py
    $ bin/buildout

    # running tests:
    $ bin/py -m unittest discover -s src/chimprewriter/tests

    # check code for imperfections
    $ bin/vvv src/chimprewriter


Usage
=====

.. sourcecode:: python

    >>> import chimprewriter
    >>> cr = chimprewriter.ChimpRewriter("<youremail>", "<yourapikey>", "<yourappname>")

    >>> cr.text_with_spintax(text="My name is Ovca!")
    "{I am|I'm|My friends call me|Throughout southern california|Im} Ovca!"

    >>> cr.unique_variation(text="My name is Ovca!")
    "Im Ovca!"

