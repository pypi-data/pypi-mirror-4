Pygments Image Examples
-----------------------

It is possible to generate image files from source code. Here is how to tell pygments to output a jpg::

    {{ d['dexy.yaml|idio|t']['jpg'] | indent(4) }}

.. image:: hello.py.jpg

And here's a png, this time without line numbers and using a custom font::

    {{ d['dexy.yaml|idio|t']['png'] | indent(4) }}

.. image:: hello.py.png

Here's a gif with the `bw` (black and white) style::

    {{ d['dexy.yaml|idio|t']['gif'] | indent(4) }}

.. image:: hello.py.gif

.. _Pygments Documentation: http://pygments.org/docs/formatters#imageformatter

Consult the `Pygments Documentation`_ for details about other options you can pass to these formatters.
