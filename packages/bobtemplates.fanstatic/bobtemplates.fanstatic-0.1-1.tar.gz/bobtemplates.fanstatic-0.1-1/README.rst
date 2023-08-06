Introduction
============

``bobtemplates.fanstatic`` provides `mr.bob`_ templates to generate
packages for `Fanstatic`_.

Available templates are:

    -   ``package``: a simple template for a Fanstatic package.

Global settings
---------------

Some variables are used with every template.  These should be added to the
mr.bob user config in ``~/.mrbob``, e.g.::

    [variables]

    author.name = Nuno Teixeira
    author.email = teixas@gmail.com
    author.github.user = teixas

Creating a Fanstatic package
----------------------------

To create a Fanstatic package run::

    mrbob -O js.some_library bobtemplates.fanstatic:package

and answer the questions::

    Welcome to mr.bob interactive mode. Before we generate directory structure,
    some questions need to be answered.

    Answer with a question mark to display help.
    Value in square brackets at the end of the questions present default value
    if there is no answer.


    --> Name of wrapped library: some_library

    --> Version of the wrapped library: 1.4.4

    --> URL of the wrapped library: http://some_library.com

Then you could add resources files::

    cd js.some_library/js/some_library/resources

Register them in __init__.py::

    cd ..
    <editor> __init__.py

Run tests::

    python bootstrap.py
    buildout
    py.test js


.. _mr.bob: http://mrbob.readthedocs.org/en/latest/
.. _Fanstatic: http://www.fanstatic.org/en/latest/
