gears-clean-css
===============

clean-css_ compressor for Gears_. This package already includes the clean-css
source code for you, so you don't need to worry about installing it yourself.

Bundled clean-css version: **0.6.0**

Installation
------------

Install ``gears-clean-css`` with pip::

    $ pip install gears-clean-css


Requirements
------------

``gears-clean-css`` requires node.js_ to be installed in your system.


Usage
-----

Add ``gears_clean_css.CleanCSSCompressor`` to ``environment``'s compressors
registry::

    from gears_clean_css import CleanCSSCompressor
    environment.compressors.register('text/css', CleanCSSCompressor.as_handler())

If you use Gears in your Django project, add this code to its settings::

    GEARS_COMPRESSORS = {
        'text/css': 'gears_clean_css.CleanCSSCompressor',
    }

.. _clean-css: https://github.com/GoalSmashers/clean-css
.. _Gears: https://github.com/gears/gears
.. _node.js: http://nodejs.org/
