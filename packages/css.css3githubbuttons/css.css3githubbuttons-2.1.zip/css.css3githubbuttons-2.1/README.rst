css.css3githubbuttons
*********************

Introduction
============

This library packages `CSS3 GitHub Buttons`_ for `fanstatic`_. Check out
a `demo`_ of this library - it's really nice. This library provides
the default buttons and various extensions as per the demo.  As a bonus, this
library also packages up minified versions of the library's CSS.

There's a *lot* of versions of this CSS library floating around,
so we're currently using the one provided by ``CodeFusion``, a fork
of the library originally provided by 
`necolas <https://github.com/necolas/css3-github-buttons>`_, on GitHub.

If development moves elsewhere, we can adjust the library accordingly.
If you're using this package and notice a change in development at
https://github.com/CodeFusion/css3-github-buttons/network (such as
someone has taken over development more than original author or is otherwise
doing more work) before we do, let us know or send a pull request.

Usage
=====

Install using your favourite method (``pip``, ``easy_install``, ``buildout``,
etc) and then in your code do this::

    import css.css3githubbuttons
    css.css3githubbuttons.buttons.need()

This requires integration between your web framework and ``fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory in ``css.css3githubbuttons``) are published to some URL.

For Pyramid, this can be as simple as installing and utilising 
`pyramid_fanstatic`_.

Extensions
----------

``CodeFusion`` has provided a number of improvements and extensions to the
original library.  This Fanstatic package provides access to these extensions
like so::

    from css.css3githubbuttons import buttons_ext_sizes, buttons_ext_icons, buttons_ext_all

For extra button sizes (see
http://demo.codefusionlab.com/css3-github-buttons/ext_button_size/index.html)::

    buttons_ext_sizes.need()

For extra (larger) icons (see
http://demo.codefusionlab.com/css3-github-buttons/ext_button_icons/index.html)::

    buttons_ext_icons.need()

Or for everything, do this::

    buttons_ext_all.need()

Keep in mind that extensions automatically depend on the original CSS so
you don't need to ``need()`` that again!

Updating this package
=====================

Given this package uses the latest (at the time of writing) GitHub master
of the CSS library, it may (will) need updating at some point.  

This process requires installation of the package for development - the
suggested method to do this is via the Buildout within this package::

    cd css.css3githubbuttons
    python boostrap.py
    ./bin/buildout

For minification of resources to succeed, you require a Java installation
as this process uses the YUI Compressor library (via the ``minify``
and ``yuicompressor`` Python packages).

Do this at the base of the repository::

    pushd css/css3githubbuttons/resources
    wget https://github.com/CodeFusion/css3-github-buttons/archive/master.tar.gz
    rm -rf css3-github-buttons
    tar xf master.tar.gz
    rm master.tar.gz
    git mv css3-github-buttons-master css3-github-buttons
    git add css3-github-buttons
    popd
    #Minify the CSS
    python setup.py minify_buttons
    python setup.py minify_buttons_ext_icons
    python setup.py minify_buttons_ext_size
    git commit -a -m "Updated to latest version"
    git push

Note
----

We could use Git submodules but setuptools seems to *hate* them,
``setuptools-git`` really doesn't want to agree with them,
``zest.releaser`` doesn't support recursive cloning (yet; pull request
sent), and so forth. Feel free to help improve this situation! Yikes!

So, let's resort to manually taking a copy of the files out of GitHub.

.. _`fanstatic`: http://fanstatic.org
.. _`CSS3 GitHub Buttons`: https://github.com/CodeFusion/css3-github-buttons
.. _`demo`: http://demo.codefusionlab.com/css3-github-buttons/
.. _`pyramid_fanstatic`: http://pypi.python.org/pypi/pyramid_fanstatic


