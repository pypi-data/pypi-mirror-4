..
    This file is part of lazr.delegates.

    lazr.delegates is free software: you can redistribute it and/or modify it
    under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, version 3 of the License.

    lazr.delegates is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
    License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with lazr.delegates.  If not, see <http://www.gnu.org/licenses/>.

=========================
Hacking on lazr.delegates
=========================

These are guidelines for hacking on the lazr.delegates project.  But first,
please see the common hacking guidelines at:

    http://dev.launchpad.net/Hacking


Getting help
------------

If you find bugs in this package, you can report them here:

    https://launchpad.net/lazr.delegates

If you want to discuss this package, join the team and mailing list here:

    https://launchpad.net/~lazr-developers

or send a message to:

    lazr-developers@lists.launchpad.net


Running the tests
=================

The tests suite requires nose_ and is compatible with both Python 2 and
Python 3.  To run the full test suite::

    $ python setup.py nosetests

Where ``python`` is the Python executable to use for the tests.  E.g. this
might be ``python3`` for Python 3, or the Python executable from a
virtualenv_.

.. _nose: https://nose.readthedocs.org/en/latest/
.. _virtualenv: http://www.virtualenv.org/en/latest/
