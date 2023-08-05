gears-uglifyjs
==============

UglifyJS_ compressor for Gears_. This package already includes the UglifyJS
source code for you, so you don't need to worry about installing it yourself.

Bundled UglifyJS version: **1.3.3**

Installation
------------

Install ``gears-uglifyjs`` with pip::

    $ pip install gears-uglifyjs


Requirements
------------

``gears-uglifyjs`` requires node.js_ to be installed in your system.


Usage
-----

Add ``gears_uglifyjs.UglifyJSCompressor`` to ``environment``'s compressors
registry::

    from gears_uglifyjs import UglifyJSCompressor
    environment.compressors.register('application/javascript', UglifyJSCompressor.as_handler())

If you use Gears in your Django project, add this code to its settings::

    GEARS_COMPRESSORS = {
        'application/javascript': 'gears_uglifyjs.UglifyJSCompressor',
    }

.. _UglifyJS: https://github.com/mishoo/UglifyJS
.. _Gears: https://github.com/gears/gears
.. _node.js: http://nodejs.org/
