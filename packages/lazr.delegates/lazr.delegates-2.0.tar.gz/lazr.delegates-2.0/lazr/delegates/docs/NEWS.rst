=======================
NEWS for lazr.delegates
=======================

2.0 (2013-01-10)
================

- Port to Python 3, which requires the use of the ``@delegate_to`` class
  decorator instead of the ``delegates()`` function call.  Officially support
  Python 2.6, 2.7, 3.2, and 3.3.

1.2.0 (2010-07-16)
==================

- Extend Passthrough so that it takes an extra (optional) callable argument,
  used to adapt the context before accessing the delegated attribute.

1.1.0 (2009-08-31)
==================

- Remove build dependencies on bzr and egg_info

- remove sys.path hack in setup.py for __version__

1.0.1 (2009-03-24)
==================

- specify only v3 of LGPL

- build/developer improvements

1.0 (2008-12-19)
================

- Initial release
