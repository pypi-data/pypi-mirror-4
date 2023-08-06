js.respond
**********

Introduction
============

This library packages `Respond.js`_ for `Fanstatic`_.

.. _`Fanstatic`: http://fanstatic.org
.. _`Respond.js`: https://github.com/scottjehl/Respond

This requires integration between your web framework and ``Fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory in ``js.respond``) are published to some URL.

Packaging
=========

The packaging is stored on GitHub at
https://github.com/davidjb/js.respond. If you happen to come
across a bug that corresponds to *packaging*, then please report it here. Pull
requests are more than welcome if you're fixing something yourself -- the more
help the better!

Any other bugs that relate to the library itself should be directed to the
original developers.

Updating this package
=====================

In order to obtain a newer version of this library, do the following::

    git clone git://github.com/davidjb/js.respond.git
    cd js.respond
    pushd js/respond/resources/
    wget https://github.com/scottjehl/Respond/raw/master/respond.src.js -O respond.src.js
    wget https://github.com/scottjehl/Respond/raw/master/respond.min.js -O respond.min.js
    #Edit version and change log
    git commit -a -m "Updated to git version v1.2.0"
    git push

If you're doing this out in your own fork of the GitHub repository, then send
through a pull request so everyone can benefit.

