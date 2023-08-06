Unipag Client for Python
========================

.. image:: https://travis-ci.org/unipag/unipag-python.png?branch=master
        :target: https://travis-ci.org/unipag/unipag-python

Requirements
------------

Python version 2.6 or 2.7, or PyPy. For better security, we recommend to
install `Python Requests`_ library, since it supports SSL certs verification.
To install Requests, simply run: ::

    $ pip install requests

or using easy_install: ::

    $ easy_install requests

Requests library is optional. If it is not installed, Unipag Client will use
urllib2 instead. All features of Unipag Client will remain fully functional, but
it will not verify SSL certificate of Unipag API.

.. _`Python Requests`: http://docs.python-requests.org/

Installation
------------

Install using pip, recommended (`why?`_): ::

    $ pip install unipag

or using easy_install: ::

    $ easy_install unipag

.. _`why?`: http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install

Report bugs
-----------

#. Report issues to the project's `Issues Tracking`_ on Github.

.. _`Issues Tracking`: https://github.com/unipag/unipag-python/issues
