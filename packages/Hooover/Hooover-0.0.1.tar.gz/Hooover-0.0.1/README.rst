hooover 0.0.1
=============
Fork of hoover library from http://www.github.com/loggly/hoover that uses requests instead of httplib2

Here's a simple usage example::

    import hooover
    handler = hooover.LogglyHttpHandler(token='your_token_here')
    import logging
    log = logging.getLogger('Loggly')
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    log.info("Hello Loggly...")

get hooover
===========
Install `requests`_ library::

    sudo easy_install hooover

Download the latest release from `Python Package Index`_
or clone `the repository`_

.. _requests: http://docs.python-requests.org/en/latest/
.. _the repository: https://bitbucket.org/juztin/hooover
.. _Python Package Index: http://pypi.python.org/pypi/Hooover
