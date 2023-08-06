Fanstatic template
******************

Introduction
============

The Fanstatic paster template is used to create Fanstatic python packages.
Fanstatic packages wrap static resources, such as javascript and CSS libraries.

For more information on Fanstatic, visit http://fanstatic.org.

Usage
=====

After installing the ``fanstatictemplate`` package, a paster template is made
available::

  $ paster create -t fanstatic

When running the ``paster create`` command, you will be asked to supply the name
of the Fanstatic package and the name, version and URL of the wrapped library.

We use the ``js`` namespace for creating javascript packages, for example
`jQuery`_ is made available as the ``js.jquery`` python package.

After running the ``paster create`` command, copy the library into the
newly created ``resources`` subdirectory and register the Resources
in ``__init__.py``.
A doctest stub is created. It is up to you to make the tests pass based on the
newly registered Resources.

.. _`jQuery`: http://jquery.com/

