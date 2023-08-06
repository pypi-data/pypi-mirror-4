js.jquery_jcrop
***************

Introduction
============

This library packages `jCrop`_ for `fanstatic`_.

.. _`fanstatic`: http://fanstatic.org
.. _`jCrop`: https://github.com/tapmodo/Jcrop/

This requires integration between your web framework and ``fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory in ``js.jquery_jcrop``) are published to some URL.

Packaging
=========

The packaging is stored on GitHub at
https://github.com/davidjb/js.jquery_jcrop. If you happen to come across a bug
that corresponds to *packaging*, then please report it here. Pull requests are
more than welcome if you're fixing something yourself -- the more help the
better!

Any other bugs that relate to the library itself should be directed to the
original developers.

Updating this package
---------------------

In order to obtain a newer version of `jCrop`_ for this library,
do the following::

    git clone https://github.com/davidjb/js.jquery_jcrop.git
    pushd js.jquery_jcrop/js/jquery_jcrop/resources
    wget https://github.com/tapmodo/Jcrop/tarball/v0.9.10 -O jcrop.tgz
    tar xf jcrop.tgz --strip=2
    rm -rf *.php *.html demo_files jcrop.tgz jquery.min.js
    popd
    #Edit changelog, setup.py for versions, etc
    git commit -a -m "Updated for release 0.9.10"
    git push

If you're doing this out in your own fork of the GitHub repository, then
send through a pull request so everyone can benefit.
