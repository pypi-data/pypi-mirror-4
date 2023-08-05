careful-requests
~~~~~~~~~~~~~~~

This module provides an HTTP adapter and session for use with `Requests`_ when
communicating with servers that are hyper-sensitive to standard HTTP headers.
It may be sad, but not all HTTP servers are HTTP-compliant and some are even
suspicious of normal headers. Use careful-requests if you still want to use the
excellent Requests module.

.. _`Requests`: http://python-requests.org/

Example usage
----------

here you go

.. code-block:: python

    from careful_requests import Careful

    s = Careful()

    >>> s.get("http://httpbin.org/get", omit_headers=["accept-encoding"])
    <Response [200]>

Install
----------

.. code-block:: bash

    sudo pip install careful-requests

.. code-block:: bash

    sudo python setup.py install

Testing
----------

.. code-block:: bash

    make test

License
----------

BSD
