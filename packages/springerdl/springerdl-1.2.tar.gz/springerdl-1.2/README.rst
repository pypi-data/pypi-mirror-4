Springer Link Downloader
========================

A fork of `Thomas Vogt's "Springer Link Downloader"
<https://github.com/tuxor1337/springerdownload>`_. Adds easier installation
through a more standard ``setup.py`` and *SOCKS*-proxy support.

Installation
------------

Preferably in a `virtual environment
<https://pypi.python.org/pypi/virtualenv>`_, install using `PyPi
<https://pypi.python.org>`_::

   pip install springerdl

Usage
-----

``springerdl 978-0-8176-8325-2`` will fetch you "A Concise Introduction to
Linear Algebra". Note that the ISBN is the so-called "Online ISBN", which
differs from the print ISBN.

An interesting use-case is downloading books through an SSH tunnel, if your
university has access to SpringerLink but you at home haven't. Assuming you
have an SSH-account on ``student.hardknocks.edu``, you can set up an SSH-tunnel
like this::

   ssh -D 8888 username@student.hardknocks.edu

After that, open another terminal and run::

   springerdl -D 8888 978-0-8176-8325-2

This will connect through the SOCKS-tunnel created by SSH and will make the
download request look as if it was coming from your university.

Run ``springerdl --help`` for a list of options. Happy reading.

LICENSE
=======

Original Source (and therefore this derivation as well):

This program is free software; you can redistribute it and/or modify it under
the terms of VERSION 2 of the GNU General Public License as published by the
Free Software Foundation provided that the above copyright notice is included.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.

Go to http://www.gnu.org/licenses/gpl-2.0.html to get a copy of the license.
