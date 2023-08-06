===============================
Python bindings for WordAi API.
===============================

`WordAi <http://wordai.com/index.php>`_ is an online
service for spinning text (synonym substitution)
that creates unique version(s) of existing text.
This package provides a way to easily interact with
`WordAi API <http://wordai.com/api.php>`_.
Usage requires an API subscription,
`get it here <http://wordai.com/pricing.php>`_.

* `Source code @ GitHub <https://github.com/niteoweb/wordai>`_


Install within virtualenv
=========================

.. sourcecode:: bash

    $ virtualenv foo
    $ cd foo
    $ git clone https://github.com/niteoweb/wordai
    $ bin/pip install wordai/

    # running tests:
    $ bin/pip install unittest2 mock
    $ bin/python -m unittest discover -s wordai/src/wordai/tests


Buildout
========

.. sourcecode:: bash

    $ git clone https://github.com/niteoweb/wordai
    $ virtualenv --no-site-packages ./wordai/
    $ cd wordai
    $ bin/python bootstrap.py
    $ bin/buildout

    # running tests and check code for imperfections
    $ ./pre-commit-hook.sh


Usage
=====

.. sourcecode:: python

    # from wordai.regular import RegularWordAi as WordAi
    >>> from wordai.turing import TuringWordAi as WordAi
    >>> wai = WordAi('demo@demo.com', 'demo')
    >>> print wai.text_with_spintax(u"Some test text whič is fü.")
    u"Some {test|evaluation} text whič is fü.\n"

